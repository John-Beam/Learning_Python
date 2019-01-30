
#
# Диалог для ввода настроек сервера.
# Предлагает пользователю ввести настройки сервера (при первом запуске системы) и даёт возможность их изменить (при последующих запусках).
# Пишет логи в FILES[log_file].
#
# Первый запуск:
#   Считывает стандартные настройки филиалов ФНС из файла fns_branches.csv (см. FILES[fns_branches] ниже), при первом запуске можно выбрать один из филиалов.
#   Считывает соответствие города часовому поясу из файла city_map.csv (см. FILES[city_map]), пытается угадать часовой пояс филиала по его городу.
#
# Каждый раз:
#   После ввода настроек скрипт делает следующее:
#   1. Сохраняет пользовательский ввод в FILES[netparam_pre],
#   2. Применяет настройки, относящиеся к линукс-части (сетевые настройки, оракл), виндовс-часть не трогает.
#   3. Если всё прошло хорошо, то переносит файл FILES[netparam_pre] в FILES[netparam].
#
# Файл с пользовательским вводом:
#   Набор пар (ключ, значение), по одной на строку; строки отсортированы по ключу. Формат строки: <ключ>\t<значение> . Список актуальных ключей с описанием:
#   tm_ip . . . . . . . IP-адрес Traffic Monitor
#   tm_host . . . . . . Имя хоста Traffic Monitor
#   full_tm_host  . . . Имя хоста Traffic Monitor с доменным суффиксом
#   domain  . . . . . . Суффикс домена (Traffic Monitor)
#   dm_ip . . . . . . . IP-адрес Device Monitor
#   dm_host . . . . . . Имя хоста Device Monitor
#   mask  . . . . . . . Маска подсети
#   gateway . . . . . . IP-адрес шлюза
#   primary_dns . . . . IP-адрес первичного DNS-сервера
#   secondary_dns . . . IP-адрес вторичного DNS-сервера, может быть пустым
#   time_zone_offset  . Часовой пояс (например, "+04:00")
#   time_zone_linux . . Название часового пояса в линуксе (например, "Europe/Moscow"), см. TIME_ZONES
#   time_zone_windows . Название часового пояса в винде (например, "Russian Standard Time"), см. TIME_ZONES

import csv
import inspect
import json
import logging
import os
import re
import socket
import struct
import subprocess
import sys
import textwrap
import traceback

DIR_NAME = os.path.dirname(os.path.abspath(__file__))

FILES = {
        'fns_branches': os.path.join(DIR_NAME, 'fns_branches.csv'),
        'city_map': os.path.join(DIR_NAME, 'city_map.csv'),
        'netparam_pre': '/root/setup/netparam.preinit.cfg',
        'netparam': '/root/setup/netparam.cfg',
        'dialog_rc': '/tmp/dialog.rc',
        'last_error_file': '/root/setup/last_error',
        'log_file': '/tmp/dialog_server_config.log',
}

TIME_ZONES = {
        '+03:00': {'description': 'Калининградское время',  'linux': 'Europe/Minsk',        'windows': 'Kaliningrad Standard Time'},
        '+04:00': {'description': 'Московское время',       'linux': 'Europe/Moscow',       'windows': 'Russian Standard Time'},
        '+06:00': {'description': 'Екатеринбургское время', 'linux': 'Asia/Yekaterinburg',  'windows': 'Ekaterinburg Standard Time'},
        '+07:00': {'description': 'Омское время',           'linux': 'Asia/Omsk',           'windows': 'N. Central Asia Standard Time'},
        '+08:00': {'description': 'Красноярское время',     'linux': 'Asia/Krasnoyarsk',    'windows': 'North Asia Standard Time'},
        '+09:00': {'description': 'Иркутское время',        'linux': 'Asia/Irkutsk',        'windows': 'North Asia East Standard Time'},
        '+10:00': {'description': 'Якутское время',         'linux': 'Asia/Yakutsk',        'windows': 'Yakutsk Standard Time'},
        '+11:00': {'description': 'Владивостокское время',  'linux': 'Asia/Vladivostok',    'windows': 'Vladivostok Standard Time'},
        '+12:00': {'description': 'Магаданское время',      'linux': 'Asia/Magadan',        'windows': 'Magadan Standard Time'},
}

MESSAGES = {
        'error_external_command_failed': 'Внешняя команда завершилась неуспешно. Команда: {0}',

        'validate_ip': 'Поле должно содержать правильный IPv4-адрес.',
        'validate_required': ' Поле обязательно для заполнения.',
        'validate_please_fill': 'Пожалуйста, заполните поле {0}.',
        'validate_wrong_ip': 'Неправильное значение IP-адреса в поле {0}.',
        'validate_hostname': 'Поле должно содержать правильное имя хоста.',
        'validate_host_shorter_64_chars': 'Поле {0} должно быть короче 64 символов.',
        'validate_host_must_not_have_dots': 'Поле {0} не должно содержать точек.',
        'validate_wrong_host': 'Недопустимые символы в доменном имени в поле {0}.',
        'validate_domain': 'Поле должно содержать правильный доменный суффикс.',
        'validate_suffix_must_not_start_from_digit': 'Доменный суффикс в поле {0} не должны начинаться с цифры.',
        'validate_tm_and_gateway_in_same_net': 'Адреса Traffic Monitor и основного шлюза должны располагаться в пределах одной подсети.',
        'validate_tm_and_gateway_must_be_in_same_net': '{labels[tm_ip]} и {labels[gateway]} находятся в разных подсетях.',

        'apply_save_settings_to_tmp': 'Не удалось сохранить настройки сервера: {0}',
        'apply_set_tz': 'Не удалось установить часовой пояс: {0}',
        'apply_change_net_settings': 'Не удалось изменить настройки сети: {0}',
        'apply_apply_net_settings': 'Не удалось применить настройки сети: {0}',
        'apply_write_to_file': 'Ошибка при записи в файл {0}: {1!s}',
        'apply_switch_managment_console_to_br0': 'Не удалось переключить консоль управления на интерфейс br0: {0}',
        'apply_stop_db': 'Не удалось остановить базу данных: {0}',
        'apply_start_db': 'Не удалось запустить базу данных: {0}',
        'apply_save_settings': 'Не удалось сохранить настройки сервера: {0}',

        'text_user_cancel': 'Отменено пользователем',
        'text_will_run_next_time': 'Выбор сетевых настроек будет предложен при следующем запуске системы.',
        'text_boot_with_old_config': 'Система продолжит загрузку со старыми параметрами.',
        'text_change_settings_or_continue': 'Если какие-либо параметры поменялись, выберите <изменить настройки>.\nЧерез 60 секунд система продолжит загрузку с указанными параметрами.',
        'text_change_what_needed': 'Измените настройки сервера, которые поменялись.',
        'text_hit_esc_esc_to_discard': '\nЕсли Вы не хотите изменять настройки, нажмите два раза клавишу <\Z2ESC\Zn>.',
        'text_error_while_loading_branches': 'Произошла ошибка при построении списка филиалов. Введите сетевые настройки вручную.\n\nИсключение: {0}',
        'text_manual_input': 'Ввести вручную',
        'text_verify_settings': 'Проверьте настройки сервера для выбранного филиала. Если какие-то данные изменились, Вы можете их сейчас исправить.',
        'text_input_settings': 'Введите настройки сервера.',
        'text_choose_tz': 'Выберите часовой пояс из списка.',
        'text_user_cancel_ctrl_c': 'Отменено пользователем (Ctrl + C)',
        'text_failed_to_apply_server_settings': 'Не удалось применить настройки сервера. {0}',
        'text_unexpected_exception': 'Неожиданная ошибка. Исключение: {0}',
        'text_operation_interrupted': 'Операция прервана.\n\nПричина: {0}\n\n{1}',
        'text_error_while_reading_config': 'Произошла ошибка при чтении конфигурационного файла: {0}. Данные конфигурационного файла не будут использованы, необходимо заново настроить сервер.',
        'text_config_file_missing_field': 'В конфигурационном файле отсутствует или не заполнен обязательный параметр {0}',
        'text_server_needs_fixing': 'Сервер необходимо будет сконфигурировать заново.',

        'label_tm_ip': 'IP-адрес Traffic Monitor',
        'label_tm_host': 'Имя хоста Traffic Monitor',
        'label_dm_ip': 'IP-адрес Device Monitor',
        'label_dm_host': 'Имя хоста Device Monitor',
        'label_domain': 'Суффикс домена',
        'label_mask': 'Маска подсети',
        'label_gateway': 'IP-адрес шлюза',
        'label_primary_dns': 'Первичный DNS-сервер',
        'label_secondary_dns': 'Вторичный DNS-сервер',
        'label_time_zone_offset': 'Часовой пояс',

        'caption_backtitle': 'Настройка сервера',
        'caption_default_ok': 'Выбрать',
        'caption_accept': 'Принять',
        'caption_cancel_operation': 'Отменить операцию',
        'caption_operation_cancelled': 'Операция отменена',
        'caption_choose_fns_branch': 'Выберите отделение ФНС',
        'caption_server_settings': 'Настройки сервера',
        'caption_choose_tz': 'Выбор часового пояса',
        'caption_incorrect_value': 'Неверное значение',
        'caption_return': 'Вернуться',
        'caption_go_back': 'Назад',
        'caption_continue': 'Продолжить',
        'caption_error': 'Ошибка',
        'caption_proceed_without_changes': 'Продолжить без изменений',
        'caption_change_settings': 'Изменить настройки',
        'caption_have_settings_changed': 'Изменились ли настройки сервера?',

        'default_domain': 'regions.tax.nalog.ru',
}


def enum(**enums):
    return type('Enum', () , enums)

SEVERITY = enum(OK=0, INFO=1, WARN=2, ERROR=3)

GLOBAL_RESULT = {
        'on_error': {
                'severity': SEVERITY.ERROR,
                'message': MESSAGES['text_will_run_next_time'],
                'exit_code': 1,
        },
        'on_cancel': {
                'severity': SEVERITY.ERROR,
                'message': MESSAGES['text_will_run_next_time'],
                'exit_code': 1,
        },
        'on_ok': {
                'exit_code': 0,
        },
}

def ApplyNotFirstRunChanges():
    GLOBAL_RESULT['on_error']['message'] = MESSAGES['text_server_needs_fixing']
    GLOBAL_RESULT['on_cancel']['severity'] = SEVERITY.WARN
    GLOBAL_RESULT['on_cancel']['message'] = MESSAGES['text_boot_with_old_config']
    GLOBAL_RESULT['on_cancel']['exit_code'] = 0
    GLOBAL_RESULT['on_ok']['exit_code'] = 2

# Всякие няшки для логирования
def Dump(object):
    return json.dumps(object, ensure_ascii=False)

def Log(message, level=logging.DEBUG, exc_info=False):
    logging.log(level, message.decode('utf-8'), exc_info=exc_info, extra={'line': inspect.currentframe().f_back.f_lineno})

def InitLogging():
    try:
        logging.basicConfig(format=u'%(filename)s:%(line)-3d [%(levelname)-8s] %(asctime)s:  %(message)s', level=logging.DEBUG, filename=FILES['log_file'])
        Log('--- initialized ---', level=logging.INFO)
    except IOError:
        # Не смогли открыть файл --- обойдёмся без логов.
        pass

def System(command, critical=True):
    Log('Executing external command: %s' % command)

    if 0 != os.system(command):
        Log('Command failed! Critical = %s' % critical, level=logging.ERROR)

        if critical:
            raise ExternalCommandFailedException(MESSAGES['error_external_command_failed'].format(command))

def Dedent(string):
    return textwrap.dedent(string).lstrip('\n')

# Вспомогательные функции
def FixMask(mask):
    if not mask:
        return ''

    try:
        if '/' in mask or not '.' in mask:
            mask_int_match = re.search('([0-9]+)$', mask)
            if mask_int_match:
                mask_int = mask_int_match.group(1)

                return NumMaskToIp(int(mask_int))
        else:
            return GetComponent(mask, component=0)
    except:
        return mask

def GetComponent(initial, component=0, return_initial=True):
    try:
        this_component = initial.split()[component].strip(',').strip(';')

        if '/' in this_component:
            this_component = this_component[:this_component.find('/')]

        return this_component
    except:
        if return_initial:
            return initial
        else:
            return ''


def GetFNSBranches():
    city_map = ParseCityMap()

    try:
        fns_branches = []

        with open(FILES['fns_branches'], 'r') as fns_id_file:
            csv_reader = csv.reader(fns_id_file, delimiter=',', quotechar='"')

            # Первые строки --- информация
            for skip in xrange(2):
                csv_reader.next()

            for row in csv_reader:
                address = row[1]

                time_zone = None

                short_address = address.lstrip('0123456789 ,').decode('utf-8')

                if short_address.startswith(u'г.'):
                    short_address = short_address[2:]

                short_address = short_address.lstrip()

                for city in city_map:
                    if short_address.startswith(city.decode('utf-8')):
                        time_zone = city_map[city]

                Log('Address: {0}, time zone offset: {1}'.format(address, time_zone))

                if not time_zone:
                    Log('Нет часового пояса для адреса {0} ({1})'.format(address, short_address.encode('utf-8')), level=logging.WARNING)

                fns_branch = {
                    'name': row[0],
                    'address': address,
                    'city': city,
                    'time_zone_offset': time_zone,
                    'mask': FixMask(row[2]),
                    'gateway': GetComponent(row[3], 0),
                    'tm_ip': GetComponent(row[5]),
                    'dm_ip': GetComponent(row[6]),
                    'tm_host': GetComponent(row[7], 0),
                    'dm_host': GetComponent(row[8], 0),
                    'primary_dns': GetComponent(row[4], 0, return_initial=False),
                    'secondary_dns': GetComponent(row[4], 1, return_initial=False),
                    'domain': MESSAGES['default_domain'],
                }

                fns_branches.append(fns_branch)

        Log('Parsed FNS branches')

        return fns_branches
    except:
        Log('Failed to parse FNS branches', exc_info=True)
        raise

def ParseCityMap():
    try:
        city_map = {}

        with open(FILES['city_map'], 'r') as fns_id_file:
            csv_reader = csv.reader(fns_id_file, delimiter=',', quotechar='"')

            csv_reader.next()

            for row in csv_reader:
                city_map[row[0]] = row[1]

        Log('Parsed city map')

        return city_map
    except:
        Log('Failed to parse city map', exc_info=True)
        return {}

def DialogRc(severity):
    screen_colors_for_severity = {
            SEVERITY.OK:    'WHITE, GREEN',
            SEVERITY.INFO:  'WHITE, BLUE',
            SEVERITY.WARN:  'WHITE, YELLOW',
            SEVERITY.ERROR: 'WHITE, RED',
    }

    contents = 'screen_color = ({0}, ON)\n'.format(screen_colors_for_severity[severity])

    for dialog_type in ('', 'inputbox_', 'menubox_'):
        contents += '{0}border_color = (BLACK, WHITE, ON)\n'.format(dialog_type)

    try:
        open(FILES['dialog_rc'], 'w').write(contents)
    except:
        pass

    env = os.environ.copy()
    env['DIALOGRC'] = FILES['dialog_rc']

    return env


class DialogException(Exception):
    def __init__(self, message, code):
        Exception.__init__(self, message)
        self.code = code

class ExternalCommandFailedException(Exception):
    pass

class FailedToApplyServerConfigException(Exception):
    pass

class RequiredSettingMissingException(Exception):
    pass

class GoBackException(Exception):
    pass

class ValidationException(Exception):
    def __init__(self, message, hint, index=0):
        self.message = message
        self.hint = hint
        self.index = index

class ThisIsNotFirstRunAndUserConfirmedSettings(Exception):
    pass

class Builder:
    def Options(self):
        if not hasattr(self, 'options'):
            return []

        return self.options

    def Type(self):
        return '--' + self.__class__.__name__[:-7].lower()

    def Debug(self):
        return {'type': self.Type(), 'options': self.Options()}

    def ProcessAndValidate(self, user_input):
        return user_input

class MenuBuilder(Builder):
    def __init__(self):
        self.options = [0]

    def Item(self, key, value):
        self.options += [key, value]
        return self

    def ProcessAndValidate(self, user_input):
        return user_input.rstrip()

class MsgboxBuilder(Builder):
    pass

class PauseBuilder(Builder):
    def __init__(self, timeout):
        self.options = [timeout]

class FormBuilder(Builder):
    def __init__(self, values, edit_offset=30, edit_width=40):
        self.options = [0]

        self.values = values
        self.edit_offset = edit_offset
        self.edit_width = edit_width

        self.validators = []
        self.extra_validators = []
        self.names = []
        self.labels = []
        self.index = 1

    def Item(self, name, validator=None):
        label = MESSAGES['label_' + name]

        self.options += [label, self.index, 1, self.values.get(name, ''), self.index, self.edit_offset, self.edit_width, 0]
        self.names += [name]
        self.labels += [label]
        self.validators += [validator]
        self.index += 1

        return self

    def Separator(self):
        self.index += 1
        return self

    def ExtraValidator(self, validator):
        self.extra_validators += [validator]
        return self

    def ProcessAndValidate(self, user_input):
        Log('User input: ' + repr(user_input))

        user_input_list = user_input.split('\n')

        for index in range(len(self.labels)):
            self.options[8 * index + 4] = user_input_list[index] # Обновляем опцию, чтобы показать пользователю его ввод при перерисовке

        structured_user_input = {}

        for index in range(len(self.labels)):
            validator = self.validators[index]
            label = self.labels[index]
            name = self.names[index]

            value = user_input_list[index]
            structured_user_input[name] = value

            if validator:
                validator_message = validator(value)

                if validator_message is not None:
                    raise ValidationException(validator_message[0].format('\Zb' + label + '\Zn'), validator_message[1], index)

        structured_labels = dict((self.names[index], '\Zb' + self.labels[index] + '\Zn') for index in range(len(self.names)))
        for validator in self.extra_validators:
            validator_message = validator(structured_user_input)

            if validator_message is not None:
                raise ValidationException(validator_message[0].format(labels=structured_labels), validator_message[1])

        return structured_user_input

class TableCreator():
    def __init__(self, values_dict, first_column_width):
        self.values = values_dict
        self.line_format = u'{0:%s} {1}\n' % first_column_width

        self.result = ''

    def Row(self, name, required=True):
        if required and (name not in self.values or not self.values[name]):
            raise RequiredSettingMissingException(MESSAGES['text_config_file_missing_field'].format(MESSAGES['label_' + name]))

        # Метку надо перевести в уникод, чтобы правильно считалась ширина столбца
        label_unicode = MESSAGES['label_' + name].decode('utf-8')
        value = self.values[name]

        if not value:
            value = u'(отсутствует)'

        self.result += self.line_format.format(label_unicode, value).encode('utf-8')

    def Separator(self):
        self.result += '\n'

def Table(values_dict, line_format, names):
    table = TableCreator(values_dict, line_format)

    for name in names:
        if name:
            table.Row(name.lstrip('?'), not name.startswith('?'))
        else:
            table.Separator()

    return table.result

def ValidateIp(address, required=True):
    hint = MESSAGES['validate_ip'] + (MESSAGES['validate_required'] if required else '')

    if not address:
        return (MESSAGES['validate_please_fill'], hint)

    try:
        socket.inet_pton(socket.AF_INET, address)
    except socket.error:
        return (MESSAGES['validate_wrong_ip'], hint)

def ValidateIpOptional(address):
    if not address:
        return

    return ValidateIp(address, required=False)

def ValidateHost(hostname):
    hint = MESSAGES['validate_hostname'] + MESSAGES['validate_required']

    if not hostname:
        return (MESSAGES['validate_please_fill'], hint)

    if len(hostname) > 63:
        return (MESSAGES['validate_host_shorter_64_chars'], hint)

    if '.' in hostname:
        return (MESSAGES['validate_host_must_not_have_dots'], hint)

    if not re.match('(?!-)[a-zA-Z\d-]{1,63}(?<!-)$', hostname):
        return (MESSAGES['validate_wrong_host'], hint)

def ValidateDomain(domain):
    hint = MESSAGES['validate_domain'] + MESSAGES['validate_required']

    if not domain:
        return (MESSAGES['validate_please_fill'], hint)

    if re.match('\d', domain):
        return (MESSAGES['validate_suffix_must_not_start_from_digit'], hint)

def IpToNum(ip):
    return struct.unpack('<L', socket.inet_aton(ip))[0]

def NumMaskToIp(num):
    return socket.inet_ntoa(struct.pack('>L', 0xFFFFFFFF & (0xFFFFFFFF << (32 - num))))

def ValidateIpsInNet(server_config):
    hint = MESSAGES['validate_tm_and_gateway_in_same_net']

    mask = IpToNum(server_config['mask'])

    tm_ip = IpToNum(server_config['tm_ip'])
    gateway = IpToNum(server_config['gateway'])

    if tm_ip & mask != gateway & mask:
        return (MESSAGES['validate_tm_and_gateway_must_be_in_same_net'], hint)

def GetServerConfigFromFile(file_path):
    server_config = {}

    with open(file_path, 'r') as config_file:
        for line in config_file:
            try:
                fields = line.rstrip('\n').split('\t', 1)

                server_config[fields[0]] = fields[1]
            except:
                pass

    return server_config

def ApplyServerConfig(server_config):
    # Для начала сохраним все наши настройки во временный файл.
    try:
        dir_netparam = os.path.dirname(os.path.abspath(FILES['netparam_pre']))
        if not os.path.exists(dir_netparam):
            os.makedirs(dir_netparam)

        net_line = '{0}\t{1}\n'
        with open(FILES['netparam_pre'], 'w') as netparam:
            for key in sorted(server_config.keys()):
                netparam.write(net_line.format(key, server_config[key]))
    except Exception as error:
        raise FailedToApplyServerConfigException(MESSAGES['apply_save_settings_to_tmp'].format(error))

    # Устанавливаем часовой пояс
    try:
        os.remove('/etc/localtime')
    except:
        pass

    try:
        os.symlink('/usr/share/zoneinfo/{time_zone_linux}'.format(**server_config), '/etc/localtime')
    except Exception as error:
        raise FailedToApplyServerConfigException(MESSAGES['apply_set_tz'].format(error))

    # Подготавливаем сеть
    try:
        System('sed -i "s/dhcp/none/" /etc/sysconfig/network-scripts/ifcfg-eth0')
        System('sed -i "s/dhcp/none/" /etc/sysconfig/network-scripts/ifcfg-eth1')
        System('sed -i "/BRIDGE/d" /etc/sysconfig/network-scripts/ifcfg-eth0')
        System('echo "BRIDGE=br0" >> /etc/sysconfig/network-scripts/ifcfg-eth0')
        System('sed -i "s/ONBOOT=no/ONBOOT=yes/" /etc/sysconfig/network-scripts/ifcfg-eth0')
        System('sed -i "s/ONBOOT=no/ONBOOT=yes/" /etc/sysconfig/network-scripts/ifcfg-eth1')
    except Exception as error:
        raise FailedToApplyServerConfigException(MESSAGES['apply_change_net_settings'].format(error))

    # Останавливаем оракл
    try:
        System('service oracle stop')
    except Exception as error:
        raise FailedToApplyServerConfigException(MESSAGES['apply_stop_db'].format(error))

    # Теперь создаём кучу наших файлов
    rules = {
            '/etc/sysconfig/network': Dedent('''
                NETWORKING=yes
                HOSTNAME={full_tm_host}
            '''),
            '/etc/hosts': Dedent('''
                127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
                ::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
                {tm_ip}     {full_tm_host} {tm_host}
                172.172.172.1   {full_tm_host} {tm_host}
            '''),
            '/etc/resolv.conf': Dedent('''
                search      {domain}
                nameserver  {primary_dns}
            ''') + \
                ('nameserver  {secondary_dns}\n' if server_config['secondary_dns'] else ''), # Если есть secondary_dns, то добавляем его тоже
            '/etc/sysconfig/network-scripts/ifcfg-br0': Dedent('''
                DEVICE=br0
                TYPE=Bridge
                IPADDR={tm_ip}
                NETMASK={mask}
                GATEWAY={gateway}
                USERCTL=no
                IPV6INIT=no
                ONBOOT=yes
                BOOTPROTO=none
            '''),
            '/etc/sysconfig/network-scripts/ifcfg-br1': Dedent('''
                DEVICE=br1
                TYPE=Bridge
                IPADDR=172.172.172.1
                NETMASK=255.255.255.252
                USERCTL=no
                IPV6INIT=no
                ONBOOT=yes
                BOOTPROTO=none
            '''),
            '/u01/app/oracle/product/db_1/network/admin/tnsnames.ora': Dedent('''
                # tnsnames.ora Network Configuration File: /u01/app/oracle/product/db_1/network/admin/tnsnames.ora
                # Generated by Oracle configuration tools.

                IWTM =
                  (DESCRIPTION =
                    (ADDRESS = (PROTOCOL = TCP)(HOST = {full_tm_host})(PORT = 1521))
                      (CONNECT_DATA =
                        (SERVER = DEDICATED)
                        (SERVICE_NAME = iwtm)
                      )
                  )
            '''),
            '/u01/app/oracle/product/db_1/network/admin/listener.ora': Dedent('''
                # listener.ora Network Configuration File: /u01/app/oracle/product/db_1/network/admin/listener.ora
                # Generated by Oracle configuration tools.

                SID_LIST_LISTENER=
                  (SID_LIST=
                    (SID_DESC=
                      (GLOBAL_DBNAME=iwtm)
                      (ORACLE_HOME=/u01/app/oracle/product/db_1)
                      (SID_NAME=iwtm)
                    )
                  )

                LISTENER =
                  (DESCRIPTION_LIST =
                    (DESCRIPTION =
                      (ADDRESS = (PROTOCOL = IPC)(KEY = EXTPROC1521))
                      (ADDRESS = (PROTOCOL = TCP)(HOST = {full_tm_host})(PORT = 1521))
                     )
                  )
            '''),
    }

    for file_path, content in rules.items():
        try:
            file_content = content.format(**server_config)
            open(file_path, 'w').write(file_content)
        except Exception as error:
            raise FailedToApplyServerConfigException(MESSAGES['apply_write_to_file'].format(file_path, error))

    # Меняем имя хоста полностью
    try:
        System("hostname {full_tm_host}".format(**server_config))
    except Exception as error:
        raise FailedToApplyServerConfigException(MESSAGES['apply_switch_managment_console_to_br0'].format(error))

    # Трешак: везде, кроме как в 242-й строке надо поменять eth0 на br0
    try:
        System("sed -i '242 ! s/eth0/br0/' /var/www/html/config.php")
    except Exception as error:
        raise FailedToApplyServerConfigException(MESSAGES['apply_switch_managment_console_to_br0'].format(error))

    # Теперь перезапустим сеть
    try:
        System('service network reload')
    except Exception as error:
        raise FailedToApplyServerConfigException(MESSAGES['apply_apply_net_settings'].format(error))

    # И оракл
    try:
        System('service oracle restart')
    except Exception as error:
        raise FailedToApplyServerConfigException(MESSAGES['apply_start_db'].format(error))

    # Всё отработало хорошо, переносим настройки из временного файла
    try:
        os.rename(FILES['netparam_pre'], FILES['netparam'])
    except Exception as error:
        raise FailedToApplyServerConfigException(MESSAGES['apply_save_settings'].format(error))


def Dialog(dialog_builder, title='', text='', ok_label=MESSAGES['caption_default_ok'], cancel_label=MESSAGES['caption_cancel_operation'], noexcept=False, default_item=None, severity=SEVERITY.OK, back_action=False, height=0, width=0):
    validation_succeeded = False

    while not validation_succeeded:
        Log('Dialog builder: ' + Dump(dialog_builder.Debug()))

        all_dialog_options = [
                'dialog',
                '--colors',
                '--no-collapse',
                '--default-item', default_item if default_item else '0',
                '--backtitle', MESSAGES['caption_backtitle'],
                '--title', title,
                '--ok-label', ok_label,
                '--yes-label', ok_label,
                '--cancel-label', cancel_label,
                '--no-label', cancel_label,
        ] + (['--extra-button', '--extra-label', MESSAGES['caption_go_back']] if back_action else []) + [
                dialog_builder.Type(),
                text, height, width
        ]

        all_dialog_options += dialog_builder.Options()

        all_dialog_options = [str(x) for x in all_dialog_options]

        Log('All dialog options: ' + Dump(all_dialog_options))

        dialog = subprocess.Popen(all_dialog_options, stderr=subprocess.PIPE, env=DialogRc(severity))
        (stderr, stdout) = dialog.communicate()
        exit_code = dialog.wait()

        if exit_code != 0:
            Log('Dialog returned non-zero code: {0}, stdout: {1}, stderr: {2}'.format(exit_code, stdout, stderr), logging.ERROR)

            if noexcept:
                return None

            if exit_code > 255: # Диалог завершился по сигналу
                raise KeyboardInterrupt

            if exit_code == 3: # Нажали дополнительную кнопку, у нас это "Назад".
                raise GoBackException()

            raise DialogException(MESSAGES['text_user_cancel'], exit_code)

        try:
            return dialog_builder.ProcessAndValidate(stdout)
        except ValidationException as error:
            default_item = error.index

            Dialog(
                    MsgboxBuilder(),
                    title = MESSAGES['caption_incorrect_value'],
                    text = '\n{0}\n\n{1}'.format(error.message, error.hint),
                    noexcept = True,
                    ok_label = MESSAGES['caption_return'],
                    severity = SEVERITY.WARN,
            )

FORM_STATE = {}

def FormInitialChoose():
    common_comment = ''
    config_comment = MESSAGES['text_input_settings']

    # Если есть актуальный файл с настройками сервера, то его и используем.
    server_config = {}
    try:
        server_config = GetServerConfigFromFile(FILES['netparam'])

        # Показываем настройки пользователю
        comment = MESSAGES['text_change_settings_or_continue']

        settings_str = '\n\n' + Table(server_config, 30, ['tm_ip', 'tm_host', '', 'dm_ip', 'dm_host', '', 'domain', 'mask', 'gateway', '', 'primary_dns', '?secondary_dns', '', 'time_zone_offset'])
        settings_str += '\n' * 5 # Это бага в dialog: на обратный отсчёт не резервируется место.

        ApplyNotFirstRunChanges()

        try:
            Dialog(
                    PauseBuilder(60),
                    title = MESSAGES['caption_have_settings_changed'],
                    text = comment + settings_str,
                    cancel_label = MESSAGES['caption_change_settings'],
                    ok_label = MESSAGES['caption_proceed_without_changes'],
            )
        except Exception:
            # Пользователь нажал "Изменить настройки"
            Log('User wants to change settings', exc_info=True)
            config_comment = MESSAGES['text_change_what_needed']
            common_comment = MESSAGES['text_hit_esc_esc_to_discard']
        else:
            Log('User confirmed settings')
            raise ThisIsNotFirstRunAndUserConfirmedSettings()
    except IOError as error: # Не прочёлся netparam.cfg
        pass
    except RequiredSettingMissingException as error: # Нет какого-либо обязательного поля
        Dialog(
                MsgboxBuilder(),
                title = MESSAGES['caption_error'],
                text = MESSAGES['text_error_while_reading_config'].format(error),
                noexcept = True,
                ok_label = MESSAGES['caption_continue'],
                severity = SEVERITY.WARN,
        )

    if not server_config:
        fns_branches = []
        try:
            fns_branches = GetFNSBranches()
        except:
            Dialog(
                    MsgboxBuilder(),
                    title = MESSAGES['caption_error'],
                    text = MESSAGES['text_error_while_loading_branches'].format(sys.exc_info()[1]),
                    noexcept = True,
                    ok_label = MESSAGES['caption_continue'],
                    severity = SEVERITY.WARN,
            )

        # Узнаём у пользователя филиал, если есть список филиалов
        if fns_branches:
            fns_id_menu = MenuBuilder()
            for index, fns_branch in enumerate(fns_branches):
                fns_id_menu.Item(index, fns_branch['name'])

            fns_id_menu.Item('-', MESSAGES['text_manual_input'])

            chosen_fns_id = Dialog(
                    fns_id_menu,
                    title = MESSAGES['caption_choose_fns_branch'],
                    default_item = FORM_STATE.get('fns_branch_index', None),
            )

            if chosen_fns_id != '-':
                server_config = fns_branches[int(chosen_fns_id)]
                config_comment = MESSAGES['text_verify_settings']

            FORM_STATE['fns_branch_index'] = chosen_fns_id

    FORM_STATE['server_config'] = server_config
    FORM_STATE['config_comment'] = config_comment
    FORM_STATE['common_comment'] = common_comment

    return FormInputNetworkSettings()

def FormInputNetworkSettings():
    server_config = FORM_STATE['server_config']

    if 'tm_host' not in server_config:
        process = subprocess.Popen(['dmidecode', '-s', 'system-serial-number'], stdout=subprocess.PIPE)
        (serial, _) = process.communicate()
        process.wait()

        serial = serial.strip()

        server_config['tm_host'] = 'iwdb-{0}'.format(serial if serial else '0')
        server_config['domain'] = MESSAGES['default_domain']

    # Запрашиваем конфигурацию сервера
    try:
        new_server_config = Dialog(
                FormBuilder(server_config, edit_width=60)
                        .Item('tm_ip', ValidateIp)
                        .Item('tm_host', ValidateHost)
                        .Separator()
                        .Item('dm_ip', ValidateIp)
                        .Item('dm_host', ValidateHost)
                        .Separator()
                        .Item('domain', ValidateDomain)
                        .Item('mask', ValidateIp)
                        .Item('gateway', ValidateIp)
                        .Separator()
                        .Item('primary_dns', ValidateIp)
                        .Item('secondary_dns', ValidateIpOptional)
                        .ExtraValidator(ValidateIpsInNet),
                title = MESSAGES['caption_server_settings'],
                text = FORM_STATE['config_comment'] + FORM_STATE['common_comment'],
                ok_label = MESSAGES['caption_accept'],
                back_action = True,
        )
    except GoBackException:
        return FormInitialChoose()

    new_server_config['full_tm_host'] = new_server_config['tm_host'] + '.' + new_server_config['domain']

    server_config.update(new_server_config)

    FORM_STATE['server_config'] = server_config

    return FormSelectTimeZone()

def FormSelectTimeZone():
    server_config = FORM_STATE['server_config']

    time_zone_menu = MenuBuilder()
    for time_zone in sorted(TIME_ZONES.keys()):
        time_zone_menu.Item(time_zone, TIME_ZONES[time_zone]['description'])

    try:
        selected_time_zone_id = Dialog(
                time_zone_menu,
                title = MESSAGES['caption_choose_tz'],
                text = MESSAGES['text_choose_tz'] + FORM_STATE['common_comment'],
                default_item = server_config.get('time_zone_offset'),
                back_action = True,
        )
    except GoBackException:
        return FormInputNetworkSettings()

    time_zone = TIME_ZONES[selected_time_zone_id]
    server_config['time_zone_offset'] = selected_time_zone_id
    server_config['time_zone_linux'] = time_zone['linux']
    server_config['time_zone_windows'] = time_zone['windows']

    ApplyServerConfig(server_config)

    pass

def main():
    InitLogging()
    Log('main')

    FormInitialChoose()

    sys.exit(GLOBAL_RESULT['on_ok']['exit_code'])

try:
    main()
except SystemExit:
    raise
except ThisIsNotFirstRunAndUserConfirmedSettings:
    sys.exit(0) # Отказ от изменения настроек --- это как бы всё хорошо
except:
    Log('Cancelling operation', level=logging.ERROR, exc_info=True)

    error_info = sys.exc_info()

    error_type = error_info[0]
    error_text = str(error_info[1])

    critical_error = True

    if error_type == DialogException:
        critical_error = False
    elif error_type == KeyboardInterrupt:
        error_text += MESSAGES['text_user_cancel_ctrl_c']
        critical_error = False
    elif error_type == FailedToApplyServerConfigException:
        error_text = MESSAGES['text_failed_to_apply_server_settings'].format(error_text)
    else:
        error_text = MESSAGES['text_unexpected_exception'].format(error_text + '\n' + traceback.format_exc())

    result_struct = GLOBAL_RESULT['on_error' if critical_error else 'on_cancel']

    text = MESSAGES['text_operation_interrupted'].format(error_text, result_struct['message'])

    if critical_error:
        try:
            open(FILES['last_error_file'], 'w').write('%s\n' % error_text)
        except:
            pass

    severity = SEVERITY.ERROR

    Dialog(
            MsgboxBuilder(),
            title = MESSAGES['caption_operation_cancelled'],
            noexcept = True,
            text = text,
            ok_label = MESSAGES['caption_accept'],
            severity = result_struct['severity'],
    )

    print "\n\n%s" % text

    sys.exit(result_struct['exit_code'])

#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'dunin'


import time
import random
import os
from shutil import move
from smtplib import SMTP
from email import message_from_file
from datetime import datetime, timedelta
from string import punctuation

from cx_Oracle import connect

SMTP_SERVER = 'tm6'
SMTP_PORT = 25

ADDR_LIST = ['Ilya.Dunin@infowatch.com', 'Anton.Ezhkov@infowatch.com', 'Vladislav.Botvin@infowatch.com',
             'Ilya.Borisenkov@infowatch.com', 'Alexander.Bobrus@infowatch.com', 'Maxim.Popesku@infowatch.com',
             'Roman.Efremenko@infowatch.com', 'Eugeny.Gorlov@infowatch.com']

FROM = 'Ilya.Dunin@infowatch.com'
TO = ['Ilya.Borisenkov@infowatch.com', 'Alexander.Bobrus@infowatch.com']

DB_USER = 'iwtm'
DB_PASS = 'xx1234'
DB_CSTR = '10.60.21.72:1521/iwtm'


def get_random_from():
    return ADDR_LIST[random.randint(0, len(ADDR_LIST) - 1)]


def get_random_to():
    to_lst = []
    num = random.randint(1, len(ADDR_LIST))
    while num > 0:
        addr = ADDR_LIST[random.randint(0, len(ADDR_LIST) - 1)]
        if addr not in to_lst:
            to_lst.append(addr)
            num -= 1
    return to_lst


def send_email(msg):
    try:
        s = SMTP(SMTP_SERVER, SMTP_PORT)
        s.sendmail(FROM, TO, msg.as_string())
        s.close()
    except Exception as exc:
        print 'Cannot send letter: %s' % exc


def open_eml(feml):
    try:
        with open(feml) as f:
            msg = message_from_file(f)
    except Exception as exc:
        print 'Cannot open eml: %s' % exc
        return None

    return msg


def get_objects_count():
    conn = connect(DB_USER, DB_PASS, DB_CSTR)
    curr = conn.cursor()
    curr.execute('select count(*) from object')
    obj_count = curr.fetchone()[0]
    curr.close()
    conn.close()
    return obj_count


def get_last_id_desc():
    conn = connect(DB_USER, DB_PASS, DB_CSTR)
    curr = conn.cursor()
    curr.execute('select object_id, description from (select * from object order by object_id desc) where rownum < 2')
    res = curr.fetchone()
    curr.close()
    conn.close()
    return res[0], res[1]


def get_all_eml(path):
    for f in os.listdir(path):
        full_path = os.path.join(path, f)
        if os.path.isfile(full_path):
            yield full_path


def rename_eml(old_fn):
    new_fn = old_fn.replace('.eml', '')

    for ch in punctuation:
        new_fn = new_fn.replace(ch, '')

    os.rename(old_fn, new_fn + '.eml')


def find_and_move(base_dir, test_name):
    queue_path = '/opt/iw/tm5/queue'
    results_path = os.path.join(base_dir, test_name)
    xml_found = False
    dat_found = False

    # Create dir for results
    if not os.path.exists(results_path):
        os.makedirs(results_path)

    t = 0
    while t < 15 or not (xml_found and dat_found):
        # Find and move files
        for root, dirs, files in os.walk(queue_path):
            for f in files:
                if f.endswith(".xml"):
                    move(os.path.join(root, f), os.path.join(results_path, f))
                    xml_found = True
                if f.endswith('*.dat'):
                    move(os.path.join(root, f), os.path.join(results_path, f))
                    dat_found = True

        time.sleep(1)



def main2(path):
    for f in get_all_eml(path):
        #print '--- %s ---' % f

        msg = open_eml(f)
        send_email(msg)

        #time.sleep(1)
        #find_and_move('old_mime', os.path.basename(f).replace('.eml', ''))


def main(path):
    for f in get_all_eml(path):
        #print '--- %s ---' % f
        #count_before = get_objects_count()

        msg = open_eml(f)
        send_email(msg)

        #timeout = datetime.now() + timedelta(0, 10)
        # object_in_db = False
        # while datetime.now() < timeout:
        #     count_after = get_objects_count()
        #     if count_after > count_before:
        #         object_in_db = True
        #         break

        # if not object_in_db:
        #     print 'Possible core dump or other errors on: %s' % f
        #     continue

        #time.sleep(1)


if __name__ == '__main__':
    for i in range(1000000):
        eml_path = 'eml_test'
        main2(eml_path)
        print i
    #rename_eml(f)

    # msg = open_eml('eml_real/sample_compiler_errors_-_Morozova_Elena_Elena.Morozovainfowatch.com_-_2013-05-17_1431.eml')
    # send_email(msg)



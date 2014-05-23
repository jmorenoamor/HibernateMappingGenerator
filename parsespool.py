################################################################################
# -*- encoding: utf-8 -*-
################################################################################
import os
import re
import sys

################################################################################
# Logging
################################################################################
import logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)-7s - %(message)s',
    level=logging.INFO,
    datefmt='%Y/%m/%d %H:%M:%S'
)

with open("/cygdrive/c/cygwin/home/L0009813/GoogleDrive/12 IAL/Esquemas BBDD/Esquema_IAL") as f:

    tablas = list()

    lines = [line.strip() for line in f]

    for line in lines:
        if line:
            column = re.sub(r'\s+', ';', line).split(';')

            if column[2] == 'VARCHAR2':
                '<property name="%s" type="%s">' % (column[1], 'string')
                '<column name="%s" length="%s" not-null="%s" unique="false" />' % (
                    column[1],
                    column[4],
                    str(column[3] == 'Y').lower(),
                )
                '</property>'
            elif column[2] == 'CHAR':
                '<property name="%s" type="%s">' % (column[1], 'string')
                '<column name="%s" length="%s" not-null="%s" unique="false" />' % (
                    column[1],
                    column[4],
                    str(column[3] == 'Y').lower(),
                )
                '</property>'
            elif column[2] == 'NUMBER':
                '<property name="%s" type="%s">' % (column[1], 'java.lang.Integer')
                '<column name="%s" not-null="%s" unique="false" />' % (
                    column[1],
                    str(column[3] == 'Y').lower(),
                )
                '</property>'
            elif column[2] == 'DATE':
                '<property name="%s" type="%s">' % (column[1], 'java.util.Date')
                '<column name="%s" not-null="%s" unique="false" />' % (
                    column[1],
                    str(column[3] == 'Y').lower(),
                )
                '</property>'
            else:
                print column

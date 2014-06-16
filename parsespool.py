################################################################################
# -*- encoding: utf-8 -*-
################################################################################
import os
import re
import sys
from inflection import *

################################################################################
# Logging
################################################################################
import logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)-7s - %(message)s',
    level=logging.INFO,
    datefmt='%Y/%m/%d %H:%M:%S'
)

def generate_xml(lines):
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

getter_method = """  public %s get%s()
  {
    return %s;
  }

"""

setter_method = """  public void set%s(%s %s)
  {
    this.%s = %s;
  }

"""

def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def generate_annotations(lines):
    missing = list()
    methods = list()
    last_table = ""
    fw = None

    for line in lines:

        if line:
            column = re.sub(r'\s+', ';', line).split(';')

            C_TABLA = column[0]
            C_NOMBRE = column[1]
            C_TIPO = column[2]
            C_NULLABLE = column[3]
            C_SIZE = column[4]

            if last_table != C_TABLA:
                if fw:
                    for method in methods:
                        fw.write(method + '\n')
                    methods = list()

                    fw.write('}' + '\n')
                    fw.close()

                fw = open('/tmp/{table}.java'.format(table=camelize(underscore(C_TABLA))), 'w')

                fw.write('package com.morenoamor.vodafone.ial;' + '\n')
                fw.write('' + '\n')
                fw.write('import javax.persistence.Column;' + '\n')
                fw.write('import javax.persistence.Entity;' + '\n')
                fw.write('import javax.persistence.GeneratedValue;' + '\n')
                fw.write('import javax.persistence.Id;' + '\n')
                fw.write('import javax.persistence.Table;' + '\n')
                fw.write('' + '\n')
                fw.write('@Entity' + '\n')
                fw.write('@Table(name="{table}")'.format(table=C_TABLA) + '\n')
                fw.write('public class {table}'.format(table=camelize(underscore(C_TABLA))) + '\n')
                fw.write('{' + '\n')

            last_table = C_TABLA

            if C_TIPO == 'VARCHAR2' or C_TIPO == 'CHAR':
                J_TIPO = "String"
                J_ATRIBUTO = camelize(underscore(C_NOMBRE))
                J_METODO = camelize(underscore(C_NOMBRE), False)

                fw.write('  @Column(name="%s", length=%s, nullable=%s)' % (C_NOMBRE, C_SIZE, str(C_NULLABLE == 'Y').lower()) + '\n')
                fw.write('  private %s %s;' % (J_TIPO, C_NOMBRE) + '\n')
                methods.append(getter_method % (J_TIPO, J_METODO, J_ATRIBUTO))
                methods.append(setter_method % (C_NOMBRE, J_TIPO, J_METODO, J_ATRIBUTO, J_ATRIBUTO))
            elif C_TIPO == 'NUMBER':
                fw.write('  @Column(name="%s", nullable=%s)' % (
                    C_NOMBRE,
                    str(C_NULLABLE == 'Y').lower(),
                ) + '\n')
                fw.write('  private int %s;' % (C_NOMBRE) + '\n')
                methods.append(getter_method % ('int', C_NOMBRE, C_NOMBRE))
                methods.append(setter_method % (C_NOMBRE, 'int', C_NOMBRE, C_NOMBRE, C_NOMBRE))
            elif C_TIPO == 'LONG':
                fw.write('  @Column(name="%s", nullable=%s)' % (
                    C_NOMBRE,
                    str(C_NULLABLE == 'Y').lower(),
                ) + '\n')
                fw.write('  private long %s;' % (C_NOMBRE) + '\n')
                methods.append(getter_method % ('long', C_NOMBRE, C_NOMBRE))
                methods.append(setter_method % (C_NOMBRE, 'long', C_NOMBRE, C_NOMBRE, C_NOMBRE))
            elif C_TIPO == 'DATE':
                fw.write('  @Column(name="%s", columnDefinition="DATE", nullable=%s)' % (
                    C_NOMBRE,
                    str(C_NULLABLE == 'Y').lower(),
                ) + '\n')
                fw.write('  private Date %s;' % (C_NOMBRE) + '\n')
                methods.append(getter_method % ('Date', C_NOMBRE, C_NOMBRE))
                methods.append(setter_method % (C_NOMBRE, 'Date', C_NOMBRE, C_NOMBRE, C_NOMBRE))
            elif C_TIPO == 'TIMESTAMP(':
                fw.write('  @Column(name="%s", columnDefinition="DATETIME", nullable=%s)' % (
                    C_NOMBRE,
                    str(C_NULLABLE == 'Y').lower(),
                ) + '\n')
                fw.write('  private Date %s;' % (C_NOMBRE) + '\n')
                methods.append(getter_method % ('Date', C_NOMBRE, C_NOMBRE))
                methods.append(setter_method % (C_NOMBRE, 'Date', C_NOMBRE, C_NOMBRE, C_NOMBRE))
            elif C_TIPO == 'CLOB':
                fw.write('  @Column(name="%s", nullable=%s)' % (
                    C_NOMBRE,
                    str(C_NULLABLE == 'Y').lower(),
                ) + '\n')
                fw.write('  @Lob(type = LobType.CLOB)' + '\n')
                fw.write('  private String %s;' % (C_NOMBRE) + '\n')
                methods.append(getter_method % ('String', C_NOMBRE, C_NOMBRE))
                methods.append(setter_method % (C_NOMBRE, 'String', C_NOMBRE, C_NOMBRE, C_NOMBRE))
            elif C_TIPO == 'BLOB':
                fw.write('  @Column(name="%s", nullable=%s)' % (
                    C_NOMBRE,
                    str(C_NULLABLE == 'Y').lower(),
                ) + '\n')
                fw.write('  @Lob(type = LobType.BLOB)' + '\n')
                fw.write('  private byte[] %s;' % (C_NOMBRE) + '\n')
                methods.append(getter_method % ('byte[]', C_NOMBRE, C_NOMBRE))
                methods.append(setter_method % (C_NOMBRE, 'byte[]', C_NOMBRE, C_NOMBRE, C_NOMBRE))
            else:
                missing.append(column)

        fw.write('' + '\n')

    for c in missing:
        print c

#with open("/cygdrive/c/cygwin/home/L0009813/GoogleDrive/12 IAL/Esquemas BBDD/Esquema_IAL") as f:
with open("/cygdrive/c/cygwin/home/L0009813/GoogleDrive/12 IAL/Esquemas BBDD/Esquema_Comanche") as f:

    tablas = list()

    lines = [line.strip() for line in f]

    generate_annotations(lines)

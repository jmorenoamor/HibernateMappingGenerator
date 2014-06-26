################################################################################
# -*- encoding: utf-8 -*-
################################################################################
import re
from inflection import *

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

getter_method = """  public {return_type} get{method_name}()
  {{
    return this.{attribute_name};
  }}
"""

setter_method = """  public void set{method_name}({attribute_type} {attribute_name})
  {{
    this.{attribute_name} = {attribute_name};
  }}
"""

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

                J_CLASE = camelize(underscore(C_TABLA))

                fw = open('/tmp/{table}.java'.format(table=J_CLASE), 'w')

                fw.write('' + '\n')
                fw.write('import javax.persistence.Column;' + '\n')
                fw.write('import javax.persistence.Entity;' + '\n')
                fw.write('import javax.persistence.GeneratedValue;' + '\n')
                fw.write('import javax.persistence.Id;' + '\n')
                fw.write('import javax.persistence.Table;' + '\n')
                fw.write('' + '\n')
                fw.write('@Entity' + '\n')
                fw.write('@Table(name="{table}")'.format(table=C_TABLA) + '\n')
                fw.write('public class {table}'.format(table=J_CLASE) + '\n')
                fw.write('{' + '\n')

            last_table = C_TABLA

            J_ATRIBUTO = camelize(underscore(C_NOMBRE.replace('FX_', 'FECHA_')), False)
            J_METODO = camelize(underscore(C_NOMBRE.replace('FX_', 'FECHA_')))
            J_TIPO = None

            if C_TIPO == 'VARCHAR2' or C_TIPO == 'CHAR':
                J_TIPO = "String"

            elif C_TIPO == 'NUMBER':
                J_TIPO = "int"

            elif C_TIPO == 'LONG':
                J_TIPO = "long"

            elif C_TIPO == 'DATE':
                J_TIPO = "Date"

            elif C_TIPO == 'TIMESTAMP(':
                J_TIPO = "Date"

            elif C_TIPO == 'CLOB':
                J_TIPO = "String"
                fw.write('  @Lob(type = LobType.CLOB)' + '\n')

            elif C_TIPO == 'BLOB':
                J_TIPO = "byte[]"
                fw.write('  @Lob(type = LobType.BLOB)' + '\n')
            else:
                missing.append(column)
                continue

            fw.write('  @Column(name="%s", length=%s, nullable=%s)' % (C_NOMBRE, C_SIZE, str(C_NULLABLE == 'Y').lower()) + '\n')
            fw.write('  private %s %s;' % (J_TIPO, J_ATRIBUTO) + '\n')
            methods.append(getter_method.format(return_type=J_TIPO, method_name=J_METODO, attribute_name=J_ATRIBUTO))
            methods.append(setter_method.format(method_name=J_METODO, attribute_type=J_TIPO, attribute_name=J_ATRIBUTO))

        fw.write('' + '\n')

    for c in missing:
        print c

with open("/cygdrive/c/cygwin/home/L0009813/GoogleDrive/12 IAL/Esquemas BBDD/Esquema_IAL") as f:
#with open("/cygdrive/c/cygwin/home/L0009813/GoogleDrive/12 IAL/Esquemas BBDD/Esquema_Comanche") as f:

    tablas = list()

    lines = [line.strip() for line in f]

    generate_annotations(lines)

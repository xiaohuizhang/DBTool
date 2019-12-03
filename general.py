#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2018/4/13 下午2:32
# @Author   : xhzhang
# @Site     : 
# @File     : general.py
# @Software : PyCharm
import getpass, socket, netifaces,re


def getCurrentSeq(db, tablename):
    """
    获取tablename当前的sequence值
    :param db: 数据库连接
    :param tablename: 表名
    :return:
    """
    sql = '''select seq from sqlite_sequence where name='%s';''' % (tablename)
    current_seq_list = db.exec_select(sql)
    if len(current_seq_list) == 0:
        return None
    else:
        return current_seq_list[0][0]


def getConnOneRecord(db, connid):
    """
    根据ID获取连接信息
    :param db: 数据库连接实例
    :param connid: 连接ID
    :return: tuple->(cname,pid,sid,suser,spassword)
    """
    sql = '''select cname,program_id,schema_id,schemauser,schemapass from conninfo where id=%d;''' % (connid)
    conn_record = db.exec_select(sql)
    if len(conn_record) == 1:
        return conn_record[0]
    else:
        return ()


def getConnAllRecord(db):
    """
    获取所有的连接信息
    :param db: 数据库连接实例
    :return: list->[(),(),()]
    """
    sql = '''select id,cname,program_id,schema_id,schemauser,schemapass from conninfo;'''
    conn_record = db.exec_select(sql)
    return conn_record


def getConnCurrentSeq(db):
    """
    获取conninfo表ID的当前sequnce值
    :param db:
    :return:
    """
    tablename = 'conninfo'
    return getCurrentSeq(db, tablename)


def insertConnRecord(db, cname, pid, sid, user, password):
    """
    插入一条连接记录
    :param db:
    :param record: (cname,pid,sid,user,password)
    :return:
    """
    sql = '''insert into conninfo values (NULL,'%s',%d,%d,'%s','%s');''' % (cname, pid, sid, user, password)
    r = db.exec_statement(sql)
    return r


def getProOneRecord(db, proid):
    """
    根据项目源ID获取该条记录
    :param db: 数据库连接实例
    :param proid: 项目源ID
    :return: ()
    """
    sql = '''select pname,driver,scriptdir from programinfo where id=%d;''' % (proid)
    pro_record = db.exec_select(sql)
    if len(pro_record) == 1:
        return pro_record[0]
    else:
        return ()


def getProAllRecord(db):
    """
    获取项目源所有记录
    :param db: 数据库连接实例
    :return: [(),(),()]
    """
    sql = '''select id,pname,driver,scriptdir from programinfo;'''
    pro_record = db.exec_select(sql)
    return pro_record


def getProCurrentSeq(db):
    """
    获取programinfo表ID的当前sequnce值
    :param db:
    :return:
    """
    tablename = 'programinfo'
    return getCurrentSeq(db, tablename)


def insertProRecord(db, pro_name, pro_driver, pro_script):
    """
    插入一条项目记录
    :param db: 数据库实例
    :param pro_name: 项目名称
    :param pro_driver: 项目驱动
    :param pro_script: 项目脚本
    :return:
    """
    sql = '''insert into programinfo VALUES (NULL,'%s','%s','%s');''' % (pro_name, pro_driver, pro_script)
    r = db.exec_statement(sql)
    return r


def getSchemaOneRecord(db, schemaid):
    """
    根据数据源ID获取该条记录
    :param db: 数据库连接实例
    :param proid: 数据源ID
    :return: ()
    """
    sql = '''select sname,host,port,servicename from schemainfo where id=%d;''' % (schemaid)
    schema_record = db.exec_select(sql)
    if len(schema_record) == 1:
        return schema_record[0]
    else:
        return ()


def getSchemaAllRecord(db):
    """
    获取数据源所有记录
    :param db: 数据库连接实例
    :return: [(),(),()]
    """
    sql = '''select id,sname,host,port,servicename from schemainfo;'''
    schema_record = db.exec_select(sql)
    return schema_record


def getSchemaCurrentSeq(db):
    """
    获取schemainfo表ID的当前sequnce值
    :param db:
    :return:
    """
    tablename = 'schemainfo'
    return getCurrentSeq(db, tablename)


def insertSchemaRecord(db, schema_name, schema_host, schema_port, schema_servicename):
    """
    插入一条数据源记录
    :param db: 数据库实例
    :param schema_name: 数据源名称
    :param schema_host: 数据库主机IP
    :param schema_port: 数据库端口
    :param schema_servicename: 数据库服务名
    :return:
    """
    sql = '''insert into schemainfo VALUES (NULL,'%s','%s',%d,'%s')''' % (
        schema_name, schema_host, int(schema_port), schema_servicename)
    r = db.exec_statement(sql)
    return r


def getOneRecordForAll(db, connid):
    """
    根据连接ID，查处该连接的所有信息
    :param db: 数据库连接实例
    :param connid: 连接ID
    :return:
    """
    pname, pdriver, pscriptdir = '', '', ''
    sname, shost, sport, servicename = '', '', '', ''

    one_record = getConnOneRecord(db, connid)
    cname = one_record[0]
    pid = one_record[1]
    sid = one_record[2]
    cuser = one_record[3]
    cpass = one_record[4]

    if pid is not None:
        pr = getProOneRecord(db, pid)
        if pr != ():
            pname, pdriver, pscriptdir = pr[0], pr[1], pr[2]

    if sid is not None:
        sr = getSchemaOneRecord(db, sid)
        if sr != ():
            sname, shost, sport, servicename = sr[0], sr[1], str(sr[2]), sr[3]

    return (connid, cname, cuser, cpass, pid, pname, pdriver, pscriptdir, sid, sname, shost, sport, servicename)


# 发送消息
def emitMessage(trigger, message):
    """
    发射信号
    :param trigger: 信号
    :param message: 信息
    :return:
    """
    if trigger is not None:
        if isinstance(message, str) and message != '':
            trigger.emit(message)
        elif isinstance(message, tuple) and message[0] != '':
            trigger.emit(message[0], message[1])


def getLocalInfo():
    """
    获取本地主机信息
    :return:
    """
    routingIPAddr, hostname, loginuser = '0.0.0.0', '', ''
    routingNicName = netifaces.gateways()['default'][netifaces.AF_INET][1]

    for interface in netifaces.interfaces():
        if interface == routingNicName:
            try:
                routingIPAddr = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
            except KeyError:
                pass
    try:
        hostname = socket.gethostname()
    except Exception:
        pass

    try:
        loginuser = getpass.getuser()
    except Exception:
        pass
    return routingIPAddr, hostname, loginuser


def IsIp(checkIP):
    """
    校验IP格式是否正确
    :param checkIP: 需要校验的IP字符串
    :return:
    """
    compile_ip = re.compile(
        '^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
    if compile_ip.match(checkIP):
        return True
    else:
        return False


def IsDomain(checkDomain):
    """
    校验是否为域名
    :param checkDomain:
    :return:
    """
    domain_regex = re.compile(
        r'(?:[A-Z0-9_](?:[A-Z0-9-_]{0,247}[A-Z0-9])?\.)+(?:[A-Z]{2,6}|[A-Z0-9-]{2,}(?<!-))\Z',
        re.IGNORECASE)
    return True if domain_regex.match(checkDomain) else False

def IsDigit(checkPort):
    """
    校验端口是否为数字
    :param checkPort:
    :return:
    """
    if type(eval(checkPort)) == int:
        return True
    else:
        return False
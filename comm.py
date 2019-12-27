#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2019/12/3 17:14
# @Author   : xhzhang
# @Site     : 
# @File     : comm.py
# @Software : PyCharm

import getpass, socket, netifaces, re

SQLITE3_DB_NAME = 'source.db'
LOG_DIR = 'dbtool.log'
DBMSVersion = '1.3'

REMOTE_RECORD_HOST = '192.168.1.41'
REMOTE_RECORD_SERVICENAME = 'afis'
REMOTE_RECORD_SCHEAMUSER = 'dboper_record'
REMOTE_RECORD_SCHEAMPASS = 'afis2018'
REMOTE_INSERT_SQL = '''insert into operate_record VALUES (SEQ_OPERATE_RECORD.NEXTVAL,'{0[0]}','{0[1]}','{0[2]}','{0[3]}','{0[4]}','{0[5]}',sysdate)'''

Driver_Type = ["oracle", "mysql"]
NormalMessage = 0
ErrorMessage = 1
WarningMessage = 2

# schema_info: if driver is oracle,Detail is sid; if driver is mysql,Detail is user&password
# conn_info:   if driver is oracle,Detail is schema_user&schema_pass ; if driver is mysql ,Detail is db name.
INIT_DB_SQL = [
    '''create table if not exists projects
    (
      ID       INTEGER not null PRIMARY key AUTOINCREMENT,
      Name     VARCHAR(100) unique not null,
      Script   VARCHAR(300) not null
    );''',
    '''create table if not exists datasources
    (
      ID          INTEGER not null PRIMARY KEY AUTOINCREMENT,
      Name        VARCHAR(100) unique not null,
      Driver      VARCHAR(20),
      Host        VARCHAR (20) not null,
      Port        int DEFAULT 1521,
      Other       VARCHAR (120)
    );''',
    '''create table if not exists connections
    (
      ID          INTEGER not null PRIMARY KEY AUTOINCREMENT,
      Name        VARCHAR (300) unique not null,
      ProjectId   INTEGER,
      SchemaId    INTEGER,
      ConnDetail   VARCHAR (120),
      FOREIGN KEY (ProjectId) REFERENCES projects(ID) ON delete SET NULL ON UPDATE SET NULL,
      FOREIGN KEY (SchemaId) REFERENCES datasources(ID) ON delete SET NULL ON UPDATE SET NULL
    );''',
    '''create table if not exists version
     (
        Version   VARCHAR (20)  not null
    );''']

def getAllTables(db):
    """
    获取所有的表名
    :param db:
    :return:
    """
    tableNames = []
    sql = '''select name from sqlite_master where type='table' And name != "sqlite_sequence";'''
    tables = db.executeQuery(sql)
    for t in tables:
        tableNames.append(t[0])
    return tableNames


def getVersion(db):
    """
    获取版本号
    :param db:
    :return:
    """
    sql = '''select Version from version;'''
    versions = db.executeQuery(sql)
    return versions


def insertVersion(db, version):
    """
    写入版本号
    :param db:
    :return:
    """
    sql = '''insert into version values({0})'''.format(version)
    r = db.executeDML(sql)
    return r


def updateVersion(db, newVersion):
    """
    更新版本号
    :param db:
    :param newVersion:
    :return:
    """
    sql = '''update version set version=({0})'''.format(newVersion)
    r = db.executeDML(sql)
    return r


def getCurrentSeq(db, tableName):
    """
    tableName
    :param db: 数据库连接
    :param tableName: 表名
    :return:
    """
    sql = '''select seq from sqlite_sequence where name='%s';''' % (tableName)
    current_seq_list = db.executeQuery(sql)
    if len(current_seq_list) == 0:
        return None
    else:
        return current_seq_list[0][0]


def getConnRecords(db, connID=None):
    """
    获取连接信息
    :param db:
    :param connID:
    :return:

    """
    connList = []
    if connID is None:
        sql = '''select * from connections;'''
    else:
        sql = '''select * from connections where id=%d;''' % (connID)

    conns = db.executeQuery(sql)
    assert isinstance(conns, list)
    for c in conns:
        _dic = {"id": c[0], "name": c[1], "pid": c[2], "did": c[3], "detail": c[4]}
        connList.append(_dic)
    return connList


def getConnCurrentSeq(db):
    """
    获取conninfo表ID的当前sequnce值
    :param db:
    :return:
    """
    tableName = 'connections'
    return getCurrentSeq(db, tableName)


def insertConnRecord(db, cname, pid, sid, detail):
    """
    插入一条连接记录
    :param db:
    :param record: (cname,pid,sid,user,password)
    :return:
    """
    sql = '''insert into connections values (NULL,'%s',%d,%d,'%s');''' % (cname, pid, sid, detail)
    r = db.executeDML(sql)
    return r

def deleteConnRecord(db,connID):
    """
    根据connID删除连接记录
    :param db:
    :param connID:
    :return:
    """
    sql = '''delete from connections where id=%d;''' % int(connID)
    r = db.executeDML(sql)
    return r


def getProjectRecords(db, projectID=None):
    projectList = []
    if projectID is None:
        sql = '''select * from projects;'''
    else:
        sql = '''select * from projects where id=%d;''' % (projectID)

    projects = db.executeQuery(sql)
    assert isinstance(projects, list)
    for p in projects:
        _dic = {"id": p[0], "name": p[1], "script": p[2]}
        projectList.append(_dic)
    return projectList


def getProCurrentSeq(db):
    """
    获取programinfo表ID的当前sequnce值
    :param db:
    :return:
    """
    tableName = 'projects'
    return getCurrentSeq(db, tableName)


def insertProRecord(db, pro_name, pro_script):
    """
    插入一条项目记录
    :param db: 数据库实例
    :param pro_name: 项目名称
    :param pro_driver: 项目驱动
    :param pro_script: 项目脚本
    :return:
    """
    sql = '''insert into projects VALUES (NULL,'%s','%s');''' % (pro_name, pro_script)
    r = db.executeDML(sql)
    return r


def deleteProRecord(db,proID):
    """
    根据ProID删除项目记录
    :param db:
    :param proID:
    :return:
    """
    sql = '''delete from projects where id=%d;''' % int(proID)
    r = db.executeDML(sql)
    return r

def getDatasourceRecords(db, datasourceID=None):
    """

    :param db:
    :param datasourceID:
    :return:
    """
    datasourceList = []
    if datasourceID is None:
        sql = '''select * from datasources;'''
    else:
        sql = '''select * from datasources where id=%d;''' % (datasourceID)
    datasources = db.executeQuery(sql)
    assert isinstance(datasources, list)
    for d in datasources:
        _dic = {"id": d[0], "name": d[1], "driver": d[2], "host": d[3], "port": d[4]}
        if d[2] == "oracle":
            _dic["sid"] = d[5]
        else:
            _l = d[5].split("&")
            _dic["user"] = _l[0]
            _dic["password"] = _l[1]
        datasourceList.append(_dic)
    return datasourceList


def getDataSourceCurrentSeq(db):
    """
    获取schemainfo表ID的当前sequnce值
    :param db:
    :return:
    """
    tableName = 'datasources'
    return getCurrentSeq(db, tableName)


def insertSchemaRecord(db, schema_name, schema_driver, schema_host, schema_port, other):
    """
    插入一条数据源记录
    :param db: 数据库实例
    :param schema_name: 数据源名称
    :param schema_driver: 数据源类型
    :param schema_host: 数据库主机IP
    :param schema_port: 数据库端口
    :param schema_servicename: 数据库服务名
    :return:
    """
    sql = '''insert into datasources VALUES (NULL,'%s','%s','%s',%d,'%s')''' % (
        schema_name, schema_driver, schema_host, int(schema_port), other)
    r = db.executeDML(sql)
    return r

def deleteSchema(db,schemaID):
    sql = '''delete from datasources where id=%d;''' % int(schemaID)
    r = db.executeDML(sql)
    return r


def getOneRecordForAll(db, connid):
    """
    根据连接ID，查处该连接的所有信息
    :param db: 数据库连接实例
    :param connid: 连接ID
    :return:
    """
    conn = getConnRecords(db, connid)
    pid = conn[0]["pid"]
    did = conn[0]["did"]
    project = getProjectRecords(db, pid)
    datasource = getDatasourceRecords(db, did)

    return {"conn": conn[0], "project": project[0], "datasource": datasource[0]}


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

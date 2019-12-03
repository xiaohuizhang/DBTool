#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2018/1/22 下午4:34
# @Author   : xhzhang
# @Site     :
# @File     : define.py
# @Software : PyCharm

import datetime

Init_DB_SQL = ['''create table if not exists programinfo
(
  id        INTEGER not null PRIMARY key AUTOINCREMENT,
  pname     VARCHAR(300) unique not null,
  driver    VARCHAR (20) DEFAULT "oracle" not null,
  scriptdir VARCHAR(100) not null
);''',

'''create table if not exists schemainfo
(
  id          INTEGER not null PRIMARY KEY AUTOINCREMENT,
  sname       VARCHAR(300) unique not null,
  host        VARCHAR (20) not null,
  port        int DEFAULT 1521,
  servicename VARCHAR (60) not null
);''',


'''create table if not exists conninfo
(
  id          INTEGER not null PRIMARY KEY AUTOINCREMENT,
  cname       VARCHAR (300) unique not null,
  program_id  int,
  schema_id   int,
  schemauser  VARCHAR (30),
  schemapass  VARCHAR (30),
  FOREIGN KEY (program_id) REFERENCES programinfo(id) ON delete CASCADE,
  FOREIGN KEY (schema_id) REFERENCES schemainfo(id) ON delete CASCADE
);''']



SQL_REPLACE_MAP = {
    '&partition_name': datetime.datetime.now().strftime('%Y%m%d'),  # today
    '&partition_date': (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y%m%d'),  # __tomorrow
    '\r': ' ',
    '\t': ' '
}

DBMS_SCHEDULER_MAP = {
    'sys.dbms_scheduler.create_job': {
        'job_name': None,
        'job_type': None,
        'job_action': None,
        'number_of_arguments': None,
        'start_date': datetime.datetime.now(),
        'repeat_interval': None,
        'job_class': None,
        'enabled': False,
        'auto_drop': False,
        'comments': None
    },
    'sys.dbms_scheduler.set_job_argument_value': {
        'job_name': None,
        'argument_position': None,
        'argument_value': None
    },
    'sys.dbms_scheduler.enable': {'name': None}
}

CLASS_TYPE_MAP = {
    'TABLE': (
        "表",
        """select table_name  from  user_tables""",
        """drop table {0} cascade constraint purge""",1),
    'INDEX': (
        "索引",
        """select object_name from user_objects where object_type='INDEX'""",
        """drop index {0}""",2),
    'VIEW': (
        "视图",
        """select tname from tab where tabtype='VIEW'""",
        """drop table {0} cascade constraint""",3),
    'SEQUENCE': (
        "序列",
        """select sequence_name from user_sequences""",
        """drop sequence {0}""",4),
    'SYNONYM': (
        "同义词",
        """select tname from tab where tabtype='SYNONYM'""",
        """drop synonym {0}""",5),
    'PROCEDURE': (
        "过程",
        """select object_name from user_objects where object_type='PROCEDURE'""",
        """drop procedure {0}""",6),
    'FUNCTION': (
        "函数",
        """select object_name from user_objects where object_type='FUNCTION'""",
        """drop function {0}""",7),
    'JOB': (
        "定时任务",
        """select job_name from user_scheduler_jobs""",
        """""",8)
}

SCRIPT_PRIORITY = {
    'init_create-ForTable.sql': 1,
    'init_create-ForForeignKey.sql': 101,
    'init_create-ForCheck.sql': 2,
    'init_create-ForSequence.sql': 3,
    'init_create-ForIndex.sql': 4,
    'init_create-ForProcedure.sql': 5,
    'init_create-ForFunction.sql': 5,
    'init_create-ForData.sql': 6
}


VERSION_TABLE_NAME = 'SCHEMA_CHANGE_LOG'
SCHEMA_CONTROL_SQL = '''select ISCONTROL from {} where isbranch = 2'''.format(VERSION_TABLE_NAME)
SCHEMA_INIT_SQL = '''select DATEALLPIED from {} where isbranch = 2'''.format(VERSION_TABLE_NAME)
SCHEMA_PATCH_SQL = '''select MAJORRELEASENUMBER,MINORRELEASENUMBER,POINTRELEASENUMBER,REVISIONRELEASENUMBER,DATERELEASENUMBER from {} where isbranch = 0'''.format(VERSION_TABLE_NAME)
SCHEMA_BRANCH_SQL = '''select MAJORRELEASENUMBER,MINORRELEASENUMBER,POINTRELEASENUMBER,REVISIONRELEASENUMBER,DATERELEASENUMBER from {} where isbranch = 1'''.format(VERSION_TABLE_NAME)

INSERT_PATCH_SQL = '''insert into %s (ID,MAJORRELEASENUMBER,MINORRELEASENUMBER,POINTRELEASENUMBER,REVISIONRELEASENUMBER,DATERELEASENUMBER,SCRIPTNAME,ISBRANCH,DATEALLPIED) VALUES (SEQ_VERSIONID.NEXTVAL,{0[0]},{0[1]},{0[2]},{0[3]},{0[4]},'{1}',0,sysdate)''' %(VERSION_TABLE_NAME)
INSERT_BRANCH_SQL = '''insert into %s (ID,MAJORRELEASENUMBER,MINORRELEASENUMBER,POINTRELEASENUMBER,REVISIONRELEASENUMBER,DATERELEASENUMBER,SCRIPTNAME,ISBRANCH,DATEALLPIED) VALUES (SEQ_VERSIONID.NEXTVAL,{0[0]},{0[1]},{0[2]},{0[3]},{0[4]},'{1}',1,sysdate)''' %(VERSION_TABLE_NAME)
INSERT_INIT_SQL = '''insert into %s (ID,MAJORRELEASENUMBER,MINORRELEASENUMBER,POINTRELEASENUMBER,REVISIONRELEASENUMBER,DATERELEASENUMBER,SCRIPTNAME,ISBRANCH,ISCONTROL,DATEALLPIED) VALUES (SEQ_VERSIONID.NEXTVAL,0,0,0,0,0,'init_trunk',2,{0},sysdate)''' %(VERSION_TABLE_NAME)

VERSION_TABLE_ISEXIST = '''select count(*) from user_tables where table_name = '{}\''''.format(VERSION_TABLE_NAME)


SQLITE3_DB_NAME = 'source.db'

REMOTE_RECORD_HOST = '192.168.1.41'
REMOTE_RECORD_SERVICENAME = 'afis'
REMOTE_RECORD_SCHEAMUSER = 'dboper_record'
REMOTE_RECORD_SCHEAMPASS = 'afis2018'

REMOTE_INSERT_SQL = '''insert into operate_record VALUES (SEQ_OPERATE_RECORD.NEXTVAL,'{0[0]}','{0[1]}','{0[2]}','{0[3]}','{0[4]}','{0[5]}',sysdate)'''
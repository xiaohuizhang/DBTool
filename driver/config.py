#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2019/12/17 14:31
# @Author   : xhzhang
# @Site     : 
# @File     : config.py
# @Software : PyCharm

import re
######################
#########common#######
######################
# 脚本优先级
SCRIPT_PRIORITY = {'init_create-ForTable.sql': 1,
                   'init_create-ForForeignKey.sql': 2,
                   'init_create-ForCheck.sql': 2,
                   'init_create-ForSequence.sql': 3,
                   'init_create-ForIndex.sql': 4,
                   'init_create-ForProcedure.sql': 5,
                   'init_create-ForFunction.sql': 5,
                   'init_create-ForData.sql': 6}
# 版本控制
VERSION_TABLE_NAME = 'SCHEMA_CHANGE_LOG'
SCHEMA_CONTROL_SQL = '''select ISCONTROL from {} where isbranch = 2'''.format(VERSION_TABLE_NAME)
SCHEMA_INIT_SQL = '''select DATEALLPIED from {} where isbranch = 2'''.format(VERSION_TABLE_NAME)
SCHEMA_PATCH_SQL = '''select MAJORRELEASENUMBER,MINORRELEASENUMBER,POINTRELEASENUMBER,REVISIONRELEASENUMBER,DATERELEASENUMBER from {} where isbranch = 0'''.format(VERSION_TABLE_NAME)
SCHEMA_BRANCH_SQL = '''select MAJORRELEASENUMBER,MINORRELEASENUMBER,POINTRELEASENUMBER,REVISIONRELEASENUMBER,DATERELEASENUMBER from {} where isbranch = 1'''.format(VERSION_TABLE_NAME)
INSERT_PATCH_SQL = '''insert into %s (ID,MAJORRELEASENUMBER,MINORRELEASENUMBER,POINTRELEASENUMBER,REVISIONRELEASENUMBER,DATERELEASENUMBER,SCRIPTNAME,ISBRANCH,DATEALLPIED) VALUES (SEQ_VERSIONID.NEXTVAL,{0[0]},{0[1]},{0[2]},{0[3]},{0[4]},'{1}',0,sysdate)''' %(VERSION_TABLE_NAME)
INSERT_BRANCH_SQL = '''insert into %s (ID,MAJORRELEASENUMBER,MINORRELEASENUMBER,POINTRELEASENUMBER,REVISIONRELEASENUMBER,DATERELEASENUMBER,SCRIPTNAME,ISBRANCH,DATEALLPIED) VALUES (SEQ_VERSIONID.NEXTVAL,{0[0]},{0[1]},{0[2]},{0[3]},{0[4]},'{1}',1,sysdate)''' %(VERSION_TABLE_NAME)
INSERT_INIT_SQL = '''insert into %s (ID,MAJORRELEASENUMBER,MINORRELEASENUMBER,POINTRELEASENUMBER,REVISIONRELEASENUMBER,DATERELEASENUMBER,SCRIPTNAME,ISBRANCH,ISCONTROL,DATEALLPIED) VALUES (SEQ_VERSIONID.NEXTVAL,0,0,0,0,0,'init_trunk',2,{0},sysdate)''' %(VERSION_TABLE_NAME)
ORACLE_VERSION_TABLE_IS_EXIST = '''select count(*) from user_tables where table_name = '{0}\''''.format(VERSION_TABLE_NAME)
MYSQL_VERSION_TABLE_IS_EXIST = '''SELECT count(*) FROM information_schema.TABLES WHERE table_name ='{0}\''''.format(VERSION_TABLE_NAME)
# 替换字符串
COMMON_SQL_REPLACE_MAP = {'\r': ' ', '\t': ' '}
# 正则表达式
REMOVE_INFO_PATTERN = re.compile('^(\s*--|\s*$|\s*prompt\s+)', re.I)  # 去单行注释,去空行,去提示信息
REMOVE_MULTILINE_COMMENT = re.compile('/\*(.|\n)*\*/')              # 去多行注释
JUDGE_PROCED_FUNC_PATTERN = re.compile(';\s*\n\s*/\s*')  # 以/分隔开的sql。例如：创建过程，函数，begin...end调用存储或者方法
JUDGE_NORMAL_PATTERN = ''
JUDGE_BLANK_LINE_PATTREN = re.compile('^\s*$')  # 判断空行或者''
JUDGE_EXEC_PATTERN = re.compile('^exec\s*', re.I)  # 判断EXEC 方式调用过程或者方法
JUDGE_BEGIN_END_PATTREN = re.compile('^begin\s*', re.I)  # 判断BEGIN...END方式调用过程或者方法
JUDGE_COMMIT_PATTERN = re.compile('^commit\s*;$', re.I)  # commit
JUDGE_CREATE_TABLE_PATTERN = re.compile(r'^create\s+table', re.I)
JUDGE_CREATE_SEQ_PATTERN = re.compile(r'^create\s+sequence', re.I)
JUDGE_CREATE_INDEX_PATTERN = re.compile(r'^create\s+index\s+.*on', re.I)
JUDGE_CREATE_VIEW_PATTERN = re.compile(r'^create\s+view\s+.*as', re.I)
JUDGE_CREATE_PROC_PATTERN = re.compile(r'^create\s+(or\s+replace\s+)?procedure', re.I)
JUDGE_CREATE_FUNC_PATTERN = re.compile(r'^create\s+(or\s+replace\s+)?function', re.I)
JUDGE_CREATE_PK_PATTERN = re.compile(r'^alter\s+table\s+.*\s+add\s+constraint\s+.*\s+primary key', re.I)
JUDGE_CREATE_FK_PATTERN = re.compile(r'^alter\s+table\s+.*\s+add\s+constraint\s+.*\s+foreign key', re.I)
JUDGE_CREATE_UK_PATTERN = re.compile(r'^alter\s+table\s+.*\s+add\s+constraint\s+.*\s+unique', re.I)
JUDGE_CREATE_CK_PATTERN = re.compile(r'^alter\s+table\s+.*\s+add\s+constraint\s+.*\s+check', re.I)
JUDGE_DROP_TABLE_PATTERN = re.compile(r'^drop\s+table', re.I)
JUDGE_DROP_SEQ_PATTERN = re.compile(r'^drop\s+sequence', re.I)
JUDGE_DROP_INDEX_PATTERN = re.compile(r'^drop\s+index', re.I)
JUDGE_DROP_VIEW_PATTERN = re.compile(r'^drop\s+view', re.I)
JUDGE_DROP_SYNONYM_PATTERN = re.compile(r'^drop\s+synonym', re.I)
JUDGE_DROP_CONSTRAINT_PATTERN = re.compile(r'^alter\s+table\s+drop\s+constraint', re.I)
JUDGE_ADD_COLUMN_PATTERN = re.compile(r'^alter\s+table\s+.*add\s*\(.*\)', re.I)
JUDGE_MODIFY_COLUMN_PATTERN = re.compile(r'^alter\s+table\s+.*modify\s*\(.*\)', re.I)
JUDGE_INSERT_RECORD_PATTERN = re.compile(r'^insert\s+into\s+', re.I)
JUDGE_ADD_COMMENT_PATTERN = re.compile(r'^comment\s+on\s+column\s+',re.I)
SPLIT_PROCED_FUNC_PATTERN = re.compile('\n\s*/')  # /必须单独一行
SPLIT_NORMAL_PATTERN = re.compile('\s*;\s*\n\s*')  # ;\n结尾的通常sql
SPLIT_BEGIN_END_PATTERN = re.compile('begin\n|;\n|end$', re.I)  # 拆分begin...end方式调用过程或者方法的sql
NAME_PATTERN = re.compile('\s+|\(.*\)')
COLUMN_PATTERN = re.compile('\s+|\s*\(|\)')
######################
#########oracle#######
######################
import datetime
ORACLE_SQL_REPLACE_MAP = {
    '&partition_name': datetime.datetime.now().strftime('%Y%m%d'),  # today
    '&partition_date': (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y%m%d'),  # __tomorrow
}

ORACLE_DBMS_SCHEDULER_MAP = {
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

ORACLE_CLASS_TYPE_MAP = {
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

######################
#########mysql#######
######################

MYSQL_CLASS_TYPE_MAP = {
    'TABLE': (
        "表",
        """select table_name from information_schema.tables where table_schema='{0}';""",
        """drop table IF EXISTS {0} cascade""",
        1),
    'INDEX': (
        "索引",
        """SELECT index_name from information_schema.STATISTICS where table_schema='{0}';""",
        """drop index  IF EXISTS {0}""",
        2),
    'PROCEDURE': (
        "过程",
        """SELECT ROUTINE_NAME from information_schema.routines where ROUTINE_SCHEMA = '{0}' and ROUTINE_TYPE='PROCEDURE';""",
        """DROP PROCEDURE IF EXISTS {0}""",
        3),
    'FUNCTION': (
        "函数",
        """SELECT ROUTINE_NAME from information_schema.routines where ROUTINE_SCHEMA = '{0}' and ROUTINE_TYPE='FUNCTION';""",
        """DROP FUNCTION IF EXISTS {0}""",
        4),
    'TRIGGER':(
        "触发器",
        """select TRIGGER_NAME from information_schema.TRIGGERS where TRIGGER_SCHEMA = "{0}";""",
        """DROP TRIGGER IF EXISTS {0}""",
        5),
    'EVENT': (
        "定时任务",
        """select EVENT_NAME from information_schema.EVENTS  where EVENT_SCHEMA = "{0}";""",
        """DROP EVENT {0}""",
        6)
}

######################
#########sqlite3######
######################

SQLITE3_CLASS_TYPE_MAP = {
    'TABLE': (
        "表",
        """select name from sqlite_master where type="table";""",
        """drop table IF EXISTS {0} cascade""",
        1),
    'INDEX': (
        "索引",
        """select name from sqlite_master where type="index";""",
        """drop index  IF EXISTS {0}""",
        2),
}

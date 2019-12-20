#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2018/1/5 下午2:31
# @Author   : xhzhang
# @Site     : xhzhang@afis.com
# @File     : myOracle.py
# @Software : PyCharm

"""This script connect oracle db,excute sql and so on"""

import copy,os,platform
from cx_Oracle import connect
from driver import *

def setOracleClientEnv():
    """
    设置oracle客户端环境变量
    :return:
    """
    platform_tuple = platform.uname()
    platform_type = platform_tuple[0]
    platform_machine = platform_tuple[4]
    if platform_type == 'Windows':
        instantclient = os.path.join(os.getcwd(), 'client', 'x86', 'instantclient_11_2')
        os.environ['PATH'] = instantclient + ';' + os.environ['PATH']

class MyOracle(Driver):
    """
        the connection of oralce , excute some sql or file,and so on.
    """
    def __init__(self, user, password, host, port=1521, coding='UTF8', **kwargs):
        """
        init oracle connect object
        :param user:     schema user
        :param password: schema user's password
        :param host:     db host
        :param port:     db port. default is 1521
        :param kwargs:   dic{}
        """
        transDict = dict(COMMON_SQL_REPLACE_MAP, **ORACLE_SQL_REPLACE_MAP)
        super().__init__(transDict)
        self.user = user
        self.host = host
        _sid = kwargs.get('SID') if 'SID' in kwargs else None
        _serviceName = kwargs.get('SERVICE_NAME') if 'SERVICE_NAME' in kwargs else None

        if _sid is None and _serviceName is None:
            sid = None
            self.login_info = '连接Oracle,需要指定SID或者SERVICE_NAME.请设置.'
        else:
            sid = _sid or _serviceName
        try:
            self.conn = connect(user, password, "{0}:{1}/{2}".format(host, str(port), sid), encoding=coding)
            self.login_info = '连接成功.'
            self.schema_version = "版本：{0}".format(self.conn.version)
            self.cur = self.conn.cursor()
        except Exception as e:
            self.login_info = "连接失败=>{0}".format(e)
            # if str(e).startswith('DPI-1047'):
            #     setOracleClientEnv()
            #     try:
            #         self.conn = connect(user, password, "{0}:{1}/{2}".format(host, str(port), sid), encoding=coding)
            #         self.login_info = '连接成功.'
            #         self.schema_version = "版本：%s" % str(self.conn.version)
            #         self.cur = self.conn.cursor()
            #     except Exception as e:
            #         self.login_info = "连接失败=>%s" % e
            # else:
            #     self.login_info = "连接失败=>%s" % e

    def executeDDLFile(self, filename, info=None, error=None):
        """
        执行ddl脚本
        :param filename: 脚本路径名称
        :param info:
        :param error:
        :return:
        """
        iInfo = ""
        iType = NormalMessage
        eInfo = ""
        eSql = ""
        sqlLines = ''
        try:
            handle = open(filename, 'r', encoding='UTF-8')
            fileLines = handle.readlines()
            handle.close()
        except Exception as e:
            emitMessage(info, str(e))
            return

        for line in fileLines:
            if not REMOVE_INFO_PATTERN.match(line):  # 去注释,去空行,去提示信息
                sqlLines += self.trans(line)  # 替换字符

        if JUDGE_PROCED_FUNC_PATTERN.search(sqlLines):  # 过程或者函数
            sqlCommands = SPLIT_PROCED_FUNC_PATTERN.split(sqlLines)
        else:  # 其他sql
            sqlCommands = SPLIT_NORMAL_PATTERN.split(sqlLines)

        for oneSql in sqlCommands:
            oneSqlType, oneSqlName, oneSqlSubtype, sql = parseDDL(oneSql)
            if oneSqlType == 'E':  # EXEC调用
                _sql_sep = sql.partition(' ')
                p_f_info = _sql_sep[2].partition('(')
                p_f_name = p_f_info[0]
                p_f_argument = "({0}".format(p_f_info[2].split(';')[0] if p_f_info[2].endswith(';') else p_f_info[2])
                try:
                    self.cur.callproc(p_f_name, eval(p_f_argument))
                    iInfo = "{0}{1}成功".format(oneSqlSubtype, oneSqlName)
                    iType = NormalMessage
                except Exception as e:
                    iInfo = "{0}{1}失败=>{2}".format(oneSqlSubtype, oneSqlName, e)
                    iType = ErrorMessage
                    eInfo = str(e)
                    eSql = sql

            elif oneSqlType == 'B':  # Begin...end调用
                my_dbms_scheduler_map = copy.deepcopy(ORACLE_DBMS_SCHEDULER_MAP)
                procedureList = SPLIT_BEGIN_END_PATTERN.split(sql)
                for _procedure in procedureList:
                    if not JUDGE_BLANK_LINE_PATTREN.match(_procedure):
                        _p_list = _procedure.strip().partition('(')
                        p_f_name = _p_list[0]
                        _p_f_arg_list = re.split(",\n|\)$", _p_list[2])
                        if p_f_name.lower() in my_dbms_scheduler_map.keys():
                            p_f_argument = my_dbms_scheduler_map[p_f_name.lower()]
                            for _p_f_arg in _p_f_arg_list:
                                if _p_f_arg != '':
                                    tmp = _p_f_arg.partition('=>')
                                    key = tmp[0].strip()
                                    val = tmp[2].strip()
                                    if key in p_f_argument.keys() and p_f_argument[key] is None:
                                        p_f_argument[key] = eval(val)
                            try:
                                self.cur.callproc(p_f_name, keywordParameters=p_f_argument)
                                iInfo += "{0}{1}成功".format(oneSqlSubtype, p_f_name)
                                iType = NormalMessage
                            except Exception as e:
                                iInfo += "{0}{1}失败=>{2};".format(oneSqlSubtype, p_f_name, str(e))
                                iType = ErrorMessage
                                eInfo += str(e)
                                eSql += p_f_name
            elif oneSqlType == 'C':
                try:
                    self.commit()
                    iInfo = '提交成功'
                    iType = NormalMessage
                except Exception as e:
                    iInfo = '提交失败%s' % (str(e))
                    iType = ErrorMessage
                    eInfo = str(e)
                    eSql = 'commit'
            elif oneSqlType == 'N':
                if JUDGE_CREATE_PROC_PATTERN.match(sql) or JUDGE_CREATE_FUNC_PATTERN.match(sql):
                    exec_sql = sql
                else:
                    if sql.endswith(';'):
                        exec_sql = sql.partition(';')[0]
                    else:
                        exec_sql = sql
                try:
                    self.cur.execute(exec_sql)
                    iInfo = "{0}{1}成功".format(oneSqlSubtype, oneSqlName)
                    iType = NormalMessage
                except Exception as e:
                    iInfo = "{0}{1}失败=>{2}".format(oneSqlSubtype, oneSqlName, str(e))
                    iType = ErrorMessage
                    eInfo = str(e)
                    eSql = sql
            else:
                pass

            emitMessage(info, (iType, iInfo))
            emitMessage(error, (eInfo, eSql))

    def dropClassData(self, classmap=ORACLE_CLASS_TYPE_MAP, info=None, error=None):
        """
        delete all data according to classtype
        :return:
        """
        # 根据drop顺序排序
        order_class_type_map = sorted(classmap.items(), key=lambda x: x[1][3])

        for classType in order_class_type_map:
            d_type = classType[0]
            d_type_ch = classType[1][0]
            query_sql = classType[1][1]
            drop_sql = classType[1][2]

            self.cur.execute(query_sql)
            object_list = self.cur.fetchall()
            for index, name in enumerate(object_list):
                eInfo = ""
                eSql = ""
                object_name = name[0]
                if d_type != 'JOB':
                    format_drop_sql = drop_sql.format(object_name)
                    drop_sql_type, drop_sql_name, drop_sql_sub_type, drop_strip_sql = parseDDL(format_drop_sql)
                    try:
                        self.cur.execute(drop_strip_sql)
                        iInfo = '%s%s成功' % (drop_sql_sub_type, drop_sql_name)
                        iType = NormalMessage
                    except Exception as e:
                        iInfo = '%s%s失败=>%s' % (drop_sql_sub_type, drop_sql_name, str(e))
                        iType = ErrorMessage
                        eInfo = str(e)
                        eSql = drop_strip_sql
                else:
                    try:
                        self.cur.callproc('sys.dbms_scheduler.drop_job', [object_name])
                        iInfo = "删除{0}个{1}:{2}成功".format(index, d_type_ch, object_name)
                        iType = NormalMessage
                    except Exception as e:
                        iInfo = "删除{0}个{1}:{2}失败=>{3}".format(index, d_type_ch, object_name, str(e))
                        iType = ErrorMessage
                        eInfo = str(e)
                        eSql = 'sys.dbms_scheduler.drop_job ' + object_name

                emitMessage(info, (iType, iInfo))
                emitMessage(error, (eInfo, eSql))
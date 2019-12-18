#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2019/12/3 16:13
# @Author   : xhzhang
# @Site     : 
# @File     : MySQLDriver.py
# @Software : PyCharm

import pymysql
from driver import *

class MyMySql(Driver):
    """
    the connection of mysql , excute some sql or file,and so on.
    """
    def __init__(self, host, port, user, password, dbname, charset="UTF8"):
        """
        connect to mysql
        :param host: mysql server host
        :param user: mysql server user name
        :param password: mysql server user password
        :param db: mysql server db name
        :param charset: choose charset
        """
        super().__init__(COMMON_SQL_REPLACE_MAP)
        self.dbName = dbname
        self.user = user

        try:
            self.conn = pymysql.connect(host=host,
                                        port=port,
                                        user=user,
                                        password=password,
                                        charset=charset)
            self.cur = self.conn.cursor()
            self.login_info = '连接成功.'
            self.schema_version = "版本：{0}".format(self.conn.get_server_info())
        except Exception as e:
            self.login_info = "连接失败=>{0}".format(e)

    def chooseDB(self):
        self.conn.select_db(self.dbName)
        self.conn.show_warnings()

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
        sqlLines = ""
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
        # 去掉多行注释
        newSqlLines = re.sub(REMOVE_MULTILINE_COMMENT, '', sqlLines)

        if JUDGE_PROCED_FUNC_PATTERN.search(newSqlLines):  # 过程或者函数
            sqlCommands = SPLIT_PROCED_FUNC_PATTERN.split(newSqlLines)
        else:  # 其他sql
            sqlCommands = SPLIT_NORMAL_PATTERN.split(newSqlLines)
        self.chooseDB()
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

    def dropClassData(self, classMap=MYSQL_CLASS_TYPE_MAP, info=None, error=None):
        """
        delete all data according to type
        :param classMap:
        :param info:
        :param error:
        :return:
        """
        # 根据drop顺序排序
        order_class_type_map = sorted(classMap.items(), key=lambda x: x[1][3])
        self.chooseDB()
        self.cur.execute("""SET FOREIGN_KEY_CHECKS = 0 """)
        for classType in order_class_type_map:
            d_type = classType[0]
            d_type_ch = classType[1][0]
            query_sql = classType[1][1].format(self.dbName)
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

                emitMessage(info, (iType,iInfo))
                emitMessage(error, (eInfo, eSql))
        self.cur.execute("""SET FOREIGN_KEY_CHECKS = 1 """)

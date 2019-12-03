#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/28 下午1:44
# @Author   : xhzhang
# @Site     : 
# @File     : Sqlite3Driver.py
# @Software : PyCharm

from sqlite3 import *
import re
from define import SQLITE3_DB_NAME


class MySqlite3(object):
    """
    sqlite3 driver
    """
    conn = None

    def __init__(self, filename=None):
        if filename is None:
            self.filename = SQLITE3_DB_NAME
        else:
            self.filename = filename

    def opendb(self):
        try:
            self.conn = connect(self.filename)
        except Exception as e:
            print (e)

    def isopen(self):
        if self.conn is not None:
            return True
        else:
            return False

    def exec_script(self, sqlList):
        """
        执行sql脚本
        :param sqlList: sql字符串列表
        :return:
        """
        sql = ''
        REMOVE_INFO_PATTERN = re.compile('^(--|\s*$)', re.I)
        # try:
        #     handle = open(sql_script, 'r')
        #     filelines = handle.readlines()
        #     for line in filelines:
        #         if not REMOVE_INFO_PATTERN.match(line):  # 去注释,去空行,去提示信息
        #             sql += line  # 替换字符
        #     handle.close()
        # except Exception as e:
        #     print (e)
        # print (sql)
        for s in sqlList:
            if not REMOVE_INFO_PATTERN.match(s):  # 去注释,去空行,去提示信息
                sql += s                          # 替换字符
        self.conn.executescript(sql)
        self.commit()


    def exec_statement(self, sql_statement):
        """
        执行insert,update,delete操作
        :param sql_statement: sql语句
        :return:
        """
        try:
            self.conn.execute(sql_statement)
            self.conn.commit()
            return
        except Exception as e:
            return str(e)

    def exec_select(self, sql_select):
        """
        执行select操作
        :param sql_select:
        :return:
        """
        try:
            cursor = self.conn.execute(sql_select)
            records = cursor.fetchall()
        except Exception as e:
            return str(e)
        return records

    def commit(self):
        if self.isopen():
            self.conn.commit()
        else:
            print ('数据库未打开')

    def closedb(self):
        if self.isopen():
            self.conn.close()
        else:
            print ('数据库未打开')



if __name__ == '__main__':
    mc = MySqlite3()
    mc.opendb()
    # # mc.isopen()
    # # mc.exec_script('init.sql')
    # mc.exec_statement('insert into programinfo(pname,driver,scriptdir) VALUES ("非法集资","oracle","/Users/xhzhang/test_script/init_ffjz")')
    # mc.exec_statement('insert into schemainfo(sname,host,port,servicename) VALUES ("41-DG1","192.168.1.41",1521,"DG1")')
    r = mc.exec_select('select * from test;')
    print (str(r[0][0]))
    mc.closedb()


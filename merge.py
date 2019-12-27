#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2019/12/24 15:29
# @Author   : xhzhang
# @Site     : 
# @File     : merge.py
# @Software : PyCharm

import sys
from driver.Sqlite3Driver import MySqlite3
from comm import INIT_DB_SQL, DBMSVersion, getVersion

mergeSql = []
if DBMSVersion == "1.3":
    mergeSql = INIT_DB_SQL + ['''INSERT INTO projects SELECT id, pname, scriptdir FROM programinfo;''',
                              '''INSERT INTO datasources SELECT id,sname,"oracle",host,port,servicename FROM schemainfo;''',
                              '''INSERT INTO connections SELECT id,cname,program_id,schema_id,schemauser||"&"||schemapass FROM conninfo;''',
                              '''drop table programinfo;''',
                              '''drop table schemainfo;''',
                              '''drop table conninfo;''']

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("请指定需要merge的数据库文件")
        sys.exit(-1)
    filename = sys.argv[1]
    print("需要merge的数据库:{0}".format(filename))
    conn = MySqlite3(filename)

    print("当前版本: {0}".format(DBMSVersion))
    conn.execScript(mergeSql)
    conn.commit()
    conn.close()

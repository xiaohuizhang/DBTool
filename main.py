#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2018/1/25 下午1:47
# @Author   : xhzhang
# @Site     : 
# @File     : main.py
# @Software : PyCharm


import logging
import logging.handlers
import sys
from os.path import dirname, join, isfile, realpath, abspath
from PyQt5.QtWidgets import QApplication
from driver.Sqlite3Driver import MySqlite3
from comm import SQLITE3_DB_NAME,INIT_DB_SQL,LOG_DIR
from page.mainwindows import uimain
from resource import *



def initSqLite(cDir,sqls):
    """
    初始化数据库
    :return:
    """
    dbDir = join(cDir,SQLITE3_DB_NAME)
    if not isfile(dbDir):
        myInit = MySqlite3(dbDir)
        myInit.openDb()
        myInit.exec_script(sqls)
        myInit.closedb()

def initlog():
    """
    初始化日志
    :return:
    """
    formatter = logging.Formatter('[%(asctime)s] - %(filename)s [Line:%(lineno)d] - [%(levelname)s] - %(message)s')
    myapp_hander = logging.handlers.RotatingFileHandler(LOG_DIR, mode='w',maxBytes=1024000, backupCount=5)
    myapp_hander.setFormatter(formatter)
    logging.basicConfig()
    myApp = logging.getLogger('dbtool')
    myApp.setLevel(logging.INFO)
    myApp.addHandler(myapp_hander)

if __name__ == "__main__":
    try:
        current_dir = dirname(realpath(__file__))
    except NameError:
        current_dir = dirname(abspath(sys.argv[0]))
    initlog()
    # 初始化数据库
    initSqLite(current_dir,INIT_DB_SQL)
    # 加载qss文件
    file = QtCore.QFile(":/resource/pre.qss")
    file.open(QtCore.QFile.ReadOnly)
    styleSheet = file.readAll()
    styleSheet = str(styleSheet, encoding='utf8')
    app = QApplication(sys.argv)
    app.setStyleSheet(styleSheet)
    ui = uimain()
    ui.show()
    sys.exit(app.exec_())
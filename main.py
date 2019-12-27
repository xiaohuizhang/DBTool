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
from PyQt5.QtCore import QSize,QFile
from PyQt5.QtGui import QIcon
from driver.Sqlite3Driver import MySqlite3
from comm import SQLITE3_DB_NAME, INIT_DB_SQL, LOG_DIR, getVersion,insertVersion,updateVersion,getAllTables
from page.mainwindows import uimain
from page.myWindow import FramelessWindow
from resource import *
from comm import DBMSVersion

def initAndCheckDatabase():
    """
    初始化并校验数据库
    :return:
    """
    dbDir = join(current_dir, SQLITE3_DB_NAME)
    ms = MySqlite3(dbDir)
    tables = getAllTables(ms)
    if "projects" not in tables or "connections" not in tables or "datasources" not in tables or "version" not in tables:
        log.warning("table not exist, will init.")
        ms.execScript(INIT_DB_SQL)
        insertVersion(ms, DBMSVersion)
    else:
        log.info("current version is {0}".format(DBMSVersion))
        version = getVersion(ms)
        if isinstance(version, str):
            log.error(version)
        else:
            if len(version) == 0:
                insertVersion(ms, DBMSVersion)
            else:
                updateVersion(ms, DBMSVersion)
    ms.close()


def initlog():
    """
    初始化日志
    :return:
    """
    formatter = logging.Formatter('[%(asctime)s] - %(filename)s [Line:%(lineno)d] - [%(levelname)s] - %(message)s')
    myAppHander = logging.handlers.RotatingFileHandler(LOG_DIR, mode='w',maxBytes=1024000, backupCount=5)
    myAppHander.setFormatter(formatter)
    logging.basicConfig()
    myApp = logging.getLogger('dbtool')
    myApp.setLevel(logging.INFO)
    myApp.addHandler(myAppHander)

if __name__ == "__main__":
    # 初始化日志
    initlog()
    log = logging.getLogger('dbtool')
    log.info("init log...")
    # 获取当前路径
    try:
        current_dir = dirname(realpath(__file__))
    except NameError:
        current_dir = dirname(abspath(sys.argv[0]))
    # 初始化数据库
    log.info("init and check database...")
    initAndCheckDatabase()
    # 加载qss文件
    log.info("Loading QSS...")
    file = QFile(":/resource/pre.qss")
    file.open(QFile.ReadOnly)
    styleSheet = file.readAll()
    styleSheet = str(styleSheet, encoding='utf8')
    app = QApplication(sys.argv)
    app.setStyleSheet(styleSheet)
    mainWnd = FramelessWindow()
    mainWnd.titleBar.setHeight(50)
    mainWnd.setWindowTitle('DataBase Manager ' + DBMSVersion)
    mainWnd.setWindowIcon(QIcon(':/resource/database.png'))
    mainWnd.resize(QSize(1250, 780))
    mainWnd.setWidget(uimain(mainWnd))  # 把自己的窗口添加进来
    mainWnd.show()
    sys.exit(app.exec_())
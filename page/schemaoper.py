#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/8 下午4:26
# @Author   : xhzhang
# @Site     : 
# @File     : schemaoper.py
# @Software : PyCharm

import os,re,operator,datetime
from PyQt5.QtCore import QThread, pyqtSignal
from driver import *
from comm import *
from driver.OracleDriver import MyOracle

def getPatchAvailableList(patchdir, latest_tuple=None):
    """
    obtain vailable patch sql list
    :param patchPath:
    :param latest_tuple: latest version from database
    :return: []
    """
    patch_dic = {}
    if not os.path.isdir(patchdir):
        return None  # 路径不存在，返回None
    else:
        for root, dirs, files in os.walk(patchdir):
            if root == patchdir:
                for fn in files:
                    if fn.startswith('.') or not fn.endswith('.sql'):
                        continue
                    fn_list = list(map(int, re.split(r'[._]', os.path.splitext(fn)[0])))  # [0,1,20180123]
                    fn_len = len(fn_list)
                    if fn_len < 2 or fn_len > 5:
                        return []
                    if fn_len == 4:
                        fn_list.insert(3, 0)
                    elif fn_len == 3:
                        fn_list.insert(2, 0)
                        fn_list.insert(3, 0)
                    elif fn_len == 2:
                        fn_list.insert(1, 0)
                        fn_list.insert(2, 0)
                        fn_list.insert(3, 0)
                    else:
                        pass

                    if latest_tuple is None:
                        patch_dic[fn] = tuple(fn_list)
                    else:
                        if operator.gt(tuple(fn_list), latest_tuple):
                            # if cmp(tuple(fn_list), latest_tuple) == 1:
                            patch_dic[fn] = tuple(fn_list)
    return sorted(patch_dic.items(), key=lambda x: x[1], reverse=True)


def getTrunkAvailableList(trunkDir):
    """
    obtain variable trunk sql list
    :param trunkDir: trunk dir
    :return: []
    """
    trunk_list = []
    if not os.path.isdir(trunkDir):
        trunk_list = []
    else:
        for root, dirs, files in os.walk(trunkDir):
            if root == trunkDir:
                for file in files:
                    if file.startswith('.') or not file.endswith('.sql'):
                        continue
                    else:
                        trunk_list.append(file)
    return trunk_list


def getTagAvailableList(tagDir):
    """
    obtain variable tag sql list
    :param tagDir: tag dir
    :return: {}
    """
    tag_dic = {}
    if not os.path.isdir(tagDir):
        tag_dic = {}
    else:
        for root, dirs, files in os.walk(tagDir):
            if root != tagDir:
                tag_dic[os.path.basename(root)] = files
    print(tag_dic)


# 记录消息到远程
def writeOperRecord(oper, dbhost, dbschema, script=None):
    """
    记录操作记录到远程数据库
    :param oper: init or upgrade
    :param dbhost: 操作的数据库host
    :param dbschema: 操作的数据库schema
    :param script: 如果是init,则为None；如果为upgrade,则为upgrade的脚本
    :return:
    """
    ip, hostname, loginuser = getLocalInfo()
    if oper == 'upgrade':
        event = script
    else:
        event = oper

    sql = REMOTE_INSERT_SQL.format((event, dbhost, dbschema, ip, hostname, loginuser))
    remote_conn = MyOracle(REMOTE_RECORD_SCHEAMUSER, REMOTE_RECORD_SCHEAMPASS, REMOTE_RECORD_HOST,
                           SERVICE_NAME=REMOTE_RECORD_SERVICENAME)
    remote_conn.executeInsert(sql)
    remote_conn.commit()
    remote_conn.close()

class ConnThread(QThread):
    currentDriver = ""
    loginTrigger = pyqtSignal([int, str])
    dataTrigger = pyqtSignal(list)
    isControlTrigger = pyqtSignal(int)
    isControl = 1  # 默认schema是受控制的

    def __init__(self, db, script, driver,parent=None):
        """
        连接指定的schema,并将信息发送到控件信号
        :param db: 数据库连接实例
        :param script: 脚本路径
        :param driver: 驱动类型
        :param parent:
        """
        super(ConnThread, self).__init__(parent)
        self.db = db
        self.script = script
        self.patch = os.path.join(self.script, 'patch')
        self.currentDriver = driver
        if self.currentDriver == "oracle":
            self.checkVersionTableSql = ORACLE_VERSION_TABLE_IS_EXIST
        elif self.currentDriver == "mysql":
            self.checkVersionTableSql = MYSQL_VERSION_TABLE_IS_EXIST
        else:
            self.checkVersionTableSql = ""
    def run(self):
        if self.db.login_info is not None and self.db.schema_version is not None:
            self.loginTrigger.emit(NormalMessage, self.db.login_info + self.db.schema_version)

        if self.db.conn is None:
            return

        isExist = self.db.executeQuery(self.checkVersionTableSql,trigger=self.loginTrigger)
        assert (isinstance(isExist,list) or isinstance(isExist,tuple))
        if isExist[0][0] == 0:         # 版本控制表不存在，则默认该schema不受控制
            self.isControl = 0
        else:
            isControl = self.db.executeQuery(SCHEMA_CONTROL_SQL, trigger=self.loginTrigger)
            assert (isinstance(isControl, list))
            if isControl[0][0] == 0:
                self.isControl = 0
            else:
                self.isControl = int(isControl[0][0])
        self.isControlTrigger.emit(self.isControl)
        self.connDisplay()

    def connDisplay(self):
        if self.isControl == 1:
            initRecords = self.db.executeQuery(SCHEMA_INIT_SQL, trigger=self.loginTrigger)
            NoBranchRecords = self.db.executeQuery(SCHEMA_PATCH_SQL, trigger=self.loginTrigger)
            BachchRecords = self.db.executeQuery(SCHEMA_BRANCH_SQL, trigger=self.loginTrigger)
            # 检测初始化信息
            if isinstance(initRecords, list):
                if len(initRecords) > 0:
                    init_time = initRecords[0][0].strftime("%Y-%m-%d %H:%M:%S")
                    self.loginTrigger.emit(NormalMessage, "初始化时间：%s" % init_time)
                else:
                    self.loginTrigger.emit(WarningMessage,  "没有初始化时间记录")
            else:
                self.loginTrigger.emit(ErrorMessage,  "初始化信息异常")
                return

            if isinstance(NoBranchRecords, list):
                if len(NoBranchRecords) > 0:
                    maxNoBranchRecord = max(NoBranchRecords)
                    curr_version = '{0[0]}.{0[1]}.{0[2]}.{0[3]}_{0[4]}'.format(maxNoBranchRecord)
                    self.loginTrigger.emit(NormalMessage, "脚本版本：%s" % curr_version)
                    if self.script is not None:
                        patch_orders = getPatchAvailableList(self.patch , maxNoBranchRecord)
                        if patch_orders is None:
                            self.loginTrigger.emit(ErrorMessage, "patch路径不存在")
                        else:
                            can_upgrade_patch = []
                            for p in patch_orders:
                                if p[1] not in BachchRecords:
                                    can_upgrade_patch.append(p)
                            self.dataTrigger.emit(can_upgrade_patch)
                else:
                    self.loginTrigger.emit(WarningMessage, "脚本当前版本: 无")
            else:
                self.loginTrigger.emit(ErrorMessage, "查询脚本版本异常，请根据错误提示检查原因")
                return
        else:
            self.loginTrigger.emit(NormalMessage, "无版本控制要求,列出所有patch以供执行")
            patch_orders = getPatchAvailableList(self.patch)
            if patch_orders is not None:
                self.dataTrigger.emit(patch_orders)
            else:
                self.loginTrigger.emit(ErrorMessage, "patch路径不存在")


class InitThread(QThread):
    infoTrigger = pyqtSignal([int,str])
    errorTrigger = pyqtSignal([str, str])

    def __init__(self, db, scriptDir, isControl, driver,parent=None):
        super(InitThread, self).__init__(parent)
        self.db = db
        self.script = scriptDir
        self.isControl = isControl
        self.driver = driver

    def run(self):
        init_scripts = {}
        trunk_dir = os.path.join(self.script, 'trunk')
        patch_dir = os.path.join(self.script, 'patch')
        if not os.path.isdir(trunk_dir):
            self.infoTrigger.emit(ErrorMessage, "{}路径不存在，无法初始化".format(trunk_dir))
            return
        trunk_script_list = getTrunkAvailableList(trunk_dir)
        for s in trunk_script_list:
            if s in SCRIPT_PRIORITY.keys():
                init_scripts[s] = SCRIPT_PRIORITY[s]
            else:
                init_scripts[s] = 100

        initScriptOrder = sorted(init_scripts.items(), key=lambda x: x[1])
        # drop
        self.db.dropClassData(info=self.infoTrigger, error=self.errorTrigger)
        # init
        for scripTuple in initScriptOrder:
            self.infoTrigger.emit(NormalMessage, '--------{}-------'.format(scripTuple[0]))
            self.db.executeDDLFile(os.path.join(trunk_dir, scripTuple[0]), self.infoTrigger, self.errorTrigger)
        self.db.executeInsert(INSERT_INIT_SQL.format(self.isControl), self.infoTrigger)
        self.db.commit()
        self.infoTrigger.emit(NormalMessage, '初始化结束.')
        # patch
        if self.isControl == 1:
            patch_order = getPatchAvailableList(patch_dir)
            if patch_order is None or len(patch_order) == 0:
                versionTuple = (0, 0, 0, 0, int(datetime.datetime.now().strftime('%Y%m%d')))
                versionSqlName = 'init'
                insert_sql = INSERT_PATCH_SQL.format(versionTuple, versionSqlName)
                curr_version = '未检索到patch脚本，系统默认为{0[0]}.{0[1]}.{0[2]}.{0[3]}_{0[4]}'.format(versionTuple)
            else:
                insert_sql = INSERT_PATCH_SQL.format(patch_order[0][1], patch_order[0][0])
                curr_version = '{0[0]}.{0[1]}.{0[2]}.{0[3]}_{0[4]}'.format(patch_order[0][1])
            self.db.executeInsert(insert_sql, self.infoTrigger)
            self.db.commit()
            self.infoTrigger.emit(NormalMessage, '初始化的脚本版本: %s' % curr_version)
        # 远程记录
        writeOperRecord('init',self.db.host,self.db.user)


class DropThread(QThread):
    infoTrigger = pyqtSignal(str)
    errorTrigger = pyqtSignal([str, str])

    def __init__(self, db, parent=None):
        super(DropThread, self).__init__(parent)
        self.db = db

    def run(self):
        self.db.drop_class_data(info=self.infoTrigger, error=self.errorTrigger)
        self.infoTrigger.emit(NormalMessage, '清除结束！')
        writeOperRecord('drop', self.db.host, self.db.user)

class UpgradeThread(QThread):
    infoTrigger = pyqtSignal(str)
    errorTrigger = pyqtSignal([str, str])

    def __init__(self, db, scriptList, scriptDir, isControl, parent=None):
        super(UpgradeThread, self).__init__(parent)
        self.db = db
        self.scripDir = scriptDir
        self.isControl = isControl
        if scriptList is None:
            return
        if isinstance(scriptList, list):
            self.scriptList = sorted(scriptList, key=lambda x: x[1])  # 升序排序
            self.flag = 0
        else:
            self.scriptList = [scriptList]
            self.flag = 1

    def run(self):
        script_str = ''
        for s in self.scriptList:
            insert_sql = ''
            _u_script = s[0]
            _u_version = s[1]
            script_str = _u_script
            _u_script_dir = os.path.join(self.scripdir, 'patch', _u_script)
            self.infoTrigger.emit(NormalMessage, '---------{0}---------'.format(_u_script_dir))
            self.db.execute_ddl_file(_u_script_dir, self.infoTrigger, self.errorTrigger)
            if self.isControl == 1:
                if self.flag == 0:
                    insert_sql = INSERT_PATCH_SQL.format(_u_version, _u_script)
                elif self.flag == 1:
                    insert_sql = INSERT_BRANCH_SQL.format(_u_version, _u_script)
                else:
                    pass
                # 插入版本控制记录
                self.db.executeInsert(insert_sql, self.infoTrigger)
                # 提交
                self.db.commit()
        self.infoTrigger.emit(NormalMessage, '更新结束！')
        writeOperRecord('upgrade', self.db.host, self.db.user,script_str)


class CloseThread(QThread):
    infoTrigger = pyqtSignal([int,str])

    def __init__(self, db, parent=None):
        super(CloseThread, self).__init__(parent)
        self.db = db

    def run(self):
        if self.db is not None:
            self.db.close(self.infoTrigger)
        else:
            self.infoTrigger.emit(WarningMessage, '数据库未连接')

#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/8 下午4:26
# @Author   : xhzhang
# @Site     : 
# @File     : schemaoper.py
# @Software : PyCharm

import datetime
import os

from PyQt5.QtCore import QThread, pyqtSignal

from driver.OracleDriver import GetPatchAvailableList, GetTrunkAvailableList,writeOperRecord
from define import SCHEMA_CONTROL_SQL, SCHEMA_PATCH_SQL, SCHEMA_BRANCH_SQL, SCHEMA_INIT_SQL, INSERT_PATCH_SQL, \
    INSERT_BRANCH_SQL, INSERT_INIT_SQL, SCRIPT_PRIORITY, VERSION_TABLE_ISEXIST



class ConnThread(QThread):
    trigger_loginfo = pyqtSignal(str)
    # trigger_errorinfo = pyqtSignal(str)
    trigger_data = pyqtSignal(list)
    trigger_iscontrol = pyqtSignal(int)
    iscontrol = 1  # 默认schema是受控制的

    def __init__(self, dbins, scriptdir, parent=None):
        """
        连接指定的schema,并将信息发送到控件信号
        :param dbins: 数据库连接实例
        :param scriptdir: 脚本路径
        :param parent:
        """
        super(ConnThread, self).__init__(parent)
        self.dbins = dbins
        self.scriptdir = scriptdir
        self.patchdir = os.path.join(self.scriptdir, 'patch')

    def run(self):
        if self.dbins.login_info is not None:
            self.trigger_loginfo.emit(self.dbins.login_info)
        if self.dbins.schema_version is not None:
            self.trigger_loginfo.emit(self.dbins.schema_version)

        if self.dbins.conn is None:
            return

        table_isexist_record = self.dbins.execute_query(VERSION_TABLE_ISEXIST, self.trigger_loginfo, flag=1)
        if table_isexist_record[0] == 0:  # 版本控制表不存在，则默认该schema不受控制
            self.iscontrol = 0
        else:
            is_control_record = self.dbins.execute_query(SCHEMA_CONTROL_SQL, self.trigger_loginfo, flag=1)
            if is_control_record is None:  # 没有初始化信息
                self.iscontrol = 0
            else:
                self.iscontrol = int(is_control_record[0])
        self.trigger_iscontrol.emit(self.iscontrol)
        self.connDisplay()

    def connDisplay(self):
        if self.iscontrol == 1:
            init_records = self.dbins.execute_query(SCHEMA_INIT_SQL, self.trigger_loginfo)
            all_nobranch_records = self.dbins.execute_query(SCHEMA_PATCH_SQL, self.trigger_loginfo)
            all_bachch_records = self.dbins.execute_query(SCHEMA_BRANCH_SQL, self.trigger_loginfo)
            # 检测初始化信息
            if isinstance(init_records, list):
                if len(init_records) > 0:
                    init_time = init_records[0][0].strftime("%Y-%m-%d %H:%M:%S")
                    self.trigger_loginfo.emit("schema初始化时间：%s" % init_time)
                else:
                    self.trigger_loginfo.emit("schema没有初始化时间记录")
            else:
                self.trigger_loginfo.emit("schema初始化信息异常")
                return

            if isinstance(all_nobranch_records, list):
                if len(all_nobranch_records) > 0:
                    max_nobranch_record = max(all_nobranch_records)
                    curr_version = '{0[0]}.{0[1]}.{0[2]}.{0[3]}_{0[4]}'.format(max_nobranch_record)
                    self.trigger_loginfo.emit("schema版本：%s" % curr_version)
                    if self.scriptdir is not None:
                        patch_orders = GetPatchAvailableList(self.patchdir , max_nobranch_record)
                        if patch_orders is None:
                            self.trigger_loginfo.emit("patch路径不存在")
                        else:
                            can_upgrade_patch = []
                            for p in patch_orders:
                                if p[1] not in all_bachch_records:
                                    can_upgrade_patch.append(p)
                            self.trigger_data.emit(can_upgrade_patch)
                else:
                    self.trigger_loginfo.emit("schema当前版本: 无")
            else:
                self.trigger_loginfo.emit("查询schema版本异常，请根据错误提示检查原因")
                return
        else:
            self.trigger_loginfo.emit("无版本控制要求,列出所有patch以供执行")
            patch_orders = GetPatchAvailableList(self.patchdir)
            if patch_orders is not None:
                self.trigger_data.emit(patch_orders)


class InitThread(QThread):
    triger_info = pyqtSignal(str)
    triger_error = pyqtSignal([str, str])

    def __init__(self, dbins, scriptdir, iscontrol, parent=None):
        super(InitThread, self).__init__(parent)
        self.dbins = dbins
        self.scriptdir = scriptdir
        self.iscontrol = iscontrol

    def run(self):
        init_scripts = {}
        trunk_dir = os.path.join(self.scriptdir, 'trunk')
        patch_dir = os.path.join(self.scriptdir, 'patch')
        if not os.path.isdir(trunk_dir):
            self.triger_info.emit("{}路径不存在，无法初始化".format(trunk_dir))
            return
        trunk_script_list = GetTrunkAvailableList(trunk_dir)
        for s in trunk_script_list:
            if s in SCRIPT_PRIORITY.keys():
                init_scripts[s] = SCRIPT_PRIORITY[s]
            else:
                init_scripts[s] = 100

        init_script_order = sorted(init_scripts.items(), key=lambda x: x[1])
        # drop
        self.dbins.drop_class_data(self.triger_info, self.triger_error)
        # init
        for scriptuple in init_script_order:
            self.triger_info.emit('--------{}-------'.format(scriptuple[0]))
            self.dbins.execute_ddl_file(os.path.join(trunk_dir, scriptuple[0]), self.triger_info, self.triger_error)
        self.dbins.execute_insert(INSERT_INIT_SQL.format(self.iscontrol), self.triger_info)
        self.dbins.commit()
        self.triger_info.emit('初始化结束！')
        # patch
        if self.iscontrol == 1:
            patch_order = GetPatchAvailableList(patch_dir)
            if patch_order is None or len(patch_order) == 0:
                verion_tuple = (0, 0, 0, 0, int(datetime.datetime.now().strftime('%Y%m%d')))
                version_sqlname = 'init'
                insert_sql = INSERT_PATCH_SQL.format(verion_tuple, version_sqlname)
                curr_version = '未检索到patch脚本，系统默认为{0[0]}.{0[1]}.{0[2]}.{0[3]}_{0[4]}'.format(verion_tuple)
            else:
                insert_sql = INSERT_PATCH_SQL.format(patch_order[0][1], patch_order[0][0])
                curr_version = '{0[0]}.{0[1]}.{0[2]}.{0[3]}_{0[4]}'.format(patch_order[0][1])
            self.dbins.execute_insert(insert_sql, self.triger_info)
            self.dbins.commit()
            self.triger_info.emit('初始化的schema版本: %s' % curr_version)
        # 远程记录
        writeOperRecord('init',self.dbins.host,self.dbins.user)


class DropThread(QThread):
    triger_info = pyqtSignal(str)
    triger_error = pyqtSignal([str, str])

    def __init__(self, dbins, parent=None):
        super(DropThread, self).__init__(parent)
        self.dbins = dbins

    def run(self):
        self.dbins.drop_class_data(self.triger_info, self.triger_error)
        self.triger_info.emit('清除结束！')
        writeOperRecord('drop', self.dbins.host, self.dbins.user)

class UpgradeThread(QThread):
    triger_info = pyqtSignal(str)
    triger_error = pyqtSignal([str, str])

    def __init__(self, dbins, scriptlist, scriptdir, iscontrol, parent=None):
        super(UpgradeThread, self).__init__(parent)
        self.dbins = dbins
        self.scripdir = scriptdir
        self.iscontrol = iscontrol
        if scriptlist is None:
            return
        if isinstance(scriptlist, list):
            self.scriptlist = sorted(scriptlist, key=lambda x: x[1])  # 升序排序
            self.flag = 0
        else:
            self.scriptlist = [scriptlist]
            self.flag = 1

    def run(self):
        script_str = ''
        for s in self.scriptlist:
            insert_sql = ''
            _u_script = s[0]
            _u_version = s[1]
            script_str = _u_script
            _u_script_dir = os.path.join(self.scripdir, 'patch', _u_script)
            self.triger_info.emit('---------{0}---------'.format(_u_script_dir))
            self.dbins.execute_ddl_file(_u_script_dir, self.triger_info, self.triger_error)
            if self.iscontrol == 1:
                if self.flag == 0:
                    insert_sql = INSERT_PATCH_SQL.format(_u_version, _u_script)
                elif self.flag == 1:
                    insert_sql = INSERT_BRANCH_SQL.format(_u_version, _u_script)
                else:
                    pass
                # 插入版本控制记录
                self.dbins.execute_insert(insert_sql, self.triger_info)
                # 提交
                self.dbins.commit()
        self.triger_info.emit('更新结束！')
        writeOperRecord('upgrade', self.dbins.host, self.dbins.user,script_str)


class CloseThread(QThread):
    triger_info = pyqtSignal(str)
    triger_error = pyqtSignal([str, str])

    def __init__(self, dbins, parent=None):
        super(CloseThread, self).__init__(parent)
        self.dbins = dbins

    def run(self):
        if self.dbins is not None:
            self.dbins.close(self.triger_info, self.triger_error)
        else:
            self.triger_info.emit('数据库未连接')

#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2018/1/25 下午2:21
# @Author   : xhzhang
# @Site     :
# @File     : uimain.py
# @Software : PyCharm

import logging
import os
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from driver.OracleDriver import MyOracle
from driver.Sqlite3Driver import MySqlite3
from driver.MySQLDriver import MyMySql
from comm import *
from page.schemaoper import ConnThread, InitThread, UpgradeThread, CloseThread, DropThread
from page.manager import SourceWindow
from page.myWindow import FramelessWindow



myLog = logging.getLogger('dbtool')

class MyWidget(QWidget):
    """对QWidget类重写，实现一些功能"""
    close_signal = pyqtSignal()

    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        self.close_signal.emit()


# 初始化确认弹出框
class initDialog(QDialog):
    """
    初始化schema确认对话框
    """
    isControl = pyqtSignal(int)

    def __init__(self):
        super(initDialog, self).__init__()
        self.setFixedSize(300, 150)
        self.setWindowTitle('初始化确认信息')
        self.SetupUI()
        self.SlotFunction()

    def SetupUI(self):

        self.info = QLabel('确定用trunk初始化？')

        self.version_control = QCheckBox('版本控制')
        self.version_control.setChecked(True)

        self.yesbutton = QPushButton('确定')
        self.nobutton = QPushButton('取消')
        self.nobutton.setObjectName('cancel')
        hbox = QHBoxLayout()
        hbox.addWidget(self.yesbutton)
        hbox.addWidget(self.nobutton)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.info)
        vbox.addWidget(self.version_control)
        vbox.addLayout(hbox)

    def SlotFunction(self):
        self.yesbutton.clicked.connect(self._handleInit)
        self.nobutton.clicked.connect(self._handleClose)

    def _handleInit(self):
        if self.version_control.isChecked():
            flag = 1
        else:
            flag = 0
        self.isControl.emit(flag)
        self.close()

    def _handleClose(self):
        self.close()

# 升级确认弹出框
class upgradeDialog(QDialog):
    """
    升级schema弹出的对话框
    """
    upgrade = pyqtSignal(int)
    logs = pyqtSignal(str)

    def __init__(self, patchname, iscontrol, psdir):
        super(upgradeDialog, self).__init__()
        self.setFixedSize(800, 400)
        self.setWindowTitle('升级确认')
        self.patchname = patchname
        self.isControl = iscontrol
        self.psdir = psdir
        self.SetupUI()
        self.SetDeaultData()
        self.SlotFunction()

    def SetupUI(self):
        self.patchname_label = QLabel('**{0}:'.format(self.patchname))
        self.sql_area = QTextBrowser()
        self.yesbutton = QPushButton('确定')
        self.cancelbutton = QPushButton('取消')
        self.cancelbutton.setObjectName('cancel')

        hbox1 = QHBoxLayout()
        hbox1.addStretch()
        hbox1.addWidget(self.yesbutton)
        hbox1.addWidget(self.cancelbutton)
        hbox1.addStretch()

        vbox1 = QVBoxLayout()
        if self.isControl == 0:
            self.attention = QLabel('当前schema无版本控制，只执行该脚本，请确认')
            vbox1.addWidget(self.attention)
        else:
            self.attention = QLabel('当前schema有版本控制')
            self.radio1 = QRadioButton('升级到该patch版本')
            self.radio2 = QRadioButton('升级单个patch版本')
            self.radio1.setChecked(True)
            vbox1.addWidget(self.radio1)
            vbox1.addWidget(self.radio2)
            vbox1.addWidget(self.attention)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.patchname_label)
        vbox2.addWidget(self.sql_area)
        vbox2.addStretch()
        vbox2.addLayout(vbox1)
        vbox2.addStretch()
        vbox2.addLayout(hbox1)
        vbox2.addStretch()
        self.setLayout(vbox2)

    def SetDeaultData(self):
        patch_dir = os.path.join(self.psdir, 'patch', self.patchname)
        handle = None
        try:
            handle = open(patch_dir, 'r', encoding="utf8")
            fileLines = handle.read()
            self.sql_area.append(fileLines)
        except Exception as e:
            myLog.error(e)
            return
        finally:
            handle.close()

    def SlotFunction(self):
        self.yesbutton.clicked.connect(self._handleUpgrade)
        self.cancelbutton.clicked.connect(self._handleClose)

    def _handleUpgrade(self):
        """
        确认按钮
        flag: 1=>升级单个patch
              0=>升级到该patch版本
        :return:
        """
        if self.isControl == 0:
            flag = 1
        else:
            if self.radio1.isChecked():
                flag = 0
            else:
                flag = 1
        self.upgrade.emit(flag)
        self.close()

    def _handleClose(self):
        # self.upgrade.emit(-1)
        self.close()

# 主窗口
class uimain(QWidget):
    moconn = None
    mysqlite = None
    can_upgrade_patch_order_list = []
    can_upgrade_script = []

    def __init__(self, flags, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.setStyleSheet("background-color: White;")
        self.mysqlite = MySqlite3()
        if self.mysqlite.isOpen():
            self.setupUI()
        else:
            self.mylog.error('open sqlite3 db failed')

    def setupUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)


        self.toolbar = QToolBar()
        self.connFrame = QFrame()
        self.scriptFrame = QFrame()
        self.scriptListFrame = QFrame()
        self.infoFrame = QTextBrowser()
        self.errorFrame = QTableWidget()

        self.scroll = QScrollArea()
        self.scroll.setAutoFillBackground(True)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.scriptListFrame)

        resultLayout = QVBoxLayout()
        resultLayout.addWidget(self.infoFrame)
        resultLayout.addWidget(self.errorFrame)

        detailLayout = QHBoxLayout()
        detailLayout.addWidget(self.scroll,2)
        detailLayout.addLayout(resultLayout, 6)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.connFrame)
        layout.addWidget(self.scriptFrame, )
        layout.addLayout(detailLayout)


        self.setToolBar()
        self.setConnFrame()
        self.setScriptFrame()
        self.setScriptListFrame()
        self.setInfoFrame()
        self.setErrorFrame()
        self.setDefaultData()
        self.setSlotFunction()

    def setToolBar(self):
        """
        设置工具栏
        :return:
        """
        self.connManagerAction = QAction(QIcon(":/resource/connManager.png"), "管理器", self)
        self.connManagerAction.triggered.connect(self._handleShowConnConfig)

        self.close_action = QAction(QIcon(":/resource/disConnect.png"), '断开当前连接', self)
        self.close_action.triggered.connect(self._handleCloseSource)
        self.close_action.setEnabled(False)

        self.reconn_action = QAction(QIcon(":/resource/reConnect.png"), '连接当前连接', self)
        self.reconn_action.triggered.connect(self._handleConnSource)
        self.reconn_action.setEnabled(False)

        self.refreshscript_action = QAction(QIcon(":/resource/reFresh.png"), '重连当前连接', self)
        self.refreshscript_action.triggered.connect(self._handleRefresh)


        self.toolbar.addAction(self.connManagerAction)
        self.toolbar.addAction(self.close_action)
        self.toolbar.addAction(self.reconn_action)
        self.toolbar.addAction(self.refreshscript_action)

    def setConnFrame(self):
        self.connFrame.setFixedHeight(40)
        self.connFrame.setObjectName("connFrame")

        # 连接
        self.conn_label = QLabel("连接(C):")
        self.conn_label.setObjectName("connLabel")
        self.conn_value = QComboBox()
        self.conn_value.setView(QListView())
        self.setConnValue()
        # 连接按钮
        self.conn_button = QPushButton('连 接')
        self.conn_button.setToolTip('连接数据库')
        self.conn_button.setEnabled(False)

        # 初始化按钮
        self.init_button = QPushButton('初始化')
        self.init_button.setToolTip('初始化schema')
        self.init_button.setEnabled(False)

        # 清除按钮
        self.drop_button = QPushButton('清 除')
        self.drop_button.setToolTip('清除schema的表结构和数据')
        self.drop_button.setEnabled(False)

        # 清空日志
        self.clearlog_button = QPushButton('清空日志')
        self.clearlog_button.setToolTip('清空日志区域')

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.conn_label)
        hbox1.addWidget(self.conn_value)
        hbox1.addStretch()

        top_hbox = QHBoxLayout(self.connFrame)
        top_hbox.setContentsMargins(5, 5, 1, 1)
        top_hbox.addLayout(hbox1)
        top_hbox.addWidget(self.conn_button)
        top_hbox.addWidget(self.init_button)
        top_hbox.addWidget(self.drop_button)
        top_hbox.addStretch(10)
        top_hbox.addWidget(self.clearlog_button)

    def setScriptFrame(self):
        self.scriptFrame.setFixedHeight(30)
        self.scriptFrame.setObjectName("scriptFrame")

        script_label = QLabel()
        script_label.setAlignment(Qt.AlignVCenter)
        script_label.setMargin(0)
        script_label.setText('脚本路径:')
        self.script_value = QLabel()
        self.script_value.setObjectName("scriptValue")
        self.script_value.setFrameShape(QFrame.NoFrame)
        self.script_value.setFrameShadow(QFrame.Sunken)
        self.script_value.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        hbox = QHBoxLayout(self.scriptFrame)
        hbox.setContentsMargins(1, 1, 1, 1)
        hbox.addWidget(script_label)
        hbox.addWidget(self.script_value)
        hbox.addStretch()

    def setScriptListFrame(self):
        self.scriptListFrame.setObjectName("scriptListFrame")
        self.gridlayout = QGridLayout(self.scriptListFrame)
        self.gridlayout.setContentsMargins(0, 0, 0, 0)
        self.gridlayout.setSpacing(5)



    def setInfoFrame(self):
        self.infoFrame.setObjectName("infoFrame")


    def setErrorFrame(self):
        self.errorFrame.setFocusPolicy(Qt.NoFocus)
        self.errorFrame.setColumnCount(3)
        self.errorFrame.setHorizontalHeaderLabels(['错误', 'SQL', '时间'])
        header = self.errorFrame.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

    def setSlotFunction(self):
        """
        设置槽函数
        :return:
        """
        # 连接QCombox变化
        self.conn_value.currentTextChanged.connect(self.setDefaultData)
        # 连接资源
        self.conn_button.clicked.connect(self._handleConnSource)
        # 初始化schema
        self.init_button.clicked.connect(self._handleInitDialog)
        # 清除schema表结构和数据
        self.drop_button.clicked.connect(self._handleDropDialog)
        # 清空日志区域信息
        self.clearlog_button.clicked.connect(self._handleclearLogArea)

    def setDefaultData(self):
        """
        设置默认数据
        :return:
        """
        conn_select_id = self.conn_value.currentData()
        if conn_select_id is not None:
            connInfos = getOneRecordForAll(self.mysqlite, int(conn_select_id))
            conn = connInfos["conn"]
            datasource = connInfos["datasource"]
            project = connInfos["project"]

            conn_detail = conn["detail"]
            self.pid = conn["pid"]
            self.pname = project["name"]
            self.pscriptdir = project["script"]

            self.sid = conn["did"]
            self.sname = datasource["name"]
            self.sdriver = datasource["driver"]
            self.shost = datasource["host"]
            self.sport = datasource["port"]

            if self.sdriver == "oracle":
                self.schema_servicename = datasource["sid"]
                self.schema_user = conn_detail.split("&")[0]
                self.schema_pass = conn_detail.split("&")[1]
            else:
                self.schema_user = datasource["user"]
                self.schema_pass = datasource["password"]
                self.schema_dbname = conn_detail
            self.script_value.setText(self.pscriptdir)

        self.conn_button.setEnabled(True)

        if self.init_button.isEnabled():
            self.init_button.setEnabled(False)

        if self.moconn is not None:
            self._handleCloseSource()
            self.close_action.setEnabled(False)
            self.reconn_action.setEnabled(True)

    def setConnValue(self):
        connections = getConnRecords(self.mysqlite)
        for index, conn in enumerate(connections):
            datasource = getDatasourceRecords(self.mysqlite, conn["did"])
            if datasource[0]["driver"] == "oracle":
                icon = QIcon(":/resource/oracle.png")
            elif datasource[0]["driver"] == "mysql":
                icon = QIcon(":/resource/mysql.png")
            elif datasource[0]["driver"] == "postgresql":
                icon = QIcon(":/resource/postgresql.png")
            elif datasource[0]["driver"] == "sqlite":
                icon = QIcon(":/resource/sqlite.png")
            else:
                icon = QIcon(":/resource/database_item.jpg")
            self.conn_value.addItem(icon, conn["name"], conn["id"])
            if index == 0:
                self.conn_value.setCurrentText(conn["name"])

    def _handleConnSchema(self):
        """
        连接数据库
        :return:
        """
        if self.sdriver == "oracle":
            mo = MyOracle(self.schema_user, self.schema_pass, self.shost, self.sport,
                          SERVICE_NAME=self.schema_servicename)
        elif self.sdriver == "mysql":
            mo = MyMySql(self.shost, self.sport, self.schema_user, self.schema_pass, self.schema_dbname)
        else:
            mo = None
        return mo

    def _handleConnSource(self):
        """
        连接按钮对应的函数
        :return:
        """
        # 清空脚本区域，日志区域
        self.clearScriptArea()
        self.clearLogArea()
        #
        if self.sdriver == "oracle":
            msg = "数据库=>{0}://{1}:{2}/{3}?user={4}".format(self.sdriver,self.shost, self.sport, self.schema_servicename, self.schema_user)
        else:
            msg = "数据库=>{0}://{1}:{2}/{3}?user={4}".format(self.sdriver,self.shost, self.sport, self.schema_dbname,self.schema_user)
        self._handleUpdateLog(0, msg)

        # 判断moconn是否已经连接，若连接则关闭
        if self.moconn is not None:
            self.moconn.close()
        self.moconn = self._handleConnSchema()
        self.conn_th = ConnThread(self.moconn, self.pscriptdir,self.sdriver)
        self.conn_th.loginTrigger.connect(self._handleUpdateLog)
        self.conn_th.dataTrigger.connect(self._handleUpdateScript)
        self.conn_th.isControlTrigger.connect(self._handleSetControl)
        self.conn_th.start()
        if self.moconn.conn is not None:
            self.init_button.setEnabled(True)  # 初始化按钮可用
            self.drop_button.setEnabled(True)  # 清除表结构和数据按钮可用
            self.close_action.setEnabled(True)  # 工具栏断开按钮可用
            self.reconn_action.setEnabled(False)  # 重连按钮不可用
            self.conn_button.setEnabled(False)  # 连接按钮不可用

    def _handleCloseSource(self):
        """
        关闭当前数据库连接
        :return:
        """
        if self.moconn is not None:
            self.close_th = CloseThread(self.moconn)
            self.close_th.infoTrigger.connect(self._handleUpdateLog)
            self.close_th.start()
            self.moconn = None
        self.clearScriptArea()
        self.init_button.setEnabled(False)  # 关闭连接后，初始化按钮不可用
        self.close_action.setEnabled(False)
        self.conn_button.setEnabled(True)  # 关闭连接后，连接按钮可用
        self.reconn_action.setEnabled(True)

    def _handleUpdateScript(self, patch_order_list):

        """
        更新脚本区域的控件
        :param patch_order_list:[('0.1.5_20180419.sql',(0, 1, 5, 0, 20180419)),(),()]
        :return:
        """
        self.can_upgrade_patch_order_list = patch_order_list
        for patch in self.can_upgrade_patch_order_list:
            self.can_upgrade_script.append(patch[0])
        patch_num = len(self.can_upgrade_script)

        if patch_num > 0:
            for index, patch_script in enumerate(self.can_upgrade_script):
                radiobutton = QRadioButton(patch_script)
                radiobutton.toggled.connect(self._handleUpgradeWindow)  # 选择弹出升级确认对话框
                self.gridlayout.addWidget(radiobutton, index, 0, 1, 1)
            
        else:
            self._handleUpdateLog(NormalMessage,"无可更新patch")
            lineinfo = QLabel('无可更新的脚本')
            lineinfo.setObjectName('nonepatch')
            lineinfo.setFrameShape(QFrame.NoFrame)

    def _handleInitDialog(self):
        """
        初始化按钮确认对话框
        :return:
        """
        self.initDialog = initDialog()
        self.initDialog.show()
        self.initDialog.isControl.connect(self._handleInitSchema)

    def _handleInitSchema(self, iscontrol):
        """
        初始化按钮对应的函数
        :return:
        """
        if not os.path.isdir(self.pscriptdir):
            QMessageBox.warning(self, 'warning', u'脚本路径不存在！\n %s' % (self.pscriptdir), QMessageBox.Cancel)
        else:
            if not self.moconn:
                self.moconn = self._handleConnSchema()
            self.isControl = iscontrol
            self.init_th = InitThread(self.moconn, self.pscriptdir, iscontrol, self.sdriver)
            self.init_th.infoTrigger.connect(self._handleUpdateLog)
            self.init_th.errorTrigger.connect(self._handleUpdateErrorLog)
            self.init_th.start()

    def _handleDropDialog(self):
        """
        清除表表结构和数据对话框
        :return:
        """
        quessionbox = QMessageBox(QMessageBox.Question, "清除", "清除表结构及数据？")
        qno = quessionbox.addButton(self.tr("取消"), QMessageBox.NoRole)
        qyes = quessionbox.addButton(self.tr("确定"), QMessageBox.YesRole)
        qno.setObjectName('cancel')
        quessionbox.exec_()
        if quessionbox.clickedButton() == qyes:
            self.drop_th = DropThread(self.moconn)
            self.drop_th.infoTrigger.connect(self._handleUpdateLog)
            self.drop_th.errorTrigger.connect(self._handleUpdateErrorLog)
            self.drop_th.start()
        else:
            return

    def _handleUpgradeWindow(self):
        self.current_upgrade_script_button = self.sender()
        self.current_upgrade_script_name = self.current_upgrade_script_button.text()
        self.upgradeWindow = upgradeDialog(self.current_upgrade_script_name, self.isControl, self.pscriptdir)
        self.upgradeWindow.show()
        self.upgradeWindow.upgrade.connect(self._handleUpgradeOper)

    def _handleUpgradeOper(self, opercode):
        if opercode == -1:  # 取消
            if self.current_upgrade_script_button.isChecked():
                self.current_upgrade_script_button.setChecked(False)
        else:
            start = 0
            for index, patchinfo in enumerate(self.can_upgrade_patch_order_list):
                if patchinfo[0] == self.current_upgrade_script_name:
                    start = index
                    break

            if opercode == 0:
                upgrade_scripts_list = self.can_upgrade_patch_order_list[start:]
            elif opercode == 1:
                upgrade_scripts_list = self.can_upgrade_patch_order_list[start]
            else:
                upgrade_scripts_list = None

            self.upgrade_th = UpgradeThread(self.moconn, upgrade_scripts_list, self.pscriptdir, self.isControl)
            self.upgrade_th.infoTrigger.connect(self._handleUpdateLog)
            self.upgrade_th.errorTrigger.connect(self._handleUpdateErrorLog)
            self.upgrade_th.start()

    def _handleShowConnConfig(self):
        self.connWindow = MyWidget()
        SourceWindow(self.connWindow)
        self.connWindow.setWindowFlags(
            Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)  # 不能最大化，有关闭按钮,置顶
        self.connWindow.setWindowTitle("连接管理器")
        self.connWindow.setWindowIcon(QIcon(":/resource/connManager.png"))
        self.connWindow.show()
        self.setEnabled(False)
        self.connWindow.close_signal.connect(self._handleCloseConfig)

    def _handleCloseConfig(self):
        """
        关闭连接配置，更新主页面的连接选项
        :return:
        # """
        self.setEnabled(True)
        self.conn_value.clear()
        self.setConnValue()

    def _handleUpdateLog(self, type, msg):
        printTime = "[{0}]".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        printTimeHtml = '<vi style = "color:0033FF;" >{0}: </vi >'.format(printTime)

        if type == ErrorMessage:
            info = '<vi style = "color:red;" >{0}</vi>'.format(msg)
            myLog.error(msg)
        elif type == WarningMessage:
            info = '<vi style = "color:yellow;" >{0}</vi>'.format(msg)
            myLog.warning(msg)
        else:
            info = '<vi style = "color:black;" >{0}</vi>'.format(msg)
            myLog.info(msg)
        printInfo = "<p>{0}{1}</p>".format(printTimeHtml, info)
        self.infoFrame.append(printInfo)

    def _handleUpdateErrorLog(self, error_reason, error_sql):
        myLog.error("{0}=>{1}".format(error_reason,error_sql))
        hTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        rowNum = self.errorFrame.rowCount()
        self.errorFrame.insertRow(rowNum)
        self.errorFrame.setItem(rowNum, 0, QTableWidgetItem(error_reason))
        self.errorFrame.setItem(rowNum, 1, QTableWidgetItem(error_sql))
        self.errorFrame.setItem(rowNum, 2, QTableWidgetItem(hTime))

    def _handleSetControl(self, controlFlag):
        """
        设置schema是否被控制
        :param controlflag:
        :return:
        """
        self.isControl = controlFlag

    def _handleclearLogArea(self):
        self.clearLogArea()

    def _handleRefresh(self):
        """
        刷新脚本显示
        :return:
        """
        self._handleConnSource()

    def clearLogArea(self):
        """
        清空日志区域
        :return:
        """
        self.infoFrame.clear()
        self.errorFrame.clearContents()
        self.errorFrame.setRowCount(0)

    def clearScriptArea(self):
        """
        清空脚本区域
        :return:
        # """
        for i in reversed(range(self.gridlayout.count())):
            try:
                self.gridlayout.itemAt(i).widget().setParent(None)
            except Exception as e:
                logging.error(e)
        self.can_upgrade_script = []

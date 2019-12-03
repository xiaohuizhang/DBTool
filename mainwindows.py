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
from general import *
from schemaoper import ConnThread, InitThread, UpgradeThread, CloseThread, DropThread
from sourceconfig import SourceWindow
import resource


class MyWidget(QWidget):
    """对QWidget类重写，实现一些功能"""
    close_signal = pyqtSignal()

    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        # reply = QMessageBox.question(self,'本程序',"是否要退出程序？",QMessageBox.Yes | QMessageBox.No,QMessageBox.No)
        # if reply == QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()
        self.close_signal.emit()


class initDialog(QDialog):
    """
    初始化schema确认对话框
    """
    iscontrol = pyqtSignal(int)

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
        self.iscontrol.emit(flag)
        self.close()

    def _handleClose(self):
        self.close()


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
        self.iscontrol = iscontrol
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
        if self.iscontrol == 0:
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
        try:
            handle = open(patch_dir, 'r')
            filelines = handle.read()
            self.sql_area.append(filelines)
        except Exception as e:
            self.logs.emit(str(e))
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
        if self.iscontrol == 0:
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


class uimain(QMainWindow):
    moconn = None
    mysqlite = None
    can_upgrade_patch_order_list = []
    can_upgrade_script = []

    def __init__(self):
        self.mylog = logging.getLogger('myapp')
        self.mysqlite = MySqlite3()
        self.mysqlite.opendb()
        if self.mysqlite.isopen():
            super(uimain, self).__init__()
            self.setupUI(self)
        else:
            self.mylog.error('sqlite3数据库打开失败')

    def setupUI(self, uimain):
        uimain.setObjectName("MainWindow")
        uimain.resize(1200, 700)
        uimain.setWindowTitle('DBTool')
        uimain.setWindowIcon(QIcon(':/resource/title.ico'))
        # 将窗口移动到屏幕中心
        qr = uimain.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        uimain.move(qr.topLeft())

        self.setMainFrame()
        self.setToolBar()

    # def setMenu(self):
    #     """
    #     设置菜单栏
    #     :return:
    #     """
    #     menubar = self.menuBar()
    #     filemenu = menubar.addMenu("")
    #     filemenu.addAction(QAction(QIcon(":/connManager1.png"), "连接管理器", self, triggered=self._handleShowConnConfig))
    #     # filemenu.addAction(QAction(QIcon("./resource/connManager.png"), "连接管理器", self, triggered=self._handleShowConnConfig))
    #     # filemenu.addAction(QAction(QIcon("./resource/conntree.png"), "添加当前连接到连接管理器", self))
    #     # filemenu.addAction("导出")
    #     # filemenu.addAction("导入")
    #
    #     # 配置
    #     # configmenu = menubar.addMenu("配置(C)")
    #     # configmenu.addAction(QAction("连接配置", self, triggered=self._handleShowConnConfig))
    #     # configmenu.addAction(QAction("项目源配置", self, triggered=self.openschemawindow))
    #     # configmenu.addAction(QAction("数据源配置", self, triggered=self.openschemawindow))
    #
    #     toolmenu = menubar.addMenu("工具(T)")
    #     toolmenu.addAction("断开当前连接")
    #     toolmenu.addAction("重连上次连接")
    #
    #     helpmenu = menubar.addMenu("帮助(H)")
    #     helpmenu.addAction("关于")

    def setToolBar(self):
        """
        设置工具栏
        :return:
        """
        toolbar1 = self.addToolBar("bar1")
        toolbar1.addAction(
            QAction(QIcon(":/resource/connManager.png"), "连接管理器", self, triggered=self._handleShowConnConfig))

        toolbar2 = self.addToolBar('bar2')
        self.close_action = QAction(QIcon(":/resource/disConnect.png"), '断开当前连接', self)
        self.close_action.triggered.connect(self._handleCloseSource)
        self.close_action.setEnabled(False)

        self.reconn_action = QAction(QIcon(":/resource/reConnect.png"), '连接当前连接', self)
        self.reconn_action.triggered.connect(self._handleConnSource)
        self.reconn_action.setEnabled(False)

        self.refreshscript_action = QAction(QIcon(":/resource/reFresh.png"), '重连当前连接', self)
        self.refreshscript_action.triggered.connect(self._handleRefresh)
        toolbar2.addAction(self.close_action)
        toolbar2.addAction(self.reconn_action)
        toolbar2.addAction(self.refreshscript_action)

    def setMainFrame(self):
        """
        设置页面整体布局
        :return:
        """
        # top
        self.topframe = QFrame(self)
        self.topframe.setObjectName('topframe')
        self.topframe.setFrameShape(QFrame.StyledPanel)
        self.topframe.setFixedHeight(40)
        # middle
        self.middle_frame = QFrame(self)
        # self.middle_frame.setFrameShape(QFrame.StyledPanel)
        self.middle_frame.setFixedHeight(20)
        # bottom_left
        self.bottom_left_bot_frame = QFrame(self)
        # self.bottom_left_bot_frame.setFrameShape(QFrame.StyledPanel)

        scroll = QScrollArea()
        scroll.setAutoFillBackground(True)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.bottom_left_bot_frame)

        # bottom_right
        self.bottom_right_info_area = QTextBrowser(self)
        self.bottom_right_error_area = QTableWidget(self)

        bottom_right_spliter = QSplitter(Qt.Vertical)
        bottom_right_spliter.setHandleWidth(1)
        bottom_right_spliter.addWidget(self.bottom_right_info_area)
        bottom_right_spliter.addWidget(self.bottom_right_error_area)

        bottom_spliter = QSplitter(Qt.Horizontal)
        bottom_spliter.setHandleWidth(1)
        bottom_spliter.addWidget(scroll)
        bottom_spliter.addWidget(bottom_right_spliter)
        bottom_spliter.setStretchFactor(0, 1)
        bottom_spliter.setStretchFactor(1, 2)
        bottom_spliter.setChildrenCollapsible(False)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setOpaqueResize(False)
        self.splitter.setHandleWidth(1)
        self.splitter.addWidget(self.topframe)
        self.splitter.addWidget(self.middle_frame)
        self.splitter.addWidget(bottom_spliter)
        self.setCentralWidget(self.splitter)

        self.setFrameTop()
        self.setFrameMiddle()
        self.setFrameBottom()
        self.setDefaultData()
        self.setSlotFunction()

    def setFrameTop(self):
        """
        设置顶部布局
        :return:
        """
        # 连接
        self.conn_label = QLabel('连接(C):')
        self.conn_label.setObjectName('connname')
        self.conn_value = QComboBox()
        self.conn_value.setView(QListView())  # 在QSS中设置完后，需要调用如下代码，否则会使用默认的item样式，导致设置无效
        currentResource = getConnAllRecord(self.mysqlite)
        if type(currentResource) == list and len(currentResource) > 0:
            for index, conn in enumerate(currentResource):
                self.conn_value.addItem(QIcon(":/resource/database_item.png"),conn[1], conn[0])
                if index == 0:
                    self.conn_value.setCurrentText(conn[1])

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

        top_hbox = QHBoxLayout(self.topframe)
        top_hbox.setContentsMargins(5, 5, 1, 1)
        top_hbox.addLayout(hbox1)
        top_hbox.addWidget(self.conn_button)
        top_hbox.addWidget(self.init_button)
        top_hbox.addWidget(self.drop_button)
        top_hbox.addStretch(10)
        top_hbox.addWidget(self.clearlog_button)
        # top_hbox.addStretch(10)
        # top_hbox.addWidget(self.version_control)
        # top_hbox.addStretch(10)

    def setFrameMiddle(self):
        """
        设置中间布局
        :return:
        """
        script_label = QLabel()
        script_label.setAlignment(Qt.AlignTop)
        script_label.setMargin(0)
        script_label.setText('脚本路径:')
        self.script_value = QLabel()
        self.script_value.setObjectName('scriptvalue')
        self.script_value.setFrameShape(QFrame.NoFrame)
        self.script_value.setFrameShadow(QFrame.Sunken)
        self.script_value.setAlignment(Qt.AlignLeft)

        hbox = QHBoxLayout(self.middle_frame)
        hbox.setContentsMargins(1, 1, 1, 1)
        hbox.addWidget(script_label)
        hbox.addWidget(self.script_value)
        hbox.addStretch()

    def setFrameBottom(self):
        """
        设置底部布局
        :return:
        """
        # middle-left
        self.gridlayout = QGridLayout(self.bottom_left_bot_frame)
        self.gridlayout.setContentsMargins(0, 0, 0, 0)
        self.gridlayout.setSpacing(5)

        self.bottom_right_error_area.setColumnCount(3)
        self.bottom_right_error_area.setHorizontalHeaderLabels(['错误', 'SQL', '时间'])
        header = self.bottom_right_error_area.horizontalHeader()
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
        # 连接所有资源
        self.conn_button.clicked.connect(self._handleConnSource)
        # 初始化schema
        self.init_button.clicked.connect(self._handleInitDialog)
        # 清除schema表结构和数据
        self.drop_button.clicked.connect(self._handleDropDialog)
        # 清空日志区域信息
        self.clearlog_button.clicked.connect(self._handleClearLogArea)

    def setDefaultData(self):
        """
        设置默认数据
        :return:
        """
        conn_select_id = self.conn_value.currentData()
        if conn_select_id is not None:
            conn_record = getOneRecordForAll(self.mysqlite, int(conn_select_id))

            self.schema_user = conn_record[2]
            self.schema_pass = conn_record[3]

            self.pid = conn_record[4]
            self.pname = conn_record[5]
            self.pdriver = conn_record[6]
            self.pscriptdir = conn_record[7]

            self.pid = conn_record[8]
            self.sname = conn_record[9]
            self.shost = conn_record[10]
            self.sport = conn_record[11]
            self.servicename = conn_record[12]

            self.script_value.setText(self.pscriptdir)

            self.conn_button.setEnabled(True)

            if self.init_button.isEnabled():
                self.init_button.setEnabled(False)

            if self.moconn is not None:
                self._handleCloseSource()
                self.close_action.setEnabled(False)
                self.reconn_action.setEnabled(True)

    def _handleConnSchema(self):
        """
        连接数据库
        :return:
        """
        mo = MyOracle(self.schema_user, self.schema_pass, self.shost, SERVICE_NAME=self.servicename)
        return mo

    def _handleConnSource(self):
        """
        连接按钮对应的函数
        :return:
        """
        # 清空脚本区域，日志区域
        self.clearscriptarea()
        self.clearlogarea()
        # 
        self._handleUpdateLog(
            u'数据库TNS=>%s:%s/%s,schema=>%s' % (self.shost, self.sport, self.servicename, self.schema_user))
        if '' in [self.shost, self.sport, self.servicename, self.schema_user]:
            self._handleUpdateLog('数据源信息为空,无法操作！')
            return
        # 判断moconn是否已经连接，若连接则关闭
        if self.moconn is not None:
            self.moconn.close()
        self.moconn = self._handleConnSchema()
        self.conn_th = ConnThread(self.moconn, self.pscriptdir)
        self.conn_th.trigger_loginfo.connect(self._handleUpdateLog)
        self.conn_th.trigger_data.connect(self._handleUpdateScript)
        self.conn_th.trigger_iscontrol.connect(self._handleSetControl)
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
            self.close_th.triger_info.connect(self._handleUpdateLog)
            self.close_th.triger_error.connect(self._handleUpdateErrorLog)
            self.close_th.start()
            self.moconn = None
        self.clearscriptarea()
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
                # listwidgetitem = QListWidgetItem(radiobutton)
                # self.script_list.addItem(listwidgetitem)
        else:
            printinfo = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]:schema无可更新的脚本"
            self.bottom_right_info_area.append(printinfo)
            lineinfo = QLabel('无可更新的脚本')
            lineinfo.setObjectName('nonepatch')
            lineinfo.setFrameShape(QFrame.NoFrame)
            # self.gridlayout.addWidget(lineinfo, 0, 0, 1, 1)

    def _handleInitDialog(self):
        """
        初始化按钮确认对话框
        :return:
        """
        self.initdialog = initDialog()
        self.initdialog.show()
        self.initdialog.iscontrol.connect(self._handleInitSchema)

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
            self.iscontrol = iscontrol
            self.init_th = InitThread(self.moconn, self.pscriptdir, iscontrol)
            self.init_th.triger_info.connect(self._handleUpdateLog)
            self.init_th.triger_error.connect(self._handleUpdateErrorLog)
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
            self.drop_th.triger_info.connect(self._handleUpdateLog)
            self.drop_th.triger_error.connect(self._handleUpdateErrorLog)
            self.drop_th.start()
        else:
            return

    def _handleUpgradeWindow(self):
        self.current_upgrade_script_button = self.sender()
        self.current_upgrade_script_name = self.current_upgrade_script_button.text()
        self.upgradewindow = upgradeDialog(self.current_upgrade_script_name, self.iscontrol, self.pscriptdir)
        self.upgradewindow.show()
        self.upgradewindow.upgrade.connect(self._handleUpgradeOper)

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

            self.upgrade_th = UpgradeThread(self.moconn, upgrade_scripts_list, self.pscriptdir, self.iscontrol)
            self.upgrade_th.triger_info.connect(self._handleUpdateLog)
            self.upgrade_th.triger_error.connect(self._handleUpdateErrorLog)
            self.upgrade_th.start()

    def _handleShowConnConfig(self):
        # self.connwindow = QWidget()
        self.connwindow = MyWidget()
        SourceWindow(self.connwindow)
        self.connwindow.setWindowFlags(
            Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)  # 不能最大化，有关闭按钮,置顶
        self.connwindow.setWindowTitle("连接管理器")
        self.connwindow.setWindowIcon(QIcon(":/resource/connManager.png"))
        self.connwindow.show()
        self.setEnabled(False)
        self.connwindow.close_signal.connect(self._handleCloseConfig)

    def _handleCloseConfig(self):
        """
        关闭连接配置，更新主页面的连接选项
        :return:
        # """
        self.setEnabled(True)
        self.conn_value.clear()
        for index, conn in enumerate(getConnAllRecord(self.mysqlite)):
            self.conn_value.addItem(conn[1], conn[0])
            if index == 0:
                self.conn_value.setCurrentText(conn[1])

    def _handleUpdateLog(self, msg):
        printinfo = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]:" + msg
        self.bottom_right_info_area.append(printinfo)

    def _handleUpdateErrorLog(self, error_reason, error_sql):
        htime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        _rownum = self.bottom_right_error_area.rowCount()
        self.bottom_right_error_area.insertRow(_rownum)
        self.bottom_right_error_area.setItem(_rownum, 0, QTableWidgetItem(error_reason))
        self.bottom_right_error_area.setItem(_rownum, 1, QTableWidgetItem(error_sql))
        self.bottom_right_error_area.setItem(_rownum, 2, QTableWidgetItem(htime))

    def _handleSetControl(self, controlflag):
        """
        设置schema是否被控制
        :param controlflag:
        :return:
        """
        self.iscontrol = controlflag

    def _handleClearLogArea(self):
        self.clearlogarea()

    def _handleRefresh(self):
        """
        刷新脚本显示
        :return:
        """
        # # 若当前schema未连接上，则不刷新
        # if self.moconn is None:
        #     printinfo = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]: schema未连接，无法刷新脚本列表"
        #     self.bottom_right_info_area.append('printinfo')
        #     return
        # # 清空脚本区域
        # self.clearscriptarea()
        # #
        self._handleConnSource()

    def clearlogarea(self):
        """
        清空日志区域
        :return:
        """
        self.bottom_right_info_area.clear()
        self.bottom_right_error_area.clearContents()
        self.bottom_right_error_area.setRowCount(0)

    def clearscriptarea(self):
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

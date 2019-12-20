#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2018/4/3 上午9:30
# @Author   : xhzhang
# @Site     : 
# @File     : sourceconfig.py
# @Software : PyCharm

from PyQt5.QtCore import *
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtWidgets import *
from PyQt5 import sip
from driver.Sqlite3Driver import *
from comm import *


class SourceWindow(QWidget):
    """
    配置页面展示
    flag=1:连接源显示页面
    flag=2:项目源显示页面
    flag=3:数据源显示页面
    flag=4:连接源添加页面
    flag=5:项目源添加页面
    flag=6:数据源添加页面
    """
    flag = 1  # 默认为连接显示页面

    def __init__(self, parent=None):
        self.mysqlite = MySqlite3()
        self.mysqlite.openDb()
        super(SourceWindow, self).__init__(parent)
        self.setFixedSize(800, 600)
        self.SetupUI()

    def SetupUI(self):
        # label
        self.describe_label = QLabel()
        self.describe_label.setText("连接信息: ")
        # tree
        self.left_tree = QTreeWidget()
        self.left_tree.setAutoScroll(True)
        self.left_tree.setFocusPolicy(Qt.NoFocus)
        self.left_tree.setStyle(QStyleFactory.create("windows"))
        self.left_tree.setFrameShape(QFrame.Box)

        self.left_tree.setColumnCount(2)
        self.left_tree.setColumnHidden(1, True)  # 不显示ID的列
        self.left_tree.setHeaderHidden(True)

        self.tree_root = QTreeWidgetItem(self.left_tree)
        self.tree_root.setText(0, '我的资源')
        self.tree_root.setText(1, 'ID')

        self.conn_tree = QTreeWidgetItem(self.tree_root)
        self.conn_tree.setText(0, '连接')
        self.conn_tree.setText(1, '0')

        self.pro_tree = QTreeWidgetItem(self.tree_root)
        self.pro_tree.setText(0, '项目源')
        self.pro_tree.setText(1, '1')

        self.schema_tree = QTreeWidgetItem(self.tree_root)
        self.schema_tree.setText(0, '数据源')
        self.schema_tree.setText(1, '2')

        # button
        self.button_frame = QFrame()
        self.button_frame.setFrameShape(QFrame.NoFrame)
        self.add_conn_btn = QPushButton(QIcon(":/resource/add.png"), '连  接')
        self.add_pro_btn = QPushButton(QIcon(":/resource/add.png"), '项目源')
        self.add_schema_btn = QPushButton(QIcon(":/resource/add.png"), '数据源')
        self.del_conn_btn = QPushButton(QIcon(":/resource/del.png"), '删  除')

        hbox1 = QHBoxLayout()
        hbox1.addStretch()
        hbox1.addWidget(self.add_schema_btn, 0, Qt.AlignCenter)
        hbox1.addWidget(self.add_pro_btn, 0, Qt.AlignCenter)
        hbox1.addStretch()

        hbox3 = QHBoxLayout()
        hbox3.addStretch()
        hbox3.addWidget(self.add_conn_btn, 0, Qt.AlignCenter)
        hbox3.addWidget(self.del_conn_btn, 0, Qt.AlignCenter)
        hbox3.addStretch()

        vbox = QVBoxLayout(self.button_frame)
        vbox.addLayout(hbox1, 1)
        vbox.addLayout(hbox3, 1)

        left_spliter = QSplitter(Qt.Vertical)
        left_spliter.setHandleWidth(1)  # 设置控件之间的宽度
        left_spliter.addWidget(self.describe_label)
        left_spliter.addWidget(self.left_tree)
        left_spliter.addWidget(self.button_frame)
        left_spliter.setSizes([20, 450, 100])  # 设置分割窗口下的控件的宽度，如果是垂直排列的则是高度
        left_spliter.setOpaqueResize(False)

        self.right_frame = QFrame()
        self.right_frame.setFrameShape(QFrame.NoFrame)

        middle_spliter = QSplitter(Qt.Horizontal)
        middle_spliter.setHandleWidth(1)
        middle_spliter.addWidget(left_spliter)
        middle_spliter.addWidget(self.right_frame)
        middle_spliter.setStretchFactor(0, 1)
        middle_spliter.setStretchFactor(1, 1)
        middle_spliter.setOpaqueResize(False)

        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(5, 5, 0, 0)
        hbox.addWidget(middle_spliter)
        self.setLayout(hbox)
        # 默认页面
        self.ShowConnectPage()
        self.DefaultData()
        self.SlotFunction()

    def ShowConnectPage(self):
        """
        设置中间区域的右部分区域,默认为连接信息页面
        :return:
        """
        self.connect_detail_group = QGroupBox()
        self.connect_detail_group.setTitle('连接信息')
        self.connect_project_group = QGroupBox()
        self.connect_project_group.setTitle('项目源')
        self.connect_datasource_group = QGroupBox()
        self.connect_datasource_group.setTitle('数据源')
        self.connect_editbutton = QPushButton(QIcon(":/resource/edit.png"), '修改')
        self.connect_editresult = QLabel()
        self.connect_editresult.setFixedWidth(100)
        self.connect_editresult.setObjectName('result')
        self.connect_editresult_detail = QLabel()
        self.connect_editresult_detail.setObjectName("result_detail")

        hbox4 = QHBoxLayout()
        hbox4.addStretch()
        hbox4.addWidget(self.connect_editbutton)
        hbox4.addWidget(self.connect_editresult)
        hbox4.addStretch()

        result_hbox = QHBoxLayout()
        result_hbox.addStretch()
        result_hbox.addWidget(self.connect_editresult_detail)
        result_hbox.addStretch()

        right_vbox = QVBoxLayout(self.right_frame)
        right_vbox.addWidget(self.connect_project_group, 3)
        right_vbox.addWidget(self.connect_datasource_group, 5)
        right_vbox.addWidget(self.connect_detail_group, 3)
        right_vbox.addLayout(hbox4, 1)
        right_vbox.addLayout(result_hbox, 1)
        # 项目源
        self.connect_pro_name_label = QLabel("名   称:")
        self.connect_pro_name_value = QComboBox()
        self.connect_pro_name_value.setView(QListView())
        # self.connect_pro_name_value.addItem('', -1)
        for p in getProjectRecords(self.mysqlite):
            self.connect_pro_name_value.addItem(p["name"], p["id"])

        self.connect_pro_script_label = QLabel("脚   本:")
        self.connect_pro_script_value = QLineEdit()
        self.connect_pro_script_value.setEnabled(False)

        grid1 = QGridLayout(self.connect_project_group)
        grid1.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid1.addWidget(self.connect_pro_name_label, 0, 0)
        grid1.addWidget(self.connect_pro_name_value, 0, 1)
        grid1.addWidget(self.connect_pro_script_label, 1, 0)
        grid1.addWidget(self.connect_pro_script_value, 1, 1)

        # # # 数据源
        # name
        self.connect_datasource_name_label = QLabel("名   称:")
        self.connect_datasource_name_value = QComboBox()
        self.connect_datasource_name_value.setView(QListView())
        # self.connect_datasource_name_value.addItem('', -1)
        for s in getDatasourceRecords(self.mysqlite):
            self.connect_datasource_name_value.addItem(s["name"], s["id"])
        # driver
        self.connect_datasource_driver_label = QLabel("驱   动:")
        self.connect_datasource_driver_value = QLineEdit()
        self.connect_datasource_driver_value.setEnabled(False)

        # host
        self.connect_datasource_host_label = QLabel("主   机:")
        self.connect_datasource_host_value = QLineEdit()
        self.connect_datasource_host_value.setEnabled(False)

        # port
        self.connect_datasource_port_label = QLabel("端   口:")
        self.connect_datasource_port_value = QLineEdit()
        self.connect_datasource_port_value.setEnabled(False)
        # other
        self.connect_datasource_other_servicename_label = QLabel("服务名:")
        self.connect_datasource_other_servicename_value = QLineEdit()
        self.connect_datasource_other_servicename_value.setEnabled(False)

        self.connect_datasource_other_user_label = QLabel("用户名:")
        self.connect_datasource_other_user_value = QLineEdit()
        self.connect_datasource_other_user_value.setEnabled(False)

        self.connect_datasource_other_pass_label = QLabel("密   码:")
        self.connect_datasource_other_pass_value = QLineEdit()
        self.connect_datasource_other_pass_value.setEnabled(False)
        self.connect_datasource_other_pass_value.setEchoMode(QLineEdit.Password)

        grid2 = QGridLayout(self.connect_datasource_group)
        grid2.setObjectName("show_connect_datasource_grid")
        grid2.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        grid2.addWidget(self.connect_datasource_name_label, 0, 0)
        grid2.addWidget(self.connect_datasource_name_value, 0, 1)

        grid2.addWidget(self.connect_datasource_driver_label, 1, 0)
        grid2.addWidget(self.connect_datasource_driver_value, 1, 1)

        grid2.addWidget(self.connect_datasource_host_label, 2, 0)
        grid2.addWidget(self.connect_datasource_host_value, 2, 1)

        grid2.addWidget(self.connect_datasource_port_label, 3, 0)
        grid2.addWidget(self.connect_datasource_port_value, 3, 1)


        # conn detail
        # conn name
        self.connect_name_label = QLabel("连接名:")
        self.connect_name_value = QLineEdit()

        # user
        self.connect_detail_user_label = QLabel("用户名:")
        self.connect_detail_user_value = QLineEdit()

        # password
        self.connect_detail_passwd_label = QLabel("密  码:")
        self.connect_detail_passwd_value = QLineEdit()
        self.connect_detail_passwd_value.setEchoMode(QLineEdit.Password)

        # dbname
        self.connect_detail_dbname_label = QLabel("数据库:")
        self.connect_detail_dbname_value = QLineEdit()
        # self.connect_detail_dbname_value.setView(QListView())
        # self.connect_detail_dbname_value.addItem('', -1)

        grid3 = QGridLayout(self.connect_detail_group)
        grid3.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid3.setObjectName("show_connect_detail_grid")

        grid3.addWidget(self.connect_name_label, 0, 0)
        grid3.addWidget(self.connect_name_value, 0, 1)


    def ShowProjectPage(self):
        """
        设置中间区域的右边部分-项目源页面
        :return:
        """
        pro_group = QGroupBox()
        pro_group.setTitle('项目源')
        pro_group.setMinimumHeight(475)
        self.pro_editbutton = QPushButton(QIcon(":/resource/edit.png"), '修改')
        self.pro_editresult = QLabel()
        self.pro_editresult.setObjectName('result')
        self.pro_editresult.setFixedWidth(100)
        self.pro_editresult_detail = QLabel()
        self.pro_editresult_detail.setObjectName("result_detail")

        hbox4 = QHBoxLayout()
        hbox4.addStretch()
        hbox4.addWidget(self.pro_editbutton)
        hbox4.addWidget(self.pro_editresult)
        hbox4.addStretch()

        result_hbox = QHBoxLayout()
        result_hbox.addStretch()
        result_hbox.addWidget(self.pro_editresult_detail)
        result_hbox.addStretch()

        right_vbox = QVBoxLayout(self.right_frame)
        right_vbox.addWidget(pro_group, 6)
        right_vbox.addStretch(10)
        right_vbox.addLayout(hbox4, 1)
        right_vbox.addLayout(result_hbox, 1)

        self.pro_pro_id_label = QLabel("项目源ID:")
        self.pro_pro_id_value = QLineEdit()
        self.pro_pro_id_value.setEnabled(False)

        self.pro_pro_name_label = QLabel("项目名称:")
        self.pro_pro_name_value = QLineEdit()


        self.pro_pro_script_label = QLabel("脚本路径:")
        self.pro_pro_script_value = QLineEdit()

        grid1 = QGridLayout(pro_group)
        grid1.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid1.addWidget(self.pro_pro_id_label, 0, 0)
        grid1.addWidget(self.pro_pro_id_value, 0, 1)
        grid1.addWidget(self.pro_pro_name_label, 1, 0)
        grid1.addWidget(self.pro_pro_name_value, 1, 1)
        grid1.addWidget(self.pro_pro_script_label, 2, 0)
        grid1.addWidget(self.pro_pro_script_value, 2, 1)

        # 修改项目源按钮对应操作
        self.pro_editbutton.clicked.connect(self._handelEditPro)

    def ShowDataSourcePage(self):
        """
        设置中间区域的右边部分-数据源页面
        :return:
        """
        schema_group = QGroupBox()
        schema_group.setTitle('数据源')
        schema_group.setMinimumHeight(475)
        self.schema_editbutton = QPushButton(QIcon(":/resource/edit.png"), '修改')
        self.schema_editresult = QLabel()
        self.schema_editresult.setObjectName('result')
        self.schema_editresult.setFixedWidth(100)
        self.schema_editresult_detail = QLabel()
        self.schema_editresult_detail.setObjectName("result_detail")

        hbox4 = QHBoxLayout()
        hbox4.addStretch()
        hbox4.addWidget(self.schema_editbutton)
        hbox4.addWidget(self.schema_editresult)
        hbox4.addStretch()

        result_hbox = QHBoxLayout()
        result_hbox.addStretch()
        result_hbox.addWidget(self.schema_editresult_detail)
        result_hbox.addStretch()

        right_vbox = QVBoxLayout(self.right_frame)
        right_vbox.addWidget(schema_group, 6)
        right_vbox.addStretch(10)
        right_vbox.addLayout(hbox4, 1)
        right_vbox.addLayout(result_hbox, 1)

        # id
        self.schema_schema_id_label = QLabel("ID:")
        self.schema_schema_id_value = QLineEdit()
        self.schema_schema_id_value.setEnabled(False)
        # name
        self.schema_schema_name_label = QLabel("名   称:")
        self.schema_schema_name_value = QLineEdit()
        # driver
        self.schema_schema_driver_label = QLabel("驱   动:")
        self.schema_schema_driver_value = QComboBox()
        self.schema_schema_driver_value.addItems(Driver_Type)
        # host
        self.schema_schema_host_label = QLabel("主   机:")
        self.schema_schema_host_value = QLineEdit()
        # port
        self.schema_schema_port_label = QLabel("端   口:")
        self.schema_schema_port_value = QLineEdit()
        # other
        self.schema_schema_servicename_label = QLabel("服务名:")
        self.schema_schema_servicename_value = QLineEdit()

        self.schema_schema_user_label = QLabel("用户名:")
        self.schema_schema_user_value = QLineEdit()

        self.schema_schema_pass_label = QLabel("密   码:")
        self.schema_schema_pass_value = QLineEdit()
        self.schema_schema_pass_value.setEchoMode(QLineEdit.Password)


        grid2 = QGridLayout(schema_group)
        grid2.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid2.setObjectName("show_datatsource_grid")

        grid2.addWidget(self.schema_schema_id_label, 0, 0)
        grid2.addWidget(self.schema_schema_id_value, 0, 1)

        grid2.addWidget(self.schema_schema_name_label, 1, 0)
        grid2.addWidget(self.schema_schema_name_value, 1, 1)

        grid2.addWidget(self.schema_schema_driver_label, 2, 0)
        grid2.addWidget(self.schema_schema_driver_value, 2, 1)

        grid2.addWidget(self.schema_schema_host_label, 3, 0)
        grid2.addWidget(self.schema_schema_host_value, 3, 1)

        grid2.addWidget(self.schema_schema_port_label, 4, 0)
        grid2.addWidget(self.schema_schema_port_value, 4, 1)

    def AddConnPage(self):
        """
        创建一个新连接
        :return:
        """
        # 清空右边区域里的所有控件
        self.clearAllChileren(self.right_frame)
        # 重置flag
        self.flag = 4
        # 整体布局
        # 连接信息
        group = QGroupBox()
        group.setTitle('新连接')
        group.setObjectName('indent')
        group.setAutoFillBackground(True)
        # 连接名
        self.conn_exist_label = QLabel('连接名:')
        self.conn_exist_value = QLineEdit()

        # 项目源
        self.pro_exist_label = QLabel("项目源:")
        self.pro_exist_label.setObjectName('indent')
        self.pro_exist_value = QComboBox()
        self.pro_exist_value.setView(QListView())
        # 数据源
        self.schema_exist_label = QLabel("数据源:")
        self.schema_exist_label.setObjectName('indent')
        self.schema_exist_value = QComboBox()
        self.schema_exist_value.setView(QListView())
        # 不显示
        self.schema_exist_driver = QLabel()
        self.schema_exist_driver.setHidden(True)

        # oracle conn detail
        self.user_exist_label = QLabel('用户名:')
        self.user_exist_value = QLineEdit()

        self.pass_exist_label = QLabel('密码:')
        self.pass_exist_value = QLineEdit()
        self.pass_exist_value.setEchoMode(QLineEdit.Password)

        # mysql conn detail
        self.dbname_exist_label = QLabel('数据库名:')
        self.dbname_exist_value = QLineEdit()

        # 保存按钮
        self.btn1 = QPushButton(QIcon(":/resource/save.png"), "保存")
        # 保存的结果
        self.add_conn_result = QLabel()
        self.add_conn_result.setObjectName('result')
        self.add_conn_result.setFixedWidth(100)
        # 保存的结果详情
        self.add_conn_result_detail = QLabel()
        self.add_conn_result_detail.setObjectName("result_detail")
        hbox0 = QHBoxLayout()
        hbox0.setContentsMargins(5, 5, 5, 0)
        hbox0.addStretch()
        hbox0.addWidget(self.btn1)
        hbox0.addWidget(self.add_conn_result)
        hbox0.addStretch()
        result_hbox = QHBoxLayout()
        result_hbox.addStretch()
        result_hbox.addWidget(self.add_conn_result_detail)
        result_hbox.addStretch()

        grid = QGridLayout(group)
        grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid.setObjectName("add_connect_grid")
        grid.addWidget(self.conn_exist_label, 0, 0)
        grid.addWidget(self.conn_exist_value, 0, 1)
        grid.addWidget(self.pro_exist_label, 1, 0)
        grid.addWidget(self.pro_exist_value, 1, 1)
        grid.addWidget(self.schema_exist_label, 2, 0)
        grid.addWidget(self.schema_exist_value, 2, 1)
        grid.addWidget(self.schema_exist_driver, 2, 3)
        if self.schema_exist_driver.text() in ["oracle", ""]:
            grid.addWidget(self.user_exist_label, 3, 0)
            grid.addWidget(self.user_exist_value, 3, 1)

            grid.addWidget(self.pass_exist_label, 4, 0)
            grid.addWidget(self.pass_exist_value, 4, 1)

        else:
            grid.addWidget(self.dbname_exist_label, 3, 0)
            grid.addWidget(self.dbname_exist_value, 3, 1)

        vbox = QVBoxLayout(self.right_frame)
        vbox.addWidget(group, 5)
        vbox.addStretch(1)
        vbox.addLayout(hbox0, 1)
        vbox.addLayout(result_hbox, 1)

        # 设置该页面的默认数据
        allProjects = getProjectRecords(self.mysqlite)
        for p in allProjects:
            self.pro_exist_value.addItem(p["name"], p["id"])

        allSchemas = getDatasourceRecords(self.mysqlite)
        for index,s in enumerate(allSchemas):
            self.schema_exist_value.addItem(s["name"], s["id"])
            if index == 0:
                self.schema_exist_driver.setText(s["driver"])

        # 设置slot函数
        # 保存函数
        self.btn1.clicked.connect(self._handleSaveConn)
        # 数据源改变
        self.schema_exist_value.currentIndexChanged.connect(self._handleSchemaChanged)

    def AddProPage(self):
        """
        创建一个新的项目源
        :return:
        """
        # 清空右边区域里的所有控件
        self.clearAllChileren(self.right_frame)
        # 重置flag
        self.flag = 5
        # 绘制
        group = QGroupBox()
        group.setTitle('新项目源')
        group.setMinimumHeight(475)
        self.new_pro_save_btn = QPushButton(QIcon(":/resource/save.png"), '保存')
        self.add_pro_result = QLabel()
        self.add_pro_result.setObjectName('result')
        self.add_pro_result.setFixedWidth(100)
        self.add_pro_result_detail = QLabel()
        self.add_pro_result_detail.setObjectName("result_detail")

        btn_hbox = QHBoxLayout()
        btn_hbox.addStretch()
        btn_hbox.addWidget(self.new_pro_save_btn)
        btn_hbox.addWidget(self.add_pro_result)
        btn_hbox.addStretch()

        result_box = QHBoxLayout()
        result_box.addStretch()
        result_box.addWidget(self.add_pro_result_detail)
        result_box.addStretch()

        right_vbox = QVBoxLayout(self.right_frame)
        right_vbox.addWidget(group, 6)
        right_vbox.addStretch(10)
        right_vbox.addLayout(btn_hbox, 1)
        right_vbox.addLayout(result_box, 1)

        self.new_pro_name_label = QLabel('名称：')
        self.new_pro_name_value = QLineEdit()
        self.new_pro_name_explain = QLabel('* 项目源的名称，唯一')

        self.new_pro_scriptdir_label = QLabel('脚本：')
        self.new_pro_scriptdir_value = QLineEdit()
        self.new_pro_scriptdir_explain = QLabel('* 脚本所在路径，脚本根节点')

        grid1 = QGridLayout(group)
        grid1.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid1.addWidget(self.new_pro_name_label, 0, 0)
        grid1.addWidget(self.new_pro_name_value, 0, 1)
        grid1.addWidget(self.new_pro_name_explain, 0, 2)
        grid1.addWidget(self.new_pro_scriptdir_label, 1, 0)
        grid1.addWidget(self.new_pro_scriptdir_value, 1, 1)
        grid1.addWidget(self.new_pro_scriptdir_explain, 1, 2)

        # 设置slot函数
        self.new_pro_save_btn.clicked.connect(self._handleSavePro)

    def AddDataSourcePage(self):
        """
        创建一个新的数据源
        :return:
        """
        # 清空右边区域里的所有控件
        self.clearAllChileren(self.right_frame)
        # 重置flag
        self.flag = 6
        # 绘制
        group = QGroupBox()
        group.setTitle('新数据源')
        group.setMinimumHeight(475)
        self.new_schema_save_btn = QPushButton(QIcon(":/resource/save.png"), '保存')
        self.add_schema_result = QLabel()
        self.add_schema_result.setObjectName('result')
        self.add_schema_result.setFixedWidth(100)
        self.add_schema_result_detail = QLabel()
        self.add_schema_result_detail.setObjectName("result_detail")

        btn_hbox = QHBoxLayout()
        btn_hbox.addStretch()
        btn_hbox.addWidget(self.new_schema_save_btn)
        btn_hbox.addWidget(self.add_schema_result)
        btn_hbox.addStretch()

        result_hbox = QHBoxLayout()
        result_hbox.addStretch()
        result_hbox.addWidget(self.add_schema_result_detail)
        result_hbox.addStretch()

        result_vbox = QVBoxLayout()
        result_vbox.addLayout(btn_hbox)
        result_vbox.addLayout(result_hbox)

        right_vbox = QVBoxLayout(self.right_frame)
        right_vbox.addWidget(group, 6)
        right_vbox.addStretch(10)
        right_vbox.addLayout(result_vbox, 2)

        self.new_schema_name_label = QLabel('名称：')
        self.new_schema_name_value = QLineEdit()
        self.new_schema_name_explain = QLabel('* 数据源的名称，唯一')

        self.new_schema_driver_label = QLabel('驱动：')
        self.new_schema_driver_value = QComboBox()
        self.new_schema_driver_explain = QLabel('* 驱动类型')
        self.new_schema_driver_value.addItems(Driver_Type)

        self.new_schema_host_label = QLabel('主机：')
        self.new_schema_host_value = QLineEdit()
        self.new_schema_host_explain = QLabel('* 数据库所在服务器IP')

        self.new_schema_port_label = QLabel('端口：')
        self.new_schema_port_limit = QIntValidator()
        self.new_schema_port_value = QLineEdit()
        self.new_schema_port_value.setValidator(self.new_schema_port_limit)
        self.new_schema_port_explain = QLabel('* 数据库的监听端口')

        self.new_schema_servicename_label = QLabel('服务名：')
        self.new_schema_servicename_value = QLineEdit()
        self.new_schema_servicename_explain = QLabel('* oracle数据库服务名')

        self.new_schema_user_label = QLabel('用户名：')
        self.new_schema_user_value = QLineEdit()
        self.new_schema_user_explain = QLabel('* 数据库用户名')

        self.new_schema_pass_label = QLabel('密码：')
        self.new_schema_pass_value = QLineEdit()
        self.new_schema_pass_value.setEchoMode(QLineEdit.Password)
        self.new_schema_pass_explain = QLabel('* 数据库密码')

        grid1 = QGridLayout(group)
        grid1.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid1.setObjectName("add_datasource_grid")
        grid1.addWidget(self.new_schema_name_label, 0, 0)
        grid1.addWidget(self.new_schema_name_value, 0, 1)
        grid1.addWidget(self.new_schema_name_explain, 0, 2)
        grid1.addWidget(self.new_schema_driver_label, 1, 0)
        grid1.addWidget(self.new_schema_driver_value, 1, 1)
        grid1.addWidget(self.new_schema_driver_explain, 1, 2)
        grid1.addWidget(self.new_schema_host_label, 2, 0)
        grid1.addWidget(self.new_schema_host_value, 2, 1)
        grid1.addWidget(self.new_schema_host_explain, 2, 2)
        grid1.addWidget(self.new_schema_port_label, 3, 0)
        grid1.addWidget(self.new_schema_port_value, 3, 1)
        grid1.addWidget(self.new_schema_port_explain, 3, 2)
        if self.new_schema_driver_value.currentText() in ["oracle", ""]:
            grid1.addWidget(self.new_schema_servicename_label, 4, 0)
            grid1.addWidget(self.new_schema_servicename_value, 4, 1)
            grid1.addWidget(self.new_schema_servicename_explain, 4, 2)
        else:
            grid1.addWidget(self.new_schema_user_label, 4, 0)
            grid1.addWidget(self.new_schema_user_value, 4, 1)
            grid1.addWidget(self.new_schema_user_explain, 4, 2)

            grid1.addWidget(self.new_schema_pass_label, 5, 0)
            grid1.addWidget(self.new_schema_pass_value, 5, 1)
            grid1.addWidget(self.new_schema_pass_explain, 5, 2)

        # slot函数
        self.new_schema_driver_value.currentIndexChanged.connect(self._handleDriverChanged)

        self.new_schema_save_btn.clicked.connect(self._handleSaveSchema)

    def DefaultData(self):
        """
        设置默认数据
        :return:
        """
        # 树初始化

        # 项目源节点
        pro_records = getProjectRecords(self.mysqlite)
        for pro in pro_records:
            pid = pro["id"]
            pname = pro["name"]

            child2 = QTreeWidgetItem(self.pro_tree)
            child2.setText(0, pname)
            child2.setText(1, str(pid))

        # 项目源节点
        schema_records = getDatasourceRecords(self.mysqlite)
        for schema in schema_records:
            sid = schema["id"]
            sname = schema["name"]
            child3 = QTreeWidgetItem(self.schema_tree)
            child3.setText(0, sname)
            child3.setText(1, str(sid))

        # 连接节点
        conn_records = getConnRecords(self.mysqlite)
        for index, conn in enumerate(conn_records):
            cid = conn["id"]
            cname = conn["name"]
            # pid = conn["pid"]
            # sid = conn["did"]
            # detail = conn["detail"]

            child = QTreeWidgetItem(self.conn_tree)
            child.setText(0, cname)
            child.setText(1, str(cid))

            if index == 0:
                self.left_tree.setCurrentItem(child)
                self.connect_name_value.setText(cname)
                self.ShowConnData(cid)
        # 展开节点
        self.left_tree.expandAll()

    def ShowConnData(self, connID):
        """
        展示连接信息页面
        :param connID: 连接的ID
        :return:
        """
        record = getOneRecordForAll(self.mysqlite, int(connID))

        self.connect_name_value.setText(record["conn"]["name"])
        self.connect_pro_name_value.setCurrentText(record["project"]["name"])
        self.connect_pro_script_value.setText(record["project"]["script"])

        self.connect_datasource_name_value.setCurrentText(record["datasource"]["name"])
        self.connect_datasource_driver_value.setText(record["datasource"]["driver"])
        self.connect_datasource_host_value.setText(record["datasource"]["host"])
        self.connect_datasource_port_value.setText(str(record["datasource"]["port"]))

        grid = self.right_frame.findChild(QGridLayout, "show_connect_datasource_grid")
        grid1 = self.right_frame.findChild(QGridLayout, "show_connect_detail_grid")
        if "sid" in record["datasource"]:
            grid.addWidget(self.connect_datasource_other_servicename_label, 4, 0)
            grid.addWidget(self.connect_datasource_other_servicename_value, 4, 1)

            grid1.addWidget(self.connect_detail_user_label, 1, 0)
            grid1.addWidget(self.connect_detail_user_value, 1, 1)

            grid1.addWidget(self.connect_detail_passwd_label, 2, 0)
            grid1.addWidget(self.connect_detail_passwd_value, 2, 1)

            self.connect_datasource_other_servicename_value.setText(record["datasource"]["sid"])
            conn_detail = record["conn"]["detail"].split("&")
            self.connect_detail_user_value.setText(conn_detail[0])
            self.connect_detail_passwd_value.setText(conn_detail[1])
        else:
            grid.addWidget(self.connect_datasource_other_user_label, 4, 0)
            grid.addWidget(self.connect_datasource_other_user_value, 4, 1)
            grid.addWidget(self.connect_datasource_other_pass_label, 5, 0)
            grid.addWidget(self.connect_datasource_other_pass_value, 5, 1)

            grid1.addWidget(self.connect_detail_dbname_label, 1, 0)
            grid1.addWidget(self.connect_detail_dbname_value, 1, 1)
            self.connect_datasource_other_user_value.setText(record["datasource"]["user"])
            self.connect_datasource_other_pass_value.setText(record["datasource"]["password"])
            self.connect_detail_dbname_value.setText(record["conn"]["detail"])

        # 修改连接按钮对应操作
        self.connect_editbutton.clicked.connect(self._handleEditConn)
        # 项目源QComboBox变换时，显示信息的变化
        self.connect_pro_name_value.currentTextChanged.connect(self._handleProChanged)
        # 数据源QComboBox变换时，显示信息的变化
        self.connect_datasource_name_value.currentIndexChanged.connect(self._handleSchemaChanged)

    def ShowProData(self, proID):
        """
        展示项目源页面数据
        :param proID: 项目源ID
        :return:
        """
        program_record = getProjectRecords(self.mysqlite, int(proID))
        self.pro_pro_id_value.setText(proID)
        self.pro_pro_name_value.setText(program_record[0]["name"])
        self.pro_pro_script_value.setText(program_record[0]["script"])

    def ShowSchemaData(self, schemaID):
        """
        展示数据源页面数据
        :param schemaID: 数据源ID
        :return:
        """
        grid = self.right_frame.findChild(QGridLayout,"show_datatsource_grid")
        schema_record = getDatasourceRecords(self.mysqlite, int(schemaID))
        s = schema_record[0]
        self.schema_schema_id_value.setText(schemaID)
        self.schema_schema_name_value.setText(s["name"])
        self.schema_schema_driver_value.setCurrentText(s["driver"])
        self.schema_schema_host_value.setText(s["host"])
        self.schema_schema_port_value.setText(str(s["port"]))
        if "sid" in s:
            self.schema_schema_user_label.setParent(None)
            self.schema_schema_user_value.setParent(None)
            self.schema_schema_user_value.setText("")
            self.schema_schema_pass_label.setParent(None)
            self.schema_schema_pass_value.setParent(None)
            self.schema_schema_pass_value.setText("")

            grid.addWidget(self.schema_schema_servicename_label, 5, 0)
            grid.addWidget(self.schema_schema_servicename_value, 5, 1)
            self.schema_schema_servicename_value.setText(s["sid"])
        else:
            self.schema_schema_servicename_label.setParent(None)
            self.schema_schema_servicename_value.setParent(None)
            self.schema_schema_servicename_value.setText("")
            grid.addWidget(self.schema_schema_user_label, 5, 0)
            grid.addWidget(self.schema_schema_user_value, 5, 1)
            grid.addWidget(self.schema_schema_pass_label, 6, 0)
            grid.addWidget(self.schema_schema_pass_value, 6, 1)
            self.schema_schema_user_value.setText(s["user"])
            self.schema_schema_pass_value.setText(s["password"])

        # 修改驱动
        self.schema_schema_driver_value.currentTextChanged.connect(self._handleDriverChanged)
        # 修改数据源按钮对应操作
        self.schema_editbutton.clicked.connect(self._handelEditSchema)

    def SlotFunction(self):
        """
        控件与槽函数的连接
        :return:
        """
        # 点击树形结构节点，展示该节点具体信息
        self.left_tree.itemClicked.connect(self._handleItemSeclect)

        # 新连接按钮
        self.add_conn_btn.clicked.connect(self.AddConnPage)

        # 新项目源按钮
        self.add_pro_btn.clicked.connect(self.AddProPage)

        # 新增数据源按钮
        self.add_schema_btn.clicked.connect(self.AddDataSourcePage)

        # 删除连接按钮
        self.del_conn_btn.clicked.connect(self._handleItemDelete)

    def _handleItemSeclect(self, item, column=None):
        """
        处理树形结构节点点击与右边详细信息的联动
        :param item:   被点击的节点对象
        :param column: 被点击的节点列树
        :return:
        """
        selectParent = item.parent()
        selectID = item.text(1)
        if selectParent is None:
            return
        if selectParent.text(1) == '0':  # 表示连接点
            if self.flag != 1:
                self.clearAllChileren(self.right_frame)
                self.ShowConnectPage()
                self.flag = 1
            else:
                self.connect_editresult.setText('')
            self.ShowConnData(selectID)
        elif selectParent.text(1) == '1':  # 表示项目源
            if self.flag != 2:
                self.clearAllChileren(self.right_frame)
                self.ShowProjectPage()
                self.flag = 2
            else:
                self.pro_editresult.setText('')
            self.ShowProData(selectID)
        elif selectParent.text(1) == '2':  # 表示数据源
            if self.flag != 3:
                self.clearAllChileren(self.right_frame)
                self.ShowDataSourcePage()
                self.flag = 3
            else:
                self.schema_editresult.setText('')
            self.ShowSchemaData(selectID)
        else:
            pass

    def _handleItemDelete(self):
        """
        删除树的一个节点
        :return:
        """
        currnet_item = self.left_tree.currentItem()
        selectparent = currnet_item.parent()
        selectID = currnet_item.text(1)
        if selectparent.text(1) == '0':  # 表示删除连接的某个节点
            self.conn_tree.removeChild(currnet_item)
            sql = '''delete from connections where id=%d;''' % int(selectID)

        elif selectparent.text(1) == '1':  # 表示删除项目源的某个节点
            self.pro_tree.removeChild(currnet_item)
            sql = '''delete from projects where id=%d;''' % int(selectID)
        elif selectparent.text(1) == '2':  # 表示删除数据源的某个节点
            self.schema_tree.removeChild(currnet_item)
            sql = '''delete from datasources where id=%d;''' % int(selectID)
        else:
            sql = None

        if sql is not None:
            del_result = self.mysqlite.exec_statement(sql)
            if del_result is None:
                current_item = self.left_tree.currentItem()
                self._handleItemSeclect(current_item)

    def _handleDriverChanged(self, text):
        """
        当驱动变化时，信息显示变化
        :return:
        """
        if self.flag == 3:
            grid1 = self.right_frame.findChild(QGridLayout,"show_datatsource_grid")
            if self.schema_schema_driver_value.currentText() == "oracle":
                self.schema_schema_user_label.setParent(None)
                self.schema_schema_user_value.setParent(None)
                self.schema_schema_pass_label.setParent(None)
                self.schema_schema_pass_value.setParent(None)
                grid1.addWidget(self.schema_schema_servicename_label, 5, 0)
                grid1.addWidget(self.schema_schema_servicename_value, 5, 1)
            else:
                self.schema_schema_servicename_label.setParent(None)
                self.schema_schema_servicename_value.setParent(None)
                grid1.addWidget(self.schema_schema_user_label, 5, 0)
                grid1.addWidget(self.schema_schema_user_value, 5, 1)
                grid1.addWidget(self.schema_schema_pass_label, 6, 0)
                grid1.addWidget(self.schema_schema_pass_value, 6, 1)
        else:
            grid1 = self.right_frame.findChild(QGridLayout, "add_datasource_grid")
            if self.new_schema_driver_value.currentText() == "oracle":
                self.new_schema_user_label.setParent(None)
                self.new_schema_user_value.setParent(None)
                self.new_schema_user_explain.setParent(None)

                self.new_schema_pass_label.setParent(None)
                self.new_schema_pass_value.setParent(None)
                self.new_schema_pass_explain.setParent(None)

                grid1.addWidget(self.new_schema_servicename_label,4,0)
                grid1.addWidget(self.new_schema_servicename_value,4,1)
                grid1.addWidget(self.new_schema_servicename_explain,4,2)
            else:
                self.new_schema_servicename_label.setParent(None)
                self.new_schema_servicename_value.setParent(None)
                self.new_schema_servicename_explain.setParent(None)

                grid1.addWidget(self.new_schema_user_label, 4, 0)
                grid1.addWidget(self.new_schema_user_value, 4, 1)
                grid1.addWidget(self.new_schema_user_explain, 4, 2)

                grid1.addWidget(self.new_schema_pass_label, 5, 0)
                grid1.addWidget(self.new_schema_pass_value, 5, 1)
                grid1.addWidget(self.new_schema_pass_explain, 5, 2)


    def _handleProChanged(self, text):
        """
        连接展示页面，当项目源改变时，信息随之变动
        :return:
        """
        id = self.connect_pro_name_value.currentData()
        program_record = getProjectRecords(self.mysqlite, int(id))
        self.connect_pro_script_value.setText(program_record[0]["script"])

    def _handleSchemaChanged(self, text):
        """

        :param text:
        :return:
        """
        if self.flag == 1:
            did = self.connect_datasource_name_value.currentData()
        elif self.flag == 4:
            did = self.schema_exist_value.currentData()
        else:
            did = None
        datasources = getDatasourceRecords(self.mysqlite, int(did))
        d = datasources[0]

        if self.flag == 1:
            grid = self.right_frame.findChild(QGridLayout,"show_connect_datasource_grid")
            grid1 = self.right_frame.findChild(QGridLayout,"show_connect_detail_grid")

            self.connect_datasource_driver_value.setText(d["driver"])
            self.connect_datasource_host_value.setText(d["host"])
            self.connect_datasource_port_value.setText(str(d["port"]))
            if "sid" in d:
                # datasource
                self.connect_datasource_other_user_label.setParent(None)
                self.connect_datasource_other_user_value.setParent(None)
                self.connect_datasource_other_pass_label.setParent(None)
                self.connect_datasource_other_pass_value.setParent(None)
                grid.addWidget(self.connect_datasource_other_servicename_label, 4, 0)
                grid.addWidget(self.connect_datasource_other_servicename_value, 4, 1)
                self.connect_datasource_other_servicename_value.setText(d["sid"])
                #detail
                self.connect_detail_dbname_label.setParent(None)
                self.connect_detail_dbname_value.setParent(None)
                self.connect_detail_dbname_value.setText("")

                grid1.addWidget(self.connect_detail_user_label, 1, 0)
                grid1.addWidget(self.connect_detail_user_value, 1, 1)

                grid1.addWidget(self.connect_detail_passwd_label, 2, 0)
                grid1.addWidget(self.connect_detail_passwd_value, 2, 1)
            else:
                self.connect_datasource_other_servicename_label.setParent(None)
                self.connect_datasource_other_servicename_value.setParent(None)
                grid.addWidget(self.connect_datasource_other_user_label, 4, 0)
                grid.addWidget(self.connect_datasource_other_user_value, 4, 1)
                grid.addWidget(self.connect_datasource_other_pass_label, 5, 0)
                grid.addWidget(self.connect_datasource_other_pass_value, 5, 1)
                self.connect_datasource_other_user_value.setText(d["user"])
                self.connect_datasource_other_pass_value.setText(d["password"])

                self.connect_detail_user_label.setParent(None)
                self.connect_detail_user_value.setParent(None)
                self.connect_detail_user_value.setText("")

                self.connect_detail_passwd_label.setParent(None)
                self.connect_detail_passwd_value.setParent(None)
                self.connect_detail_passwd_value.setText("")

                grid1.addWidget(self.connect_detail_dbname_label, 1, 0)
                grid1.addWidget(self.connect_detail_dbname_value, 1, 1)
        elif self.flag == 4:
            grid = self.right_frame.findChild(QGridLayout,"add_connect_grid")
            self.schema_exist_driver.setText(d["driver"])
            if "sid" in d:
                self.dbname_exist_label.setParent(None)
                self.dbname_exist_value.setParent(None)
                grid.addWidget(self.user_exist_label, 3, 0)
                grid.addWidget(self.user_exist_value, 3, 1)

                grid.addWidget(self.pass_exist_label, 4, 0)
                grid.addWidget(self.pass_exist_value, 4, 1)
            else:
                self.user_exist_label.setParent(None)
                self.user_exist_value.setParent(None)

                self.pass_exist_label.setParent(None)
                self.pass_exist_value.setParent(None)

                grid.addWidget(self.dbname_exist_label, 3, 0)
                grid.addWidget(self.dbname_exist_value, 3, 1)


    def _handleEditConn(self):
        """
        处理修改后的数据
        :return:
        """
        # 清空结果显示
        if self.connect_editresult.text() != '':
            self.connect_editresult.setText("")
        # pro
        current_pro_id = self.connect_pro_name_value.currentData()
        # schema
        current_sche_id = self.connect_datasource_name_value.currentData()
        # conn
        current_conn_id = self.left_tree.currentItem().text(1)
        current_conn_name = self.connect_name_value.text()
        if self.connect_datasource_driver_value.text() == "oracle":
            current_conn_detail = "{0}&{1}".format(self.connect_detail_user_value.text(),self.connect_detail_passwd_value.text())
        else:
            current_conn_detail = self.connect_detail_dbname_value.text()

        new_conn = {"id":int(current_conn_id),"name":current_conn_name,"pid":int(current_pro_id),"did":int(current_sche_id),"detail":current_conn_detail}
        old_conn = getConnRecords(self.mysqlite,int(current_conn_id))
        if new_conn == old_conn[0]:
            _result = '无改动'
            _detail = ""
            self.connect_editresult.setStyleSheet("color:gray;")
        else:
            sql = '''update connections set Name='%s',ProjectId=%d,SchemaId=%d,ConnDetail='%s' where id=%d;''' % (current_conn_name, int(current_pro_id), int(current_sche_id),current_conn_detail,int(current_conn_id))
            r = self.mysqlite.exec_statement(sql)
            if r is None:
                _result = '成功'
                _detail = ""
                self.connect_editresult.setStyleSheet("color:green;")
                # self.left_tree.setText(current_conn_id,current_conn_name)
            else:
                _result = "失败"
                _detail = "{0}".format(r)
                self.connect_editresult.setStyleSheet("color:red;")

        self.connect_editresult.setText(_result)
        self.connect_editresult_detail.setText(_detail)

    def _handelEditPro(self):
        """
        处理项目源操作
        :return:
        """
        id = self.pro_pro_id_value.text()
        name = self.pro_pro_name_value.text()
        script = self.pro_pro_script_value.text()

        new_project = {"id":id,"name":name,"script":script}
        old_project = getProjectRecords(self.mysqlite, int(id))
        if new_project != old_project[0]:
            sql = '''update projects set Name='%s',Script='%s' where id=%d;''' % (name,script,int(id))
            r = self.mysqlite.exec_statement(sql)
            if r is None:
                _result = '成功'
                self.pro_editresult.setStyleSheet("color:green;")
                current_item = self.left_tree.currentItem()
                if current_item.text(0) != name:
                    current_item.setText(0, name)
            else:
                _result = "失败"
                _detail = "{0}".format(r)
                self.pro_editresult.setStyleSheet("color:red;")
                self.pro_editresult_detail.setText(_detail)
                self.pro_editresult_detail.setStyleSheet("color:red;")
        else:
            _result = '无改动'
            self.pro_editresult.setStyleSheet("color:gray;")
        self.pro_editresult.setText(_result)

    def _handelEditSchema(self):
        """
        处理修改数据源
        :return:
        """
        id = self.schema_schema_id_value.text()
        name = self.schema_schema_name_value.text()
        driver = self.schema_schema_driver_value.currentText()
        host = self.schema_schema_host_value.text()
        port = self.schema_schema_port_value.text()
        if driver == "oracle":
            other = self.schema_schema_servicename_value.text()
        else:
            other = "{0}&{1}".format(self.schema_schema_user_value.text(),self.schema_schema_pass_value.text())
        new_datasource = {"id":id,"name":name,"driver":driver,"host":host,"port":port,"other":other}
        old_datasource = getDatasourceRecords(self.mysqlite, int(id))

        if new_datasource != old_datasource[0]:
            sql = '''update datasources set Name='%s',Driver='%s',Host='%s',Port=%d,Other='%s' where id=%d;''' % (name, driver, host, int(port), other, int(id))
            r = self.mysqlite.exec_statement(sql)
            if r is None:
                _result = '成功'
                self.schema_editresult.setStyleSheet("color:green;")
                current_item = self.left_tree.currentItem()
                if current_item.text(0) != name:
                    current_item.setText(0, name)
            else:
                _result = '失败'
                self.schema_editresult.setStyleSheet("color:red;")

                _detail = "{0}".format(r)
                self.schema_editresult_detail.setText(_detail)
                self.schema_editresult_detail.setStyleSheet("color:red;")

        else:
            _result = '无改动'
            self.schema_editresult.setStyleSheet("color:gray;")
        self.schema_editresult.setText(_result)

    # def _handleRadioExist(self):
    #     """
    #     :return:
    #     """
    #     radiobutton = self.sender()
    #     if radiobutton.isChecked():
    #         self.group1.setEnabled(True)
    #     else:
    #         self.group1.setEnabled(False)
    #
    # def _handleRadionNew(self):
    #     """
    #     :return:
    #     """
    #     radiobutton = self.sender()
    #     if radiobutton.isChecked():
    #         self.pstab.setEnabled(True)
    #     else:
    #         self.pstab.setEnabled(False)

    def _handleSaveConn(self):
        """
        添加连接时保存槽函数
        :return:
        """
        conn_name = self.conn_exist_value.text()
        pro_id = self.pro_exist_value.currentData()
        schema_id = self.schema_exist_value.currentData()
        if self.schema_exist_driver.text() == "oracle":
            conn_user = self.user_exist_value.text()
            conn_pass = self.pass_exist_value.text()
            conn_detail = "{0}&{1}".format(conn_user,conn_pass)
        else:
            conn_detail = self.dbname_exist_value.text()

        if conn_name == "" or conn_detail == "":
            _result = "失败"
            _detail = "信息不完整"
            self.add_conn_result.setStyleSheet("color:red;")
            self.add_conn_result.setText(_result)
            self.add_conn_result_detail.setText(_detail)
            return
        # 插入连接记录
        cr = insertConnRecord(self.mysqlite, conn_name, pro_id, schema_id, conn_detail)
        if cr is None:
            conn_id = getConnCurrentSeq(self.mysqlite)
            child1 = QTreeWidgetItem(self.conn_tree)
            child1.setText(0, conn_name)
            child1.setText(1, str(conn_id))
            self.left_tree.setCurrentItem(child1)
            _result = "成功"
            _detail = ""
            self.add_conn_result.setStyleSheet("color:green;")
        else:
            _result = "失败"
            _detail = '{0}'.format(cr)
            self.add_conn_result.setStyleSheet("color:red;")
        self.add_conn_result.setText(_result)
        self.add_conn_result_detail.setText(_detail)

    def _handleSavePro(self):
        """
        新添加的项目源信息保存到数据库
        :return:
        """
        pro_name = self.new_pro_name_value.text()
        pro_scriptDir = self.new_pro_scriptdir_value.text()

        if pro_name == "" or pro_scriptDir == "":
            _result = "失败"
            _detail = "项目信息不完整"
            self.add_conn_result.setStyleSheet("color:red;")
            self.add_conn_result.setText(_result)
            self.add_conn_result_detail.setText(_detail)
            return

        pr = insertProRecord(self.mysqlite, pro_name, pro_scriptDir)
        if pr is None:
            pro_id = getProCurrentSeq(self.mysqlite)
            child1 = QTreeWidgetItem(self.pro_tree)
            child1.setText(0, pro_name)
            child1.setText(1, str(pro_id))
            _result = '成功'
            _detail = ""
            self.add_pro_result.setStyleSheet("color:green;")
        else:
            _result = '失败'
            _detail = "{0}".format(pr)
            self.add_pro_result.setStyleSheet("color:red;")

        self.add_pro_result.setText(_result)
        self.add_pro_result_detail.setText(_detail)

    def _handleSaveSchema(self):
        """
        新添加的数据源信息保存到数据库
        :return:
        """
        schema_name = self.new_schema_name_value.text()
        schema_driver = self.new_schema_driver_value.currentText()
        schema_host = self.new_schema_host_value.text()
        schema_port = self.new_schema_port_value.text()
        if schema_driver == "oracle":
            schema_service_name = self.new_schema_servicename_value.text()
            datasource_other = schema_service_name
        else:
            schema_user = self.new_schema_user_value.text()
            schema_pass = self.new_schema_pass_value.text()
            datasource_other = "{0}&{1}".format(schema_user,schema_pass)

        if schema_name == "" or schema_host == "" or schema_port == "" or datasource_other == "":
            _result = "失败"
            _detail = "信息不完整"
            self.add_schema_result.setStyleSheet("color:red;")
            self.add_schema_result.setText(_result)
            self.add_schema_result_detail.setText(_detail)
            return

        if not (IsIp(schema_host) or IsDomain(schema_host)):
            _result = "失败"
            _detail = "主机信息错误,不是IP或者域名"
            self.add_schema_result.setStyleSheet("color:red;")
            self.add_schema_result.setText(_result)
            self.add_schema_result_detail.setText(_detail)
            return

        sr = insertSchemaRecord(self.mysqlite, schema_name, schema_driver,schema_host, schema_port, datasource_other)
        if sr is None:
            schema_id = getDataSourceCurrentSeq(self.mysqlite)
            child1 = QTreeWidgetItem(self.schema_tree)
            child1.setText(0, schema_name)
            child1.setText(1, str(schema_id))
            self.left_tree.setCurrentItem(child1)
            _result = "成功"
            _detail = ""
            self.add_schema_result.setStyleSheet("color:green;")
        else:
            _result = "失败"
            _detail = "{0}".format(sr)
            self.add_schema_result.setStyleSheet("color:red;")
        self.add_schema_result.setText(_result)
        self.add_schema_result_detail.setText(_detail)

    def clearAllChileren(self, obj):
        """
        清空对象下所有子控件
        :param obj:
        :return:
        """
        for subobj in obj.children():
            sip.delete(subobj)

    def closeEvent(self, event):
        print("Closed")

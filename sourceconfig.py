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
from general import *


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
        self.mysqlite.opendb()
        super(SourceWindow, self).__init__(parent)
        self.setFixedSize(800, 600)
        self.SetupUI()

    def SetupUI(self):
        self.left_top_frame = QFrame()
        self.left_top_frame.setFrameShape(QFrame.NoFrame)
        self.left_bot_frame = QFrame()
        self.left_bot_frame.setFrameShape(QFrame.NoFrame)
        self.right_frame = QFrame()
        self.right_frame.setFrameShape(QFrame.NoFrame)
        self.bottome_frame = QFrame()

        left_spliter = QSplitter(Qt.Vertical)
        left_spliter.setHandleWidth(1)
        left_spliter.setOpaqueResize(False)
        left_spliter.addWidget(self.left_top_frame)
        left_spliter.addWidget(self.left_bot_frame)

        mspliter = QSplitter(Qt.Horizontal)
        mspliter.setHandleWidth(1)
        mspliter.addWidget(left_spliter)
        mspliter.addWidget(self.right_frame)
        mspliter.setStretchFactor(0, 1)
        mspliter.setStretchFactor(1, 4)

        spliter = QSplitter(Qt.Vertical)
        spliter.setHandleWidth(1)
        spliter.addWidget(mspliter)
        spliter.addWidget(self.bottome_frame)

        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(spliter)
        self.setLayout(hbox)
        # 默认各个页面
        # self.DefaultTop()
        self.DefaultMiddle()
        self.DefaultBottom()
        self.DefaultData()
        self.SlotFunction()

    def DefaultTop(self):
        """
        设置顶端label
        :return:
        """
        self.label.setText('配置项：')
        self.label.setFixedHeight(20)

    def DefaultBottom(self):
        """
        默认页面--设置底部
        :return:
        """
        self.bottome_frame.setFixedHeight(20)

    def DefaultMiddle(self):
        """
        默认页面--设置中间分割
        :return:
        """
        self.left_bot_frame.setFixedHeight(100)
        self.left_top_frame.setFixedWidth(200)
        self.left_bot_frame.setFixedWidth(200)

        # 左侧
        self.DeafultMiddleLeftTop()
        self.DefaultMiddleLeftBot()
        # 右侧
        self.DefaultMiddleRight()

    def DeafultMiddleLeftTop(self):
        """
        设置中间区域的左部分区域
        :return:
        """
        self.left_tree = QTreeWidget(self.left_top_frame)
        self.left_tree.setAutoScroll(True)
        self.left_tree.setGeometry(QRect(5, 5, 189, 470))

        self.left_tree.setColumnCount(2)
        self.left_tree.setColumnHidden(1, True)  # 不显示ID的列
        self.left_tree.setHeaderHidden(True)

        self.tree_root = QTreeWidgetItem(self.left_tree)
        self.tree_root.setText(0, '资源信息')
        self.tree_root.setText(1, 'ID')

        self.conn_tree = QTreeWidgetItem(self.tree_root)
        self.conn_tree.setText(0, '连接信息')
        self.conn_tree.setText(1, '0')

        self.pro_tree = QTreeWidgetItem(self.tree_root)
        self.pro_tree.setText(0, '项目源')
        self.pro_tree.setText(1, '1')

        self.schema_tree = QTreeWidgetItem(self.tree_root)
        self.schema_tree.setText(0, '数据源')
        self.schema_tree.setText(1, '2')

    def DefaultMiddleLeftBot(self):
        self.add_conn_btn = QPushButton(QIcon(":/resource/add.png"),'连  接')
        self.add_pro_btn = QPushButton(QIcon(":/resource/add.png"),'项目源')
        self.add_schema_btn = QPushButton(QIcon(":/resource/add.png"),'数据源')
        self.del_conn_btn = QPushButton(QIcon(":/resource/del.png"),'删  除')

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.add_schema_btn, 1)
        hbox1.addWidget(self.add_pro_btn, 1)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.add_conn_btn, 1)
        hbox3.addWidget(self.del_conn_btn, 1)

        vbox = QVBoxLayout(self.left_bot_frame)
        vbox.addLayout(hbox1, 1)
        vbox.addLayout(hbox3, 1)

    def DefaultMiddleRight(self):
        """
        设置中间区域的右部分区域,默认为连接信息页面
        :return:
        """
        self.conn_user_group = QGroupBox()
        self.conn_user_group.setTitle('用户信息')
        self.conn_program_group = QGroupBox()
        self.conn_program_group.setTitle('项目源')
        self.conn_schema_group = QGroupBox()
        self.conn_schema_group.setTitle('数据源')

        self.default_editbutton = QPushButton(QIcon(":/resource/edit.png"),'修改')
        self.default_editresult = QLabel()
        self.default_editresult.setFixedWidth(100)
        self.default_editresult.setObjectName('result')
        self.default_editresult_detail = QLabel()
        self.default_editresult_detail.setObjectName("result_detail")

        hbox4 = QHBoxLayout()
        hbox4.addStretch()
        hbox4.addWidget(self.default_editbutton)
        hbox4.addWidget(self.default_editresult)
        hbox4.addStretch()

        result_hbox = QHBoxLayout()
        result_hbox.addStretch()
        result_hbox.addWidget(self.default_editresult_detail)
        result_hbox.addStretch()

        right_vbox = QVBoxLayout(self.right_frame)
        right_vbox.addWidget(self.conn_user_group,3)
        right_vbox.addWidget(self.conn_program_group,4)
        right_vbox.addWidget(self.conn_schema_group,4)
        right_vbox.addLayout(hbox4,1)
        right_vbox.addLayout(result_hbox,1)



        self.default_pro_name_label = QLabel("项目名称:")
        self.default_pro_name_value = QComboBox()
        self.default_pro_name_value.setView(QListView())
        self.default_pro_name_value.addItem('', -1)
        for program in getProAllRecord(self.mysqlite):
            id = program[0]
            pname = program[1]
            self.default_pro_name_value.addItem(pname, id)

        self.default_pro_id_label = QLabel("项目源ID:")
        self.default_pro_id_value = QLineEdit()
        self.default_pro_id_value.setEnabled(False)
        self.default_pro_driver_label = QLabel("项目驱动:")
        self.default_pro_driver_value = QLineEdit()
        self.default_pro_driver_value.setEnabled(False)
        self.default_pro_script_label = QLabel("脚本路径:")
        self.default_pro_script_value = QLineEdit()
        self.default_pro_script_value.setEnabled(False)

        grid1 = QGridLayout(self.conn_program_group)
        grid1.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        # grid1.addWidget(self.default_pro_id_label, 0, 0)
        # grid1.addWidget(self.default_pro_id_value, 0, 1)
        grid1.addWidget(self.default_pro_name_label, 1, 0)
        grid1.addWidget(self.default_pro_name_value, 1, 1)
        grid1.addWidget(self.default_pro_driver_label, 2, 0)
        grid1.addWidget(self.default_pro_driver_value, 2, 1)
        grid1.addWidget(self.default_pro_script_label, 3, 0)
        grid1.addWidget(self.default_pro_script_value, 3, 1)

        # # 数据源
        # name
        self.default_schema_name_label = QLabel("名   称:")
        self.default_schema_name_value = QComboBox()
        self.default_schema_name_value.setView(QListView())
        self.default_schema_name_value.addItem('', -1)
        for schema in getSchemaAllRecord(self.mysqlite):
            id = schema[0]
            sname = schema[1]
            self.default_schema_name_value.addItem(sname, id)
        # id
        self.default_schema_id_label = QLabel("数据源ID:")
        self.default_schema_id_value = QLineEdit()
        self.default_schema_id_value.setEnabled(False)
        # host
        self.default_schema_host_label = QLabel("主   机:")
        self.default_schema_host_value = QLineEdit()
        self.default_schema_host_value.setEnabled(False)

        # port
        self.default_schema_port_label = QLabel("端   口:")
        self.default_schema_port_value = QLineEdit()
        self.default_schema_port_value.setEnabled(False)
        # servicename
        self.default_schema_servicename_label = QLabel("服务名:")
        self.default_schema_servicename_value = QLineEdit()
        self.default_schema_servicename_value.setEnabled(False)

        grid2 = QGridLayout(self.conn_schema_group)
        grid2.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # grid2.addWidget(self.default_schema_id_label, 0, 0)
        # grid2.addWidget(self.default_schema_id_value, 0, 1)

        grid2.addWidget(self.default_schema_name_label, 1, 0)
        grid2.addWidget(self.default_schema_name_value, 1, 1)

        grid2.addWidget(self.default_schema_host_label, 2, 0)
        grid2.addWidget(self.default_schema_host_value, 2, 1)

        grid2.addWidget(self.default_schema_port_label, 3, 0)
        grid2.addWidget(self.default_schema_port_value, 3, 1)

        grid2.addWidget(self.default_schema_servicename_label, 4, 0)
        grid2.addWidget(self.default_schema_servicename_value, 4, 1)

        # # 用户信息tab
        # conn name
        self.default_conn_name_label = QLabel("连接名:")
        self.default_conn_name_value = QLineEdit()

        # user
        self.default_schema_user_label = QLabel("用户名:")
        self.default_schema_user_value = QLineEdit()

        # password
        self.default_schema_passwd_label = QLabel("密    码:")
        self.default_schema_passwd_value = QLineEdit()
        self.default_schema_passwd_value.setEchoMode(QLineEdit.Password)

        grid3 = QGridLayout(self.conn_user_group)
        grid3.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        grid3.addWidget(self.default_conn_name_label, 0, 0)
        grid3.addWidget(self.default_conn_name_value, 0, 1)

        grid3.addWidget(self.default_schema_user_label, 1, 0)
        grid3.addWidget(self.default_schema_user_value, 1, 1)

        grid3.addWidget(self.default_schema_passwd_label, 2, 0)
        grid3.addWidget(self.default_schema_passwd_value, 2, 1)

    def DeaultMiddleRightPro(self):
        """
        设置中间区域的右边部分-项目源页面
        :return:
        """
        pro_group = QGroupBox()
        pro_group.setTitle('项目源')
        self.pro_editbutton = QPushButton(QIcon(":/resource/edit.png"),'修改')
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
        right_vbox.addWidget(pro_group,6)
        right_vbox.addStretch(10)
        right_vbox.addLayout(hbox4,1)
        right_vbox.addLayout(result_hbox,1)


        self.pro_pro_id_label = QLabel("项目源ID:")
        self.pro_pro_id_value = QLineEdit()
        self.pro_pro_id_value.setEnabled(False)

        self.pro_pro_name_label = QLabel("项目名称:")
        self.pro_pro_name_value = QLineEdit()

        self.pro_pro_driver_label = QLabel("项目驱动:")
        self.pro_pro_driver_value = QLineEdit()

        self.pro_pro_script_label = QLabel("脚本路径:")
        self.pro_pro_script_value = QLineEdit()

        grid1 = QGridLayout(pro_group)
        grid1.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid1.addWidget(self.pro_pro_id_label, 0, 0)
        grid1.addWidget(self.pro_pro_id_value, 0, 1)
        grid1.addWidget(self.pro_pro_name_label, 1, 0)
        grid1.addWidget(self.pro_pro_name_value, 1, 1)
        grid1.addWidget(self.pro_pro_driver_label, 2, 0)
        grid1.addWidget(self.pro_pro_driver_value, 2, 1)
        grid1.addWidget(self.pro_pro_script_label, 3, 0)
        grid1.addWidget(self.pro_pro_script_value, 3, 1)

        # 修改项目源按钮对应操作
        self.pro_editbutton.clicked.connect(self._handelEditPro)

    def DeaultMiddleRightSchema(self):
        """
        设置中间区域的右边部分-数据源页面
        :return:
        """
        schema_group = QGroupBox()
        schema_group.setTitle('数据源')
        self.schema_editbutton = QPushButton(QIcon(":/resource/edit.png"),'修改')
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
        right_vbox.addWidget(schema_group,6)
        right_vbox.addStretch(10)
        right_vbox.addLayout(hbox4,1)
        right_vbox.addLayout(result_hbox,1)

        # id
        self.schema_schema_id_label = QLabel("数据源ID:")
        self.schema_schema_id_value = QLineEdit()
        self.schema_schema_id_value.setEnabled(False)
        # name
        self.schema_schema_name_label = QLabel("名   称:")
        self.schema_schema_name_value = QLineEdit()

        # host
        self.schema_schema_host_label = QLabel("主   机:")
        self.schema_schema_host_value = QLineEdit()

        # port
        self.schema_schema_port_label = QLabel("端   口:")
        self.schema_schema_port_value = QLineEdit()
        # servicename
        self.schema_schema_servicename_label = QLabel("服务名:")
        self.schema_schema_servicename_value = QLineEdit()

        grid2 = QGridLayout(schema_group)
        grid2.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        grid2.addWidget(self.schema_schema_id_label, 0, 0)
        grid2.addWidget(self.schema_schema_id_value, 0, 1)

        grid2.addWidget(self.schema_schema_name_label, 1, 0)
        grid2.addWidget(self.schema_schema_name_value, 1, 1)

        grid2.addWidget(self.schema_schema_host_label, 2, 0)
        grid2.addWidget(self.schema_schema_host_value, 2, 1)

        grid2.addWidget(self.schema_schema_port_label, 3, 0)
        grid2.addWidget(self.schema_schema_port_value, 3, 1)

        grid2.addWidget(self.schema_schema_servicename_label, 4, 0)
        grid2.addWidget(self.schema_schema_servicename_value, 4, 1)

        # 修改数据源按钮对应操作
        self.schema_editbutton.clicked.connect(self._handelEditSchema)

    def DefaultData(self):
        """
        设置默认数据
        :return:
        """
        # 树初始化
        # 连接节点
        conn_records = getConnAllRecord(self.mysqlite)
        for index, conn in enumerate(conn_records):
            cid = conn[0]
            cname = conn[1]
            pid = conn[2]
            sid = conn[3]
            user = conn[4]
            passwd = conn[5]
            child = QTreeWidgetItem(self.conn_tree)
            child.setText(0, cname)
            child.setText(1, str(cid))

            if index == 0:
                self.left_tree.setCurrentItem(child)
                self.default_conn_name_value.setText(cname)
                self.default_schema_user_value.setText(user)
                self.default_schema_passwd_value.setText(passwd)
                if pid is not None:
                    pro_record = getProOneRecord(self.mysqlite, pid)
                    if len(pro_record) > 0:
                        self.default_pro_name_value.setCurrentText(pro_record[0])
                        self.default_pro_driver_value.setText(pro_record[1])
                        self.default_pro_script_value.setText(pro_record[2])
                    else:
                        pass
                if sid is not None:
                    sechma_record = getSchemaOneRecord(self.mysqlite, sid)
                    if len(sechma_record) > 0:
                        self.default_schema_name_value.setCurrentText(sechma_record[0])
                        self.default_schema_host_value.setText(sechma_record[1])
                        self.default_schema_port_value.setText(str(sechma_record[2]))
                        self.default_schema_servicename_value.setText(sechma_record[3])

        # 项目源节点
        pro_records = getProAllRecord(self.mysqlite)
        for pro in pro_records:
            pid = pro[0]
            pname = pro[1]

            child2 = QTreeWidgetItem(self.pro_tree)
            child2.setText(0, pname)
            child2.setText(1, str(pid))

        # 项目源节点
        schema_records = getSchemaAllRecord(self.mysqlite)
        for schema in schema_records:
            sid = schema[0]
            sname = schema[1]
            child3 = QTreeWidgetItem(self.schema_tree)
            child3.setText(0, sname)
            child3.setText(1, str(sid))

        # 展开节点
        self.left_tree.expandAll()

    def SlotFunction(self):
        """
        控件与槽函数的连接
        :return:
        """
        # 点击树形结构节点，展示该节点具体信息
        self.left_tree.itemClicked.connect(self._handleItemSeclect)

        # 项目源QComboBox变换时，显示信息的变化
        self.default_pro_name_value.currentTextChanged.connect(self._handleProChanged)

        # 数据源QComboBox变换时，显示信息的变化
        self.default_schema_name_value.currentTextChanged.connect(self._handleSchemaChanged)

        # 修改连接按钮对应操作
        self.default_editbutton.clicked.connect(self._handleEditConn)

        # 新连接按钮
        self.add_conn_btn.clicked.connect(self.AddConnPage)

        # 新项目源按钮
        self.add_pro_btn.clicked.connect(self.AddProPage)

        # 新增数据源按钮
        self.add_schema_btn.clicked.connect(self.AddSchemaPage)

        # 删除连接按钮
        self.del_conn_btn.clicked.connect(self._handleItemDelete)

    def _handleItemSeclect(self, item, column=None):
        """
        处理树形结构节点点击与右边详细信息的联动
        :param item:   被点击的节点对象
        :param column: 被点击的节点列树
        :return:
        """
        selectparent = item.parent()
        selectID = item.text(1)
        if selectparent is None:
            return
        if selectparent.text(1) == '0':  # 表示连接点
            if self.flag != 1:
                self.clearAllChileren(self.right_frame)
                self.DefaultMiddleRight()
                self.flag = 1
            else:
                self.default_editresult.setText('')
            self._showConnData(selectID)
        elif selectparent.text(1) == '1':  # 表示项目源
            if self.flag != 2:
                self.clearAllChileren(self.right_frame)
                self.DeaultMiddleRightPro()
                self.flag = 2
            else:
                self.pro_editresult.setText('')
            self._showProData(selectID)
        elif selectparent.text(1) == '2':  # 表示数据源
            if self.flag != 3:
                self.clearAllChileren(self.right_frame)
                self.DeaultMiddleRightSchema()
                self.flag = 3
            else:
                self.schema_editresult.setText('')
            self._showSchemaData(selectID)
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
            sql = '''delete from conninfo where id=%d;''' % int(selectID)

        elif selectparent.text(1) == '1':  # 表示删除项目源的某个节点
            self.pro_tree.removeChild(currnet_item)
            sql = '''delete from programinfo where id=%d;''' % int(selectID)
        elif selectparent.text(1) == '2':  # 表示删除数据源的某个节点
            self.schema_tree.removeChild(currnet_item)
            sql = '''delete from schemainfo where id=%d;''' % int(selectID)
        else:
            sql = None

        if sql is not None:
            del_result = self.mysqlite.exec_statement(sql)
            if del_result is None:
                current_item = self.left_tree.currentItem()
                self._handleItemSeclect(current_item)

    def _handleProChanged(self, text):
        """
        连接展示页面，当项目源改变时，信息随之变动
        :return:
        """
        id = self.default_pro_name_value.currentData()
        program_record = getProOneRecord(self.mysqlite, int(id))
        if program_record != ():
            self.default_pro_driver_value.setText(program_record[1])
            self.default_pro_script_value.setText(program_record[2])

    def _handleSchemaChanged(self, text):
        """

        :param text:
        :return:
        """
        id = self.default_schema_name_value.currentData()
        schema_record = getSchemaOneRecord(self.mysqlite, int(id))
        if schema_record != ():
            self.default_schema_host_value.setText(schema_record[1])
            self.default_schema_port_value.setText(str(schema_record[2]))
            self.default_schema_servicename_value.setText(schema_record[3])

    def _handleEditConn(self):
        """
        处理修改后的数据
        :return:
        """
        # 清空结果显示
        if self.default_editresult.text() != '':
            self.default_editresult.setText('')
        # conn
        current_conn_id = self.left_tree.currentItem().text(1)
        current_conn_name = self.default_conn_name_value.text()
        current_conn_user = self.default_schema_user_value.text()
        current_conn_passwd = self.default_schema_passwd_value.text()

        # pro
        current_pro_id = self.default_pro_name_value.currentData()

        # schema
        current_sche_id = self.default_schema_name_value.currentData()

        current_conn = getConnOneRecord(self.mysqlite, int(current_conn_id))

        if (current_conn_name, int(current_pro_id), int(current_sche_id), current_conn_user,current_conn_passwd) != current_conn:
            sql = '''update conninfo set cname='%s',schemauser='%s',schemapass='%s',program_id=%d,schema_id=%d where id=%d;''' % (
                current_conn_name,current_conn_user, current_conn_passwd, int(current_pro_id), int(current_sche_id), int(current_conn_id))
            r = self.mysqlite.exec_statement(sql)
            if r is None:
                _result = '成功'
                _detail = ""
                self.default_editresult.setStyleSheet("color:green;")
                # self.left_tree.setText(current_conn_id,current_conn_name)
            else:
                _result = "失败"
                _detail = "{0}".format(r)
                self.default_editresult.setStyleSheet("color:red;")
        else:
            _result = '无改动'
            _detail = ""
            self.default_editresult.setStyleSheet("color:gray;")

        self.default_editresult.setText(_result)
        self.default_editresult.setText(_detail)

    def _handelEditPro(self):
        """
        处理项目源操作
        :return:
        """
        id = self.pro_pro_id_value.text()
        name = self.pro_pro_name_value.text()
        driver = self.pro_pro_driver_value.text()
        scriptdir = self.pro_pro_script_value.text()

        program_record = getProOneRecord(self.mysqlite, int(id))
        if (name, driver, scriptdir) != program_record:
            sql = '''update programinfo set pname='%s',driver='%s',scriptdir='%s' where id=%d;''' % (
                name, driver, scriptdir, int(id))
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
        host = self.schema_schema_host_value.text()
        port = self.schema_schema_port_value.text()
        serviceName = self.schema_schema_servicename_value.text()

        schema_record = getSchemaOneRecord(self.mysqlite, int(id))
        if (name, host, int(port), serviceName) != schema_record:
            sql = '''update schemainfo set sname='%s',host='%s',port=%d,servicename='%s' where id=%d;''' % (
                name, host, int(port), serviceName, int(id))
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
        self.group_top = QGroupBox()
        self.group_top.setTitle('基本信息')
        self.group_top.setAutoFillBackground(True)
        # 数据源和项目源
        self.group_bot = QGroupBox()
        self.group_bot.setTitle('资源信息')
        self.group_bot.setAutoFillBackground(True)
        # 保存按钮
        self.btn1 = QPushButton(QIcon(":/resource/save.png"),"保存")
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

        vbox0 = QVBoxLayout(self.right_frame)
        vbox0.addWidget(self.group_top, 3)
        vbox0.addStretch(1)
        vbox0.addWidget(self.group_bot, 5)
        vbox0.addLayout(hbox0, 1)
        vbox0.addLayout(result_hbox, 1)
        # 上部分
        self.conn_exist_label = QLabel('连接名:')
        self.conn_exist_value = QLineEdit()
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.conn_exist_label)
        hbox1.addWidget(self.conn_exist_value)
        hbox1.addStretch()

        self.user_exist_label = QLabel('用户名:')
        self.user_exist_value = QLineEdit()

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.user_exist_label)
        hbox2.addWidget(self.user_exist_value)
        hbox2.addStretch()

        self.pass_exist_label = QLabel('密码:')
        self.pass_exist_value = QLineEdit()
        self.pass_exist_value.setEchoMode(QLineEdit.Password)
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.pass_exist_label)
        hbox3.addWidget(self.pass_exist_value)
        hbox3.addStretch()

        user_hbox = QHBoxLayout()
        user_hbox.addLayout(hbox2)
        user_hbox.addLayout(hbox3)
        user_hbox.addStretch(10)

        vbox1 = QVBoxLayout(self.group_top)
        vbox1.setAlignment(Qt.AlignTop)
        vbox1.addLayout(hbox1)
        vbox1.addLayout(user_hbox)
        vbox1.addStretch()

        # 下部分
        self.radio1 = QRadioButton("选择已有的项目源和数据源")
        self.radio2 = QRadioButton("创建新的数据源和项目源")
        self.group1 = QGroupBox()
        self.group1.setObjectName('indent')
        # self.group2 = QGroupBox()
        # self.group2.setWindowOpacity(0)
        # self.group2.setObjectName('indent')
        self.pstab = QTabWidget()

        vbox2 = QVBoxLayout(self.group_bot)
        vbox2.addWidget(self.radio1, 1)
        vbox2.addWidget(self.group1, 1)
        vbox2.addWidget(self.radio2, 1)
        vbox2.addWidget(self.pstab, 6)

        # 在已存在的项目源和数据源中选择
        self.pro_exist_label = QLabel("项目源名称:")
        self.pro_exist_label.setObjectName('indent')
        self.pro_exist_value = QComboBox()
        self.pro_exist_value.setView(QListView())

        self.schema_exist_label = QLabel("数据源名称:")
        self.schema_exist_label.setObjectName('indent')
        self.schema_exist_value = QComboBox()
        self.schema_exist_value.setView(QListView())

        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.pro_exist_label)
        hbox4.addWidget(self.pro_exist_value)
        hbox4.addStretch()

        hbox5 = QHBoxLayout()
        hbox5.addWidget(self.schema_exist_label)
        hbox5.addWidget(self.schema_exist_value)
        hbox5.addStretch()

        vbox3 = QVBoxLayout(self.group1)
        vbox3.setAlignment(Qt.AlignTop)
        vbox3.addLayout(hbox4)
        vbox3.addLayout(hbox5)

        # 创建新的项目源，数据源，用户
        # self.pstab = QTabWidget(self.group2)
        self.pstab.setGeometry(35, 0, self.group1.width(), self.group1.height() * 2)
        self.protabpage = QWidget()
        self.schtabpage = QWidget()
        self.usertabpage = QWidget()
        self.pstab.addTab(self.protabpage, '项目源')
        self.pstab.addTab(self.schtabpage, '数据源')

        ##项目源tab
        # name
        self.add_pro_name_label = QLabel("项目名称:")
        self.add_pro_name_value = QLineEdit()
        self.add_pro_name_explain = QLabel('*项目的名称')
        self.add_pro_name_explain.setObjectName('explain')
        # driver
        self.add_pro_driver_label = QLabel("项目驱动:")
        self.add_pro_driver_value = QComboBox()
        self.add_pro_driver_value.addItem('oracle')
        self.add_pro_driver_explain = QLabel('*项目所用数据库的类型,默认是oracle')
        self.add_pro_driver_explain.setObjectName('explain')
        # scripts
        self.add_pro_script_label = QLabel("脚本路径:")
        self.add_pro_script_value = QLineEdit()
        self.add_pro_script_explain = QLabel('*项目数据库脚本的路径')
        self.add_pro_script_explain.setObjectName('explain')

        grid0 = QGridLayout(self.protabpage)
        grid0.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid0.addWidget(self.add_pro_name_label, 0, 0)
        grid0.addWidget(self.add_pro_name_value, 0, 1)
        grid0.addWidget(self.add_pro_name_explain, 0, 2)

        grid0.addWidget(self.add_pro_driver_label, 1, 0)
        grid0.addWidget(self.add_pro_driver_value, 1, 1)
        grid0.addWidget(self.add_pro_driver_explain, 1, 2)

        grid0.addWidget(self.add_pro_script_label, 2, 0)
        grid0.addWidget(self.add_pro_script_value, 2, 1)
        grid0.addWidget(self.add_pro_script_explain, 2, 2)

        ##数据源tab
        # name
        self.add_schema_name_label = QLabel("名   称:")
        self.add_schema_name_value = QLineEdit()
        self.add_schema_name_explain = QLabel('*数据源名称,唯一')
        self.add_schema_name_explain.setObjectName('explain')
        # host
        self.add_schema_host_label = QLabel("主   机:")
        self.add_schema_host_value = QLineEdit()
        self.add_schema_host_explain = QLabel('*数据库所在主机')
        self.add_schema_host_explain.setObjectName('explain')
        # port

        self.add_schema_port_label = QLabel("端   口:")
        self.add_schema_port_limit = QIntValidator()
        self.add_schema_port_value = QLineEdit()
        self.add_schema_port_value.setText('1521')
        self.add_schema_port_value.setValidator(self.add_schema_port_limit)
        self.add_schema_port_explain = QLabel('*数据库端口，默认为1521')
        self.add_schema_port_explain.setObjectName('explain')
        # servicename
        self.add_schema_servicename_label = QLabel("服务名:")
        self.add_schema_servicename_value = QLineEdit()
        self.add_schema_servicename_explain = QLabel('*数据库服务名')
        self.add_schema_servicename_explain.setObjectName('explain')

        grid1 = QGridLayout(self.schtabpage)
        grid1.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid1.addWidget(self.add_schema_name_label, 0, 0)
        grid1.addWidget(self.add_schema_name_value, 0, 1)
        grid1.addWidget(self.add_schema_name_explain, 0, 2)

        grid1.addWidget(self.add_schema_host_label, 1, 0)
        grid1.addWidget(self.add_schema_host_value, 1, 1)
        grid1.addWidget(self.add_schema_host_explain, 1, 2)

        grid1.addWidget(self.add_schema_port_label, 2, 0)
        grid1.addWidget(self.add_schema_port_value, 2, 1)
        grid1.addWidget(self.add_schema_port_explain, 2, 2)

        grid1.addWidget(self.add_schema_servicename_label, 3, 0)
        grid1.addWidget(self.add_schema_servicename_value, 3, 1)
        grid1.addWidget(self.add_schema_servicename_explain, 3, 2)

        # 设置该页面的默认属性
        self.radio1.setChecked(True)  # 默认选择已有
        self.pstab.setEnabled(False)  # 新添加为disable

        # 设置该页面的默认数据
        allprograms = getProAllRecord(self.mysqlite)
        for p in allprograms:
            self.pro_exist_value.addItem(p[1], p[0])

        allschemas = getSchemaAllRecord(self.mysqlite)
        for s in allschemas:
            self.schema_exist_value.addItem(s[1], s[0])

        # 设置slot函数
        self.btn1.clicked.connect(self._handleSaveConn)  # 保存函数
        self.radio1.toggled.connect(self._handleRadioExist)
        self.radio2.toggled.connect(self._handleRadionNew)

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
        group.setTitle('新增项目源')
        self.new_pro_save_btn = QPushButton(QIcon(":/resource/save.png"),'保存')
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
        right_vbox.addWidget(group,6)
        right_vbox.addStretch(10)
        right_vbox.addLayout(btn_hbox,1)
        right_vbox.addLayout(result_box,1)

        self.new_pro_name_label = QLabel('名\t称：')
        self.new_pro_name_value = QLineEdit()
        self.new_pro_name_explain = QLabel('* 项目源的名称，唯一')

        self.new_pro_driver_label = QLabel('驱\t动：')
        self.new_pro_driver_value = QComboBox()
        self.new_pro_driver_value.addItem('oracle')
        self.new_pro_driver_explain = QLabel('* 驱动类型，默认为oracle')

        self.new_pro_scriptdir_label = QLabel('脚\t本：')
        self.new_pro_scriptdir_value = QLineEdit()
        self.new_pro_scriptdir_explain = QLabel('* 脚本所在路径，脚本根节点')

        grid1 = QGridLayout(group)
        grid1.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid1.addWidget(self.new_pro_name_label, 0, 0)
        grid1.addWidget(self.new_pro_name_value, 0, 1)
        grid1.addWidget(self.new_pro_name_explain, 0, 2)
        grid1.addWidget(self.new_pro_driver_label, 1, 0)
        grid1.addWidget(self.new_pro_driver_value, 1, 1)
        grid1.addWidget(self.new_pro_driver_explain, 1, 2)
        grid1.addWidget(self.new_pro_scriptdir_label, 2, 0)
        grid1.addWidget(self.new_pro_scriptdir_value, 2, 1)
        grid1.addWidget(self.new_pro_scriptdir_explain, 2, 2)

        # 设置slot函数
        self.new_pro_save_btn.clicked.connect(self._handleSavePro)

    def AddSchemaPage(self):
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
        group.setTitle('新增数据源')
        self.new_schema_save_btn = QPushButton(QIcon(":/resource/save.png"),'保存')
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
        right_vbox.addWidget(group,6)
        right_vbox.addStretch(10)
        right_vbox.addLayout(result_vbox,2)


        self.new_schema_name_label = QLabel('名   称：')
        self.new_schema_name_value = QLineEdit()
        self.new_schema_name_explain = QLabel('* 数据源的名称，唯一')

        self.new_schema_host_label = QLabel('主机IP：')
        self.new_schema_host_value = QLineEdit()
        self.new_schema_host_explain = QLabel('* 数据库所在服务器IP')

        self.new_schema_port_label = QLabel('端   口：')
        self.new_schema_port_limit = QIntValidator()
        self.new_schema_port_value = QLineEdit()
        self.new_schema_port_value.setText('1521')
        self.new_schema_port_value.setValidator(self.new_schema_port_limit)
        self.new_schema_port_explain = QLabel('* 数据库的监听端口')

        self.new_schema_servicename_label = QLabel('服务名：')
        self.new_schema_servicename_value = QLineEdit()
        self.new_schema_servicename_explain = QLabel('* 数据库servicename')

        grid1 = QGridLayout(group)
        grid1.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        grid1.addWidget(self.new_schema_name_label, 0, 0)
        grid1.addWidget(self.new_schema_name_value, 0, 1)
        grid1.addWidget(self.new_schema_name_explain, 0, 2)
        grid1.addWidget(self.new_schema_host_label, 1, 0)
        grid1.addWidget(self.new_schema_host_value, 1, 1)
        grid1.addWidget(self.new_schema_host_explain, 1, 2)
        grid1.addWidget(self.new_schema_port_label, 2, 0)
        grid1.addWidget(self.new_schema_port_value, 2, 1)
        grid1.addWidget(self.new_schema_port_explain, 2, 2)
        grid1.addWidget(self.new_schema_servicename_label, 3, 0)
        grid1.addWidget(self.new_schema_servicename_value, 3, 1)
        grid1.addWidget(self.new_schema_servicename_explain, 3, 2)

        # slot函数
        self.new_schema_save_btn.clicked.connect(self._handleSaveSchema)

    def _handleRadioExist(self):
        """
        :return:
        """
        radiobutton = self.sender()
        if radiobutton.isChecked():
            self.group1.setEnabled(True)
        else:
            self.group1.setEnabled(False)

    def _handleRadionNew(self):
        """
        :return:
        """
        radiobutton = self.sender()
        if radiobutton.isChecked():
            self.pstab.setEnabled(True)
        else:
            self.pstab.setEnabled(False)

    def _handleSaveConn(self):
        """
        添加连接时保存槽函数
        :return:
        """
        conn_name = self.conn_exist_value.text()
        conn_user = self.user_exist_value.text()
        conn_pass = self.pass_exist_value.text()

        if conn_name == "" or conn_user == "" or conn_pass == "":
            _result = "失败"
            _detail = "连接信息不完整"
            self.add_conn_result.setStyleSheet("color:red;")
            self.add_conn_result.setText(_result)
            self.add_conn_result_detail.setText(_detail)
            return

        if self.radio1.isChecked():
            pro_id = self.pro_exist_value.currentData()
            schema_id = self.schema_exist_value.currentData()
        else:
            pro_name = self.add_pro_name_value.text()
            pro_driver = self.add_pro_driver_value.currentText()
            pro_script = self.add_pro_script_value.text()

            schema_name = self.add_schema_name_value.text()
            schema_host = self.add_schema_host_value.text()
            schema_port = self.add_schema_port_value.text()
            schema_serviceName = self.add_schema_servicename_value.text()

            if pro_name == "" or pro_script == "":
                _result = "失败"
                _detail = "项目信息不完整"
                self.add_conn_result.setStyleSheet("color:red;")
                self.add_conn_result.setText(_result)
                self.add_conn_result_detail.setText(_detail)
                return

            if schema_name == "" or schema_host == "" or schema_port == "" or schema_serviceName == "":
                _result = "失败"
                _detail = "数据源项信息不完整"
                self.add_conn_result.setStyleSheet("color:red;")
                self.add_conn_result.setText(_result)
                self.add_conn_result_detail.setText(_detail)
                return

            if not (IsIp(schema_host) or IsDomain(schema_host)):
                _result = "失败"
                _detail = "数据源主机信息错误,不是IP或者域名"
                self.add_conn_result.setStyleSheet("color:red;")
                self.add_conn_result.setText(_result)
                self.add_conn_result_detail.setText(_detail)
                return

            if not IsDigit(schema_port):
                _result = "失败"
                _detail = "数据源端口错误, 不是数字"
                self.add_conn_result.setStyleSheet("color:red;")
                self.add_conn_result.setText(_result)
                self.add_conn_result_detail.setText(_detail)
                return



            # 插入项目源记录
            pr = insertProRecord(self.mysqlite, pro_name, pro_driver, pro_script)
            if pr is None:
                pro_id = getProCurrentSeq(self.mysqlite)
                child2 = QTreeWidgetItem(self.pro_tree)
                child2.setText(0, pro_name)
                child2.setText(1, str(pro_id))
            else:
                pro_id = None

            # 插入数据源记录
            sr = insertSchemaRecord(self.mysqlite, schema_name, schema_host, schema_port, schema_serviceName)
            if sr is None:
                schema_id = getSchemaCurrentSeq(self.mysqlite)
                child3 = QTreeWidgetItem(self.schema_tree)
                child3.setText(0, schema_name)
                child3.setText(1, str(schema_id))
            else:
                schema_id = None

            if pro_id is None or schema_id is None:
                _result = "失败"
                _detail = "项目源错误:{0}\n数据源错误:{1}".format(pr,sr)
                self.add_conn_result.setStyleSheet("color:red;")
                self.add_conn_result.setText(_result)
                self.add_conn_result_detail.setText(_detail)
                return

                # 插入连接记录
        cr = insertConnRecord(self.mysqlite, conn_name, pro_id, schema_id, conn_user, conn_pass)
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
        pro_driver = self.new_pro_driver_value.currentText()
        pro_scriptDir = self.new_pro_scriptdir_value.text()

        if pro_name == "" or pro_scriptDir == "":
            _result = "失败"
            _detail = "项目信息不完整"
            self.add_conn_result.setStyleSheet("color:red;")
            self.add_conn_result.setText(_result)
            self.add_conn_result_detail.setText(_detail)
            return


        pr = insertProRecord(self.mysqlite, pro_name, pro_driver, pro_scriptDir)
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
        schema_host = self.new_schema_host_value.text()
        schema_port = self.new_schema_port_value.text()
        schema_serviceName = self.new_schema_servicename_value.text()

        if schema_name == "" or schema_host == "" or schema_port == "" or schema_serviceName == "":
            _result = "失败"
            _detail = "数据源项信息不完整"
            self.add_conn_result.setStyleSheet("color:red;")
            self.add_conn_result.setText(_result)
            self.add_conn_result_detail.setText(_detail)
            return

        if not (IsIp(schema_host) or IsDomain(schema_host)):
            _result = "失败"
            _detail = "数据源主机信息错误,不是IP或者域名"
            self.add_conn_result.setStyleSheet("color:red;")
            self.add_conn_result.setText(_result)
            self.add_conn_result_detail.setText(_detail)
            return

        if not IsDigit(schema_port):
            _result = "失败"
            _detail = "数据源端口错误, 不是数字"
            self.add_conn_result.setStyleSheet("color:red;")
            self.add_conn_result.setText(_result)
            self.add_conn_result_detail.setText(_detail)
            return


        sr = insertSchemaRecord(self.mysqlite, schema_name, schema_host, schema_port, schema_serviceName)
        if sr is None:
            schema_id = getSchemaCurrentSeq(self.mysqlite)
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


    def _showConnData(self, connID):
        """
        展示连接信息页面
        :param connID: 连接的ID
        :return:
        """
        record = getOneRecordForAll(self.mysqlite, int(connID))

        self.default_conn_name_value.setText(record[1])
        self.default_schema_user_value.setText(record[2])
        self.default_schema_passwd_value.setText(record[3])

        self.default_pro_name_value.setCurrentText(record[5])
        self.default_pro_driver_value.setText(record[6])
        self.default_pro_script_value.setText(record[7])

        self.default_schema_name_value.setCurrentText(record[9])
        self.default_schema_host_value.setText(record[10])
        self.default_schema_port_value.setText(record[11])
        self.default_schema_servicename_value.setText(record[12])

    def _showProData(self, proID):
        """
        展示项目源页面数据
        :param proID: 项目源ID
        :return:
        """
        program_record = getProOneRecord(self.mysqlite, int(proID))
        if program_record != ():
            self.pro_pro_id_value.setText(proID)
            self.pro_pro_name_value.setText(program_record[0])
            self.pro_pro_driver_value.setText(program_record[1])
            self.pro_pro_script_value.setText(program_record[2])

    def _showSchemaData(self, schemaID):
        """
        展示数据源页面数据
        :param schemaID: 数据源ID
        :return:
        """
        schema_record = getSchemaOneRecord(self.mysqlite, int(schemaID))
        if schema_record != ():
            self.schema_schema_id_value.setText(schemaID)
            self.schema_schema_name_value.setText(schema_record[0])
            self.schema_schema_host_value.setText(schema_record[1])
            self.schema_schema_port_value.setText(str(schema_record[2]))
            self.schema_schema_servicename_value.setText(schema_record[3])

    def clearAllChileren(self, obj):
        """
        清空对象下所有子控件
        :param obj:
        :return:
        """
        for subobj in obj.children():
            sip.delete(subobj)

    def closeEvent(self, event):
        print ("Closed")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ui = SourceWindow()
    ui.show()
    sys.exit(app.exec_())

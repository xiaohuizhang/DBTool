#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2018/1/5 下午2:31
# @Author   : xhzhang
# @Site     : xhzhang@afis.com
# @File     : myOracle.py
# @Software : PyCharm

"""This script connect oracle db,excute sql and so on"""

import os, platform, copy,operator
from cx_Oracle import connect
from define import SQL_REPLACE_MAP, DBMS_SCHEDULER_MAP, CLASS_TYPE_MAP, REMOTE_INSERT_SQL, \
    REMOTE_RECORD_SERVICENAME, REMOTE_RECORD_HOST, REMOTE_RECORD_SCHEAMPASS, REMOTE_RECORD_SCHEAMUSER
from .PATTERN_MAP import *
from general import emitMessage, getLocalInfo


def set_oracleclient_env():
    """
    设置oracle客户端环境变量
    :return:
    """
    platform_tuple = platform.uname()
    platform_type = platform_tuple[0]
    platform_machine = platform_tuple[4]
    if platform_type == 'Windows':
        instantclient = os.path.join(os.getcwd(), 'client', 'x86', 'instantclient_11_2')
        os.environ['PATH'] = instantclient + ';' + os.environ['PATH']


class make_xlat:
    """
        一次替换多个字符串
    """

    def __init__(self, *args, **kwds):
        self.adict = dict(*args, **kwds)
        self.rx = self.make_rx()

    def make_rx(self):
        return re.compile('|'.join(map(re.escape, self.adict)))

    def one_xlat(self, match):
        return self.adict[match.group(0)]

    def __call__(self, text):
        return self.rx.sub(self.one_xlat, text)


class MyOracle(object):
    """
        the connection of oralce , excute some sql or file,and so on.
    """
    conn = None
    cur = None
    trans = None
    login_info = None
    schema_version = None

    def __init__(self, user, password, host, port=1521, coding='UTF8', **kwargs):
        """
        init oracle connect object
        :param user:     schema user
        :param password: schema user's password
        :param host:     db host
        :param port:     db port. default is 1521
        :param kwargs:   dic{}
        """
        self.user = user
        self.host = host
        self.trans = make_xlat(SQL_REPLACE_MAP)
        para_sid = kwargs.get('SID') if 'SID' in kwargs else None
        para_servicename = kwargs.get('SERVICE_NAME') if 'SERVICE_NAME' in kwargs else None

        if para_sid is None and para_servicename is None:
            self.login_info = '连接Oracle,需要指定SID或者SERVICE_NAME.请设置.'
        else:
            sid = para_sid or para_servicename
        try:
            self.conn = connect(user, password, "{0}:{1}/{2}".format(host, str(port), sid), encoding=coding)
            self.login_info = '连接数据库成功'
            self.schema_version = "数据库版本：%s" % str(self.conn.version)
            self.cur = self.conn.cursor()
        except Exception as e:
            if str(e).startswith('DPI-1047'):
                set_oracleclient_env()
                try:
                    self.conn = connect(user, password, "{0}:{1}/{2}".format(host, str(port), sid), encoding=coding)
                    self.login_info = '连接数据库成功'
                    self.schema_version = "数据库版本：%s" % str(self.conn.version)
                    self.cur = self.conn.cursor()
                except Exception as e:
                    self.login_info = "数据库连接失败=>%s" % e
            else:
                self.login_info = "数据库连接失败=>%s" % e

    def execute_query(self, statement, error=None, flag=None):
        """
        execute a query statement
        :param statement: '',sql
        :param flag: 是None获取所有记录，否则获取一条记录
        :return: [(),(),()],query result.
        """
        try:
            self.cur.execute(statement)
            if flag is None:
                return self.cur.fetchall()  # 获取所有记录
            else:
                return self.cur.fetchone()  # 获取一条记录
        except Exception as e:
            emitMessage(error, str(e))

    def execute_insert(self, statement, error=None):
        """
        插入数据库记录
        :param statement: sql
        :param error:
        :return:
        """
        try:
            self.cur.execute(statement)
        except Exception as e:
            emitMessage(error, str(e))

    def execute_ddl_file(self, filename, info=None, error=None):
        """
        执行ddl脚本
        :param filename: 脚本路径名称
        :param log:
        :return:
        """
        handle = None
        sqllines = ''
        try:
            handle = open(filename, 'r',encoding='UTF-8')
            filelines = handle.readlines()
            handle.close()
        except Exception as e:
            emitMessage(info, str(e))
            return

        for line in filelines:
            if not REMOVE_INFO_PATTERN.match(line):  # 去注释,去空行,去提示信息
                sqllines += self.trans(line)  # 替换字符

        if JUDGE_PROCED_FUNC_PATTERN.search(sqllines):  # 过程或者函数
            sqlcommands = SPLIT_PROCED_FUNC_PATTERN.split(sqllines)
        else:  # 其他sql
            sqlcommands = SPLIT_NORMAL_PATTERN.split(sqllines)

        for onesql in sqlcommands:
            einfo, esql, iinfo = '', '', ''
            onesql_type, onesql_name, onesql_subtype, sql = get_ddl_name(onesql)
            if onesql_type == 'E':  # EXEC调用
                _sql_sep = sql.partition(' ')
                p_f_info = _sql_sep[2].partition('(')
                p_f_name = p_f_info[0]
                p_f_argument = "({0}".format(
                    p_f_info[2].split(';')[0] if p_f_info[2].endswith(';') else p_f_info[2])
                try:
                    self.cur.callproc(p_f_name, eval(p_f_argument))
                    iinfo = '%s%s成功' % (onesql_subtype, onesql_name)
                except Exception as e:
                    iinfo = '%s%s失败=>%s' % (onesql_subtype, onesql_name, str(e))
                    eeino = str(e)
                    esql = sql

            elif onesql_type == 'B':  # Begin...end调用
                my_dbms_scheduler_map = copy.deepcopy(DBMS_SCHEDULER_MAP)
                _proceduer_list = SPLIT_BEGIN_END_PATTERN.split(sql)
                for _procedure in _proceduer_list:
                    if not JUDGE_BLANK_LINE_PATTREN.match(_procedure):
                        _p_list = _procedure.strip().partition('(')
                        p_f_name = _p_list[0]
                        _p_f_arg_list = re.split(',\n|\)$', _p_list[2])
                        if p_f_name.lower() in my_dbms_scheduler_map.keys():
                            p_f_argument = my_dbms_scheduler_map[p_f_name.lower()]
                            for _p_f_arg in _p_f_arg_list:
                                if _p_f_arg != '':
                                    tmp = _p_f_arg.partition('=>')
                                    key = tmp[0].strip()
                                    val = tmp[2].strip()
                                    if key in p_f_argument.keys() and p_f_argument[key] is None:
                                        p_f_argument[key] = eval(val)
                            try:
                                self.cur.callproc(p_f_name, keywordParameters=p_f_argument)
                                iinfo += '%s%s成功;' % (onesql_subtype, p_f_name)
                            except Exception as e:
                                iinfo += '%s%s失败=>%s;' % (onesql_subtype, p_f_name, str(e))
                                einfo += str(e)
                                esql += p_f_name
            elif onesql_type == 'C':
                try:
                    self.commit()
                    iinfo = '提交成功'
                except Exception as e:
                    iinfo = '提交失败%s' % (str(e))
                    einfo = str(e)
                    esql = 'commit'
            elif onesql_type == 'N':
                if JUDGE_CREATE_PROC_PATTERN.match(sql) or JUDGE_CREATE_FUNC_PATTERN.match(sql):
                    exec_sql = sql
                else:
                    if sql.endswith(';'):
                        exec_sql = sql.partition(';')[0]
                    else:
                        exec_sql = sql
                try:
                    self.cur.execute(exec_sql)
                    iinfo = '%s%s成功' % (onesql_subtype, onesql_name)
                except Exception as e:
                    iinfo = '%s%s失败=>%s' % (onesql_subtype, onesql_name, str(e))
                    einfo = str(e)
                    esql = sql
            else:
                pass

            emitMessage(info, iinfo)
            emitMessage(error, (einfo, esql))

    def drop_class_data(self, info=None, error=None):
        """
        delete all data according to classtype
        :return:
        """
        # 根据drop顺序排序
        order_class_type_map = sorted(CLASS_TYPE_MAP.items(), key=lambda x: x[1][3])

        for classtype in order_class_type_map:
            d_type = classtype[0]
            d_type_ch = classtype[1][0]
            query_sql = classtype[1][1]
            drop_sql = classtype[1][2]

            self.cur.execute(query_sql)
            object_list = self.cur.fetchall()
            for index, name in enumerate(object_list):
                iinfo, einfo, esql = '', '', ''
                object_name = name[0]
                if d_type != 'JOB':
                    format_drop_sql = drop_sql.format(object_name)
                    drop_sql_type, drop_sql_name, drop_sql_sub_type, drop_strip_sql = get_ddl_name(format_drop_sql)
                    try:
                        self.cur.execute(drop_strip_sql)
                        iinfo = '%s%s成功' % (drop_sql_sub_type, drop_sql_name)
                    except Exception as e:
                        iinfo = '%s%s失败=>%s' % (drop_sql_sub_type, drop_sql_name, str(e))
                        einfo = str(e)
                        esql = drop_strip_sql
                else:
                    try:
                        self.cur.callproc('sys.dbms_scheduler.drop_job', [object_name])
                        iinfo = "删除{0}个{1}:{2}成功".format(index, d_type_ch, object_name)
                    except Exception as e:
                        iinfo = "删除{0}个{1}:{2}失败=>{3}".format(index, d_type_ch, object_name, str(e))
                        einfo = str(e)
                        esql = 'sys.dbms_scheduler.drop_job ' + object_name

                emitMessage(info, iinfo)
                emitMessage(error, (einfo, esql))

    def commit(self):
        self.conn.commit()

    def close(self, info=None, error=None):
        iinfo, einfo = '', ''
        # 关闭
        try:
            self.cur.close()
            self.conn.close()
            iinfo = '数据库连接断开'
        except Exception as e:
            einfo = '关闭数据库失败' + str(e)

        emitMessage(info, iinfo)
        emitMessage(error, (einfo, ''))


def GetPatchAvailableList(patchdir, latest_tuple=None):
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
                    fn_list = list(map(int, re.split(r'\.|_', os.path.splitext(fn)[0])))  # [0,1,20180123]
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


def GetTrunkAvailableList(trunkdir):
    """
    obtain vailable trunk sql list
    :param trunkdir: trunk dir
    :return: []
    """
    trunk_list = []
    if not os.path.isdir(trunkdir):
        trunk_list = []
    else:
        for root, dirs, files in os.walk(trunkdir):
            if root == trunkdir:
                for file in files:
                    if file.startswith('.') or not file.endswith('.sql'):
                        continue
                    else:
                        trunk_list.append(file)
    return trunk_list


def GetTagAvailableList(tagdir):
    """
    obtain vailable tag sql list
    :param tagdir: tag dir
    :return: {}
    """
    tag_dic = {}
    if not os.path.isdir(tagdir):
        tag_dic = {}
    else:
        for root, dirs, files in os.walk(tagdir):
            if root != tagdir:
                tag_dic[os.path.basename(root)] = files
    print (tag_dic)


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
    remote_conn.execute_insert(sql)
    remote_conn.commit()
    remote_conn.close()
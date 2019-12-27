#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2018/5/17 下午1:51
# @Author   : xhzhang
# @Site     : 
# @File     : __init__.py.py
# @Software : PyCharm


from driver.config import *
from comm import emitMessage,NormalMessage,WarningMessage,ErrorMessage


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


class Driver:
    """
    All driven base classes
    """

    def __init__(self, trans):
        """
        批量替换字符串
        :param trans: 需要替换的字符串对应关系. eg: {"\r":'',"\n":''},将\r,\n替换为空
        """
        self.trans = make_xlat(trans)
        self.login_info = ""
        self.selectDBInfo = ""
        self.schema_version = ""
        self.conn = None
        self.cur = None
        self.host = ""
        self.user = ""

    def executeQuery(self, statement, recordCount=None, trigger=None):
        """
        执行一次查询，返回查询结果.
        :param statement: 查询sql
        :param recordCount: 查询结果返回条数, 若为None则全部返回
        :param trigger: pyqt信号.将错误信息发送给pyqt信号
        :return: [(),(),()]
        """
        try:
            self.cur.execute(statement)
            if recordCount is None:
                return self.cur.fetchall()
            else:
                return self.cur.fetchmany(recordCount)
        except Exception as e:
            emitMessage(trigger, (ErrorMessage, str(e)))
            return str(e)

    def executeDML(self, statement, trigger=None):
        """
        插入数据
        :param statement: 插入sql
        :param error:
        :return:
        """
        try:
            self.cur.execute(statement)
            self.commit()
        except Exception as e:
            emitMessage(trigger, (ErrorMessage, str(e)))
            return str(e)

    def executeDDLFile(self, filename, info=None, error=None):
        pass

    def dropClassData(self, classMap, info=None, error=None):
        pass

    def commit(self):
        self.conn.commit()

    def close(self, trigger=None):
        """
        关闭连接
        :param info:
        :param error:
        :return:
        """
        # 关闭
        try:
            if self.cur is not None:
                self.cur.close()
            if self.conn is not None:
                self.conn.close()
            emitMessage(trigger, (NormalMessage,'数据库连接关闭成功'))
        except Exception as e:
            emitMessage(trigger, (ErrorMessage,"数据库连接关闭失败: {0}".format(e)))


def parseDDL(sqlstate):
    """
    判断sql的类型，获取sql对象名称
    :param sqlstate: sql语句
    :return:
    """
    sql = None
    sql_type = None
    sql_name = None
    sql_sub_type = None
    # 判断空行或者''
    if not JUDGE_BLANK_LINE_PATTREN.match(sqlstate):
        sql = sqlstate.strip()
        # 判断exec调用存储过程，函数
        if JUDGE_EXEC_PATTERN.match(sql):
            sql_type = 'E'
            sql_sub_type = 'exec调用'
            sql_name = re.split(NAME_PATTERN, sql)[1]
        # 判断BEGIN...END方式调用过程或者方法
        elif JUDGE_BEGIN_END_PATTREN.match(sql):
            sql_type = 'B'
            sql_sub_type = 'begin执行'
            sql_name = None
        elif JUDGE_COMMIT_PATTERN.search(sql):
            sql_type = 'C'
            sql_sub_type = '提交'
            sql_name = "提交"
        else:
            sql_type = 'N'
            if JUDGE_CREATE_TABLE_PATTERN.match(sql):
                sql_sub_type = '创建表'
                sql_name = re.split(NAME_PATTERN, sql)[2]
            elif JUDGE_CREATE_SEQ_PATTERN.match(sql):
                sql_sub_type = '创建序列'
                sql_name = re.split(NAME_PATTERN, sql)[2]
            elif JUDGE_CREATE_INDEX_PATTERN.match(sql):
                sql_sub_type = '创建索引'
                sql_name = re.split(NAME_PATTERN, sql)[2]
            elif JUDGE_CREATE_VIEW_PATTERN.match(sql):
                sql_sub_type = '创建视图'
                sql_name = re.split(NAME_PATTERN, sql)[2]
            elif JUDGE_CREATE_PK_PATTERN.match(sql):
                sql_sub_type = '添加主键约束'
                pk_split_list = re.split(NAME_PATTERN, sql)
                sql_name = pk_split_list[5]
            elif JUDGE_CREATE_FK_PATTERN.match(sql):
                sql_sub_type = '添加外键约束'
                fk_split_list = re.split(NAME_PATTERN, sql)
                sql_name = fk_split_list[5]
            elif JUDGE_CREATE_UK_PATTERN.match(sql):
                sql_sub_type = '添加唯一键约束'
                uk_split_list = re.split(NAME_PATTERN, sql)
                sql_name = uk_split_list[5]
            elif JUDGE_CREATE_CK_PATTERN.match(sql):
                sql_sub_type = '添加检查约束'
                ck_split_list = re.split(NAME_PATTERN, sql)
                sql_name = ck_split_list[5]
            elif JUDGE_CREATE_PROC_PATTERN.match(sql):
                sql_sub_type = '创建存储过程'
                proc_split_list = re.split(NAME_PATTERN, sql)
                if proc_split_list[1] == 'or' and proc_split_list[2] == 'replace':
                    sql_name = proc_split_list[4]
                else:
                    sql_name = proc_split_list[2]
            elif JUDGE_CREATE_FUNC_PATTERN.match(sql):
                sql_sub_type = '创建函数'
                func_split_list = re.split(NAME_PATTERN, sql)
                if func_split_list[1] == 'or' and func_split_list[2] == 'replace':
                    sql_name = func_split_list[4]
                else:
                    sql_name = func_split_list[2]
            elif JUDGE_DROP_CONSTRAINT_PATTERN.match(sql):
                sql_sub_type = '删除约束'
                sql_name = re.split(NAME_PATTERN, sql)[4]
            elif JUDGE_DROP_TABLE_PATTERN.match(sql):
                sql_sub_type = '删除表'
                sqlAttr = re.split(NAME_PATTERN, sql)
                if re.match("IF", sqlAttr[2], re.I):  # DROP TABLE IF EXISTS `cu_customer`
                    sql_name = sqlAttr[4]
                else:
                    sql_name = sqlAttr[2]
            elif JUDGE_DROP_SEQ_PATTERN.match(sql):
                sql_sub_type = '删除序列'
                sql_name = re.split(NAME_PATTERN, sql)[2]
            elif JUDGE_DROP_INDEX_PATTERN.match(sql):
                sql_sub_type = '删除索引'
                sql_name = re.split(NAME_PATTERN, sql)[2]
            elif JUDGE_DROP_VIEW_PATTERN.match(sql):
                sql_sub_type = '删除视图'
                sql_name = re.split(NAME_PATTERN, sql)[2]
            elif JUDGE_DROP_SYNONYM_PATTERN.match(sql):
                sql_sub_type = '删除同义词'
                sql_name = re.split(NAME_PATTERN, sql)[2]
            elif JUDGE_ADD_COLUMN_PATTERN.match(sql):
                sql_list = re.split(COLUMN_PATTERN, sql)
                for i in range(sql_list.count('')):
                    sql_list.remove('')
                table_name = sql_list[2]
                column_name = sql_list[4]
                sql_sub_type = "%s 添加列" % (table_name)
                sql_name = '[%s]' % column_name
            elif JUDGE_MODIFY_COLUMN_PATTERN.match(sql):
                sql_list = re.split(COLUMN_PATTERN, sql)
                for i in range(sql_list.count('')):
                    sql_list.remove('')
                table_name = sql_list[2]
                column_name = sql_list[4]
                sql_sub_type = "%s 修改列" % (table_name)
                sql_name = '[%s]' % column_name
            elif JUDGE_INSERT_RECORD_PATTERN.match(sql):
                sql_list = re.split(NAME_PATTERN, sql)
                table_name = sql_list[2]
                sql_sub_type = '%s 插入记录' % table_name
                sql_name = ''
            elif JUDGE_ADD_COMMENT_PATTERN.match(sql):
                sql_list = re.split(r'\s+', sql)
                column_name = sql_list[3]
                sql_sub_type = '添加列注释 %s' % column_name
                sql_name = ''
            else:
                sql_sub_type = ''
                sql_name = sql
    return sql_type, sql_name, sql_sub_type, sql

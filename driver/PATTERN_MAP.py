#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time     : 2018/1/22 下午4:06
# @Author   : xhzhang
# @Site     : 
# @File     : PATTERN_MAP.py
# @Software : PyCharm
import re

# 处理
REMOVE_INFO_PATTERN = re.compile('^(\s*--|\s*$|\s*prompt\s+)', re.I)  # 去注释,去空行,去提示信息
# 判断
JUDGE_PROCED_FUNC_PATTERN = re.compile(';\s*\n\s*/\s*')  # 以/分隔开的sql。例如：创建过程，函数，begin...end调用存储或者方法
JUDGE_NORMAL_PATTERN = ''
JUDGE_BLANK_LINE_PATTREN = re.compile('^\s*$')  # 判断空行或者''
JUDGE_EXEC_PATTERN = re.compile('^exec\s*', re.I)  # 判断EXEC 方式调用过程或者方法
JUDGE_BEGIN_END_PATTREN = re.compile('^begin\s*', re.I)  # 判断BEGIN...END方式调用过程或者方法
JUDGE_COMMIT_PATTERN = re.compile('^commit\s*;$', re.I)  # commit
JUDGE_CREATE_TABLE_PATTERN = re.compile(r'^create\s+table', re.I)
JUDGE_CREATE_SEQ_PATTERN = re.compile(r'^create\s+sequence', re.I)
JUDGE_CREATE_INDEX_PATTERN = re.compile(r'^create\s+index\s+.*on', re.I)
JUDGE_CREATE_VIEW_PATTERN = re.compile(r'^create\s+view\s+.*as', re.I)
JUDGE_CREATE_PROC_PATTERN = re.compile(r'^create\s+(or\s+replace\s+)?procedure', re.I)
JUDGE_CREATE_FUNC_PATTERN = re.compile(r'^create\s+(or\s+replace\s+)?function', re.I)
JUDGE_CREATE_PK_PATTERN = re.compile(r'^alter\s+table\s+.*\s+add\s+constraint\s+.*\s+primary key', re.I)
JUDGE_CREATE_FK_PATTERN = re.compile(r'^alter\s+table\s+.*\s+add\s+constraint\s+.*\s+foreign key', re.I)
JUDGE_CREATE_UK_PATTERN = re.compile(r'^alter\s+table\s+.*\s+add\s+constraint\s+.*\s+unique', re.I)
JUDGE_CREATE_CK_PATTERN = re.compile(r'^alter\s+table\s+.*\s+add\s+constraint\s+.*\s+check', re.I)

JUDGE_DROP_TABLE_PATTERN = re.compile(r'^drop\s+table', re.I)
JUDGE_DROP_SEQ_PATTERN = re.compile(r'^drop\s+sequence', re.I)
JUDGE_DROP_INDEX_PATTERN = re.compile(r'^drop\s+index', re.I)
JUDGE_DROP_VIEW_PATTERN = re.compile(r'^drop\s+view', re.I)
JUDGE_DROP_SYNONYM_PATTERN = re.compile(r'^drop\s+synonym', re.I)
JUDGE_DROP_CONSTRAINT_PATTERN = re.compile(r'^alter\s+table\s+drop\s+constraint', re.I)

JUDGE_ADD_COLUMN_PATTERN = re.compile(r'^alter\s+table\s+.*add\s*\(.*\)', re.I)
JUDGE_MODIFY_COLUMN_PATTERN = re.compile(r'^alter\s+table\s+.*modify\s*\(.*\)', re.I)

JUDGE_INSERT_RECORD_PATTERN = re.compile(r'^insert\s+into\s+', re.I)

JUDGE_ADD_COMMENT_PATTERN = re.compile(r'^comment\s+on\s+column\s+',re.I)

# 拆分
SPLIT_PROCED_FUNC_PATTERN = re.compile('\n\s*/')  # /必须单独一行
SPLIT_NORMAL_PATTERN = re.compile('\s*;\s*\n\s*')  # ;\n结尾的通常sql
SPLIT_BEGIN_END_PATTERN = re.compile('begin\n|;\n|end$', re.I)  # 拆分begin...end方式调用过程或者方法的sql

NAME_PATTERN = re.compile('\s+|\(.*\)')
COLUMN_PATTERN = re.compile('\s+|\s*\(|\)')


def get_ddl_name(sqlstate):
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
                sql_name = re.split(NAME_PATTERN, sql)[2]
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
                sql_sub_type = "%s添加列" % (table_name)
                sql_name = '[%s]' % column_name
            elif JUDGE_MODIFY_COLUMN_PATTERN.match(sql):
                sql_list = re.split(COLUMN_PATTERN, sql)
                for i in range(sql_list.count('')):
                    sql_list.remove('')
                table_name = sql_list[2]
                column_name = sql_list[4]
                sql_sub_type = "%s修改列" % (table_name)
                sql_name = '[%s]' % column_name
            elif JUDGE_INSERT_RECORD_PATTERN.match(sql):
                sql_list = re.split(NAME_PATTERN, sql)
                table_name = sql_list[2]
                sql_sub_type = '%s插入一行' % table_name
                sql_name = ''
            elif JUDGE_ADD_COMMENT_PATTERN.match(sql):
                sql_list = re.split(r'\s+',sql)
                column_name = sql_list[3]
                sql_sub_type = '添加列注释%s' %column_name
                sql_name = ''
            else:
                sql_sub_type = ''
                sql_name = sql
    return sql_type, sql_name, sql_sub_type, sql

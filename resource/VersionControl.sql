-- 版本控制表
CREATE TABLE SCHEMA_CHANGE_LOG
(
    ID                     NUMBER NOT NULL,
	MAJORRELEASENUMBER     NUMBER NOT NULL,
	MINORRELEASENUMBER     NUMBER NOT NULL,
	POINTRELEASENUMBER     NUMBER NOT NULL,
	REVISIONRELEASENUMBER  NUMBER NOT NULL,
	DATERELEASENUMBER      NUMBER NOT NULL,
	SCRIPTNAME             VARCHAR2(200) NOT NULL,
	ISBRANCH               CHAR(1) DEFAULT 0 NOT NULL,
	ISCONTROL              CHAR(1),
	DATEALLPIED            TIMESTAMP (6) NOT NULL
);

ALTER TABLE  SCHEMA_CHANGE_LOG ADD CONSTRAINT PK_SCHEMA_CHANGE_LOG PRIMARY KEY (ID);

CREATE SEQUENCE  SEQ_VERSIONID
MINVALUE 1
MAXVALUE 999999999
INCREMENT BY 1
START WITH 1
CACHE 20
NOORDER
NOCYCLE;

--整改sql
alter table shcema_change_log add (ISBRANCH  CHAR(1) DEFAULT 0 NOT NULL);
alter table shcema_change_log add (ISCONTROL CHAR(1));

alter table shcema_change_log rename to schema_change_log;

insert into schema_change_log  (ID,MAJORRELEASENUMBER,MINORRELEASENUMBER,POINTRELEASENUMBER,REVISIONRELEASENUMBER,DATERELEASENUMBER,SCRIPTNAME,ISBRANCH,ISCONTROL,DATEALLPIED)
values
(SEQ_VERSIONID.NEXTVAL,0,0,0,0,0,'init_trunk',2,1,to_date('2018-01-01 09:00:00','yyyy-mm-dd hh24:mi:ss'));

commit;


--操作记录信息表
CREATE TABLE OPERATE_RECORD
(
  ID                NUMBER NOT NULL,
  OPER_EVENT        VARCHAR2(100) NOT NULL,
  OPER_DBHOST       VARCHAR2(15) NOT NULL,
  OPER_DBSCHEMA     VARCHAR2(60) NOT NULL,
  OPER_IP           VARCHAR2(15) NOT NULL,
  OPER_HOSTNAME     VARCHAR2(60) NOT NULL,
  OPER_LOGINNAME    VARCHAR2(60) NOT NULL,
  OPER_TIME         TIMESTAMP (6) NOT NULL
);

alter table OPERATE_RECORD ADD CONSTRAINT PK_OPERATE_RECORD PRIMARY KEY (ID);

CREATE SEQUENCE  SEQ_OPERATE_RECORD
MINVALUE 1
MAXVALUE 999999999
INCREMENT BY 1
START WITH 1
CACHE 20
NOORDER
NOCYCLE;
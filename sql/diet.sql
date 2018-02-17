--------------------------------------------------------
--  File created - Friday-February-16-2018   
--------------------------------------------------------
--------------------------------------------------------
--  DDL for Table DIET
--------------------------------------------------------

  CREATE TABLE "PS8"."DIET" 
   (	"ID" NUMBER(3,0), 
	"NAME" VARCHAR2(100 BYTE)
   ) PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 NOCOMPRESS NOLOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "CISETS" ;
REM INSERTING into PS8.DIET
SET DEFINE OFF;
--------------------------------------------------------
--  DDL for Index DIET_PK
--------------------------------------------------------

  CREATE UNIQUE INDEX "PS8"."DIET_PK" ON "PS8"."DIET" ("ID") 
  PCTFREE 10 INITRANS 2 MAXTRANS 255 NOLOGGING 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "CISETS" ;
--------------------------------------------------------
--  Constraints for Table DIET
--------------------------------------------------------

  ALTER TABLE "PS8"."DIET" ADD CONSTRAINT "DIET_PK" PRIMARY KEY ("ID")
  USING INDEX PCTFREE 10 INITRANS 2 MAXTRANS 255 NOLOGGING 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "CISETS"  ENABLE;
 
  ALTER TABLE "PS8"."DIET" MODIFY ("ID" NOT NULL ENABLE);

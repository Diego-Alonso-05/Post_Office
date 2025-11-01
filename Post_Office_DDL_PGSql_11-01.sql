/*==============================================================*/
/* DBMS name:      PostgreSQL 9.x                               */
/* Created on:     01/11/2025 02:01:03                          */
/*==============================================================*/


drop table CLIENT;

drop table DELIVERY;

drop table EMPLOYEE;

drop table EMPLOYEE_DRIVER;

drop table EMPLOYEE_STAFF;

drop table INVOICE;

drop table NOTIFICATION;

drop table PICKS_UP_AT;

drop table POST_OFFICE_STORE;

drop table ROUTE;

drop table "USER";

drop table VEHICLE;

/*==============================================================*/
/* Table: CLIENT                                                */
/*==============================================================*/
create table CLIENT (
   USE_ID_USER          INT4                 not null,
   ID_USER              SERIAL               not null,
   ID_DELIVERY          INT4                 null,
   ID_POSTOFFICE_STORE  INT4                 null,
   USERNAME             VARCHAR(20)          null,
   PSSWD_HASH           VARCHAR(50)          null,
   NAME                 VARCHAR(100)         null,
   CONTACT              VARCHAR(20)          null,
   ADDRESS              VARCHAR(255)         null,
   EMAIL                VARCHAR(100)         null,
   CREATED_AT           DATE                 null,
   UPDATED_AT           DATE                 null,
   ROLE                 VARCHAR(16)          null,
   TAX_ID               VARCHAR(50)          null,
   constraint PK_CLIENT primary key (USE_ID_USER, ID_USER)
);

/*==============================================================*/
/* Table: DELIVERY                                              */
/*==============================================================*/
create table DELIVERY (
   ID_DELIVERY          SERIAL               not null,
   ID_INVOICE           INT4                 null,
   USE_ID_USER          INT4                 null,
   ID_USER              INT4                 null,
   TRACKING_NUMBER      VARCHAR(50)          null,
   DESCRIPTION          TEXT                 null,
   SENDER_NAME          VARCHAR(100)         null,
   SENDER_ADDRESS       TEXT                 null,
   SENDER_PHONE         VARCHAR(20)          null,
   SENDER_EMAIL         VARCHAR(100)         null,
   RECIPIENT_NAME       VARCHAR(100)         null,
   RECIPIENT_ADDRESS    TEXT                 null,
   RECIPIENT_PHONE      VARCHAR(20)          null,
   RECIPIENT_EMAIL      VARCHAR(100)         null,
   ITEM_TYPE            VARCHAR(20)          null,
   WEIGHT               INT4                 null,
   DIMENSIONS           VARCHAR(50)          null,
   STATUS               VARCHAR(20)          null,
   PRIORITY             VARCHAR(20)          null,
   REGISTERED_AT        DATE                 null,
   UPDATED_AT           DATE                 null,
   IN_TRANSITION        BOOL                 null,
   constraint PK_DELIVERY primary key (ID_DELIVERY)
);

/*==============================================================*/
/* Table: EMPLOYEE                                              */
/*==============================================================*/
create table EMPLOYEE (
   USE_ID_USER          INT4                 not null,
   ID_USER              SERIAL               not null,
   ID_POSTOFFICE_STORE  INT4                 null,
   USERNAME             VARCHAR(20)          null,
   PSSWD_HASH           VARCHAR(50)          null,
   NAME                 VARCHAR(100)         null,
   CONTACT              VARCHAR(20)          null,
   ADDRESS              VARCHAR(255)         null,
   EMAIL                VARCHAR(100)         null,
   CREATED_AT           DATE                 null,
   UPDATED_AT           DATE                 null,
   ROLE                 VARCHAR(16)          null,
   "POSITION"           VARCHAR(32)          null,
   SCHEDULE             TEXT                 null,
   WAGE                 DECIMAL(10,2)        null,
   IS_ACTIVE            BOOL                 null,
   HIRE_DATE            DATE                 null,
   constraint PK_EMPLOYEE primary key (USE_ID_USER, ID_USER)
);

/*==============================================================*/
/* Table: EMPLOYEE_DRIVER                                       */
/*==============================================================*/
create table EMPLOYEE_DRIVER (
   USE_ID_USER          INT4                 not null,
   EMP_ID_USER          INT4                 not null,
   ID_USER              SERIAL               not null,
   ID_POSTOFFICE_STORE  INT4                 null,
   USERNAME             VARCHAR(20)          null,
   PSSWD_HASH           VARCHAR(50)          null,
   NAME                 VARCHAR(100)         null,
   CONTACT              VARCHAR(20)          null,
   ADDRESS              VARCHAR(255)         null,
   EMAIL                VARCHAR(100)         null,
   CREATED_AT           DATE                 null,
   UPDATED_AT           DATE                 null,
   ROLE                 VARCHAR(16)          null,
   "POSITION"           VARCHAR(32)          null,
   SCHEDULE             TEXT                 null,
   WAGE                 DECIMAL(10,2)        null,
   IS_ACTIVE            BOOL                 null,
   HIRE_DATE            DATE                 null,
   LICENSE_NUMBER       VARCHAR(50)          null,
   LICENSE_CATEGORY     VARCHAR(20)          null,
   LICENSE_EXPIRY_DATE  DATE                 null,
   DRIVING_EXPERIENCE_YEARS INT4                 null,
   DRIVER_STATUS        VARCHAR(20)          null,
   constraint PK_EMPLOYEE_DRIVER primary key (USE_ID_USER, EMP_ID_USER, ID_USER)
);

/*==============================================================*/
/* Table: EMPLOYEE_STAFF                                        */
/*==============================================================*/
create table EMPLOYEE_STAFF (
   USE_ID_USER          INT4                 not null,
   EMP_ID_USER          INT4                 not null,
   ID_USER              SERIAL               not null,
   ID_POSTOFFICE_STORE  INT4                 null,
   USERNAME             VARCHAR(20)          null,
   PSSWD_HASH           VARCHAR(50)          null,
   NAME                 VARCHAR(100)         null,
   CONTACT              VARCHAR(20)          null,
   ADDRESS              VARCHAR(255)         null,
   EMAIL                VARCHAR(100)         null,
   CREATED_AT           DATE                 null,
   UPDATED_AT           DATE                 null,
   ROLE                 VARCHAR(16)          null,
   "POSITION"           VARCHAR(32)          null,
   SCHEDULE             TEXT                 null,
   WAGE                 DECIMAL(10,2)        null,
   IS_ACTIVE            BOOL                 null,
   HIRE_DATE            DATE                 null,
   DEPARTMENT           VARCHAR(32)          null,
   constraint PK_EMPLOYEE_STAFF primary key (USE_ID_USER, EMP_ID_USER, ID_USER)
);

/*==============================================================*/
/* Table: INVOICE                                               */
/*==============================================================*/
create table INVOICE (
   ID_INVOICE           SERIAL               not null,
   ID_POSTOFFICE_STORE  INT4                 not null,
   EMP_USE_ID_USER      INT4                 not null,
   EMP_ID_USER          INT4                 not null,
   ID_USER              INT4                 not null,
   USE_ID_USER          INT4                 not null,
   CLI_ID_USER          INT4                 not null,
   INVOICE_STATUS       VARCHAR(30)          null,
   INVOICE_TYPE         VARCHAR(50)          null,
   QUANTITY             INT4                 null,
   INVOICE_DATETIME     DATE                 null,
   COST                 DECIMAL(10,2)        null,
   PAID                 BOOL                 null,
   PAYMENT_METHOD       VARCHAR(30)          null,
   NOME                 TEXT                 null,
   MORADA               TEXT                 null,
   CONTACTO             TEXT                 null,
   constraint PK_INVOICE primary key (ID_INVOICE)
);

/*==============================================================*/
/* Table: NOTIFICATION                                          */
/*==============================================================*/
create table NOTIFICATION (
   NOTIFICATION_ID      SERIAL               not null,
   ID_DELIVERY          INT4                 not null,
   NOTIFICATION_TYPE    VARCHAR(20)          null,
   RECIPIENT_CONTACT    VARCHAR(100)         null,
   SUBJECT              VARCHAR(255)         null,
   MESSAGE              TEXT                 null,
   STATUS               VARCHAR(20)          null,
   CREATED_AT           DATE                 null,
   ERROR_MESSAGE        TEXT                 null,
   constraint PK_NOTIFICATION primary key (NOTIFICATION_ID)
);

/*==============================================================*/
/* Table: PICKS_UP_AT                                           */
/*==============================================================*/
create table PICKS_UP_AT (
   USE_ID_USER          INT4                 not null,
   ID_USER              INT4                 not null,
   ID_POSTOFFICE_STORE  INT4                 not null,
   constraint PK_PICKS_UP_AT primary key (USE_ID_USER, ID_USER, ID_POSTOFFICE_STORE)
);

/*==============================================================*/
/* Table: POST_OFFICE_STORE                                     */
/*==============================================================*/
create table POST_OFFICE_STORE (
   ID_POSTOFFICE_STORE  SERIAL               not null,
   NAME                 VARCHAR(100)         null,
   CONTACT              VARCHAR(20)          null,
   ADDRESS              VARCHAR(255)         null,
   OPENING_TIME         TIME                 null,
   CLOSING_TIME         TIME                 null,
   PO_SCHEDULE          TEXT                 null,
   MAXIMUM_STORAGE      INT4                 null,
   constraint PK_POST_OFFICE_STORE primary key (ID_POSTOFFICE_STORE)
);

/*==============================================================*/
/* Table: ROUTE                                                 */
/*==============================================================*/
create table ROUTE (
   ID_ROUTE             SERIAL               not null,
   USE_ID_USER          INT4                 not null,
   EMP_ID_USER          INT4                 not null,
   ID_USER              INT4                 not null,
   ID_DELIVERY          INT4                 not null,
   ID_POSTOFFICE_STORE  INT4                 not null,
   DESCRIPTION          TEXT                 null,
   DELIVERY_STATUS      VARCHAR(20)          null,
   DELIVERY_DATE        DATE                 null,
   DELIVERY_START_TIME  DATE                 null,
   DELIVERY_END_TIME    DATE                 null,
   EXPECTED_DURATION    TIME                 null,
   KMS_TRAVELLED        DECIMAL(8,2)         null,
   DRIVER_NOTES         TEXT                 null,
   constraint PK_ROUTE primary key (ID_ROUTE)
);

/*==============================================================*/
/* Table: "USER"                                                */
/*==============================================================*/
create table "USER" (
   ID_USER              SERIAL               not null,
   ID_POSTOFFICE_STORE  INT4                 not null,
   USERNAME             VARCHAR(20)          null,
   PSSWD_HASH           VARCHAR(50)          null,
   NAME                 VARCHAR(100)         null,
   CONTACT              VARCHAR(20)          null,
   ADDRESS              VARCHAR(255)         null,
   EMAIL                VARCHAR(100)         null,
   CREATED_AT           DATE                 null,
   UPDATED_AT           DATE                 null,
   ROLE                 VARCHAR(16)          null,
   constraint PK_USER primary key (ID_USER)
);

/*==============================================================*/
/* Table: VEHICLE                                               */
/*==============================================================*/
create table VEHICLE (
   ID_VEHICLE           SERIAL               not null,
   ID_ROUTE             INT4                 not null,
   VEHICLE_TYPE         VARCHAR(50)          null,
   PLATE_NUMBER         VARCHAR(20)          null,
   CAPACITY             DECIMAL(10,2)        null,
   BRAND                VARCHAR(50)          null,
   MODEL                VARCHAR(50)          null,
   VEHICLE_STATUS       VARCHAR(20)          null,
   YEAR                 INT4                 null,
   FUEL_TYPE            VARCHAR(30)          null,
   LAST_MAINTENANCE_DATE DATE                 null,
   constraint PK_VEHICLE primary key (ID_VEHICLE)
);


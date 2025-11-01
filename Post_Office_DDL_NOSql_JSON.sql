/*==============================================================*/
/* DBMS name:      NoSQL Document Schema (JSON)                 */
/* Created on:     01/11/2025 02:00:22                          */
/*==============================================================*/


if exists(select 1 from sys.systable where table_name='CLIENT' and table_type='BASE') then
   drop table CLIENT
end if;

if exists(select 1 from sys.systable where table_name='DELIVERY' and table_type='BASE') then
   drop table DELIVERY
end if;

if exists(select 1 from sys.systable where table_name='EMPLOYEE' and table_type='BASE') then
   drop table EMPLOYEE
end if;

if exists(select 1 from sys.systable where table_name='EMPLOYEE_DRIVER' and table_type='BASE') then
   drop table EMPLOYEE_DRIVER
end if;

if exists(select 1 from sys.systable where table_name='EMPLOYEE_STAFF' and table_type='BASE') then
   drop table EMPLOYEE_STAFF
end if;

if exists(select 1 from sys.systable where table_name='INVOICE' and table_type='BASE') then
   drop table INVOICE
end if;

if exists(select 1 from sys.systable where table_name='NOTIFICATION' and table_type='BASE') then
   drop table NOTIFICATION
end if;

if exists(select 1 from sys.systable where table_name='PICKS_UP_AT' and table_type='BASE') then
   drop table PICKS_UP_AT
end if;

if exists(select 1 from sys.systable where table_name='POST_OFFICE_STORE' and table_type='BASE') then
   drop table POST_OFFICE_STORE
end if;

if exists(select 1 from sys.systable where table_name='ROUTE' and table_type='BASE') then
   drop table ROUTE
end if;

if exists(select 1 from sys.systable where table_name='"USER"' and table_type='BASE') then
   drop table "USER"
end if;

if exists(select 1 from sys.systable where table_name='VEHICLE' and table_type='BASE') then
   drop table VEHICLE
end if;

/*==============================================================*/
/* Table: CLIENT                                                */
/*==============================================================*/
create table CLIENT (
USE_ID_USER boolean not null,
ID_USER NO not null,
ID_DELIVERY boolean,
ID_POSTOFFICE_STORE boolean,
USERNAME VA20,
PSSWD_HASH VA50,
NAME VA100,
CONTACT VA20,
ADDRESS VA255,
EMAIL VA100,
CREATED_AT DT,
UPDATED_AT DT,
ROLE VA16,
TAX_ID VA50
);

/*==============================================================*/
/* Table: DELIVERY                                              */
/*==============================================================*/
create table DELIVERY (
ID_DELIVERY NO not null,
ID_INVOICE boolean,
USE_ID_USER boolean,
ID_USER boolean,
TRACKING_NUMBER VA50,
DESCRIPTION TXT,
SENDER_NAME VA100,
SENDER_ADDRESS TXT,
SENDER_PHONE VA20,
SENDER_EMAIL VA100,
RECIPIENT_NAME VA100,
RECIPIENT_ADDRESS TXT,
RECIPIENT_PHONE VA20,
RECIPIENT_EMAIL VA100,
ITEM_TYPE VA20,
WEIGHT boolean,
DIMENSIONS VA50,
STATUS VA20,
PRIORITY VA20,
REGISTERED_AT TS,
UPDATED_AT DT,
IN_TRANSITION BL
);

/*==============================================================*/
/* Table: EMPLOYEE                                              */
/*==============================================================*/
create table EMPLOYEE (
USE_ID_USER boolean not null,
ID_USER NO not null,
ID_POSTOFFICE_STORE boolean,
USERNAME VA20,
PSSWD_HASH VA50,
NAME VA100,
CONTACT VA20,
ADDRESS VA255,
EMAIL VA100,
CREATED_AT DT,
UPDATED_AT DT,
ROLE VA16,
POSITION VA32,
SCHEDULE TXT,
WAGE DC10,2,
IS_ACTIVE BL,
HIRE_DATE DT
);

/*==============================================================*/
/* Table: EMPLOYEE_DRIVER                                       */
/*==============================================================*/
create table EMPLOYEE_DRIVER (
USE_ID_USER boolean not null,
EMP_ID_USER boolean not null,
ID_USER NO not null,
ID_POSTOFFICE_STORE boolean,
USERNAME VA20,
PSSWD_HASH VA50,
NAME VA100,
CONTACT VA20,
ADDRESS VA255,
EMAIL VA100,
CREATED_AT DT,
UPDATED_AT DT,
ROLE VA16,
POSITION VA32,
SCHEDULE TXT,
WAGE DC10,2,
IS_ACTIVE BL,
HIRE_DATE DT,
LICENSE_NUMBER VA50,
LICENSE_CATEGORY VA20,
LICENSE_EXPIRY_DATE D,
DRIVING_EXPERIENCE_YEARS boolean,
DRIVER_STATUS VA20
);

/*==============================================================*/
/* Table: EMPLOYEE_STAFF                                        */
/*==============================================================*/
create table EMPLOYEE_STAFF (
USE_ID_USER boolean not null,
EMP_ID_USER boolean not null,
ID_USER NO not null,
ID_POSTOFFICE_STORE boolean,
USERNAME VA20,
PSSWD_HASH VA50,
NAME VA100,
CONTACT VA20,
ADDRESS VA255,
EMAIL VA100,
CREATED_AT DT,
UPDATED_AT DT,
ROLE VA16,
POSITION VA32,
SCHEDULE TXT,
WAGE DC10,2,
IS_ACTIVE BL,
HIRE_DATE DT,
DEPARTMENT VA32
);

/*==============================================================*/
/* Table: INVOICE                                               */
/*==============================================================*/
create table INVOICE (
ID_INVOICE NO not null,
ID_POSTOFFICE_STORE boolean not null,
EMP_USE_ID_USER boolean not null,
EMP_ID_USER boolean not null,
ID_USER boolean not null,
USE_ID_USER boolean not null,
CLI_ID_USER boolean not null,
INVOICE_STATUS VA30,
INVOICE_TYPE VA50,
QUANTITY boolean,
INVOICE_DATETIME TS,
COST DC10,2,
PAID BL,
PAYMENT_METHOD VA30,
NOME TXT,
MORADA TXT,
CONTACTO TXT
);

/*==============================================================*/
/* Table: NOTIFICATION                                          */
/*==============================================================*/
create table NOTIFICATION (
NOTIFICATION_ID NO not null,
ID_DELIVERY boolean not null,
NOTIFICATION_TYPE VA20,
RECIPIENT_CONTACT VA100,
SUBJECT VA255,
MESSAGE TXT,
STATUS VA20,
CREATED_AT TS,
ERROR_MESSAGE TXT
);

/*==============================================================*/
/* Table: PICKS_UP_AT                                           */
/*==============================================================*/
create table PICKS_UP_AT (
USE_ID_USER boolean not null,
ID_USER boolean not null,
ID_POSTOFFICE_STORE boolean not null
);

/*==============================================================*/
/* Table: POST_OFFICE_STORE                                     */
/*==============================================================*/
create table POST_OFFICE_STORE (
ID_POSTOFFICE_STORE NO not null,
NAME VA100,
CONTACT VA20,
ADDRESS VA255,
OPENING_TIME T,
CLOSING_TIME T,
PO_SCHEDULE TXT,
MAXIMUM_STORAGE boolean
);

/*==============================================================*/
/* Table: ROUTE                                                 */
/*==============================================================*/
create table ROUTE (
ID_ROUTE NO not null,
USE_ID_USER boolean not null,
EMP_ID_USER boolean not null,
ID_USER boolean not null,
ID_DELIVERY boolean not null,
ID_POSTOFFICE_STORE boolean not null,
DESCRIPTION TXT,
DELIVERY_STATUS VA20,
DELIVERY_DATE D,
DELIVERY_START_TIME DT,
DELIVERY_END_TIME DT,
EXPECTED_DURATION T,
KMS_TRAVELLED DC8,2,
DRIVER_NOTES TXT
);

/*==============================================================*/
/* Table: "USER"                                                */
/*==============================================================*/
create table "USER" (
ID_USER NO not null,
ID_POSTOFFICE_STORE boolean not null,
USERNAME VA20,
PSSWD_HASH VA50,
NAME VA100,
CONTACT VA20,
ADDRESS VA255,
EMAIL VA100,
CREATED_AT DT,
UPDATED_AT DT,
ROLE VA16
);

/*==============================================================*/
/* Table: VEHICLE                                               */
/*==============================================================*/
create table VEHICLE (
ID_VEHICLE NO not null,
ID_ROUTE boolean not null,
VEHICLE_TYPE VA50,
PLATE_NUMBER VA20,
CAPACITY DC10,2,
BRAND VA50,
MODEL VA50,
VEHICLE_STATUS VA20,
YEAR boolean,
FUEL_TYPE VA30,
LAST_MAINTENANCE_DATE D
);


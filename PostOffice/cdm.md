# Conceptual Data Model (CDM) — PostOffice

Entities contain only their **intrinsic attributes** (PK + natural attributes).
**No foreign keys**, no derived FK columns — those are generated when the PDM resolves relationships.

---

## Inheritance Structure

```
                        USER
                         |
           +-------------+-------------+
           |   MUTUALLY EXCLUSIVE (d)   |
           v                            v
        CLIENT                      EMPLOYEE
                                       |
                         +-------------+-------------+
                         |   MUTUALLY EXCLUSIVE (d)   |
                         v                            v
                  EMPLOYEE_DRIVER              EMPLOYEE_STAFF

- A User can be Client OR Employee, never both
- An Employee can be Driver OR Staff, never both
- Admins/Managers exist only in User (no child record)
```

---

## Entities

### USER
Base identity for all system users (clients, employees, admins, managers).

| Attribute    | Type         | Constraints                     |
|--------------|--------------|---------------------------------|
| id           | SERIAL       | PK                              |
| password     | VARCHAR(128) | NOT NULL                        |
| is_superuser | BOOLEAN      | NOT NULL, DEFAULT FALSE         |
| username     | VARCHAR(150) | NOT NULL, UNIQUE                |
| first_name   | VARCHAR(150) | NOT NULL, DEFAULT ''            |
| last_name    | VARCHAR(150) | NOT NULL, DEFAULT ''            |
| email        | VARCHAR(254) | NOT NULL, DEFAULT ''            |
| is_staff     | BOOLEAN      | NOT NULL, DEFAULT FALSE         |
| contact      | VARCHAR(50)  | DEFAULT ''                      |
| address      | VARCHAR(255) | DEFAULT ''                      |
| role         | VARCHAR(20)  | NOT NULL, DEFAULT 'client'      |
| created_at   | TIMESTAMPTZ  | NOT NULL, DEFAULT NOW()         |
| updated_at   | TIMESTAMPTZ  | NOT NULL, DEFAULT NOW()         |

CHECK: `role IN ('admin', 'client', 'driver', 'staff', 'manager')`

---

### CLIENT
Extension of User for customers who request delivery services.

| Attribute | Type        | Constraints |
|-----------|-------------|-------------|
| id        | SERIAL      | PK          |
| tax_id    | VARCHAR(50) | DEFAULT ''  |

---

### EMPLOYEE
Extension of User for post office workers (common to drivers and staff).

| Attribute | Type         | Constraints                |
|-----------|--------------|----------------------------|
| id        | SERIAL       | PK                         |
| position  | VARCHAR(20)  | NOT NULL                   |
| schedule  | VARCHAR(50)  | DEFAULT ''                 |
| wage      | DECIMAL(8,2) | NOT NULL, DEFAULT 0.00     |
| is_active | BOOLEAN      | NOT NULL, DEFAULT TRUE     |
| hire_date | DATE         | NULL                       |

CHECK: `position IN ('Driver', 'Staff')`, `wage >= 0`

---

### EMPLOYEE_DRIVER
Sub-entity of Employee for drivers. Exclusive with Employee_Staff.

| Attribute                | Type        | Constraints                   |
|--------------------------|-------------|-------------------------------|
| id                       | SERIAL      | PK                            |
| license_number           | VARCHAR(50) | NOT NULL                      |
| license_category         | VARCHAR(10) | NOT NULL                      |
| license_expiry_date      | DATE        | NOT NULL                      |
| driving_experience_years | INTEGER     | NOT NULL, DEFAULT 0           |
| driver_status            | VARCHAR(50) | NOT NULL, DEFAULT 'Available' |

CHECK: `driving_experience_years >= 0`, `driver_status IN ('Available', 'OnDuty', 'OffDuty', 'OnLeave')`

---

### EMPLOYEE_STAFF
Sub-entity of Employee for office/warehouse staff. Exclusive with Employee_Driver.

| Attribute  | Type        | Constraints |
|------------|-------------|-------------|
| id         | SERIAL      | PK          |
| department | VARCHAR(32) | NOT NULL    |

---

### WAREHOUSE
Physical post office locations/warehouses.

| Attribute                | Type         | Constraints                |
|--------------------------|--------------|----------------------------|
| id                       | SERIAL       | PK                         |
| name                     | VARCHAR(100) | NOT NULL                   |
| address                  | VARCHAR(200) | NOT NULL                   |
| contact                  | VARCHAR(50)  | NOT NULL                   |
| schedule_open            | TIME         | NOT NULL                   |
| schedule_close           | TIME         | NOT NULL                   |
| schedule                 | TEXT         | NOT NULL                   |
| maximum_storage_capacity | INTEGER      | NOT NULL                   |
| is_active                | BOOLEAN      | NOT NULL, DEFAULT TRUE     |
| created_at               | TIMESTAMPTZ  | NOT NULL, DEFAULT NOW()    |
| updated_at               | TIMESTAMPTZ  | NOT NULL, DEFAULT NOW()    |

CHECK: `maximum_storage_capacity > 0`, `schedule_close > schedule_open`

---

### VEHICLE
Fleet vehicles used for deliveries.

| Attribute             | Type          | Constraints                     |
|-----------------------|---------------|---------------------------------|
| id                    | SERIAL        | PK                              |
| vehicle_type          | VARCHAR(100)  | NOT NULL                        |
| plate_number          | VARCHAR(20)   | NOT NULL, UNIQUE                |
| capacity              | DECIMAL(10,2) | NOT NULL                        |
| brand                 | VARCHAR(100)  | NOT NULL                        |
| model                 | VARCHAR(100)  | NOT NULL                        |
| vehicle_status        | VARCHAR(50)   | NOT NULL, DEFAULT 'Available'   |
| year                  | INTEGER       | NOT NULL                        |
| fuel_type             | VARCHAR(50)   | NOT NULL                        |
| last_maintenance_date | DATE          | NOT NULL                        |
| is_active             | BOOLEAN       | NOT NULL, DEFAULT TRUE          |
| created_at            | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()         |
| updated_at            | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()         |

CHECK: `capacity > 0`, `year BETWEEN 1900 AND 2100`, `vehicle_status IN ('Available', 'InUse', 'Maintenance', 'Retired')`

---

### INVOICE
Record of services a client wants to send. Snapshot fields (name, address, contact) preserve client info at creation time for record integrity.

| Attribute        | Type          | Constraints                  |
|------------------|---------------|------------------------------|
| id               | SERIAL        | PK                           |
| invoice_status   | VARCHAR(30)   | NOT NULL, DEFAULT 'Pending'  |
| invoice_type     | VARCHAR(50)   | DEFAULT ''                   |
| quantity         | INTEGER       | NULL                         |
| invoice_datetime | TIMESTAMPTZ   | NULL                         |
| cost             | DECIMAL(10,2) | NULL                         |
| paid             | BOOLEAN       | NOT NULL, DEFAULT FALSE      |
| payment_method   | VARCHAR(50)   | DEFAULT ''                   |
| name             | VARCHAR(100)  | DEFAULT ''                   |
| address          | VARCHAR(200)  | DEFAULT ''                   |
| contact          | VARCHAR(50)   | DEFAULT ''                   |
| created_at       | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()      |
| updated_at       | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()      |

CHECK: `invoice_status IN ('Pending', 'Confirmed', 'Paid', 'Cancelled', 'Refunded')`, `cost IS NULL OR cost >= 0`

Note: `cost` is auto-calculated by trigger as the sum of all related invoice_item totals (`quantity * unit_price`).

---

### INVOICE_ITEM
Individual line items within an Invoice.

| Attribute      | Type          | Constraints                |
|----------------|---------------|----------------------------|
| id_item        | SERIAL        | PK                         |
| shipment_type  | VARCHAR(50)   | NOT NULL                   |
| weight         | DECIMAL(10,2) | NOT NULL                   |
| delivery_speed | VARCHAR(50)   | NOT NULL                   |
| quantity       | INTEGER       | NOT NULL, DEFAULT 1        |
| unit_price     | DECIMAL(10,2) | NOT NULL                   |
| notes          | TEXT          | DEFAULT ''                 |
| created_at     | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()    |
| updated_at     | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()    |

CHECK: `quantity > 0`, `unit_price >= 0`, `weight > 0`, `delivery_speed IN ('Standard', 'Express', 'Overnight', 'Economy')`

---

### ROUTE
A driver's journey from a warehouse carrying deliveries.

| Attribute           | Type          | Constraints                     |
|---------------------|---------------|---------------------------------|
| id                  | SERIAL        | PK                              |
| description         | TEXT          | NOT NULL                        |
| delivery_status     | VARCHAR(50)   | NOT NULL, DEFAULT 'Scheduled'   |
| delivery_date       | DATE          | NULL                            |
| delivery_start_time | TIME          | NULL                            |
| delivery_end_time   | TIME          | NULL                            |
| expected_duration   | INTERVAL      | NULL                            |
| kms_travelled       | DECIMAL(10,2) | NOT NULL, DEFAULT 0             |
| driver_notes        | TEXT          | DEFAULT ''                      |
| is_active           | BOOLEAN       | NOT NULL, DEFAULT TRUE          |
| created_at          | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()         |
| updated_at          | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()         |

CHECK: `delivery_status IN ('Scheduled', 'InProgress', 'Completed', 'Cancelled')`, `kms_travelled >= 0`, `delivery_end_time IS NULL OR delivery_start_time IS NULL OR delivery_end_time > delivery_start_time`

---

### DELIVERY
Individual package to be delivered. Sender/recipient info is stored as flattened snapshot fields because they may not be registered users.

| Attribute         | Type          | Constraints                       |
|-------------------|---------------|-----------------------------------|
| id                | SERIAL        | PK                                |
| tracking_number   | VARCHAR(50)   | NOT NULL, UNIQUE                  |
| description       | TEXT          | DEFAULT ''                        |
| sender_name       | VARCHAR(100)  | NOT NULL                          |
| sender_address    | VARCHAR(255)  | NOT NULL                          |
| sender_phone      | VARCHAR(50)   | DEFAULT ''                        |
| sender_email      | VARCHAR(254)  | DEFAULT ''                        |
| recipient_name    | VARCHAR(100)  | NOT NULL                          |
| recipient_address | VARCHAR(255)  | NOT NULL                          |
| recipient_phone   | VARCHAR(50)   | DEFAULT ''                        |
| recipient_email   | VARCHAR(254)  | DEFAULT ''                        |
| item_type         | VARCHAR(50)   | NOT NULL                          |
| weight            | DECIMAL(10,2) | NOT NULL                          |
| dimensions        | VARCHAR(100)  | DEFAULT ''                        |
| status            | VARCHAR(20)   | NOT NULL, DEFAULT 'Registered'    |
| priority          | VARCHAR(10)   | NOT NULL, DEFAULT 'normal'        |
| in_transition     | BOOLEAN       | NOT NULL, DEFAULT FALSE           |
| delivery_date     | DATE          | NULL                              |
| created_at        | TIMESTAMPTZ   | NOT NULL, DEFAULT NOW()           |
| updated_at        | TIMESTAMPTZ   | NULL                              |

CHECK: `status IN ('Registered', 'Ready', 'Pending', 'In Transit', 'Completed', 'Cancelled')`, `priority IN ('normal', 'urgent')`, `weight > 0`

---

### DELIVERY_TRACKING
Append-only event log recording every status change of a delivery.

| Attribute  | Type        | Constraints             |
|------------|-------------|-------------------------|
| id         | SERIAL      | PK                      |
| status     | VARCHAR(20) | NOT NULL                |
| notes      | TEXT        | DEFAULT ''              |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

CHECK: `status IN ('Registered', 'Ready', 'Pending', 'In Transit', 'Completed', 'Cancelled')`

---

### NOTIFICATION (MongoDB)
Notification records stored in MongoDB.

| Attribute         | Type     | Constraints |
|-------------------|----------|-------------|
| _id               | ObjectId | PK (auto)   |
| notification_type | String   | NOT NULL    |
| recipient_contact | String   | NOT NULL    |
| subject           | String   | NULL        |
| message           | String   | NOT NULL    |
| status            | String   | NOT NULL    |
| error_message     | String   | NULL        |
| created_at        | Date     | DEFAULT NOW |

---

## Relationships

| #  | Relationship                         | Cardinality    | Participation                  | Description                                             |
|----|--------------------------------------|----------------|--------------------------------|---------------------------------------------------------|
| R1 | User — Client                        | 1:1            | User(optional), Client(mandatory) | A User may be a Client; every Client is a User       |
| R2 | User — Employee                      | 1:1            | User(optional), Employee(mandatory) | A User may be an Employee; every Employee is a User |
| R3 | Employee — Employee_Driver           | 1:1            | Employee(optional), Driver(mandatory) | An Employee may be a Driver                        |
| R4 | Employee — Employee_Staff            | 1:1            | Employee(optional), Staff(mandatory)  | An Employee may be Staff                           |
| R5 | Warehouse — Employee                 | 1:N            | Warehouse(optional), Employee(optional) | A Warehouse has many Employees; an Employee works at one Warehouse |
| R6 | Client — Invoice                     | 1:N            | Client(optional), Invoice(optional)   | A Client can have many Invoices                    |
| R7 | Employee — Invoice (processed_by)    | 1:N            | Employee(optional), Invoice(optional) | A Staff Employee processes many Invoices           |
| R8 | Warehouse — Invoice                  | 1:N            | Warehouse(optional), Invoice(optional) | Invoices are created at a Warehouse               |
| R9 | Invoice — Invoice_Item               | 1:N            | Invoice(mandatory), Item(mandatory)   | An Invoice has many line items                     |
| R10| Employee — Route (driver)            | 1:N            | Employee(optional), Route(optional)   | A Driver is assigned to many Routes                |
| R11| Vehicle — Route                      | 1:N            | Vehicle(optional), Route(optional)    | A Vehicle is assigned to many Routes               |
| R12| Warehouse — Route (origin)           | 1:N            | Warehouse(optional), Route(optional)  | Routes depart from a Warehouse                     |
| R13| Invoice — Delivery                   | 1:N            | Invoice(optional), Delivery(optional) | An Invoice generates one or more Deliveries        |
| R14| Employee — Delivery (driver)         | 1:N            | Employee(optional), Delivery(optional)| A Driver is assigned to many Deliveries            |
| R15| Client — Delivery                    | 1:N            | Client(optional), Delivery(optional)  | A Client requests many Deliveries                  |
| R16| Route — Delivery                     | 1:N            | Route(optional), Delivery(optional)   | A Route carries many Deliveries                    |
| R17| Warehouse — Delivery                 | 1:N            | Warehouse(optional), Delivery(optional)| Deliveries are dispatched from a Warehouse        |
| R18| Delivery — Delivery_Tracking         | 1:N            | Delivery(mandatory), Tracking(mandatory) | A Delivery has many tracking events             |
| R19| Employee — Delivery_Tracking (changed_by) | 1:N     | Employee(optional), Tracking(optional)| An Employee logs tracking events                   |
| R20| Warehouse — Delivery_Tracking        | 1:N            | Warehouse(optional), Tracking(optional)| Tracking events record the location              |

### Exclusivity Constraints
- **R1 XOR R2**: A User participates in R1 (Client) OR R2 (Employee), never both.
- **R3 XOR R4**: An Employee participates in R3 (Driver) OR R4 (Staff), never both.

### Unique Combination Constraint
- **Route**: The combination (driver + vehicle + delivery_date) must be unique — prevents double-booking.

---

## Relationship Diagram

```
                                 WAREHOUSE
                               /    |    \      \
                         R5  /   R8 |  R12\   R17\  R20
                            /      |      \      \    \
    USER ----R1---- CLIENT --R6-- INVOICE  ROUTE  DELIVERY  DELIVERY_TRACKING
      |                |             |       / \      |           |
      R2            R15 \         R9 |  R10/R11\  R16/         R18|
      |                  \           |    /     \  /              |
    EMPLOYEE           DELIVERY  INV_ITEM  VEHICLE           DELIVERY
      |  \               ^
      |   \           R13|  R14
     R3    R4            |  /
      |     \        INVOICE / EMPLOYEE
      v      v
   DRIVER   STAFF
```

---

## CDM DDL

Clean conceptual DDL — no FK columns, no FK constraints.
Relationships above generate FKs when converted to PDM.

```sql
/*==============================================================*/
/* Conceptual Data Model — PostOffice                           */
/* No FK columns — relationships resolved in PDM generation     */
/*==============================================================*/

-- USER
CREATE TABLE "user" (
    id               SERIAL          PRIMARY KEY,
    password         VARCHAR(128)    NOT NULL,
    is_superuser     BOOLEAN         NOT NULL DEFAULT FALSE,
    username         VARCHAR(150)    NOT NULL UNIQUE,
    first_name       VARCHAR(150)    NOT NULL DEFAULT '',
    last_name        VARCHAR(150)    NOT NULL DEFAULT '',
    email            VARCHAR(254)    NOT NULL DEFAULT '',
    is_staff         BOOLEAN         NOT NULL DEFAULT FALSE,
    contact          VARCHAR(50)     DEFAULT '',
    address          VARCHAR(255)    DEFAULT '',
    role             VARCHAR(20)     NOT NULL DEFAULT 'client',
    created_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_user_role CHECK (role IN ('admin', 'client', 'driver', 'staff', 'manager'))
);

-- CLIENT
CREATE TABLE client (
    id      SERIAL      PRIMARY KEY,
    tax_id  VARCHAR(50) DEFAULT ''
);

-- EMPLOYEE
CREATE TABLE employee (
    id        SERIAL       PRIMARY KEY,
    position  VARCHAR(20)  NOT NULL,
    schedule  VARCHAR(50)  DEFAULT '',
    wage      DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    is_active BOOLEAN      NOT NULL DEFAULT TRUE,
    hire_date DATE         NULL,

    CONSTRAINT chk_employee_position CHECK (position IN ('Driver', 'Staff')),
    CONSTRAINT chk_employee_wage     CHECK (wage >= 0)
);

-- EMPLOYEE_DRIVER
CREATE TABLE employee_driver (
    id                       SERIAL      PRIMARY KEY,
    license_number           VARCHAR(50) NOT NULL,
    license_category         VARCHAR(10) NOT NULL,
    license_expiry_date      DATE        NOT NULL,
    driving_experience_years INTEGER     NOT NULL DEFAULT 0,
    driver_status            VARCHAR(50) NOT NULL DEFAULT 'Available',

    CONSTRAINT chk_driver_experience CHECK (driving_experience_years >= 0),
    CONSTRAINT chk_driver_status     CHECK (driver_status IN ('Available', 'OnDuty', 'OffDuty', 'OnLeave'))
);

-- EMPLOYEE_STAFF
CREATE TABLE employee_staff (
    id         SERIAL      PRIMARY KEY,
    department VARCHAR(32) NOT NULL
);

-- WAREHOUSE
CREATE TABLE warehouse (
    id                       SERIAL       PRIMARY KEY,
    name                     VARCHAR(100) NOT NULL,
    address                  VARCHAR(200) NOT NULL,
    contact                  VARCHAR(50)  NOT NULL,
    schedule_open            TIME         NOT NULL,
    schedule_close           TIME         NOT NULL,
    schedule                 TEXT         NOT NULL,
    maximum_storage_capacity INTEGER      NOT NULL,
    is_active                BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at               TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at               TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_warehouse_capacity CHECK (maximum_storage_capacity > 0),
    CONSTRAINT chk_warehouse_schedule CHECK (schedule_close > schedule_open)
);

-- VEHICLE
CREATE TABLE vehicle (
    id                    SERIAL        PRIMARY KEY,
    vehicle_type          VARCHAR(100)  NOT NULL,
    plate_number          VARCHAR(20)   NOT NULL UNIQUE,
    capacity              DECIMAL(10,2) NOT NULL,
    brand                 VARCHAR(100)  NOT NULL,
    model                 VARCHAR(100)  NOT NULL,
    vehicle_status        VARCHAR(50)   NOT NULL DEFAULT 'Available',
    year                  INTEGER       NOT NULL,
    fuel_type             VARCHAR(50)   NOT NULL,
    last_maintenance_date DATE          NOT NULL,
    is_active             BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at            TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_vehicle_capacity CHECK (capacity > 0),
    CONSTRAINT chk_vehicle_year     CHECK (year BETWEEN 1900 AND 2100),
    CONSTRAINT chk_vehicle_status   CHECK (vehicle_status IN ('Available', 'InUse', 'Maintenance', 'Retired'))
);

-- INVOICE
CREATE TABLE invoice (
    id               SERIAL        PRIMARY KEY,
    invoice_status   VARCHAR(30)   NOT NULL DEFAULT 'Pending',
    invoice_type     VARCHAR(50)   DEFAULT '',
    quantity         INTEGER       NULL,
    invoice_datetime TIMESTAMPTZ   NULL,
    cost             DECIMAL(10,2) NULL,
    subtotal         DECIMAL(10,2) NULL,
    tax_amount       DECIMAL(10,2) NULL,
    paid             BOOLEAN       NOT NULL DEFAULT FALSE,
    payment_method   VARCHAR(50)   DEFAULT '',
    name             VARCHAR(100)  DEFAULT '',
    address          VARCHAR(200)  DEFAULT '',
    contact          VARCHAR(50)   DEFAULT '',
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_invoice_status CHECK (invoice_status IN ('Pending', 'Confirmed', 'Paid', 'Cancelled', 'Refunded')),
    CONSTRAINT chk_invoice_cost   CHECK (cost IS NULL OR cost >= 0)
);

-- INVOICE_ITEM
CREATE TABLE invoice_item (
    id_item        SERIAL        PRIMARY KEY,
    shipment_type  VARCHAR(50)   NOT NULL,
    weight         DECIMAL(10,2) NOT NULL,
    delivery_speed VARCHAR(50)   NOT NULL,
    quantity       INTEGER       NOT NULL DEFAULT 1,
    unit_price     DECIMAL(10,2) NOT NULL,
    notes          TEXT          DEFAULT '',
    created_at     TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_invoiceitem_quantity       CHECK (quantity > 0),
    CONSTRAINT chk_invoiceitem_unit_price     CHECK (unit_price >= 0),
    CONSTRAINT chk_invoiceitem_weight         CHECK (weight > 0),
    CONSTRAINT chk_invoiceitem_delivery_speed CHECK (delivery_speed IN ('Standard', 'Express', 'Overnight', 'Economy'))
);

-- ROUTE
CREATE TABLE route (
    id                  SERIAL        PRIMARY KEY,
    description         TEXT          NOT NULL,
    delivery_status     VARCHAR(50)   NOT NULL DEFAULT 'Scheduled',
    delivery_date       DATE          NULL,
    delivery_start_time TIME          NULL,
    delivery_end_time   TIME          NULL,
    expected_duration   INTERVAL      NULL,
    kms_travelled       DECIMAL(10,2) NOT NULL DEFAULT 0,
    driver_notes        TEXT          DEFAULT '',
    is_active           BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_route_status CHECK (delivery_status IN ('Scheduled', 'InProgress', 'Completed', 'Cancelled')),
    CONSTRAINT chk_route_kms    CHECK (kms_travelled >= 0),
    CONSTRAINT chk_route_times  CHECK (delivery_end_time IS NULL OR delivery_start_time IS NULL OR delivery_end_time > delivery_start_time)
);

-- DELIVERY
CREATE TABLE delivery (
    id                SERIAL        PRIMARY KEY,
    tracking_number   VARCHAR(50)   NOT NULL UNIQUE,
    description       TEXT          DEFAULT '',
    sender_name       VARCHAR(100)  NOT NULL,
    sender_address    VARCHAR(255)  NOT NULL,
    sender_phone      VARCHAR(50)   DEFAULT '',
    sender_email      VARCHAR(254)  DEFAULT '',
    recipient_name    VARCHAR(100)  NOT NULL,
    recipient_address VARCHAR(255)  NOT NULL,
    recipient_phone   VARCHAR(50)   DEFAULT '',
    recipient_email   VARCHAR(254)  DEFAULT '',
    item_type         VARCHAR(50)   NOT NULL,
    weight            DECIMAL(10,2) NOT NULL,
    dimensions        VARCHAR(100)  DEFAULT '',
    status            VARCHAR(20)   NOT NULL DEFAULT 'Registered',
    priority          VARCHAR(10)   NOT NULL DEFAULT 'normal',
    in_transition     BOOLEAN       NOT NULL DEFAULT FALSE,
    delivery_date     DATE          NULL,
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ   NULL,

    CONSTRAINT chk_delivery_status   CHECK (status IN ('Registered', 'Ready', 'Pending', 'In Transit', 'Completed', 'Cancelled')),
    CONSTRAINT chk_delivery_priority CHECK (priority IN ('normal', 'urgent')),
    CONSTRAINT chk_delivery_weight   CHECK (weight > 0)
);

-- DELIVERY_TRACKING
CREATE TABLE delivery_tracking (
    id         SERIAL      PRIMARY KEY,
    status     VARCHAR(20) NOT NULL,
    notes      TEXT        DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_tracking_status CHECK (status IN ('Registered', 'Ready', 'Pending', 'In Transit', 'Completed', 'Cancelled'))
);
```

---

## CDM → PDM: What Gets Generated

When this CDM is converted to a PDM, the relationships above produce:

| Relationship | PDM Result (FK column added to child table) |
|---|---|
| R1 User — Client | `client.user_id → user.id` (UNIQUE, NOT NULL, CASCADE) |
| R2 User — Employee | `employee.user_id → user.id` (UNIQUE, NOT NULL, CASCADE) |
| R3 Employee — Employee_Driver | `employee_driver.employee_id → employee.id` (UNIQUE, NOT NULL, CASCADE) |
| R4 Employee — Employee_Staff | `employee_staff.employee_id → employee.id` (UNIQUE, NOT NULL, CASCADE) |
| R5 Warehouse — Employee | `employee.warehouse_id → warehouse.id` (NULL, SET NULL) |
| R6 Client — Invoice | `invoice.client_id → client.id` (NULL, SET NULL) |
| R7 Employee — Invoice | `invoice.processed_by_id → employee.id` (NULL, SET NULL) |
| R8 Warehouse — Invoice | `invoice.warehouse_id → warehouse.id` (NULL, SET NULL) |
| R9 Invoice — Invoice_Item | `invoice_item.invoice_id → invoice.id` (NOT NULL, CASCADE) |
| R10 Employee — Route | `route.driver_id → employee.id` (NULL, SET NULL) |
| R11 Vehicle — Route | `route.vehicle_id → vehicle.id` (NULL, SET NULL) |
| R12 Warehouse — Route | `route.warehouse_id → warehouse.id` (NULL, SET NULL) |
| R13 Invoice — Delivery | `delivery.invoice_id → invoice.id` (NULL, SET NULL) |
| R14 Employee — Delivery | `delivery.driver_id → employee.id` (NULL, SET NULL) |
| R15 Client — Delivery | `delivery.client_id → client.id` (NULL, SET NULL) |
| R16 Route — Delivery | `delivery.route_id → route.id` (NULL, SET NULL) |
| R17 Warehouse — Delivery | `delivery.warehouse_id → warehouse.id` (NULL, SET NULL) |
| R18 Delivery — Delivery_Tracking | `delivery_tracking.delivery_id → delivery.id` (NOT NULL, CASCADE) |
| R19 Employee — Delivery_Tracking | `delivery_tracking.changed_by_id → employee.id` (NULL, SET NULL) |
| R20 Warehouse — Delivery_Tracking | `delivery_tracking.warehouse_id → warehouse.id` (NULL, SET NULL) |

Plus the unique combination constraint: `UNIQUE(driver_id, vehicle_id, delivery_date)` on Route.

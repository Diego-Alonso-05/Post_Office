DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bdII_14366',
        'USER': 'postgres',
        'PASSWORD': 'Al1711',
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {   --Add this
            'NAME': 'bdII_14366', 
        },
    }
}




--Procedures


DROP PROCEDURE IF EXISTS create_user(
    VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR
);

CREATE OR REPLACE PROCEDURE create_user(
    p_username    VARCHAR(20),
    p_psswd_hash  VARCHAR(50),
    p_name        VARCHAR(100),
    p_contact     VARCHAR(20),
    p_address     VARCHAR(255),
    p_email       VARCHAR(100),
    p_role        VARCHAR(16)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO "USER" (
        USERNAME, PSSWD_HASH, NAME, CONTACT, ADDRESS, EMAIL,
        CREATED_AT, UPDATED_AT, ROLE
    ) VALUES (
        p_username, p_psswd_hash, p_name, p_contact, p_address, p_email,
        CURRENT_DATE, CURRENT_DATE, p_role
    );
END;
$$;

DROP PROCEDURE IF EXISTS create_client(
    INT, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR
);

CREATE OR REPLACE PROCEDURE create_client(
    p_use_id_user INT,
    p_username VARCHAR(20),
    p_psswd_hash VARCHAR(50),
    p_name VARCHAR(100),
    p_contact VARCHAR(20),
    p_address VARCHAR(255),
    p_email VARCHAR(100),
    p_tax_id VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO CLIENT (
        USE_ID_USER, USERNAME, PSSWD_HASH, NAME, CONTACT, ADDRESS, EMAIL,
        CREATED_AT, UPDATED_AT, ROLE, TAX_ID
    ) VALUES (
        p_use_id_user, p_username, p_psswd_hash, p_name, p_contact,
        p_address, p_email, CURRENT_DATE, CURRENT_DATE, 'CLIENT', p_tax_id
    );
END;
$$;

DROP PROCEDURE IF EXISTS create_post_office_store(
    INT, INT, VARCHAR, VARCHAR, VARCHAR, TIME, TIME, TEXT, INT
);

CREATE OR REPLACE PROCEDURE create_post_office_store(
    p_use_id_user     INT,
    p_id_user         INT,
    p_name            VARCHAR(100),
    p_contact         VARCHAR(20),
    p_address         VARCHAR(255),
    p_opening_time    TIME,
    p_closing_time    TIME,
    p_po_schedule     TEXT,
    p_max_storage     INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO POST_OFFICE_STORE (
        USE_ID_USER, ID_USER, NAME, CONTACT, ADDRESS,
        OPENING_TIME, CLOSING_TIME, PO_SCHEDULE, MAXIMUM_STORAGE
    ) VALUES (
        p_use_id_user, p_id_user, p_name, p_contact, p_address,
        p_opening_time, p_closing_time, p_po_schedule, p_max_storage
    );
END;
$$;

DROP PROCEDURE IF EXISTS create_employee(
    INT, INT, INT, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR,
    VARCHAR, TEXT, DECIMAL, BOOL, DATE
);

CREATE OR REPLACE PROCEDURE create_employee(
    p_use_id_user        INT,
    p_id_user            INT,
    p_id_postoffice_store INT,
    p_username           VARCHAR(20),
    p_psswd_hash         VARCHAR(50),
    p_name               VARCHAR(100),
    p_contact            VARCHAR(20),
    p_address            VARCHAR(255),
    p_email              VARCHAR(100),
    p_role               VARCHAR(16),
    p_position           VARCHAR(32),
    p_schedule           TEXT,
    p_wage               DECIMAL,
    p_is_active          BOOL,
    p_hire_date          DATE
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO EMPLOYEE (
        USE_ID_USER, ID_USER, ID_POSTOFFICE_STORE, USERNAME, PSSWD_HASH, NAME,
        CONTACT, ADDRESS, EMAIL, CREATED_AT, UPDATED_AT, ROLE, "POSITION",
        SCHEDULE, WAGE, IS_ACTIVE, HIRE_DATE
    ) VALUES (
        p_use_id_user, p_id_user, p_id_postoffice_store, p_username, p_psswd_hash, p_name,
        p_contact, p_address, p_email, CURRENT_DATE, CURRENT_DATE, p_role,
        p_position, p_schedule, p_wage, p_is_active, p_hire_date
    );
END;
$$;

CREATE OR REPLACE PROCEDURE create_invoice(
    p_id_postoffice_store INTEGER,
    p_use_id_user INTEGER,
    p_emp_use_id_user INTEGER,
    p_emp_id_user INTEGER,
    p_id_user INTEGER,
    p_id_client INTEGER,
    p_total NUMERIC,
    p_issue_date DATE,
    p_due_date DATE,
    p_status VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO INVOICE (
        id_postoffice_store,
        use_id_user,
        emp_use_id_user,
        emp_id_user,
        id_user,
        cli_id_user,
        cost,
        invoice_datetime,
        invoice_status
    )
    VALUES (
        p_id_postoffice_store,
        p_use_id_user,
        p_emp_use_id_user,
        p_emp_id_user,
        p_id_user,
        p_id_client,
        p_total,
        p_issue_date,
        p_status
    );
END;
$$;

CREATE OR REPLACE PROCEDURE create_delivery(
    p_use_id_user INTEGER,
    p_id_user INTEGER,
    p_id_invoice INTEGER,
    p_delivery_date DATE,
    p_delivery_status VARCHAR,
    p_delivery_address VARCHAR,
    p_comments TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO DELIVERY (
        use_id_user,
        id_user,
        id_invoice,
        status,
        recipient_address,
        description,
        registered_at
    )
    VALUES (
        p_use_id_user,
        p_id_user,
        p_id_invoice,
        p_delivery_status,
        p_delivery_address,
        p_comments,
        p_delivery_date
    );
END;
$$;

CREATE OR REPLACE PROCEDURE create_route(
    p_use_id_user INT,
    p_emp_id_user INT,
    p_id_user INT,
    p_id_delivery INT,
    p_id_postoffice_store INT,
    p_description TEXT,
    p_delivery_status VARCHAR,
    p_delivery_date DATE,
    p_delivery_start_time DATE,
    p_delivery_end_time DATE,
    p_expected_duration TIME,
    p_kms_travelled DECIMAL,
    p_driver_notes TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO ROUTE (
        USE_ID_USER,
        EMP_ID_USER,
        ID_USER,
        ID_DELIVERY,
        ID_POSTOFFICE_STORE,
        DESCRIPTION,
        DELIVERY_STATUS,
        DELIVERY_DATE,
        DELIVERY_START_TIME,
        DELIVERY_END_TIME,
        EXPECTED_DURATION,
        KMS_TRAVELLED,
        DRIVER_NOTES
    )
    VALUES (
        p_use_id_user,
        p_emp_id_user,
        p_id_user,
        p_id_delivery,
        p_id_postoffice_store,
        p_description,
        p_delivery_status,
        p_delivery_date,
        p_delivery_start_time,
        p_delivery_end_time,
        p_expected_duration,
        p_kms_travelled,
        p_driver_notes
    );
END;
$$;

CREATE OR REPLACE PROCEDURE create_vehicle(
    p_id_route INT,
    p_vehicle_type VARCHAR(50),
    p_plate_number VARCHAR(20),
    p_capacity DECIMAL(10,2),
    p_brand VARCHAR(50),
    p_model VARCHAR(50),
    p_vehicle_status VARCHAR(20),
    p_year INT,
    p_fuel_type VARCHAR(30),
    p_last_maintenance_date DATE
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO VEHICLE (
        ID_ROUTE,
        VEHICLE_TYPE,
        PLATE_NUMBER,
        CAPACITY,
        BRAND,
        MODEL,
        VEHICLE_STATUS,
        YEAR,
        FUEL_TYPE,
        LAST_MAINTENANCE_DATE
    )
    VALUES (
        p_id_route,
        p_vehicle_type,
        p_plate_number,
        p_capacity,
        p_brand,
        p_model,
        p_vehicle_status,
        p_year,
        p_fuel_type,
        p_last_maintenance_date
    );
END;
$$;

CREATE OR REPLACE PROCEDURE create_notification(
    p_id_delivery INT,
    p_notification_type VARCHAR(20),
    p_recipient_contact VARCHAR(100),
    p_subject VARCHAR(255),
    p_message TEXT,
    p_status VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO NOTIFICATION (
        ID_DELIVERY,
        NOTIFICATION_TYPE,
        RECIPIENT_CONTACT,
        SUBJECT,
        MESSAGE,
        STATUS,
        CREATED_AT
    )
    VALUES (
        p_id_delivery,
        p_notification_type,
        p_recipient_contact,
        p_subject,
        p_message,
        p_status,
        CURRENT_DATE
    );
END;
$$;



--Test



import uuid
import pytest
from django.db import connections


@pytest.mark.django_db
def test_create_user_inserts_one_row():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")

    username = f"u_{uuid.uuid4().hex[:10]}"
    params = {
        "p_username": username,
        "p_psswd_hash": "hash_demo",
        "p_name": "Test User",
        "p_contact": "600123123",
        "p_address": "Demo Street 1",
        "p_email": f"{username}@example.com",
        "p_role": "CLIENT"
    }

    cur.execute("""
        CALL create_user(%(p_username)s, %(p_psswd_hash)s, %(p_name)s,
                         %(p_contact)s, %(p_address)s, %(p_email)s, %(p_role)s);
    """, params)

    cur.execute('SELECT COUNT(*) FROM "USER" WHERE USERNAME = %s;', [username])
    count = cur.fetchone()[0]
    assert count == 1, "Procedure create_user did not insert exactly one row."

    cur.execute("ROLLBACK;")


@pytest.mark.django_db
def test_create_client_inserts_one_row():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")

    cur.execute("""
        INSERT INTO "USER" (USERNAME, PSSWD_HASH, NAME, CONTACT, ADDRESS, EMAIL, CREATED_AT, UPDATED_AT, ROLE)
        VALUES ('user_client_test', 'hash', 'User Client', '600000000', 'Street 0', 'user_client@test.com', CURRENT_DATE, CURRENT_DATE, 'CLIENT')
        RETURNING ID_USER;
    """)
    use_id_user = cur.fetchone()[0]

    username = f"cli_{uuid.uuid4().hex[:8]}"
    params = {
        "p_use_id_user": use_id_user,
        "p_username": username,
        "p_psswd_hash": "hash_demo",
        "p_name": "Client Test",
        "p_contact": "600555111",
        "p_address": "Client Street 45",
        "p_email": f"{username}@mail.com",
        "p_tax_id": "TX1234567"
    }

    cur.execute("""
        CALL create_client(
            %(p_use_id_user)s, %(p_username)s, %(p_psswd_hash)s,
            %(p_name)s, %(p_contact)s, %(p_address)s, %(p_email)s, %(p_tax_id)s
        );
    """, params)

    cur.execute("SELECT COUNT(*) FROM CLIENT WHERE USERNAME = %s;", [username])
    count = cur.fetchone()[0]
    assert count == 1, "Procedure create_client did not insert exactly one row."

    cur.execute("ROLLBACK;")


@pytest.mark.django_db
def test_create_post_office_store_inserts_one_row():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")

    cur.execute("""
        INSERT INTO "USER" (USERNAME, PSSWD_HASH, NAME, CONTACT, ADDRESS, EMAIL, CREATED_AT, UPDATED_AT, ROLE)
        VALUES ('store_user_test', 'hash', 'Owner User', '600000001', 'Street 1', 'owner@test.com', CURRENT_DATE, CURRENT_DATE, 'STAFF')
        RETURNING ID_USER;
    """)
    user_id = cur.fetchone()[0]

    store_name = f"Store_{uuid.uuid4().hex[:8]}"
    params = {
        "p_use_id_user": user_id,
        "p_id_user": user_id,
        "p_name": store_name,
        "p_contact": "232000111",
        "p_address": "Main Avenue 100",
        "p_opening_time": "08:30",
        "p_closing_time": "18:30",
        "p_po_schedule": "Mon-Fri 08:30-18:30",
        "p_max_storage": 500
    }

    cur.execute("""
        CALL create_post_office_store(
            %(p_use_id_user)s, %(p_id_user)s, %(p_name)s, %(p_contact)s, %(p_address)s,
            %(p_opening_time)s, %(p_closing_time)s, %(p_po_schedule)s, %(p_max_storage)s
        );
    """, params)

    cur.execute("""
        SELECT COUNT(*) FROM POST_OFFICE_STORE
        WHERE NAME = %s AND USE_ID_USER = %s AND ID_USER = %s;
    """, [store_name, user_id, user_id])
    count = cur.fetchone()[0]
    assert count == 1, "Procedure create_post_office_store did not insert exactly one row."

    cur.execute("ROLLBACK;")


@pytest.mark.django_db
def test_create_employee_inserts_one_row():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")

    cur.execute("""
        INSERT INTO "USER" (USERNAME, PSSWD_HASH, NAME, CONTACT, ADDRESS, EMAIL, CREATED_AT, UPDATED_AT, ROLE)
        VALUES ('emp_user_test', 'hash', 'Emp User', '611111111', 'Street 5', 'emp@test.com', CURRENT_DATE, CURRENT_DATE, 'STAFF')
        RETURNING ID_USER;
    """)
    user_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO POST_OFFICE_STORE (USE_ID_USER, ID_USER, NAME, CONTACT, ADDRESS, OPENING_TIME, CLOSING_TIME, PO_SCHEDULE, MAXIMUM_STORAGE)
        VALUES (%s, %s, 'Store Emp Test', '232111333', 'Store Street', '08:30', '17:30', 'Mon-Fri 08:30-17:30', 400)
        RETURNING ID_POSTOFFICE_STORE;
    """, [user_id, user_id])
    store_id = cur.fetchone()[0]

    emp_name = f"Emp_{uuid.uuid4().hex[:8]}"
    params = {
        "p_use_id_user": user_id,
        "p_id_user": user_id,
        "p_id_postoffice_store": store_id,
        "p_username": emp_name.lower(),
        "p_psswd_hash": "hash_demo",
        "p_name": emp_name,
        "p_contact": "600999000",
        "p_address": "Employee Street 10",
        "p_email": f"{emp_name.lower()}@mail.com",
        "p_role": "EMPLOYEE",
        "p_position": "Courier",
        "p_schedule": "Mon-Fri 9-17",
        "p_wage": 900.00,
        "p_is_active": True,
        "p_hire_date": "2024-01-15"
    }

    cur.execute("""
        CALL create_employee(
            %(p_use_id_user)s, %(p_id_user)s, %(p_id_postoffice_store)s,
            %(p_username)s, %(p_psswd_hash)s, %(p_name)s, %(p_contact)s,
            %(p_address)s, %(p_email)s, %(p_role)s, %(p_position)s,
            %(p_schedule)s, %(p_wage)s, %(p_is_active)s, %(p_hire_date)s
        );
    """, params)

    cur.execute("SELECT COUNT(*) FROM EMPLOYEE WHERE USERNAME = %s;", [params["p_username"]])
    count = cur.fetchone()[0]
    assert count == 1, "Procedure create_employee did not insert exactly one row."

    cur.execute("ROLLBACK;")


@pytest.mark.django_db
def test_create_invoice_inserts_one_row():
    cur = connections['default'].cursor()
    cur.execute("BEGIN;")

    cur.execute("""
        INSERT INTO "USER" (USERNAME, PSSWD_HASH, NAME, CONTACT, ADDRESS, EMAIL, CREATED_AT, UPDATED_AT, ROLE)
        VALUES ('inv_user_test', 'hash', 'Inv User', '622222222', 'Street 6', 'inv@test.com', CURRENT_DATE, CURRENT_DATE, 'CLIENT')
        RETURNING ID_USER;
    """)
    user_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO CLIENT (USE_ID_USER, USERNAME, PSSWD_HASH, NAME, CONTACT, ADDRESS, EMAIL,
                            CREATED_AT, UPDATED_AT, ROLE, TAX_ID)
        VALUES (%s, 'cli_invoice', 'hash', 'Client Inv', '600111000', 'Client Street 10', 'cli_invoice@test.com',
                CURRENT_DATE, CURRENT_DATE, 'CLIENT', 'TX999')
        RETURNING ID_USER;
    """, [user_id])
    client_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO POST_OFFICE_STORE (USE_ID_USER, ID_USER, NAME, CONTACT, ADDRESS, OPENING_TIME, CLOSING_TIME, PO_SCHEDULE, MAXIMUM_STORAGE)
        VALUES (%s, %s, 'Invoice Store', '600111999', 'Central Street 10', '08:00', '18:00', 'Mon-Fri', 500)
        RETURNING ID_USER;
    """, [user_id, user_id])
    store_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO EMPLOYEE (USE_ID_USER, ID_USER, ID_POSTOFFICE_STORE, "POSITION", WAGE)
        VALUES (%s, %s, %s, 'CASHIER', 1500.00)
        RETURNING USE_ID_USER, ID_USER;
    """, [user_id, user_id, store_id])
    emp_use_id_user, emp_id_user = cur.fetchone()

    params = {
        "p_id_postoffice_store": store_id,
        "p_use_id_user": user_id,
        "p_emp_use_id_user": emp_use_id_user,
        "p_emp_id_user": emp_id_user,
        "p_id_user": user_id,
        "p_id_client": client_id,
        "p_total": 154.75,
        "p_issue_date": "2024-04-01",
        "p_due_date": "2024-04-10",
        "p_status": "PENDING"
    }

    cur.execute("""
        CALL create_invoice(
            %(p_id_postoffice_store)s,
            %(p_use_id_user)s,
            %(p_emp_use_id_user)s,
            %(p_emp_id_user)s,
            %(p_id_user)s,
            %(p_id_client)s,
            %(p_total)s,
            %(p_issue_date)s,
            %(p_due_date)s,
            %(p_status)s
        );
    """, params)

    cur.execute("SELECT COUNT(*) FROM INVOICE WHERE cost = %s;", [154.75])
    count = cur.fetchone()[0]
    assert count == 1, "Procedure create_invoice did not insert correctly."


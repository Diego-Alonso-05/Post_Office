import pytest
from django.db import connections

@pytest.mark.django_db
def testeprocedimentoupdate():
    cur = connections['default'].cursor()

    # Start transaction
    cur.execute("BEGIN;")

    # Insert a test invoice using Django’s actual field names
    cur.execute("""
        INSERT INTO invoices
        (invoice_status, invoice_type, quantity, invoice_datetime, cost, paid, payment_method, morada, contacto)
        VALUES
        ('Pending', 'Online', 3, CURRENT_TIMESTAMP, 150.00, FALSE, 'Card', '456 Update St', '999-8888');
    """)

    # Get the ID of the invoice we just inserted
    cur.execute("""
        SELECT id
        FROM invoices
        WHERE morada='456 Update St'
        ORDER BY id DESC
        LIMIT 1;
    """)
    invoice_id = cur.fetchone()[0]

    # UPDATE the invoice (change status and cost)
    cur.execute("""
        UPDATE invoices
        SET invoice_status = 'Paid', cost = 200.00
        WHERE id = %s;
    """, [invoice_id])

    # Verify the update
    cur.execute("SELECT invoice_status, cost FROM invoices WHERE id = %s;", [invoice_id])
    updated_status, updated_cost = cur.fetchone()

    assert updated_status == 'Paid', "Invoice status was not updated correctly"
    assert float(updated_cost) == 200.00, "Invoice cost was not updated correctly"

    print(f"Invoice {invoice_id} successfully updated to status '{updated_status}' with cost {updated_cost}.")

    # Rollback so database remains unchanged
    cur.execute("ROLLBACK;")

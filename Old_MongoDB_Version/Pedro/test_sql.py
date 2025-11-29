import pytest
from django.db import connections

@pytest.mark.django_db
def testeprocedimentox():
    cur = connections['default'].cursor()
    
    # Start transaction
    cur.execute("BEGIN;")
    
    # Insert invoice
    cur.execute("""
        INSERT INTO invoices 
        (invoice_status, invoice_type, quantity, invoice_datetime, cost, paid, payment_method, name, address, contact)
        VALUES 
        ('Pending', 'Online', 3, CURRENT_TIMESTAMP, 150.00, FALSE, 'Credit Card', 'John Doe', '123 Main St', '555-1234');
    """)
    
    # Get the ID of the invoice we just inserted
    cur.execute("""
        SELECT id_invoice 
        FROM invoices 
        WHERE name='John Doe' 
        ORDER BY id_invoice DESC 
        LIMIT 1;
    """)
    invoice_id = cur.fetchone()[0]
    
    # Delete the invoice
    cur.execute("DELETE FROM invoices WHERE id_invoice = %s;", [invoice_id])
    
    # Check if deletion succeeded
    cur.execute("SELECT COUNT(*) FROM invoices WHERE id_invoice = %s;", [invoice_id])
    count = cur.fetchone()[0]
    
    assert count == 0, "Invoice was not deleted successfully"
    
    # Rollback transaction so database remains unchanged
    cur.execute("ROLLBACK;")


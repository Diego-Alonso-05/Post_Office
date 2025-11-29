from django.db import models
from django.contrib.auth.models import User


class Invoice(models.Model):
    PAYMENT_METHODS = [
        ('Credit Card', 'Credit Card'),
        ('Cash', 'Cash'),
        ('Transfer', 'Transfer'),
    ]

    id_invoice = models.BigAutoField(primary_key=True)
    invoice_status = models.CharField(max_length=20, default='Pending')
    invoice_type = models.CharField(max_length=50, default='Standard')
    quantity = models.IntegerField(default=1)
    invoice_datetime = models.DateTimeField(auto_now_add=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='Credit Card')
    name = models.CharField(max_length=100, default='Unknown')
    address = models.CharField(max_length=200, default='Unknown')
    contact = models.CharField(max_length=50, default='N/A')

    class Meta:
        db_table = "invoices"

    def __str__(self):
        return f"Invoice #{self.id_invoice} - {self.name}"

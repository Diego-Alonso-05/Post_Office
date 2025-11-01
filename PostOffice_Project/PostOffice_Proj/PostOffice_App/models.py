from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Invoice(models.Model):
    PAYMENT_METHODS = [
        ('Card', 'Card'),
        ('Cash', 'Cash'),
        ('Transfer', 'Transfer'),
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invoice_status = models.CharField(max_length=50)
    invoice_type = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    invoice_datetime = models.DateTimeField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    morada = models.CharField(max_length=255)
    contacto = models.CharField(max_length=20)

    class Meta:
        db_table = "invoices"

    def __str__(self):
        return f"Invoice #{self.id} - {self.user.username}"

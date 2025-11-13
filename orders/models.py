from django.db import models


class Order(models.Model):
    """
    Pedido simplificado para el experimento de autenticación y autorización.
    """
    id = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    products_list = models.TextField()
    picker_name = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default="Alistamiento")

    def __str__(self):
        return f"Pedido #{self.id}"

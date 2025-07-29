from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal
from django.db.models import Sum, Max
from datetime import date
from django.utils import timezone
from django.contrib.auth import get_user_model


class Product(models.Model):
    class Category(models.TextChoices):
        MOVING_HEAD = 'Moving Head', 'Moving Head'
        LED_PAR = 'Led Par', 'Led Par'
        SMOKE = 'Smoke', 'Smoke'
        CONTROLS = 'Controlls', 'Controlls'
        LASER_BEAM = 'Laser Beam', 'Laser Beam'
        LAMPS = 'Lamps', 'Lamps'
        TRUSS = 'Truss', 'Truss'
        LED_SCREENS = 'Led Screens', 'Led Screens'
        ACCESSORIES = 'Accessories', 'Accessories'
        OTHER = 'Other', 'Other'

    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
        verbose_name="Product Category"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    details = models.TextField(blank=True, null=True)
    main_image = models.ImageField(upload_to='products/main_images/')
    video = models.FileField(upload_to='products/videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_quantity(self):
        """Returns the sum of all quantities of this product across all warehouses"""
        result = WarehouseProduct.objects.filter(
            product=self
        ).aggregate(total=Sum('quantity'))
        return result['total'] or 0

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        related_name='images', 
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='products/images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def total_inventory_value(self):
        return sum(
            item.total_value 
            for item in self.warehouse_products.select_related('product')
        )


class WarehouseProduct(models.Model):
    warehouse = models.ForeignKey(
        Warehouse, 
        related_name='warehouse_products', 
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, 
        related_name='warehouse_products', 
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('warehouse', 'product')
        verbose_name = 'Warehouse Inventory'
        verbose_name_plural = 'Warehouse Inventory'

    def __str__(self):
        return f"{self.product.name} in {self.warehouse.name} - {self.quantity} units"

    @property
    def total_value(self):
        return self.quantity * self.product.price


class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name="Client Name")
    address = models.TextField(verbose_name="Full Address")
    phone = models.CharField(
        max_length=20, 
        verbose_name="Phone Number",
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'."
            )
        ]
    )
    email = models.EmailField(blank=True, null=True, verbose_name="Email Address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"{self.name} ({self.phone})"









User = get_user_model()

class Invoice(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_SENT = 'sent'
    STATUS_PAID = 'paid'
    STATUS_INSTALLMENT = 'installment'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SENT, 'Sent'),
        (STATUS_PAID, 'Paid'),
        (STATUS_INSTALLMENT, 'Installment'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    # Core Invoice Fields
    number = models.AutoField(primary_key=True, verbose_name="Invoice Number")
    client = models.ForeignKey(
        'Client',
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name="Client"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='assigned_invoices',
        verbose_name="Assigned To",
        null=True,
        blank=True
    )
    
    # Date Fields
    date_created = models.DateTimeField(auto_now_add=True)
    last_edit_time = models.DateTimeField(auto_now=True)
    date_due = models.DateField(verbose_name="Due Date")
    
    # Financial Fields
    tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Tax Percentage (%)"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Discount Amount"
    )
    
    # Status and Notes
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Additional Notes")
    
    # Installment Specific Fields
    is_installment = models.BooleanField(default=False)
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    installment_plan = models.TextField(blank=True, null=True, verbose_name="Installment Plan Details")

    class Meta:
        ordering = ['-last_edit_time']
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def save(self, *args, **kwargs):
            """Auto-assign to current user if not assigned and handle status changes"""
            if not self.assigned_to and hasattr(self, '_current_user'):
                self.assigned_to = self._current_user
            
            # Handle status-specific logic
            if self.status == self.STATUS_PAID:
                if not self.items.exists() and not kwargs.get('force_insert'):
                    raise ValueError("Cannot mark empty invoice as paid")
                self.amount_paid = self.total
                self.is_installment = False
            elif self.status == self.STATUS_INSTALLMENT:
                self.is_installment = True
            else:
                self.is_installment = False
                
            super().save(*args, **kwargs)
    

    # Financial Calculations
    @property
    def subtotal(self):
        """Calculate subtotal from all items"""
        return sum(item.total for item in self.items.all()) if self.items.exists() else Decimal('0')
    
    @property
    def tax_amount(self):
        """Calculate tax amount based on subtotal"""
        return (self.subtotal * self.tax_percentage / 100).quantize(Decimal('0.01'))
    
    @property
    def total(self):
        """Calculate final total after tax and discount"""
        return (self.subtotal + self.tax_amount - self.discount_amount).quantize(Decimal('0.01'))
    
    @property
    def balance_due(self):
        """Calculate remaining balance"""
        return (self.total - self.amount_paid).quantize(Decimal('0.01'))
    
    @property
    def payment_progress(self):
        """Calculate payment progress percentage"""
        if self.total == 0:
            return 0
        return (self.amount_paid / self.total * 100).quantize(Decimal('1'))

    # Status Helpers
    def is_overdue(self):
        """Check if invoice is overdue"""
        return self.date_due < timezone.now().date() and self.status not in [self.STATUS_PAID, self.STATUS_CANCELLED]
    
    def can_mark_paid(self):
        """Check if invoice can be marked as paid"""
        return self.status in [self.STATUS_DRAFT, self.STATUS_SENT, self.STATUS_INSTALLMENT]
    
    def can_edit(self):
        """Check if invoice can be edited"""
        return self.status != self.STATUS_CANCELLED

    def __str__(self):
        return f"Invoice #{self.number} - {self.client.name} (Status: {self.get_status_display()})"


class Installment(models.Model):
    """Model for tracking installment payments"""
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='installments'
    )
    due_date = models.DateField()
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date']
        verbose_name = "Installment Payment"
        verbose_name_plural = "Installment Payments"

    def save(self, *args, **kwargs):
        """Update parent invoice when installment is paid"""
        if self.is_paid and not self.payment_date:
            self.payment_date = timezone.now().date()
            
            # Update parent invoice
            self.invoice.amount_paid += self.amount
            if self.invoice.amount_paid >= self.invoice.total:
                self.invoice.status = Invoice.STATUS_PAID
            self.invoice.save()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Installment #{self.id} for Invoice #{self.invoice.number} - {self.amount}"



class InvoiceItem(models.Model):
    """
    Represents a product line item within an invoice
    Stores product, quantity, and price at time of invoicing
    """
    invoice = models.ForeignKey(
        'Invoice',
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Invoice"
    )
    
    product = models.ForeignKey(
        'Product',
        on_delete=models.PROTECT,  # Prevent deletion if used in invoices
        related_name='invoice_items',
        verbose_name="Product"
    )
    
    # Price at time of invoicing (snapshot)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Unit Price"
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Quantity"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Invoice Item"
        verbose_name_plural = "Invoice Items"
        ordering = ['-created_at']
        unique_together = ('invoice', 'product')  # Prevent duplicate products in same invoice

    @property
    def total(self):
        """Calculate total for this line item with null checks"""
        if self.unit_price is None or self.quantity is None:
            return Decimal('0.00')
        return self.unit_price * Decimal(self.quantity)

    def __str__(self):
        return f"{self.quantity} × {self.product.name} @ {self.unit_price}"

    def save(self, *args, **kwargs):
        """Automatically set unit price from product if not set"""
        if not self.unit_price and self.product_id:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)
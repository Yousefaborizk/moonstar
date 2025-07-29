# forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Product, Warehouse, ProductImage , WarehouseProduct ,Client  ,Installment

class ProductForm(forms.ModelForm):
    category = forms.ChoiceField(
        choices=Product.Category.choices,
        initial=Product.Category.OTHER,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'details', 'main_image', 'video']
        widgets = {
            'details': forms.Textarea(attrs={'rows': 3}),
        }


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

# Formset for product images
ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    fields=('image',),
    extra=1,  # Start with one empty form
    can_delete=True,
    widgets={
        'image': forms.FileInput(attrs={'class': 'form-control'})
    }
)


class WarehouseProductFormUpdate(forms.ModelForm):
    class Meta:
        model = WarehouseProduct
        fields = ['quantity']  # Make sure product is included
        
        
class WarehouseProductFormAdd(forms.ModelForm):
    class Meta:
        model = WarehouseProduct
        fields = [ 'product', 'quantity']  # Make sure product is included
        
        
        
        
        
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'address', 'phone', 'email']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'phone': forms.TextInput(attrs={'placeholder': '+CountryCode Area Number'}),
        }
        
        









from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, Product , InvoiceItem
from django.contrib.auth import get_user_model  # Add this import

User = get_user_model()  # Add this line

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'assigned_to', 'date_due', 'tax_percentage', 
                 'discount_amount', 'notes', 'status']
        widgets = {
            'date_due': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            # Limit assigned_to choices to staff users
            self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)
            if not self.instance.pk:  # Only for new invoices
                self.initial['assigned_to'] = self.user

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'unit_price', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control product-select'}),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control unit-price',
                'min': '0.01',
                'step': '0.01'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control quantity',
                'min': '1'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'product' in self.initial:
            product = Product.objects.get(pk=self.initial['product'])
            self.fields['unit_price'].initial = product.price

InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,
    can_delete=True
)




class InstallmentForm(forms.ModelForm):
    class Meta:
        model = Installment
        fields = ['due_date', 'amount']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'})
        }

InstallmentFormSet = forms.inlineformset_factory(
    Invoice,
    Installment,
    form=InstallmentForm,
    extra=1,
    can_delete=True
)
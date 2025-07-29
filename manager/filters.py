# products/filters.py
import django_filters
from django import forms
from .models import Product

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains', 
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name...',
            'class': 'form-control'
        })
    )
    
    price_min = django_filters.NumberFilter(
        field_name='price', 
        lookup_expr='gte',
        label='',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Min price',
            'class': 'form-control',
            'min': '0'
        })
    )
    
    price_max = django_filters.NumberFilter(
        field_name='price', 
        lookup_expr='lte',
        label='',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Max price',
            'class': 'form-control',
            'min': '0'
        })
    )
    
    category = django_filters.ChoiceFilter(
        choices=Product.Category.choices,
        label='',
        empty_label='All Categories',
        widget=forms.Select  # Note: Passing the class, not an instance
    )
    
    ordering = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('price', 'price'),
            ('created_at', 'last_added'),
        ),
        field_labels={
            'name': 'Name (A-Z)',
            '-name': 'Name (Z-A)',
            'price': 'Price (Low to High)',
            '-price': 'Price (High to Low)',
            'created_at': 'Oldest First',
            '-created_at': 'Newest First',
        },
        label='Sort by',
        empty_label='Default',
        widget=forms.Select  # Note: Passing the class, not an instance
    )

    class Meta:
        model = Product
        fields = []
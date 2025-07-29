# sales/filters.py
import django_filters
from django import forms
from django.db.models import Q
from manager.models import Product

class ProductFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search',
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search products...',
            'class': 'form-control'
        })
    )
    
    price = django_filters.RangeFilter(
        field_name='price',
        label='Price Range',
        widget=django_filters.widgets.RangeWidget(attrs={
            'class': 'form-control',
            'placeholder': 'Min / Max'
        })
    )
    
    category = django_filters.ChoiceFilter(
        choices=Product.Category.choices,
        label='Category',
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sort = django_filters.OrderingFilter(
        fields=(
            ('name', 'Name'),
            ('price', 'Price'),
            ('created_at', 'Newest'),
        ),
        field_labels={
            'name': 'Name (A-Z)',
            '-name': 'Name (Z-A)',
            'price': 'Price (Low to High)',
            '-price': 'Price (High to Low)',
            'created_at': 'Oldest First',
            '-created_at': 'Newest First',
        },
        label='Sort By',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | 
            Q(details__icontains=value)
        )

    class Meta:
        model = Product
        fields = []
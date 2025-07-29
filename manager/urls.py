# urls.py
from django.urls import path
from .views import (
    ProductListView,     ProductCreateView,   ProductDetailView, ProductUpdateView,
    WarehouseListView, WarehouseCreateView, WarehouseDetailView, WarehouseUpdateView,
    WarehouseProductCreateView,WarehouseProductUpdateView,
    ClientListView, ClientCreateView, ClientDetailView, ClientUpdateView,ClientExportView,
    InvoiceCreateView, InvoiceListView,  InvoiceDetailView ,  InvoiceUpdateView, MarkInvoicePaidView, MarkInstallmentPaidView

)
from . import views

urlpatterns = [
    # Product URLs
    path('products/list/', ProductListView.as_view(), name='product_list'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/add-image-field/', views.add_image_field, name='add_image_field'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update'),
    
    # Warehouse URLs
    path('warehouses/', WarehouseListView.as_view(), name='warehouse_list'),
    path('warehouses/create/', WarehouseCreateView.as_view(), name='warehouse_create'),
    path('warehouses/<int:pk>/', WarehouseDetailView.as_view(), name='warehouse_detail'),
    path('warehouses/<int:pk>/edit/', WarehouseUpdateView.as_view(), name='warehouse_update'),

    # WarehouseProduct URLs
    path('warehouses/<int:warehouse_id>/add-product/', WarehouseProductCreateView.as_view(), name='warehouseproduct_create'),
    path('warehouse-product/<int:pk>/edit/', WarehouseProductUpdateView.as_view(), name='warehouseproduct_update'),

    
    # Clients URLs    
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/create/', ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='client_update'),
    path('clients/export/', ClientExportView.as_view(), name='client_export'),
    
    
    # Invoices URLs        
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/create/', InvoiceCreateView.as_view(), name='invoice_create'),   
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'), 
    path('invoices/<int:pk>/edit/', InvoiceUpdateView.as_view(), name='invoice_update'),
    path('invoice/<int:pk>/mark-paid/', MarkInvoicePaidView.as_view(), name='mark_invoice_paid'),
    path('invoices/installment/<int:pk>/mark-paid/', MarkInstallmentPaidView.as_view(), name='mark_installment_paid'),
]
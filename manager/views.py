# views.py
from django.shortcuts import render, redirect
from .models import Product, Warehouse, ProductImage, WarehouseProduct, Client,Invoice, InvoiceItem  ,Installment
from .forms import ProductForm, WarehouseForm, ProductImageFormSet ,WarehouseProductFormUpdate,WarehouseProductFormAdd ,ClientForm ,InstallmentFormSet
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DetailView, ListView, View
from .forms import InvoiceForm, InvoiceItemFormSet
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django_filters.views import FilterView
from .filters import ProductFilter



class MarkInvoicePaidView(LoginRequiredMixin, View):
    def post(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        invoice.status = 'paid'
        invoice.save()
        return JsonResponse({'status': 'success', 'new_status': 'paid'})



class ProductListView(LoginRequiredMixin, FilterView):
    model = Product
    template_name = 'manager/products/list.html'
    context_object_name = 'products'
    filterset_class = ProductFilter
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = context['filter']  # Make filter available in template
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'manager/products/create.html'
    success_url = reverse_lazy('product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = ProductImageFormSet(self.request.POST, self.request.FILES, prefix='images')
        else:
            context['image_formset'] = ProductImageFormSet(queryset=ProductImage.objects.none(), prefix='images')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        if image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

def add_image_field(request):
    """AJAX view to return a new empty image form"""
    formset = ProductImageFormSet(queryset=ProductImage.objects.none(), prefix='images')
    form = formset.empty_form
    return JsonResponse({
        'form_html': form.as_p(),
        'prefix': form.prefix
    })

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'manager/products/detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warehouse_stock'] = self.object.warehouse_products.select_related('warehouse')
        return context

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'manager/products/update.html'
    success_url = reverse_lazy('product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = ProductImageFormSet(
                self.request.POST, self.request.FILES,
                instance=self.object, prefix='images'
            )
        else:
            context['image_formset'] = ProductImageFormSet(
                instance=self.object, prefix='images'
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        if image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))


# Warehouse Views
class WarehouseListView(LoginRequiredMixin, ListView):
    model = Warehouse
    template_name = 'manager/warehouses/list.html'  
    context_object_name = 'warehouses'

class WarehouseCreateView(LoginRequiredMixin, CreateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'manager/warehouses/create.html'
    success_url = reverse_lazy('warehouse_list')
    


class WarehouseDetailView(LoginRequiredMixin, DetailView):
    model = Warehouse
    template_name = 'manager/warehouses/detail.html'
    context_object_name = 'warehouse'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory = self.object.warehouse_products.select_related('product')
        for item in inventory:
            item.edit_url = reverse('warehouseproduct_update', kwargs={'pk': item.pk})
        context['inventory'] = inventory
        return context


    
class WarehouseUpdateView(LoginRequiredMixin, UpdateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'manager/warehouses/update.html'
    success_url = reverse_lazy('warehouse_list')
    
    
from django.contrib import messages
from django.views.generic import CreateView

class WarehouseProductCreateView(LoginRequiredMixin, CreateView):
    model = WarehouseProduct
    form_class = WarehouseProductFormAdd
    template_name = 'manager/warehouseproduct/create.html'

    def get_initial(self):
        initial = super().get_initial()
        warehouse_id = self.kwargs.get('warehouse_id')
        if warehouse_id:
            initial['warehouse'] = get_object_or_404(Warehouse, pk=warehouse_id)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        warehouse_id = self.kwargs.get('warehouse_id')
        if warehouse_id:
            context['warehouse'] = get_object_or_404(Warehouse, pk=warehouse_id)
        return context

    def form_valid(self, form):
        warehouse_id = self.kwargs.get('warehouse_id')
        warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
        product = form.cleaned_data['product']
        quantity = form.cleaned_data['quantity']
        
        # Check if product already exists in warehouse
        try:
            existing_item = WarehouseProduct.objects.get(
                warehouse=warehouse,
                product=product
            )
            # Update existing quantity
            existing_item.quantity += quantity
            existing_item.save()
            messages.success(self.request, 
                f"Updated {product.name} quantity in inventory (Added {quantity} units)")
            self.object = existing_item
        except WarehouseProduct.DoesNotExist:
            form.instance.warehouse = warehouse
            response = super().form_valid(form)
            messages.success(self.request, 
                f"Added {product.name} to inventory ({quantity} units)")
            return response
            
        return redirect(self.get_success_url())

    def get_success_url(self):
        warehouse_id = self.kwargs.get('warehouse_id')
        return reverse('warehouse_detail', kwargs={'pk': warehouse_id})
    
    

################## Clients ##################    
from django.views import View
from django.http import HttpResponse
import csv

class ClientExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="clients_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Name', 
            'Address', 
            'Phone', 
            'Email', 
            'Created At',
            'Updated At'
        ])
        
        for client in Client.objects.all().order_by('name'):
            writer.writerow([
                client.name,
                client.address,
                client.phone,
                client.email or '',
                client.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                client.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        return response

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'manager/clients/list.html'
    context_object_name = 'clients'
    paginate_by = 20

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'manager/clients/create.html'
    success_url = reverse_lazy('client_list')

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'manager/clients/update.html'
    success_url = reverse_lazy('client_list')

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'manager/clients/detail.html'
    
    
    
    















































from django.core.exceptions import PermissionDenied
class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'manager/invoices/create.html'
    success_url = reverse_lazy('invoice_list')
    
    ALLOWED_USERS = ['yousef', 'hany']

    def dispatch(self, request, *args, **kwargs):
        if request.user.username.lower() not in [u.lower() for u in self.ALLOWED_USERS]:
            raise PermissionDenied("You don't have permission to create invoices.")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['formset'] = InvoiceItemFormSet(
                self.request.POST, prefix='items'
            )
            context['installment_formset'] = InstallmentFormSet(
                self.request.POST, prefix='installments'
            )
        else:
            context['formset'] = InvoiceItemFormSet(
                queryset=InvoiceItem.objects.none(), prefix='items'
            )
            context['installment_formset'] = InstallmentFormSet(
                queryset=Installment.objects.none(), prefix='installments'
            )
            
        context['payment_info'] = {
            'subtotal': Decimal('0.00'),
            'tax_amount': Decimal('0.00'),
            'discount': Decimal('0.00'),
            'total': Decimal('0.00'),
            'amount_paid': Decimal('0.00'),
            'balance_due': Decimal('0.00')
        }
        
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        installment_formset = context['installment_formset']
        
        if formset.is_valid() and installment_formset.is_valid():
            # First save the base invoice to get a PK
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            
            # Save the invoice first to get a PK
            self.object.save()
            
            # Now handle the items
            instances = formset.save(commit=False)
            for item in instances:
                item.invoice = self.object
                item.save()
            formset.save_m2m()
            
            # Handle payment status
            status = form.cleaned_data['status']
            if status == Invoice.STATUS_PAID:
                self.object.amount_paid = self.object.total  # Now we can calculate total
                self.object.save()
            elif status == Invoice.STATUS_INSTALLMENT:
                self.object.is_installment = True
                self.object.amount_paid = Decimal('0.00')
                self.object.save()
                
                # Handle installments
                installments = installment_formset.save(commit=False)
                for installment in installments:
                    installment.invoice = self.object
                    installment.save()
                
                self.update_installment_plan()
            
            return super().form_valid(form)
        
        return self.render_to_response(self.get_context_data(form=form))

    def update_installment_plan(self):
        """Generate installment plan description"""
        installments = self.object.installments.order_by('due_date')
        if installments.exists():
            plan = [
                f"Installment {i}: {inst.amount} due {inst.due_date}"
                for i, inst in enumerate(installments, 1)
            ]
            self.object.installment_plan = "\n".join(plan)
            self.object.save()

    def get_success_url(self):
        return reverse('invoice_detail', kwargs={'pk': self.object.pk})







class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'manager/invoices/update.html'
    success_url = reverse_lazy('invoice_list')

    def get_form_kwargs(self):
        """Add the current user to form kwargs"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        """Add formsets and additional context data"""
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['formset'] = InvoiceItemFormSet(
                self.request.POST, 
                instance=self.object,
                prefix='items'
            )
            context['installment_formset'] = InstallmentFormSet(
                self.request.POST,
                instance=self.object,
                prefix='installments'
            )
        else:
            context['formset'] = InvoiceItemFormSet(
                instance=self.object,
                prefix='items'
            )
            context['installment_formset'] = InstallmentFormSet(
                instance=self.object,
                prefix='installments'
            )
            
        # Add payment information
        context['payment_info'] = {
            'subtotal': self.object.subtotal,
            'tax_amount': self.object.tax_amount,
            'discount': self.object.discount_amount,
            'total': self.object.total,
            'amount_paid': self.object.amount_paid,
            'balance_due': self.object.balance_due
        }
        
        return context

    def form_valid(self, form):
        """Handle form submission with validation for both formsets"""
        context = self.get_context_data()
        formset = context['formset']
        installment_formset = context['installment_formset']
        
        # Validate all forms
        if formset.is_valid() and installment_formset.is_valid():
            self.object = form.save(commit=False)
            
            # Handle payment status changes
            self.update_payment_status(form)
            
            # Save the invoice first
            self.object.save()
            
            # Save the formsets
            formset.instance = self.object
            formset.save()
            
            # Only save installments if invoice is in installment status
            if self.object.status == Invoice.STATUS_INSTALLMENT:
                installment_formset.instance = self.object
                installment_formset.save()
                
                # Update installment plan description
                self.update_installment_plan()
            else:
                # Clean up any existing installments if status changed
                self.object.installments.all().delete()
                self.object.is_installment = False
                self.object.save()

            return super().form_valid(form)
        
        return self.render_to_response(self.get_context_data(form=form))

    def update_payment_status(self, form):
        """Handle payment status changes and amount tracking"""
        new_status = form.cleaned_data['status']
        
        # If changing to paid, mark full amount as paid
        if new_status == Invoice.STATUS_PAID:
            self.object.amount_paid = self.object.total
        
        # If changing from paid to another status, reset amount paid
        elif self.object.status == Invoice.STATUS_PAID and new_status != Invoice.STATUS_PAID:
            self.object.amount_paid = Decimal('0.00')
        
        # If changing to installment, initialize payment tracking
        elif new_status == Invoice.STATUS_INSTALLMENT:
            self.object.is_installment = True
            if self.object.amount_paid >= self.object.total:
                self.object.amount_paid = Decimal('0.00')

    def update_installment_plan(self):
        """Generate a description of the installment plan"""
        installments = self.object.installments.order_by('due_date')
        if installments.exists():
            plan = []
            for i, installment in enumerate(installments, 1):
                status = "Paid" if installment.is_paid else "Pending"
                plan.append(
                    f"Installment {i}: {installment.amount} due {installment.due_date} ({status})"
                )
            self.object.installment_plan = "\n".join(plan)
            self.object.save()

    def get_success_url(self):
        """Redirect to detail view after successful update"""
        return reverse('invoice_detail', kwargs={'pk': self.object.pk})





































from django.views.generic import ListView
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from decimal import Decimal

class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'manager/invoices/list.html'
    context_object_name = 'invoices'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('client', 'assigned_to')
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by date range if provided
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(date_created__gte=date_from)
        if date_to:
            queryset = queryset.filter(date_created__lte=date_to)
            
        return queryset.order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Add today to context for overdue comparison
        context['today'] = today
        
        # Add filter parameters to context
        context['status_choices'] = Invoice.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        
        # Calculate summary statistics
        total_amount = Decimal('0')
        paid_amount = Decimal('0')
        overdue_count = 0
        
        for invoice in context['invoices']:
            invoice_total = invoice.total  # Using the property
            total_amount += invoice_total
            
            if invoice.status == 'paid':
                paid_amount += invoice_total
                
            if invoice.status != 'paid' and invoice.date_due < today:
                overdue_count += 1
        
        context['total_amount'] = total_amount
        context['paid_amount'] = paid_amount
        context['overdue_count'] = overdue_count
        
        return context
    
    
    
class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'manager/invoices/detail.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        return context
    
    
    
    
    
class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'manager/invoices/update.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = InvoiceItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = InvoiceItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('invoice_detail', kwargs={'pk': self.object.pk})
    
    
    
    
    
    
class WarehouseProductUpdateView(UpdateView):
    model = WarehouseProduct
    form_class = WarehouseProductFormUpdate
    template_name = 'manager/warehouseproduct/update.html'

    def get_success_url(self):
        return reverse('warehouse_detail', kwargs={'pk': self.object.warehouse.pk})

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Updated quantity for {self.object.product.name} in {self.object.warehouse.name} to {form.cleaned_data['quantity']}"
        )
        return super().form_valid(form)
    
    
    
    
class MarkInstallmentPaidView(LoginRequiredMixin, View):
    def post(self, request, pk):
        installment = get_object_or_404(Installment, pk=pk)
        
        if not installment.is_paid:
            installment.is_paid = True
            installment.payment_date = timezone.now().date()
            installment.save()
            
            # Update invoice amount paid
            invoice = installment.invoice
            invoice.amount_paid += installment.amount
            if invoice.amount_paid >= invoice.total:
                invoice.status = 'paid'
            invoice.save()
            
            return JsonResponse({'status': 'success'})
        
        return JsonResponse({'status': 'error', 'message': 'Installment already paid'})
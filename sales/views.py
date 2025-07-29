from django.shortcuts import render, redirect, get_object_or_404
from manager.models import Product
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DetailView, ListView


#################################### Products ####################################





class HomeView(ListView):
    model = Product
    template_name = 'sales/home.html'  
    context_object_name = 'products'

# Dashboard
def All_Dash(request):
    return render(request,"sales\products\All_products.html",{'product':Product.objects.all()})

def Moving_dashboard(request):
    return render(request,"sales\products\moving_head.html",{'product':Product.objects.all()})


def Led_par_dashboard(request):
    return render(request,"sales\products\led_par.html",{'product':Product.objects.all()})

def Smoke_dashboard(request):
    return render(request,"sales\products\smoke.html",{'product':Product.objects.all()})

def Controlls_dashboard(request):
    return render(request,"sales\products\controlls.html",{'product':Product.objects.all()})

def Laser_Beam_dashboard(request):
    return render(request,"sales\products\laser_beam.html",{'product':Product.objects.all()})

def Lamps_dashboard(request):
    return render(request,"sales\products\lamps.html",{'product':Product.objects.all()})

def Truss_dashboard(request):
    return render(request,"sales/products/truss.html",{'product':Product.objects.all()})
    # return render(request,"sales.html",{'product':Product.objects.all()})

def Led_Screens_dashboard(request):
    return render(request,"sales\products\led_screens.html",{'product':Product.objects.all()})

def Accessories_dashboard(request):
    return render(request,"sales\products/accessories.html",{'product':Product.objects.all()})

def dashboard(request):
    return render(request,"sales\products\led_screens.html",{'product':Product.objects.all()})


def product_details_copy(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    all_products = Product.objects.all()
    context = {
        'product': product,
        'all_products': all_products,
    }
    return render(request, "sales/products/product_details_copy.html", context)

def About_us(request):
    return render(request,"sales/About_us.html",{'product':Product.objects.all()})

def contact(request):
    return render(request,"sales/contact.html",{'product':Product.objects.all()})

def services(request):
    return render(request,"sales/services.html",{'product':Product.objects.all()})


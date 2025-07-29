from django.urls import path,include
from . import views,models
from .views import (
    HomeView,product_details_copy,
)
urlpatterns=[
    path('', HomeView.as_view(), name='Home'),
    path('All_products/', views.All_Dash , name='All_products'),    
    path('Moving_dashboard/', views.Moving_dashboard , name='Moving_dashboard'),
    path('Led_par_dashboard/', views.Led_par_dashboard , name='Led_par_dashboard'),
    path('Smoke_dashboard/', views.Smoke_dashboard , name='Smoke_dashboard'),
    path('Controlls_dashboard/', views.Controlls_dashboard , name='Controlls_dashboard'),
    path('Laser_Beam_dashboard/', views.Laser_Beam_dashboard , name='Laser_Beam_dashboard'),
    path('Lamps_dashboard/', views.Lamps_dashboard , name='Lamps_dashboard'),
    path('Truss_dashboard/', views.Truss_dashboard , name='Truss_dashboard'),
    path('Led_Screens_dashboard/', views.Led_Screens_dashboard , name='Led_Screens_dashboard'),
    path('Accessories_dashboard/', views.Accessories_dashboard , name='Accessories_dashboard'),
    path('services/', views.services , name='services'),
    path('contact/', views.contact , name='contact'),
    path('About_us/', views.About_us , name='About_us'),
    path('show_product/<int:product_id>/', views.product_details_copy, name='product_details_copy'),

]
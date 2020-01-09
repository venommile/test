from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from ecomapp.views import *

urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    path('change_item_qty/', change_item_qty, name='change_item_qty'),
    path('category/<str:category_slug>', CategoryView.as_view(), name='category_detail'),
    path('remove_from_cart/', RemoveFromCart.as_view(), name='remove_from_cart'),
    path('add_to_cart/', AddToCart.as_view(), name='add_to_cart'),
    path('product/<str:product_slug>', ProductView.as_view(), name='product_detail'),
    path('cart/', Cart.as_view(), name='cart'),
    path('checkout/', Checkout.as_view(), name='checkout'),
    path('order/', order_create_view, name='create_order'),
    path('make_order/', make_order_view, name='make_order'),
    path('thank_you/', TemplateView.as_view(template_name='ecomapp/thank_you.html'), name='thank_you'),
    path('account/', account_view, name='account'),
    path('registration/', registration_view, name='registration'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('base')), name='logout'),
]

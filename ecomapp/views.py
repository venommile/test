# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import login, authenticate
from ecomapp.forms import OrderForm, RegistrationForm, LoginForm
from ecomapp.models import Category, Product, CartItem, Cart, Order
from django.views.generic import View
from django.contrib.auth.models import User
from ecomapp.utilits import *
from django.db.models import Q


# запилить нормальный DetailView и Base View
# Объединить base_view,product_view,category_view в Base
# def base_view(request):
# 	cart=get_cart(request)
# 	categories = Category.objects.all()
# 	products = Product.objects.all()
# 	context = {
# 		'categories': categories,
# 		'products': products,
# 		'cart': cart
# 	}
# 	return render(request, 'ecomapp/base.html', context)


class BaseView(BaseMixin, View):
    template = 'ecomapp/base.html'

    # доработать!!!!!!!!!!!!!!
    def view_object_function(*args, **kwargs):
        products = Product.objects.all()
        try:
            search_query = args[-1].GET.get('search', '')# -1 элемент - запрос Get
        except:
            pass
        if search_query:
            products = Product.objects.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        print(products)
        if not products:
            products = Product.objects.all()#костыль ...


        # Do products_for corusea
        new_context = {'products': products,}
        return new_context
    # product = Product.objects.get(slug=product_slug)


class ProductView(BaseMixin, View):
    template = 'ecomapp/product.html'

    def view_object_function(new_details, *args, **kwargs):
        product_slug = new_details.kwargs['product_slug']
        product = Product.objects.get(slug=product_slug)
        new_context = {'product': product}
        return new_context


# def product_view(request, product_slug):
# 	cart=get_cart(request)
# 	product = Product.objects.get(slug=product_slug)
# 	categories = Category.objects.all()
# 	context = {
# 		'product': product,
# 		'categories': categories,
# 		'cart': cart,
# 	}
# 	return render(request, 'ecomapp/product.html', context)
class CategoryView(BaseMixin, View):
    template = 'ecomapp/category.html'

    def view_object_function(new_details, request, *args, **kwargs):
        category_slug = new_details.kwargs['category_slug']
        category = Category.objects.get(slug=category_slug)
        products_of_category = Product.objects.filter(category=category)
        # price_filter_type = request.GET.get('price_filter_type')
        new_context = {'products_of_category': products_of_category, 'category': category, }
        return new_context


# def category_view(request, category_slug):
# 	cart=get_cart(request)
# 	category = Category.objects.get(slug=category_slug)
# 	price_filter_type = request.GET.get('price_filter_type')
# 	for i in range(100):
# 		print(price_filter_type)
# 	products_of_category = Product.objects.filter(category=category)
# 	categories = Category.objects.all()
# 	context = {
# 		'category': category,
# 		'products_of_category': products_of_category,
# 		'cart': cart,
# 		'categories': categories,
# 	}
# 	return render(request, 'ecomapp/category.html', context)


# объединить в Cart
class Cart(CartMixin, View):
    template = 'ecomapp/cart.html'


# def cart_view(request):
# 	cart=get_cart(request)
# 	categories = Category.objects.all()
# 	context = {
# 		'cart': cart,
# 		'categories': categories
# 	}
# 	return render(request, 'ecomapp/cart.html', context)
class Checkout(CartMixin, View):
    template = 'ecomapp/checkout.html'


# def checkout_view(request):
# 	cart=get_cart(request)
# 	categories = Category.objects.all()
# 	context = {
# 		'cart': cart,
# 		'categories': categories
# 	}
# 	return render(request, 'ecomapp/checkout.html', context)
# Объединить add_to_cart_view,remove_from_cart_view,
# change_item_qty,checkout_view в Cart_actions'
class AddToCart(CartActionsMixin, View):
    def action(garbage, product_slug, cart):
        cart.add_to_cart(product_slug)
        reload_cart_cost(cart)
        return cart


# def add_to_cart_view(request):
# 	cart=get_cart(request)
# 	product_slug=request.GET.get('product_slug')
# 	#product = Product.objects.get(slug = product_slug)
# 	cart.add_to_cart(product_slug)
# 	reload_cart_cost(cart)
# 	return JsonResponse({'cart_total': cart.items.count(),
# 		'cart_total_price': cart.cart_total,})
class RemoveFromCart(CartActionsMixin, View):
    def action(garbage, product_slug, cart):
        cart.remove_from_cart(product_slug)
        reload_cart_cost(cart)
        return cart


# def remove_from_cart_view(request):
# 	cart=get_cart(request)

# 	product_slug=request.GET.get('product_slug')
# 	cart.remove_from_cart(product_slug)
# 	reload_cart_cost(cart)
# 	return JsonResponse({'cart_total': cart.items.count(),
# 		'cart_total_price': cart.cart_total,})
def change_item_qty(request):
    cart = get_cart(request)
    qty = request.GET.get('qty')
    item_id = request.GET.get('item_id')
    cart.change_qty(qty, item_id)
    cart_item = CartItem.objects.get(id=int(item_id))
    return JsonResponse(
        {'cart_total': cart.items.count(),
         'item_total': cart_item.item_total,
         'cart_total_price': cart.cart_total})


def order_create_view(request):
    cart = get_cart(request)
    form = OrderForm(request.POST or None)
    categories = Category.objects.all()
    context = {
        'form': form,
        'cart': cart,
        'categories': categories
    }
    return render(request, 'ecomapp/order.html', context)


def make_order_view(request):
    cart = get_cart(request)

    form = OrderForm(request.POST or None)
    categories = Category.objects.all()

    if form.is_valid():
        name = form.cleaned_data['name']
        last_name = form.cleaned_data['last_name']
        phone = form.cleaned_data['phone']
        buying_type = form.cleaned_data['buying_type']
        address = form.cleaned_data['address']
        comments = form.cleaned_data['comments']
        new_order = Order.objects.create(
            user=request.user,
            items=cart,
            total=cart.cart_total,
            first_name=name,
            last_name=last_name,
            phone=phone,
            address=address,
            buying_type=buying_type,
            comments=comments
        )

        del request.session['cart_id']
        del request.session['total']

        return HttpResponseRedirect(reverse('thank_you'))
    return render(request, 'ecomapp/order.html', {'categories': categories})


def account_view(request):
    try:
        order = Order.objects.filter(user=request.user).order_by('-id')

    except:
        return HttpResponseRedirect(reverse('registration'))

    categories = Category.objects.all()
    context = {
        'order': order,
        'categories': categories
    }

    return render(request, 'ecomapp/account.html', context)


def registration_view(request):
    form = RegistrationForm(request.POST or None)
    categories = Category.objects.all()

    if form.is_valid():
        new_user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        new_user.username = username
        new_user.set_password(password)
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.email = email
        new_user.save()
        login_user = authenticate(username=username, password=password)

        if login_user:
            login(request, login_user)
            return HttpResponseRedirect(reverse('base'))
    context = {
        'form': form,
        'categories': categories
    }
    return render(request, 'ecomapp/registration.html', context)


def login_view(request):
    form = LoginForm(request.POST or None)
    categories = Category.objects.all()
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        login_user = authenticate(username=username, password=password)
        if login_user:
            login(request, login_user)
            return HttpResponseRedirect(reverse('base'))
    context = {
        'form': form,
        'categories': categories
    }
    return render(request, 'ecomapp/login.html', context)

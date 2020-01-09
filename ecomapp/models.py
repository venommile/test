# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
import pytils
from time import time
import notifications
from django.contrib.auth.models import User
from PIL import Image
import os
import glob
from django.utils import timezone


def gen_slug(cls):
    # соднание уникального  слага,принимает объект,и из его название делает ссылку на товар

    title = str(cls.title)
    new_slug = pytils.translit.translify(slugify(title, allow_unicode=True))

    for i in cls.__class__.objects.all():
        if new_slug == i.slug:
            return new_slug + '-' + str(int(time()))
    else:
        return new_slug


class Category(models.Model):
    # класс категорий
    title = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            self.slug = gen_slug(self)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'category_slug': self.slug})


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


def image_folder(instance, filename):
    # функция для загрузки изображений.Принимает товар,к которому должен быть загружен фото товара
    #  и бывшое называние файла(для подлучения расширения)Возвращает новое называние фото
    filename = instance.slug + '.' + filename.split('.')[1]
    return "{0}/{1}".format(instance.slug, filename)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, models.CASCADE)
    title = models.CharField(max_length=120)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to=image_folder)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'product_slug': self.slug})


# def product_available_notification(sender, instance, *args, **kwargs):
# 	if instance.available:
# 		await_for_notify = [notification for notification in MiddlwareNotification.objects.filter(
# 			product=instance)]
# 		for notification in await_for_notify:
# 			notify.send(
# 				instance,
# 				recipient=[notification.user_name],
# 				verb='Уважаемый {0}! {1}, который Вы ждете, поступил'.format(
# 					notification.user_name.username,
# 					instance.title),
# 				description=instance.slug
# 				)
# 			notification.delete()


# post_save.connect(product_available_notification, sender=Product)	


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    item_total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return "Cart item for product {0}".format(self.product.title)


class Cart(models.Model):
    items = models.ManyToManyField(CartItem, blank=True)
    cart_total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def add_to_cart(self, product_slug):
        cart = self
        product = Product.objects.get(slug=product_slug)
        new_item, _ = CartItem.objects.get_or_create(product=product)
        for item in cart.items.all():
            if str(product_slug) == str(item.product.slug):
                new_item.qty += 1
                # for i in range(10):
                #     print(new_item.qty)
                new_item.item_total = int(new_item.qty) * Decimal(new_item.product.price)
                new_item.save()
                cart.save()
                break

        else:
            new_item.item_total = Decimal(new_item.product.price)
            new_item.save()
            cart.items.add(new_item)
            cart.save()

    def remove_from_cart(self, product_slug):

        cart = self
        product = Product.objects.get(slug=product_slug)
        new_item, _ = CartItem.objects.get_or_create(product=product)

        for cart_item in cart.items.all():
            if cart_item.product == product:
                cart.items.remove(cart_item)
                new_item.delete()
                cart.save()

    def change_qty(self, qty, item_id):
        cart = self

        cart_item = CartItem.objects.get(id=int(item_id))
        cart_item.qty = int(qty)
        cart_item.item_total = int(qty) * Decimal(cart_item.product.price)
        cart_item.save()
        # переделать в отдельную функцию
        new_cart_total = 0.00
        for item in cart.items.all():
            new_cart_total += float(item.item_total)
        cart.cart_total = new_cart_total
        cart.save()

    def __str__(self):
        return str(self.id)


ORDER_STATUS_CHOICES = (
    ('Принят в обработку', 'Принят в обработку'),
    ('Выполняется', 'Выполняется'),
    ('Оплачен', 'Оплачен')
)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ForeignKey(Cart, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    buying_type = models.CharField(max_length=40, choices=(('Самовывоз', 'Самовывоз'),
                                                           ('Доставка', 'Доставка')), default='Самовывоз')
    date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField()
    status = models.CharField(max_length=100, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_CHOICES[0][0])

    def __str__(self):
        return "Заказ №{0}".format(str(self.id))

# class MiddlwareNotification(models.Model):

# 	user_name = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
# 	product = models.ForeignKey(Product,on_delete=models.CASCADE)
# 	is_notified = models.BooleanField(default=False)

# 	def __str__(self):
# 		return "Нотификация для пользователя {0} о поступлении товара {1}".format(
# 	   	self.user_name.username, 
# 	   	self.product.title
# 	   	)

from django.views.generic import View
from ecomapp.models import *
from .views import *


def get_cart(request):
    try:
        cart_id = request.session['cart_id']
        cart = Cart.objects.get(id=cart_id)
        request.session['total'] = cart.items.count()
    except:
        cart = Cart()
        cart.save()
        cart_id = cart.id
        request.session['cart_id'] = cart_id
        cart = Cart.objects.get(id=cart_id)
    finally:
        return cart


def reload_cart_cost(cart):
    new_cart_total = 0.00
    for item in cart.items.all():
        new_cart_total += float(item.item_total)
    cart.cart_total = new_cart_total
    cart.save()
    return cart


class BaseMixin:
    template = None
    obj = None
    object_slug = None

    def get(self, request, *args, **kwargs):
        new_details = kwargs
        cart = get_cart(request)
        categories = Category.objects.all()

        context = {
            'categories': categories,
            'cart': cart
        }
        new_context = self.view_object_function(new_details, request)
        context.update(new_context)

        return render(request, self.__class__.template, context)
    # добавить инит чтобы убрать получение продукта и слага


class CartMixin:
    template = None

    def get(self, request):
        cart = get_cart(request)
        categories = Category.objects.all()
        context = {
            'cart': cart,
            'categories': categories
        }
        return render(request, self.__class__.template, context)


class CartActionsMixin:
    obj_slug = None
    cart = Cart()

    def get(self, request, *args, **kwargs):
        cart = get_cart(request)
        product_slug = request.GET.get('product_slug')
        print(self.__class__.__dict__)
        cart = self.action(product_slug, cart)
        return JsonResponse({'cart_total': cart.items.count(),
                             'cart_total_price': cart.cart_total, })

# def view_object_function(*args,**kwa):
# 	pass
# 	cart=get_cart(request)
# 	product_slug=request.GET.get('product_slug')
# 	#product = Product.objects.get(slug = product_slug)
# 	cart.add_to_cart(product_slug)
# 	reload_cart_cost(cart)
# 	return JsonResponse({'cart_total': cart.items.count(),
# 		'cart_total_price': cart.cart_total,})
# class CartActionMixin:


# 	def get(self,request):
# 		cart=get_cart(request)
# 		name=str(self.__class__.__name__)
# 		product_slug = request.GET.get('product_slug')
# 		product = Product.objects.get(slug=product_slug)

# 		action=name.lower()

# 		print(action,'dddddddddddddddddddddddddddddddddddddddddd')
# 		cart.action(product.slug)
# 		new_cart_total = 0.00
# 		for item in cart.items.all():
# 			new_cart_total += float(item.item_total)
# 		cart.cart_total = new_cart_total
# 		cart.save()
# 		return JsonResponse({'cart_total': cart.items.count(), 'cart_total_price': cart.cart_total})

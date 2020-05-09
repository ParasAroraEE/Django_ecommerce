from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder
# Create your views here.


def store(request):
    # 14
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    # this is utils.py
    # if request.user.is_authenticated:
    #     customer = request.user.customer
    #     order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #     items = order.orderitem_set.all()
    #     cartItems = order.get_cart_item
    # else:
    #     # 11
    #     cookieData = cookieCart(request)
    #     cartItems = cookieData['cartItems']
    #     order = cookieData['order']
    #     items = cookieData['items']
    #     # 11 end

    #     # this all in utils.py so no use
    #     # items = []
    #     # order = {'get_cart_total': 0, 'get_cart_item': 0, 'shipping': False}
    #     # cartItems = order['get_cart_item']

    products = Product.objects.all()

    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    # 14
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    # this is utils.py
    # if request.user.is_authenticated:
    #     customer = request.user.customer
    #     order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #     items = order.orderitem_set.all()
    #     cartItems = order.get_cart_item
    # else:
    #     # 11
    #     cookieData = cookieCart(request)
    #     cartItems = cookieData['cartItems']
    #     order = cookieData['order']
    #     items = cookieData['items']
    #     # 11 end

    #     # this all in utils.py so no use
    #     # # 4
    #     # try:
    #     #     cart = json.loads(request.COOKIES['cart'])
    #     # except:
    #     #     cart = {}
    #     #     print('CART:', cart)
    #     # # 4 end

    #     # items = []
    #     # order = {'get_cart_total': 0, 'get_cart_item': 0, 'shipping': False}
    #     # cartItems = order['get_cart_item']

    #     # # 5
    #     # for i in cart:
    #     #     # 9
    #     #     try:
    #     #         # 9 end
    #     #         cartItems += cart[i]['quantity']
    #     #     # 5 end

    #     #     # 6
    #     #         product = Product.objects.get(id=i)
    #     #         total = (product.price * cart[i]['quantity'])

    #     #         order['get_cart_total'] += total
    #     #         order['get_cart_item'] += cart[i]['quantity']
    #     #     # 6 end

    #     #     # 7
    #     #         item = {
    #     #             'id': product.id,
    #     #             'product': {'id': product.id, 'name': product.name, 'price': product.price, 'imageURL': product.imageURL},
    #     #             'quantity': cart[i]['quantity'],
    #     #             'digital': product.digital,
    #     #             'get_total': total,
    #     #         }
    #     #         items.append(item)
    #     #     # 7 end
    #     #     # 8
    #     #         if product.digital == False:
    #     #             order['shipping'] = True
    #     #     # 8 end

    #     #     # 9
    #     #     except:
    #     #         pass
    #     #     # 9end

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    # 14
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    # this is utils.py
    # if request.user.is_authenticated:
    #     customer = request.user.customer
    #     order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #     items = order.orderitem_set.all()
    #     cartItems = order.get_cart_item
    # else:
    #     # 11
    #     cookieData = cookieCart(request)
    #     cartItems = cookieData['cartItems']
    #     order = cookieData['order']
    #     items = cookieData['items']
    #     # 11 end

    #     # this all in utils.py so no use
    #     # items = []
    #     # order = {'get_cart_total': 0, 'get_cart_item': 0, 'shipping': False}
    #     # cartItems = order['get_cart_item']

    context = {'items': items, 'order': order, 'cartItems': cartItems}

    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)


def processOrder(request):

    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    # 16
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)

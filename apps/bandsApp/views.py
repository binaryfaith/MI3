# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import *
import re
import bcrypt
from django.utils import timezone
from django.contrib import messages

# Display home page

def index (request) :  
    context = {}

    __setActiveOrder__(request)
    
    context = __addNavBarDetailsToContext__(request)

    # Get artists featured items
    artistFeaturedBands = Band.objects.filter(vendor__vendorType='artist', isFeatured='True')
    
    print artistFeaturedBands

    # Get exclusive featured items
    exclusiveFeaturedBands = Band.objects.filter(vendor__vendorType='exclusive', isFeatured='True')
    print exclusiveFeaturedBands

    # Get exclusive featured items    
    charityFeaturedBands = Band.objects.filter(vendor__vendorType='charity', isFeatured='True')
    print charityFeaturedBands

    context['featuredArtist'] = artistFeaturedBands
    context['featuredExclusive'] = exclusiveFeaturedBands
    context['featuredCharity'] = charityFeaturedBands

    print "context: ", context
    return render(request, 'bandsApp/index.html', context)

# Display all the bands by local artists. 
def artists (request) :  
    context = {}
    context = __addNavBarDetailsToContext__(request)
    bands = Band.objects.filter(vendor__vendorType='artist')
    print bands
    context['bands'] = bands
    context['type'] = 'artist'
    return render(request, 'bandsApp/vendorBands.html', context)

# Display all the bands by exclusive brands. 
def exclusives (request) :  
    context = {}
    context = __addNavBarDetailsToContext__(request)
    bands = Band.objects.filter(vendor__vendorType='exclusive')
    print bands
    context['bands'] = bands
    context['type'] = 'exclusive'
    return render(request, 'bandsApp/vendorBands.html', context)

# Display all the bands by charities. 
def cause (request) :  
    context = {}
    context = __addNavBarDetailsToContext__(request)

    bands = Band.objects.filter(vendor__vendorType='charity')
    print bands
    context['bands'] = bands
    context['type'] = 'charity'
    return render(request, 'bandsApp/vendorBands.html', context)

# Display the search results 
def search (request) :  
    context = {}
    return render(request, 'bandsApp/searchResults.html', context)

# Display shopping cart 
def showCart (request) :  
    context = {}
    order = __isActiveOrder__(request)
    if (order) :
        context = __addNavBarDetailsToContext__(request)

        bands = OrderDetails.objects.filter(order=order)
        totalPrice = 0
        for band in bands :
            totalPrice += (band.band.price * band.qty)
        request.session['totalPrice'] = totalPrice
        user = __isLoggedIn__(request)
        
        context['bands'] = bands
        context['totalPrice']= totalPrice
        context['orderId'] = request.session['order_id']
        
        return render(request, 'bandsApp/shoppingCart.html', context)
    else :
        return redirect(reverse('bands:home'))

# Edit shopping cart. some problem here. i need to fix it 
def editCart (request, orderId) :  
    context = {'orderId':orderId}
    # Edit the order table entry and redirect to showCart 
    return redirect(reverse('bands:cart'))

def vendorDetails(request, vendorId) :
    context = {}
    context = __addNavBarDetailsToContext__(request)
    # Get the vendor 
    vendor = Vendor.objects.get(pk=vendorId) 
    print vendor
    # Get all bands by this vendor
    bands = Band.objects.filter(vendor=vendor)

    context['vendor'] = vendor
    context['bands']  = bands
    return render(request, 'bandsApp/vendorDetails.html', context)

def checkout(request):
    if request.method == "POST":
        if not 'logged_in_user' in request.session :
            return redirect(reverse('bands:register_login'))
        else :
            return redirect(reverse('bands:checkoutDetails'))

def register_login(request) :
    context = __addNavBarDetailsToContext__(request)
    return render(request, 'bandsApp/register_login.html', context)

def checkoutDetails(request) :

    conext = {}
    context = __addNavBarDetailsToContext__(request)

    user = __isLoggedIn__(request)
    credit_card = user.creditCard
    print credit_card
    shipping_address = user.shippingAddress()
    billing_address = user.billingAddress()
    print shipping_address
    print billing_address
    # print request.session['totalPrice']

    # If order is placed then show thank you message
    order  = __isActiveOrder__(request)

    context['shipping_address'] = shipping_address
    context['credit_card'] = credit_card
    context['billing_address'] = billing_address

    if not order:
        context['orderStatus'] = 'received'
        

    print context
    return render(request, 'bandsApp/checkoutDetails.html', context)

def confirmCheckout(request):
    # Update order status
    order = Order.objects.get(pk=int(request.session['order_id'])) 
    order.status = 'received'
    order.save()
    del request.session['order_id']
    del request.session['totalPrice']
    print "chnaged order status"
    
    return redirect(reverse('bands:checkoutDetails'))

def register(request) :
    error = False
    context = {}
    print "in register"

    if request.method == "POST":
        print request.POST

        returnVal = User.objects.register(request.POST)
        if returnVal['user'] :
            request.session['logged_in_user'] = returnVal['user'].id
            print "logged in user: ",request.session['logged_in_user']
            return redirect(reverse('bands:home'))
        else :
            for error in returnVal['errors'] :
                print error
                messages.error(request,error['message'],extra_tags=error['extra_tags'])
            return redirect(reverse("bands:register_login"))

def login (request):
    if request.method == "POST":
        returnVal = User.objects.login(request.POST)
        if returnVal['user']:
            request.session['logged_in_user'] = returnVal['user'].id
            if 'order_id' in request.session :
                order = Order.objects.get(pk=request.session['order_id'])
                order.user = returnVal['user']
            print "logged in user: ",request.session['logged_in_user']
            return redirect(reverse('bands:home'))
        else:
            for error in returnVal['errors'] :
                print error
                messages.error(request,error['message'],extra_tags=error['extra_tags'])
            return redirect(reverse('bands:login_register'))

def logout (request) :
    del request.session['logged_in_user']
    return redirect(reverse('bands:home'))

def bandDetails(request, bandId):
    context = {}
    context = __addNavBarDetailsToContext__(request)
    print "bandDetails ", bandId
    band = Band.objects.get(pk=bandId)
    context['band'] = band
    print band
    
    return render(request, 'bandsApp/bandDetails.html', context)

def addToCart(request, bandId) :
    order = None
    band = None
    print "bandId", bandId
    print "inside addToCart"
    if request.method == "POST" :
        print "post ", request.POST
        qty = float(request.POST['qty'])
        band = Band.objects.get(pk=bandId)
        order = __isActiveOrder__(request)
        session_key = request.session.session_key
        if not order:
            print "creating new order"
            user = __isLoggedIn__(request)
            order = Order.objects.create(user=user, session_id=session_key, created_at=timezone.now(), updated_at = timezone.now())
            request.session['order_id'] = order.id
        try :
            details = OrderDetails.objects.get(order=order, band=band)
            details.qty += 1
            details.save()
        except OrderDetails.DoesNotExist :
            etails = OrderDetails.objects.create(order=order, band=band, qty = qty, totalPrice = band.price * qty)
        print "added to cart"

    return redirect(reverse('bands:showCart'))

def updateQty(request, bandId) :
    if request.method == "POST":
        print bandId
        print request.POST
        band = Band.objects.get(pk=bandId)
        print band
        order = __isActiveOrder__(request)
        print order
        details = OrderDetails.objects.get(order=order, band=band)
        # print "qty before ", details.qty
        details.qty = int(request.POST['qty'])
        details.totalPrice = int(request.POST['qty']) * band.price
        details.save()
    return redirect(reverse('bands:showCart'))

def deleteBand(request, bandId) :
    band = Band.objects.get(pk=bandId)
    print band
    order = __isActiveOrder__(request)
    print order
    details = OrderDetails.objects.get(order=order, band=band)
    
    details.delete()
    print "deleted band"
    orderDetails = order.details.all()
    print details
    if (len(orderDetails) == 0) :
        order.delete()
        del request.session['order_id']
        del request.session['totalPrice']
        return redirect(reverse('bands:home'))
    else:
        return redirect(reverse('bands:showCart'))

# @background(schedule=60)
# def deleteGhostOrders():
#     # lookup user by id and send them a message
  

def __isLoggedIn__(request):
    if 'logged_in_user' in request.session:
        user = User.objects.get(pk=int(request.session['logged_in_user']))
        return user
    else :
        return None

def __isActiveOrder__(request) :
    order = None
    if 'order_id' in request.session :
        try :
            order  = Order.objects.get(pk=int(request.session['order_id'])) 
        except Order.DoesNotExist :
            del request.session['order_id']
            del request.session['totalPrice']
        return order 
    else :
        return None

def __setActiveOrder__(request) :

    user = __isLoggedIn__(request)
    if (user):
        order = Order.objects.filter(user=user, status="active")
    else :
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key   
        print session_key
        # Find if the session key exists in orders db 
        order = Order.objects.filter(session_id=session_key, status='active')
    
    if (len(order) > 0) :
        print "__setActiveOrder__ ", order
        request.session['order_id'] = order[0].id

def __getNumCartItems__(request) :
    numCartItems = 0
    order = __isActiveOrder__(request)
    
    if (order) :
        bands = OrderDetails.objects.filter(order=order)
        for band in bands:
            numCartItems += band.qty

    print "__getNumCartItems__ ",numCartItems
    return numCartItems

def __addNavBarDetailsToContext__(request) :

    context = {}
    numCartItems = __getNumCartItems__(request)
    print "__addNavBarDetailsToContext__ numCartItems: ", numCartItems
    context['numCartItems'] = numCartItems

    user = __isLoggedIn__(request)
    if (user) :
        context['logged_in'] = True
        context['logText'] = user.name
    else :
        context['logged_in'] = False
        context['logText'] = 'Login'

    print "__addNavBarDetailsToContext__ context: ", context
    return context
    

       
        





   





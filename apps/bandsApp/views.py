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
    bands = Band.objects.filter(vendor__vendorType='artist')
    print bands
    context = {'bands':bands, 'type':'artist'}
    return render(request, 'bandsApp/vendorBands.html', context)

# Display all the bands by exclusive brands. 
def exclusives (request) :  
    bands = Band.objects.filter(vendor__vendorType='exclusive')
    print bands
    context = {'bands':bands, 'type':'exclusive'}
    return render(request, 'bandsApp/vendorBands.html', context)

# Display all the bands by charities. 
def cause (request) :  
    bands = Band.objects.filter(vendor__vendorType='charity')
    print bands
    context = {'bands':bands, 'type':'charity'}
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
        context['totalItems'] = len(bands)
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
    
    # Get the vendor 
    vendor = Vendor.objects.get(pk=vendorId) # pk = primary key. You can put id instead of pk
    # Get all bands by this vendor
    bands = Band.objects.filter(vendor=vendor)

    context = {'vendor':vendor, 'bands':bands} 
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
    del equest.session['totalPrice']
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

def __isLoggedIn__(request):
    if 'logged_in_user' in request.session:
        user = User.objects.get(pk=int(request.session['logged_in_user']))
        return user
    else :
        return None

def __isActiveOrder__(request) :
    if 'order_id' in request.session :
         order  = Order.objects.get(pk=int(request.session['order_id'])) 
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
        numCartItems = len(bands)

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
    

       
        





   





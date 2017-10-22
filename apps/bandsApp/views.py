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
    
    numCartItems = 0
    context = {}

    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key   
    print session_key

    # Find if the session key exists in orders db 
    try :
        order = Order.objects.get(session_id=session_key)
        request.session['order_id'] = order.id
        bands = OrderDetails.objects.filter(order=order)
        numCartItems = len(bands)
        print numCartItems
    except Order.DoesNotExist :
        numCartItems = 0
    
    user = __isLoggedIn__(request)
    if (user) :
        context['logged_in'] = True
        context['logText'] = user.name
    else :
        context['logged_in'] = False
        context['logText'] = 'Login'
    
    # Get artists featured items
    artistFeaturedBands = Band.objects.filter(vendor__vendorType='artist', isFeatured='True')
    
    print artistFeaturedBands

    # Get exclusive featured items
    exclusiveFeaturedBands = Band.objects.filter(vendor__vendorType='exclusive', isFeatured='True')
    print exclusiveFeaturedBands

    # Get exclusive featured items    
    charityFeaturedBands = Band.objects.filter(vendor__vendorType='charity', isFeatured='True')
    print charityFeaturedBands

    context['numCartItems'] = numCartItems 
    context['featuredArtist'] = artistFeaturedBands
    context['featuredExclusive'] = exclusiveFeaturedBands
    context['featuredCharity'] = charityFeaturedBands
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
    
    order = Order.objects.get(pk=int(request.session['order_id']))
    bands = OrderDetails.objects.filter(order=order)
    totalPrice = 0
    for band in bands :
        totalPrice += (band.band.price * band.qty)
    request.session['totalPrice'] = totalPrice
    user = __isLoggedIn__(request)
    
    context = {'bands':bands, 'totalPrice':totalPrice, 'totalItems':len(bands), 'orderId': request.session['order_id']}
    if (user) :
        context['logged_in'] = True
        context['logText'] = user.name
    else :
        context['logged_in'] = False
        context['logText'] = 'Login'
    
    return render(request, 'bandsApp/shoppingCart.html', context)

# Edit shopping cart. some problem here. i need to fix it 
def editCart (request, orderId) :  
    context = {'orderId':orderId}
    # Edit the order table entry and redirect to showCart 
    return redirect(reverse('bands:cart'))

def vendorDetails(request, vendorId) :
    print "in vendor detials"
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
    return render(request, 'bandsApp/register_login.html', {})

def checkoutDetails(request) :
    user = __isLoggedIn__(request)
    credit_card = user.creditCard
    print credit_card
    shipping_address = user.shippingAddress()
    print shipping_address
    print request.session['totalPrice']
    context = {'shipping_address':shipping_address, 'credit_card':credit_card}
    return render(request, 'bandsApp/checkoutDetails.html', context)

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
    request.session.flush()
    return redirect(reverse('poke:home'))

def __isLoggedIn__(request):
    if 'logged_in_user' in request.session:
        user = User.objects.get(pk=int(request.session['logged_in_user']))
        return user
    else :
        return None




   





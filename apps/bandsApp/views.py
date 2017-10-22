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

    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key   
    print session_key

    # Find if the session key exists in orders db 
    try :
        order = Order.objects.get(session_id=session_key)
        request.session['order_id'] = order.id
        bands = order.bands.all()
        numCartItems = len(bands)
        print numCartItems
    except Order.DoesNotExist :
        numCartItems = 0
    
    # Get artists featured items
    artistFeaturedBands = Band.objects.filter(vendor__vendorType='artist', isFeatured='True')
    print artistFeaturedBands

    # Get exclusive featured items
    exclusiveFeaturedBands = Band.objects.filter(vendor__vendorType='exclusive', isFeatured='True')
    print exclusiveFeaturedBands

    # Get exclusive featured items    
    charityFeaturedBands = Band.objects.filter(vendor__vendorType='charity', isFeatured='True')
    print charityFeaturedBands

    context = {'numCartItems':numCartItems, 'featuredArtist':artistFeaturedBands, 'featuredExclusive':exclusiveFeaturedBands, 'featuredCharity':charityFeaturedBands}
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
def showCart (request, orderId) :  
    context = {'orderId':orderId}
    order = Order.objects.get(pk=orderId)
    bands = order.bands.all()
    totalPrice = 0
    for band in bands :
        totalPrice += band.price
    context = {'bands':bands, 'totalPrice':totalPrice}
    return render(request, 'bandsApp/shoppingCart.html', context)

# Edit shopping cart. some problem here. i need to fix it 
def editCart (request, orderId) :  
    context = {'orderId':orderId}
    # Edit the order table entry and redirect to showCart 
    return redirect(reverse('bands:cart'))




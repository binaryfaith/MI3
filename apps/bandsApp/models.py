# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

import bcrypt
import re

# Create your models here.
class UserManager(models.Manager) :
   

    def register(self,post):
        errorMsgs = []
        user = {}
        returnVal = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]')

        if post['name'] == "" :
            errorMsgs.append({'message': 'Name is required', 'extra_tags':"register"})
        elif len(post['name']) < 3 :
            errorMsgs.append({'message':'Name has to be minimum 3 characters long', 'extra_tags':"register"})

        if post['username'] == "" :
            errorMsgs.append({'message':'alias is required', 'extra_tags':"register"})
        elif len(post['username']) < 3 :
            errorMsgs.append({'message':'alias has to be minimum 3 characters long', 'extra_tags':"register"})

        if not post['email']:
		    error = {'message': 'Email is required', 'extra_tags': 'register'}
		    errorMsgs.append(error)
        elif not EMAIL_REGEX.match(post['email']):
			error = {'message': 'Invalid email address', 'extra_tags': 'register'}
			errorMsgs.append(error)
		
        if post['password'] == "" :
            errorMsgs.append({'message':'password is required', 'extra_tags':"register"})
        elif len(post['password']) < 8:
            errorMsgs.append({'message':'Password has to be mininum 8 characters long', 'extra_tags':"register"})
            print "password less than 8"      
        elif post['password'] != post['confirm_password'] :
            errorMsgs.append({'message':'Passwords do not match.', 'extra_tags':"register"})
            print "password mismatch"

        # if 'birth_date' not in post or post['birth_date'] == "":
		#     error = {'message': 'Please select birth date', 'extra_tags': 'register'}
		#     errorMsgs.append(error)
        # elif post['birth_date'] == "":
		# 	error = {'message': 'Invalid birth date', 'extra_tags': 'register'}
		# 	errorMsgs.append(error)

        try: 
            user = User.objects.get(email = post['email'])
            print "user: ", user
            errorMsgs.append({'message':'User with {} email already exists.'.format(post['email']), 'extra_tags':"register"})
            print "user exists"
            error = True
        except User.DoesNotExist:
            if (len(errorMsgs) == 0):
                hash1 = bcrypt.hashpw(post['password'].encode(), bcrypt.gensalt())
                user = User.objects.create(name=post['name'], username=post['username'], email=post['email'], password = hash1)
                print "added user"
                print "User does not exist"
                
        returnVal = {'user':user,'errors':errorMsgs}
        return returnVal

    def login (self, post) :
        errorMsgs = []
        user = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]')

        if post['login_email'] == "" :
            errorMsgs.append({'message':'username is required', 'extra_tags':"login"})
        if post['login_password'] == "" :
            errorMsgs.append({'message':'password is required', 'extra_tags':"login"})
        if not EMAIL_REGEX.match(post['login_email']) :
            errorMsgs.append({'message':'Invalid email', 'extra_tags':"login"})

        if (len(errorMsgs) == 0):
            try :
                user = User.objects.get(email = post['login_email'])
                print user
                print user.password
                # if bcrypt.checkpw(post['login_password'].encode(), user.password.encode()):
                if post['login_password'] == user.password:
                    print "login successful"
                else: 
                    print "password mismatch"
                    errorMsgs.append({'message':'Incorrect User Id or Password. Please try again', 'extra_tags':'login'})
                    user = {}
            except User.DoesNotExist:
                print "user not found"
                errorMsgs.append({'message':'Incorrect User Id or Password. Please try again', 'extra_tags':'login'})

        return {'user': user, 'errors': errorMsgs}

class User(models.Model):
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=8)
    email = models.EmailField()
    creditCard = models.CharField(max_length=16, null= True, blank=True)
    shipping_street_address = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255, null=True, blank=True)
    shipping_state = models.CharField(max_length=2, null=True, blank=True)
    shipping_country = models.CharField(max_length=50, null=True, blank=True)
    billing_street_address = models.CharField(max_length=255, null=True, blank=True)
    billing_city = models.CharField(max_length=255, null=True, blank=True)
    billing_state = models.CharField(max_length=2, null=True, blank=True)
    billing_country = models.CharField(max_length=50, null=True, blank=True)
  
    objects = UserManager()

    def shippingAddress(self):
        address = "{}\n{} {}\n {}".format(self.shipping_street_address, self.shipping_city, self.shipping_state, self.shipping_country)
        print address
        return address
    
    def billingAddress(self):
        address = "{}\n{} {}\n {}".format(self.billing_street_address, self.billing_city, self.billing_state, self.billing_country)
        print address
        return address

    def __str__(self):
        return "{} {} {} {}".format(self.name, self.username, self.email, self.password) 

class Vendor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField() # for contacting the vendor, about specific product questions
    vendorType = models.CharField(max_length=20) # localArtist, brand, charity
    bio = models.CharField(max_length=255)  # vendor short bio.
    imageUrl = models.CharField(max_length=255)


class Band(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    size = models.CharField(max_length=10)
    imageUrl = models.CharField(max_length=255)
    vendor = models.ForeignKey('Vendor', related_name = "bands")
    isFeatured = models.BooleanField(default=False)
    price = models.FloatField(default=0)
    def __str__(self):
        return "{} {}".format(self.name, self.vendor.name) 

class Order(models.Model):
    user = models.ForeignKey('user', related_name = "orders", null=True, blank=True)
    session_id = models.CharField(max_length=50,null=True, blank=True)
    status = models.CharField(max_length=10)
    created_at = models.DateTimeField('date created')
    updated_at = models.DateTimeField('date updated')
    
    def __str__(self):
        return "{} {}".format(self.id, self.status) 

class OrderDetails(models.Model):
    order = models.ForeignKey('Order', related_name = "details")
    band = models.ForeignKey('Band', related_name = "order_bands")
    qty = models.IntegerField()
    totalPrice = models.FloatField()
from django.conf.urls import include, url
from django.contrib import admin
from . import views

app_name = 'bands'
urlpatterns = [
    url(r'^$', views.index, name="home"),
    url(r'^registerLogin/$', views.register_login, name="register_login"),
    url(r'^register/$', views.register, name="register"),
    url(r'^login/$', views.login, name="login"),
    url(r'^logout/$', views.logout, name="logout"),
    url(r'^artists/$', views.artists, name="artists"),
    url(r'^exclusives/$', views.exclusives, name="exclusives"),
    url(r'^cause/$', views.cause, name="cause"),
    url(r'^search/$', views.search, name="search"),
    url(r'^cart/$', views.showCart, name="showCart"),
    url(r'^cart/(?P<orderId>[0-9]+)/edit/$', views.editCart, name="editCart"),
    # url(r'^cart/(?P<orderId>[0-9]+)/delete/$', views.editCart, name="editCart"),
    url(r'^cart/checkout/$', views.checkout, name="checkout"),
    url(r'^cart/checkoutDetails/$', views.checkoutDetails, name="checkoutDetails"),
    url(r'^cart/confirmCheckout/$', views.confirmCheckout, name="confirmCheckout"),
    url(r'^vendor/(?P<vendorId>[0-9]+)/$', views.vendorDetails, name="vendorDetails"),
    # url(r'^vendor/(?P<vendorId>[0-9]+)/contact/$', views.contactVendor, name="contactVendor"),
    url(r'^band/(?P<bandId>[0-9]+)/$', views.bandDetails, name="bandDetails"),
    url(r'^band/(?P<bandId>[0-9]+)/addToCart/$', views.addToCart, name="addToCart"),
    url(r'^band/(?P<bandId>[0-9]+)/updateQty/$', views.updateQty, name="updateQty"),
    url(r'^band/(?P<bandId>[0-9]+)/deleteBand/$', views.deleteBand, name="deleteBand"),

]
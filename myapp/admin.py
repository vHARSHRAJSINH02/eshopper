from django.utils.html import format_html
from django.contrib import admin
from .models import *
# Register your models here.

class Users_admin(admin.ModelAdmin):
    list_display = ['id','Email','Mobile','Password','Active','OTP','Token']
    search_fields=  ['id','Email','Mobile','Active']
    list_filter = ['Active']

admin.site.register(SignUpUser, Users_admin)

class State_admin(admin.ModelAdmin):
    list_display = ['id','State_Name']
    search_fields = ['id','State_Name']

admin.site.register(State, State_admin)

class City_admin(admin.ModelAdmin):
    list_display = ['id','City_Name','State_Name']
    search_fields = ['id','City_Name']
    list_filter = ['State_Name']

admin.site.register(City, City_admin)

class Area_admin(admin.ModelAdmin):
    list_display = ['id','Area_Name','City_Name']
    search_fields = ['id','Area_Name']
    list_filter = ['City_Name']

admin.site.register(Area, Area_admin)

class CustomerProfile_admin(admin.ModelAdmin):
    list_display = ['id','First_Name','Last_Name','DOB','Address','Area_Name','Image']
    search_fields = ['id','First_Name','Last_Name','DOB','Address','Area_Name']
    list_filter = ['DOB','Area_Name']

    def Image(self, obj):
        if obj.dp:
            return format_html('<img src="{}" width="180" height="100" />', obj.dp.url)
        else:
            return 'No Image'

admin.site.register(Customer_Profile, CustomerProfile_admin)

class Category_admin(admin.ModelAdmin):
    list_display = ['c_id','Category_Name']
    search_fields = ['c_id','Category_Name']

admin.site.register(Category, Category_admin)

class SubCategory_admin(admin.ModelAdmin):
    list_display = ['s_id','Subcategory_Name','c_id']
    search_fields = ['s_id','Subcategory_Name','c_id']
    list_filter = ['c_id']


admin.site.register(Subcategory, SubCategory_admin)

class Product_admin(admin.ModelAdmin):
    list_display = ['p_id','s_id','Pro_Name','Pro_Price','image','Pro_Disc']
    search_fields = ['p_id','s_id','Pro_Name','Pro_Price']
    search_fields = ['s_id','Pro_Price']

    def image(self, obj):
        if obj.Pro_Image:
            return format_html('<img src="{}" width="180" height="100"/>', obj.Pro_Image.url)
        else:
            return 'No Image'

admin.site.register(Product, Product_admin)

class CartItems_admin(admin.ModelAdmin):
    list_display = ['cart_id','lid','p_id','P_name','P_Price','c_QTY','c_Total','c_DateTime','c_Status']
    search_fields = ['cart_id','lid','p_id','P_name','P_Price','c_QTY','c_Total','c_DateTime','c_Status']
    list_filter = ['P_name','c_Status']

admin.site.register(Cart_Items, CartItems_admin)

class OrderDetails_admin(admin.ModelAdmin):
    list_display = ['o_id','lid','shipadd_id','o_Status','o_DateTime','Grand_Total','Payment_Status']
    search_fields = ['o_id','lid','shipadd_id','o_Status','o_DateTime','Grand_Total','Payment_Status']
    list_filter = ['o_Status','o_DateTime','Payment_Status']

admin.site.register(Order_Details, OrderDetails_admin)

class Stockdetails_admin(admin.ModelAdmin):
    list_display = ['sto_id','p_id','sto_Quantity']

admin.site.register(Stock_Details, Stockdetails_admin)

class Shippingdetails_Admin(admin.ModelAdmin):
    list_display = ['Ship_id','Area_Name','Ship_Charege']

admin.site.register(Shipping, Shippingdetails_Admin)

class Wistlistdetails_Admin(admin.ModelAdmin):
    list_display = ['W_id','lid','p_id']

admin.site.register(Wishlist, Wistlistdetails_Admin)

class ShippingAddress_admin(admin.ModelAdmin):
    list_display = ['shipadd_id','First_Name','Last_Name','Email','Mobile','Address','Area_Name','lid']
    search_fields = ['shipadd_id','First_Name','Last_Name','Email','Mobile','Address','Area_Name','lid']
    list_filter = ['Area_Name','lid']

admin.site.register(ShippingAddress, ShippingAddress_admin)

class CardDetails_admin(admin.ModelAdmin):
    list_display = ['card_id','Card_Number','Card_Name','Cvv_Code','Expire_Date','Balance']

admin.site.register(Card_Details, CardDetails_admin)

class Delivery_Signup_admin(admin.ModelAdmin):
    list_display = ['d_id','Mobile','Email','Password','OTP','Active']
    search_fields = ['d_id','Mobile','Email','Active']
    list_filter = ['Active']

admin.site.register(Delivery_Signup, Delivery_Signup_admin)

class Delivery_Profile_admin(admin.ModelAdmin):
    list_display = ['dp_id','d_id','First_Name','Last_Name','DOB','Address','Area','dp']

admin.site.register(Deliery_Profile, Delivery_Profile_admin)


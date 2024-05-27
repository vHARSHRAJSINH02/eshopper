from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.urls import reverse
import jwt
from django.core import serializers
from myapp.tokens import generate_token,expire_token,generate_delivery_token,expire_delivery_token
from datetime import datetime, timedelta
from .models import *

from django.db.models import Q

from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from random import *
import decimal
from django.utils import timezone
from django.shortcuts import get_object_or_404
import json
from django.core.paginator import Paginator
from itertools import zip_longest
from django.forms.models import model_to_dict
from django.core import serializers


def otp(request):
    return render(request,'otpverify.html')

def index(request):
    product = Product.objects.all().order_by('p_id')
    subcategories = Subcategory.objects.select_related('c_id').all()
    lid = request.session.get('lid')

    for subcategory in subcategories:
        subcategory.product_count = Product.objects.filter(s_id=subcategory.s_id).count()

    if lid:
        wishlist_ids = Wishlist.objects.filter(lid=lid).values_list('p_id__p_id', flat=True)
    else:
        wishlist_ids = []

    paginator = Paginator(product, 4) 
    page_number = request.GET.get('page')
    
    products = paginator.get_page(page_number)

    subcategories = list(zip_longest(*(iter(subcategories),) * 3))
    

    return render(request, 'index.html', {'products': products, 'subcategories': subcategories,'wishlist_ids': wishlist_ids})

def header(request):
    return render(request,'header.html')

def subcategories(request, c_id):
    if c_id:
        subcategories = Subcategory.objects.filter(c_id=c_id)
        subcategories_with_counts = []
        for subcategory in subcategories:
            product_count = Product.objects.filter(s_id=subcategory.s_id).count()
            subcategories_with_counts.append((subcategory, product_count))
    else:
        return JsonResponse({"Status": False, "msg": "There is no subcategory in this!!"})
    return render(request, 'subcategory.html', {'subcategories_with_counts': subcategories_with_counts})

# def subcategories(request,c_id):
#     if c_id:
#         subcategory = Subcategory.objects.filter(c_id=c_id)
#     else:
#         return JsonResponse({"Status":False,"msg":"There is no subcategory in this!!"})
#     return render(request,'subcategory.html',{'subcategory':subcategory})
    
# @api_view(["POST"])
def cart(request):
    lid = request.session.get('lid')
    token = request.session.get('token')

    try:
        user = SignUpUser.objects.get(id=lid)
    except:
        messages.error(request,"You have to login first!!")
        return redirect('login')

    if not token:
        user.Active=False
        user.save()
        del request.session['lid']
        del request.session['username']
        messages.error(request, "Your token is missing!!,please login!!")
        return redirect('login')
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'

    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        user.Action=False
        user.save()
        del request.session['lid']
        del request.session['username']
        messages.error(request, "Your token is expired, please login!!")
        return redirect('login')
    except jwt.DecodeError:
        user.Active=False
        user.save()
        del request.session['lid']
        del request.session['username']
        messages.error(request, "Your Token decode error!!")
        return redirect('login')
    try:
        cart = Cart_Items.objects.filter(lid=lid,c_Status='pending')
    except:
        messages.error(request, "Your cart is empty!!")
        return redirect('index')
    if cart.count() == 0:
        messages.error(request, "Your cart is empty please add items to cart!!")
        return redirect('index')
    subtotal = sum(item.c_Total for item in cart)
    return render(request, 'cart.html',{'cart':cart, 'subtotal': subtotal})

def wishlist(request):
    lid = request.session.get('lid')
    token = request.session.get('token')
    username = request.session.get('username')

    try:
        user = SignUpUser.objects.get(id=lid)
    except SignUpUser.DoesNotExist:
        user.Active=False
        user.save()
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "You need to login first!!")
        return redirect('login')
    
    if not token:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        messages.error(request, "Your token is missing Please login again!!")
        return redirect('login')
            

    
    secret_key ='django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(token, secret_key , algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your Token has Expired Please login again!!")
        return redirect('login')
    except jwt.DecodeError:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your token has decode error Please login again!!")
        return redirect('login')    

    try:
        wish_items = Wishlist.objects.filter(lid=lid)
    except Wishlist.DoesNotExist:
        messages.error(request, "Your wishlist is empty!!")

    paginator = Paginator(wish_items, 8) 
    page_number = request.GET.get('page')
    
    wish_items = paginator.get_page(page_number)

    wishlist_ids = Wishlist.objects.filter(lid=lid).values_list('p_id__p_id', flat=True)
    return render(request, 'wishlist.html',{'wish_items':wish_items,'wishlist_ids': wishlist_ids})

def orders(request):
    lid = request.session.get('lid')
    token = request.session.get('token')
    username = request.session.get('username')
    try:
        user = SignUpUser.objects.get(id=lid)
    except SignUpUser.DoesNotExist:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request , "You have to login first!!")
        return redirect('login')

    if not token:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your token is missing please login in again!!")
        return redirect('login')

    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your Token is expired Please  login again!!")
        return redirect('login')
    except jwt.DecodeError:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your Token has decode error Please login again!!")
        return redirect('login')


    try:
        current_orders = Order_Details.objects.filter(lid=lid,o_Status='pending')
        past_orders = Order_Details.objects.filter(lid=lid, o_Status='placed')
        canceled_orders = Order_Details.objects.filter(lid=lid,o_Status='cancled')
        inreplace_orders = Order_Details.objects.filter(lid=lid,o_Status='inreplace')
        replaced_orders = Order_Details.objects.filter(lid=lid,o_Status='replaced')
    except:
        pass
    return render(request , 'orders.html',{'current_orders': current_orders,'past_orders': past_orders,'inreplace_orders':inreplace_orders,'canceled_orders':canceled_orders,'replaced_orders':replaced_orders})

def checkout(request):
    lid = request.session.get('lid')
    token = request.session.get('token')
    try:
        user = SignUpUser.objects.get(id=lid)
        u_details = Customer_Profile.objects.get(lid=lid)
    except SignUpUser.DoesNotExist:
        messages.error(request, "You have to login first!!")
        return redirect('login')
    except Customer_Profile.DoesNotExist:
        messages.warning(request, "Please complete your profile!!")
        return render(request, 'profile.html')
    

    if not token:
        user.Active=False
        user.save()
        del request.session['lid']
        del request.session['username']
        messages.error(request, "You have to login first!!")
        return redirect('login')

    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        user.Active=False
        user.save()
        del request.session['lid']
        del request.session['token']
        del request.session['username']
        messages.error(request, "Your Token has expired please login again !")
        return redirect('login')
    except jwt.DecodeError:
        user.Active=False
        user.save()
        del request.session['lid']
        del request.session['token']
        del request.session['username']
        messages.error(request, "Your token has deocode error please login again!!")
    
    try:
        shippings = ShippingAddress.objects.filter(lid=lid)
    except:
        shippings = []
        pass

    userdetails = [u_details]
    cart_items = Cart_Items.objects.filter(lid=lid, c_Status='pending')
    if cart_items.count() == 0:
        messages.error(request, "You have no items in cart for checkout!!")
        return redirect('index')
    # Calculate the subtotal
    subtotal = sum(item.c_Total for item in cart_items)

    # # Calculate the shipping cost
    # ship = Shipping.objects.get(Area_Name=u_details.Area_Name)
    # shipping = ship.Ship_Charege  # This is a placeholder. You'll need to replace it with your actual shipping cost calculation.

    # # Calculate the total
    # total = subtotal + shipping
    
    return render(request, 'checkout.html', {'userdetails': userdetails,'cart_items': cart_items,'subtotal': subtotal,'shippings':shippings})

def contact(request):
    return render(request, 'contact.html')

def detail(request, p_id):
    product = Product.objects.filter(p_id=p_id)
    return render(request, 'detail.html',{'product':product})

def shop(request, s_id):
    lid = request.session.get('lid')
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', None)

    if s_id:
        product = Product.objects.filter(s_id=s_id)
    else:
        product = Product.objects.all()

    if min_price:
        product = product.filter(Pro_Price__gte=min_price)
    if max_price:
        product = product.filter(Pro_Price__lte=max_price)
    else:
        product = product.filter(Pro_Price__gte=min_price)
    paginator = Paginator(product, 6) 
    page_number = request.GET.get('page')
    
    products = paginator.get_page(page_number)

    if lid:
        wishlist_ids = Wishlist.objects.filter(lid=lid).values_list('p_id__p_id', flat=True)
    else:
        wishlist_ids = []
    return render(request, 'shop.html', {'products': products,'wishlist_ids':wishlist_ids})

def Shop(request):
    lid = request.session.get('lid')
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', None)

    product = Product.objects.all().order_by('p_id')

    if min_price:
        product = product.filter(Pro_Price__gte=min_price)
    if max_price:
        product = product.filter(Pro_Price__lte=max_price)
    else:
        product = product.filter(Pro_Price__gte=min_price)

    paginator = Paginator(product, 6) 
    page_number = request.GET.get('page')
    
    products = paginator.get_page(page_number)

    if lid:
        wishlist_ids = Wishlist.objects.filter(lid=lid).values_list('p_id__p_id', flat=True)
    else:
        wishlist_ids = []
    return render(request,'shop.html',{'products': products,'wishlist_ids':wishlist_ids})

def login(request):
    return render(request, 'login.html')

def forgetpass(request):
    return render(request, 'forgetpassword.html')

@csrf_exempt
@api_view(["POST"])
def SignUp(request):
    email = request.data.get('Email')
    mobile = request.data.get('Mobile')
    pass1= request.data.get('Password1')
    pass2 = request.data.get('Password2')

    if SignUpUser.objects.filter(Q(Email=email) | Q(Mobile=mobile)).exists():
        messages.error(request, "You are Already registered!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    
    if (not any(char.isupper()  for char in pass1) or 
        not any(char.islower() for char in pass1) or 
        not any(char.isdigit() for char in pass1) or 
        not any(char in '!@#$%^&*()' for char in pass1) or
        len(pass1)<8 or len(pass1)>16):
        print(pass1,'-->')
        messages.error(request, "Please enter strong password!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    if pass1 != pass2:
        print(pass2,'--->')
        messages.error(request, "Please enter both password same!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})

    SignUpUser.objects.create(
        Email=email,
        Mobile=mobile,
        Password=pass1
    )
    print(email,'-->')
    messages.success(request, "Your registration is successfully!!")
    return JsonResponse({"Status":True,"redirect_url":reverse('login')})

@csrf_exempt
@api_view(["POST"])
def userlogin(request):
    emailormobile = request.data.get('EmailorMobile')
    # mobile = request.data.get('Mobile')
    pass1 = request.data.get('Password1')
    
    try:
        user = SignUpUser.objects.get(Email=emailormobile)
    except SignUpUser.DoesNotExist:
        try:
            user = SignUpUser.objects.get(Mobile=emailormobile)
        except SignUpUser.DoesNotExist:
            messages.error(request, "Please enter valid emailid or mobile!!")
            return JsonResponse({"Status":False,"redirect_url":reverse('login')})

    if pass1 != user.Password:
        messages.error(request, "Wrong Password!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})

    otp = randint(100000,999999)
    print(otp,'-->')
    from django.core.mail import send_mail
    send_mail(
        'Your OTP for forget password',
        f'Your OTP for forget password is  {otp}',
        'divybavishi001@gmail.com',
        [user.Email],
        fail_silently=False
    )
    
    user.OTP= otp
    user.save()
    request.session['lid']=user.id
    messages.success(request, "Your OTP is sent to your mail please Verify it!!")
    return JsonResponse({"Status":True,"redirect_url":reverse('otp')})

@api_view(["POST"])
def resendOTP(request):
    lid = request.session.get('lid')
    try:
        user = SignUpUser.objects.get(id=lid)
    except:
        messages.error(request, "Please Login first!!")
        return redirect('login')
    otp = randint(100000,999999)
    from django.core.mail import send_mail
    send_mail(
        'Your OTP for login',
        f'Your OTP for login  is {otp}',
        'divybavishi001@gmail.com',
        [user.Email],
        fail_silently=False
    )
    user.OTP = otp
    user.save()
    messages.success(request, "Your OTP is sent to your mail please Verify it!!")
    return redirect('otp')

# @api_view(["POST"])
def verifyuser_login(request):
    if request.method == 'POST':
        otp = request.POST.get('OTP')
        lid = request.session.get('lid')

        try:
            user = SignUpUser.objects.get(id=lid)
        except:
            messages.error(request, "Please login first!!")
            return redirect('login')

        if otp != user.OTP:
            messages.error(request, "Wrong OTP please enter currect OTP!!")
            return redirect('otp')
        
        udetail = Customer_Profile.objects.get(lid=lid)
        token = generate_token(user)

        user.Token=token
        user.Active=True
        user.save()
        request.session['token']=token
        request.session['username']=udetail.First_Name
        messages.success(request, "You are logged in Successfully!!")
        return redirect('index')
    else:
        return redirect('login')
    
def userlogout(request):
    lid = request.session.get('lid')
    token = request.session.get('token')

    try:
        user = SignUpUser.objects.get(id=lid)
    except:
        user.Active=False
        user.save()
        del request.session['lid']
        messages.error(request, "Invalid Token!!")
        return redirect('index')
        
    
    if not token:
        del request.session['lid']
        messages.error(request, "Token is missing!!")
        return redirect('index')
    
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        user.Active=False
        user.save()
        del request.session['lid']
        messages.error(request, "Token has expired!!,Please Login again")
        return redirect('index')
    except jwt.DecodeError:
        messages.error(request, "Error decoding token!!")
        return redirect('index')
    
    if token != user.Token:
        del request.session['lid']
        messages.error(request, "Invalid Token!!")
        return redirect('index')
    
    extoken= expire_token(user)
    user.Token = extoken
    user.Active=False
    user.save()
    del request.session['lid']
    del request.session['username']
    # del request.session['token']
    messages.success(request, "You are logged Out Successfully!!")
    return redirect('index')

def profile(request):
    lid = request.session.get('lid')
    token = request.session.get('token')
    username = request.session.get('username')

    try:
        user = SignUpUser.objects.get(id=lid)
    except SignUpUser.DoesNotExist:
        messages.error(request , "Please Login first!!")
        return redirect('login')

    if not token:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        messages.error(request, "Your token is missing!!")
        return redirect('login')
    
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'

    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request , "Your token is expired ,please login again!!")
        return redirect('login')
    except jwt.DecodeError:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your token has decode error!!, Please login again.")
        return redirect('login') 
    
    try:
        u_details = Customer_Profile.objects.get(lid=lid)
    except:
        pass

    userdetails = [u_details]
    return render(request, 'profile.html',{'userdetails':userdetails})

# @api_view(["POST"])
def CustomerProfile(request):
    fname = request.data.get('First_Name')
    lname = request.data.get('Last_Name')
    dob = request.data.get('DOB')
    DP = request.data.get('DP')
    address = request.data.get('Address')
    lid = request.session.get('lid')
    token = request.session.get('token')

    try:
        user = SignUpUser.objects.get(id=lid)
    except:
        return JsonResponse({"Status":False,"msg":"Please Login first!!"})
    
    if not token:
        messages.error(request, "Token is missing!!")
        return redirect('index')
    
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        user.Active=False
        user.save()
        del request.session['lid']
        messages.error(request, "Token has expired!!,Please Login again")
        return redirect('index')
    except jwt.DecodeError:
        messages.error(request, "Error decoding token!!")
        return redirect('index')
    if token != user.Token:
        messages.error(request, "Invalid Token!!")
        return redirect('index')

    if not  fname:
        messages.error(request, "Please enter your first name!!")
        
    if not dob:
        messages.error(request, "Please enter your birthdate!!")
        return redirect('profile')
    if not address:
        messages.error(request, "Please enter your address!!")
        return redirect('profile')
    
    profile, created = Customer_Profile.objects.get_or_create(
        lid=user.id,
        defaults={
            'First_Name': fname,
            'Last_Name': lname,
            'DOB': dob,
            'dp': DP,
            'Address': address,
        }
    )
    
    if created:
        msg = "Your Profile is created!!"
    else:
        profile.First_Name = fname
        profile.Last_Name = lname
        profile.DOB = dob
        profile.dp = DP
        profile.Address = address
        profile.save()
        msg = "Your Profile is updated!!"
    
    messages.success(request, msg)
    return redirect('profile')

@csrf_exempt
@api_view(["POST"])
def add_to_cart(request):
    lid = request.session.get('lid')
    token = request.session.get('token')
    username = request.session.get('username')
    p_id = request.data.get('p_id')
    Quant = request.data.get('Quantity')
    qty = decimal.Decimal(Quant)

    # print(Quant,'-->')
    # print(p_id,'-->')
    try:
        user = SignUpUser.objects.get(id=lid)
    except SignUpUser.DoesNotExist:
        if user:
            user.Active=False
            user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your id was not found please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    
    if not token:
        if user:
            user.Active=False
            user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        messages.error(request, "Please login first!!")
        return JsonResponse({"Status":False,"redirect_url": reverse('login')})
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'

    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        if user:
            user.Active=False
            user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        if token:
            del request.session['token']
        messages.error(request, "Your Token is expired ,Please Login first!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    except jwt.DecodeError:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        if token:
            del request.session['token']
        messages.error(request, "You have to login first!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})

    try:
        pro = Product.objects.get(p_id=p_id)
        p_stock = Stock_Details.objects.get(p_id=p_id)
    except Product.DoesNotExist:
        messages.error(request, "Product is not selected!!")
        return JsonResponse({"Status":True,"redirect_url":reverse('Shop')})
    except Stock_Details.DoesNotExist:
        messages.error(request, "Product is out of stock!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('Shop')})
   


    if qty > p_stock.sto_Quantity:
        messages.error(request, "Product is not in stock currently!!")
        return JsonResponse({"Status":True, "redirect_url": reverse('index')})
    
    cart_items = Cart_Items.objects.filter(p_id=p_id,c_Status='pending',lid=lid)

    if cart_items: 
        cart = cart_items.first() 
        QTY = cart.c_QTY + qty
        c_total = pro.Pro_Price * QTY

        cart.c_QTY=QTY
        cart.c_Total=c_total
        cart.c_Status='pending'
        cart.save()
    else:  
        c_total = qty * pro.Pro_Price
        Cart_Items.objects.create(
            lid=user,
            p_id=pro,
            P_name=pro.Pro_Name,
            P_Price=pro.Pro_Price,
            c_QTY=qty,
            c_Total=c_total,
            c_Status='pending'
        )

    stock = p_stock.sto_Quantity - qty
    p_stock.sto_Quantity=stock
    p_stock.save()
    messages.success(request, "Product added in cart successfully!!")
    return JsonResponse({"Status":True, "redirect_url": reverse('cart')})
    
@csrf_exempt
@api_view(["POST"])    
def remove_cart(request):
    cartid = request.data.get('cartid')
    lid = request.session.get('lid')
    token = request.session.get('token')
    print(lid,'-->')
    try:
        user = SignUpUser.objects.get(id=lid)
        print(user,'-->')
    except:
        return JsonResponse({"Status":False,"Msg":"You need to logi first!!","redirect_url":reverse('login')})
    if not token:
        user.Active=False
        user.save()
        del request.session['lid']
        del request.session['username']
        return JsonResponse({"Status":False,"Msg":"Token is missing!!","redirect_url":reverse('login')})
    
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        user.Action=False
        user.save()
        del request.session['lid']
        del request.session['username']
        return JsonResponse({"Status":False,"Msg":"Your Token has expired, please login again!!","redirect_url":reverse('login')})
    except jwt.DecodeError:
        user.Active=False
        user.save()
        del request.session['lid']
        del request.session['username']
        return JsonResponse({"Status":False,"Msg":"Your Token has decode error,please login again","redirect_url":reverse('login')})
    
    try:
        cart_item = Cart_Items.objects.get(cart_id=cartid)
    except:
        return JsonResponse({"Status":False,"Msg":"Your cart id is not found!!","redirect_url":reverse('cart')})
    
    cart_item.delete()
    return JsonResponse({"Status":True,"Msg":"Your cart is was delete successfully!!","redirect_url":reverse('cart')})

@csrf_exempt
@api_view(["POST"])
def cartupdate(request):
    lid = request.session.get('lid')
    token = request.session.get('token')
    cartid = request.data.get('cartid')
    Quant = request.data.get('Quantity')
    qty = decimal.Decimal(Quant)

    try:
        user = SignUpUser.objects.get(id=lid)
    except:
        return JsonResponse({"Status":False,"Msg":"You need to login first!!"})
    cart = Cart_Items.objects.get(cart_id=cartid)

    product = Product.objects.get(p_id=cart.p_id)

    p_stock = Stock_Details.objects.get(p_id=product.p_id)

    if qty > p_stock.sto_Quantity:
        messages.error(request, "Product is not in stock currently!!")
        return JsonResponse({"Status":False, "redirect_url": reverse('cart')})
    
    QTY = cart.c_QTY + qty
    c_total = product.Pro_Price * QTY
    cart.c_QTY=QTY
    cart.c_Total=c_total
    cart.c_Status='pending'
    cart.save()
    messages.success(request, "Your Cart have been updated!!")
    return JsonResponse({"Status":True,"redirect_url":reverse('cart')})

@csrf_exempt
@api_view(["POST"])
def shippingaddress(request):
    lid = request.session.get('lid')
    token = request.session.get('token')
    username = request.session.get('username')
    try:
        user = SignUpUser.objects.get(id=lid)
    except SignUpUser.DoesNotExist:
        user.Active=False
        user.save()

        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "You have to login first!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    
    if not token:
        user.Active=False 
        user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        messages.error(request, "Your oken is missing please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        if token:
            del request.session['token']
        messages.error(request, "Your token has expired please login again!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    except jwt.DecodeError:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        if token:
            del request.session['token']
        messages.error(request, "Your token has decode error please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    
    if token!=user.Token:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your token is invalid please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    
    fname = request.data.get('First_Name')
    lname = request.data.get('Last_Name')
    email = request.data.get('Email')
    mobile = request.data.get('Mobile')
    address = request.data.get('Address')

    area_name = request.data.get('Area')
    area = get_object_or_404(Area, Area_Name=area_name)

    ShippingAddress.objects.create(
        First_Name=fname,
        Last_Name = lname,
        Email=email,
        Mobile= mobile,
        Address =address,
        Area_Name= area,
        lid=user
    )
    messages.success(request, "Your Shipping address Added!!")
    return JsonResponse({"Status":True,"redirect_url":reverse('checkout')})

@csrf_exempt
@api_view(["POST"])
def editshipaddress(request):
    lid = request.session.get('lid')
    token = request.session.get('token')
    username = request.session.get('username')
    try:
        user = SignUpUser.objects.get(id=lid)
    except SignUpUser.DoesNotExist:
        user.Active=False
        user.save()
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "You have to login first!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    
    if not token:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        messages.error(request, "Your Token is missing Please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your Token has expired Please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    except jwt.DecodeError:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your Token has decode error,please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})

    if token != user.Token:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        if token:
            del request.session['token']
        messages.error(request, "Your Token is incurrect please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    
    shipadd_id = request.data.get('Shipadd_id')
    print(shipadd_id,'-->')
    fname = request.data.get('First_Name')
    lname = request.data.get('Last_Name')
    email = request.data.get('Email')
    mobile = request.data.get('Mobile')
    address = request.data.get('Address')
    area_name = request.data.get('Area')
    area = get_object_or_404(Area, Area_Name=area_name)

    try:
        shipadd = ShippingAddress.objects.get(shipadd_id=shipadd_id)
    except ShippingAddress.DoesNotExist:
        print(shipadd_id,'---->')
        messages.error(request, "Your Ship address id is missing!!please try again!!")
        return JsonResponse({"status":False,"redirect_url":reverse('checkout')})
    
    shipadd.First_Name=fname
    shipadd.Last_Name=lname
    shipadd.Email=email
    shipadd.Mobile=mobile
    shipadd.Address=address
    shipadd.Area_Name=area
    shipadd.save()
    messages.success(request, "Your Address is edited!!")
    return JsonResponse({"Status":True,"redirect_url":reverse('checkout')})

def deleteshippingaddress(request, shipaddid):
    lid = request.session.get('lid')
    token = request.session.get('token')
    username = request.session.get('username')
    try:
        user = SignUpUser.objects.get(id=lid)
    except SignUpUser.DoesNotExist:
        user.Active=False
        user.save()
        if token:
            del request.session['lid']
        if username:
            del request.session['username']
        messages.error(request, "You have to  login first!!")
        return redirect('login')
    if not token:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        messages.error(request, "Your Token is missing please login again!!")
        return redirect('login')
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        if token:
            del request.session['token']
        messages.error(request, "your roken has been expired please login again!!")
        return redirect('login')
    except jwt.DecodeError:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        if token:
            del request.session['token']
        messages.error(request, "Your token has decode error please login again!!")
        return redirect('login')
    
    shippingadd = ShippingAddress.objects.get(shipadd_id=shipaddid)
    shippingadd.delete()
    
    messages.success(request, "Selectede shipping address was deleted successfully!!")
    return redirect('checkout')

def get_shipping_charge(request):
    area_name = request.GET.get('area_name', None)
    if area_name is not None:
        try:
            shipping = Shipping.objects.get(Area_Name__Area_Name=area_name)
            print(shipping.Ship_Charege,'--->')
            return JsonResponse({'shipping_charge': str(shipping.Ship_Charege)})
        except Shipping.DoesNotExist:
            return JsonResponse({'error': 'Shipping does not exist for this area'}, status=404)
    return JsonResponse({'error': 'Invalid parameters'}, status=400)

@csrf_exempt
@api_view(["POST"])
def Complete_Order(request):
    lid =request.session.get('lid')
    token = request.session.get('token')
    username = request.session.get('username')
    card_number = request.data.get('card_number')
    card_name = request.data.get('card_name')
    payment_method = request.data.get('payment_method')
    cvv_code = request.data.get('cvv_code')
    expire_date = request.data.get('expire_date')
    shipaddid = request.data.get('shipping_id')
    try:
        user = SignUpUser.objects.get(id=lid)
        ship_address = ShippingAddress.objects.get(shipadd_id=shipaddid)
    except SignUpUser.DoesNotExist:
        user.Active=False
        user.save()
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Please login first!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    except ShippingAddress.DoesNotExist:
        messages.error(request, "Your Shipping address is missing!!,Please Select")
        return JsonResponse({"Status":False,"redirect_url":reverse('checkout')})
    
    if not token:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        messages.error(request, "Your Token is missing please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})

    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'

    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        user.Active = False
        user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your Token is expired please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    except jwt.DecodeError:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username :
            del request.session['username']
        messages.error(request, "Your token has decode error please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})

    if token != user.Token:
        user.Active=False
        user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Invalid token please login!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})

    try:
        cart = Cart_Items.objects.filter(lid=lid,c_Status='pending')
        shipping = Shipping.objects.get(Area_Name=ship_address.Area_Name)
    except Cart_Items.DoesNotExist:
        messages.error(request, "Your Cart is empty please add items to shop!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('index')})
    except Shipping.DoesNotExist:
        messages.error(request, "We can not deliver your order to this area please change the order address!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('checkout')})
    
    
    total = 0
    for i in cart:
        total += i.c_Total 

    gtotal = total + shipping.Ship_Charege

    if payment_method == 'card':  
        card = Card_Details.objects.get(card_id=1)
        print(card.Card_Number,'-->')
        cnumber = card.Card_Number
        cname = card.Card_Name
        cvvcode = card.Cvv_Code
        exp_date = card.Expire_Date
        balance = card.Balance

        if cnumber == card_number and cvv_code == cvvcode and exp_date == expire_date:
            if gtotal > balance:
                messages.error(request, "Your card has no balance!!")
                return JsonResponse({"Status":False,"redirect_url":reverse('checkout')})
            bal = balance - gtotal
            card.Balance=bal
            card.save()

    
    order = Order_Details.objects.create(
        lid = user,
        shipadd_id=ship_address, 
        o_Status='pending',
        Grand_Total=gtotal,
        Payment_Status=payment_method  
    )
    for item in cart:
        order.Cart_Items.add(item)
    cart.update(c_Status='inorder')
    messages.success(request, "Your order was placed successfully!!")
    return JsonResponse({"Status":True,"redirect_url":reverse('index')})

def sentMessage(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if not name:
            messages.error(request,"Please Enter your name!!")
            return redirect('contact')
        if not email:
            messages.error(request, "Please Enter your Email!!")
        if not subject:
            messages.error(request, "Please Enter Subject!!")
        if not message:
            messages.error(request, "Please Enter Messages!!")
        from django.core.mail import send_mail
        send_mail(
            subject,
            message,
            email,
            ['divybavishi001@gmail.com'],
            fail_silently=False
        )
        messages.success(request, "Your Message will send successfully!! Our team will be connect you soon!!")
        return redirect('contact')
    
@csrf_exempt
@api_view(["POST"])
def forgetpassword(request):
    email = request.data.get('Email')
    mobile = request.data.get('Mobile')
    try:
        if email:
            user = SignUpUser.objects.get(Email=email)
        elif mobile:
            user = SignUpUser.objects.get(Mobile=mobile)
        else:
            messages.error(request, "Please enter email or mobile number to forget password!!")
            return JsonResponse({"Status":False,"redirect_url":reverse('forgetpass')})
    except:
        messages.error(request, "Please Enter Registered email or mobile!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('forgetpass')})

    otp = randint(100000,999999)
    from django.core.mail import send_mail
    send_mail(
        'Your OTP for forget password',
        f'Your OTP for forget password is  {otp}',
        'divybavishi001@gmail.com',
        [user.Email],
        fail_silently=False
    )
    user.OTP=otp
    user.save()
    request.session['lid']=user.id
    messages.success(request, "Your OTP is sent to your mail please verify it!")
    return JsonResponse({"Status":True,"redirect_url":reverse('forgetotp')})

def forgetotp(request):
    return render(request, 'forgetotp.html')

@csrf_exempt
@api_view(["POST"])
def verifyforgetotp(request):
    otp = request.data.get('OTP')
    lid = request.session.get('lid')

    try:
        user = SignUpUser.objects.get(id=lid)
    except:
        messages.error(request, "Your login id does not exist!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('forgetpass')})
    
    if otp != user.OTP:
        messages.error(request, "Your otp is invalid!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('forgetotp')})
    
    u_details=Customer_Profile.objects.get(lid=lid)

    token = generate_token(user)
    user.Active=True
    user.Token=token
    user.save()
    request.session['token']=token
    request.session['username']=u_details.First_Name
    messages.success(request, "OTP verified!!, Please create new password!!")
    return JsonResponse({"Status":True,"redirect_url":reverse('resetpass')})

def resetpass(request):
    return render(request, 'resetpass.html')

@csrf_exempt
@api_view(["POST"])
def resetpassword(request):
    pass1 = request.data.get('Password1')
    pass2 = request.data.get('Password2')
    lid = request.session.get('lid')
    token = request.session.get('token')

    try:
        user = SignUpUser.objects.get(id=lid)
    except:
        messages.error(request, "You are not logged in, please login first!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    
    if not token:
        user.Active=False
        user.save()
        del request.session['lid']
        del request.session['username']
        messages.error(request, "Your token is missing!!, please login first!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})

    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'

    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        user.Active=False
        user.save()
        del request.session['lid']
        del request.session['token']
        del request.session['username']
        messages.error(request, "Your token has expired please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    except jwt.DecodeError:
        user.Active=False
        user.save()
        del request.session['lid']
        del request.session['token']
        del request.session['username']
        messages.error(request, "Your token has decode error,please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    
    if token != user.Token:
        user.Active=False
        user.save()
        del request.session['lid']
        del request.session['username']
        del request.session['token']
        messages.error(request, "Your token is invalid!!,please login again")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})

    if (not any(char.isdigit() for char in pass1) or
        not any(char.islower() for char in pass1) or
        not any(char.isupper() for char in pass1) or 
        not any(char in '!@#$%^*&*()' for char in pass1) or
        len(pass1)<8 or len(pass1)>16):
        messages.warning(request, "Your password must have contain lowercase, uppercase, digits and special charectors and lenght must be between 8 - 16")
        return JsonResponse({"Status":False,"redirect_url":reverse('resetpass')})
    
    if pass1 != pass2:
        messages.error(request, "Both passwords must be same !!")
        return JsonResponse({"Status":False,"redirect_url":reverse('resetpass')})
    
    user.Password=pass1
    user.save()
    messages.success(request, "Your passsword changed successfully!!")
    return JsonResponse({"Status":True,"redirect_url":reverse('index')})

@csrf_exempt
@api_view(["POST"])
def toggle_wishlist(request):
    lid = request.session.get('lid')

    try:
        user = SignUpUser.objects.get(id=lid)
    except SignUpUser.DoesNotExist:
        messages.error(request , "You have to login first if you want to wishlist product!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    
    product_id = request.data.get('product_id')
    product = Product.objects.get(p_id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(lid=user, p_id=product)

    if not created:
        wishlist.delete()
    
    return JsonResponse({"Status":True,"redirect_url":reverse('wishlist')})

@csrf_exempt
@api_view(["GET"])
def update_cart_plus(request):
    cart_id = request.GET.get('cart_id', None)
    pqty = request.GET.get('pQTY', None)
    p_qty = decimal.Decimal(pqty)
    if cart_id is not None:
        try:
            cart = Cart_Items.objects.get(cart_id=cart_id)
            try:
                p_stock = Stock_Details.objects.get(p_id=cart.p_id)
            except:
                return JsonResponse({'error': 'This product is not in stock!!'}, status=404)
            qty = cart.c_QTY + p_qty
            if p_stock.sto_Quantity < qty:
                return JsonResponse({'error': 'This product is not in stock!!'}, status=404)
            pprice = cart.P_Price * qty

            cart.c_Total=pprice
            cart.c_QTY=qty
            cart.save()
            return JsonResponse({'p_QTY': str(qty)})
        except Cart_Items.DoesNotExist:
            return JsonResponse({'error': 'This product is not in your cart'}, status=404)
    return JsonResponse({'error': 'Invalid parameters'}, status=400)

@csrf_exempt
@api_view(["GET"])
def update_cart_minus(request):
    cart_id = request.GET.get('cart_id', None)
    pqty = request.GET.get('pQTY', None)
    p_qty = decimal.Decimal(pqty)
    if cart_id is not None:
        try:
            cart = Cart_Items.objects.get(cart_id=cart_id)
            qty = cart.c_QTY - p_qty
            if qty < 1:
                qty = 1
            pprice = cart.P_Price * qty

            cart.c_Total=pprice
            cart.c_QTY=qty
            cart.save()
            return JsonResponse({'p_QTY': str(qty)})
        except Cart_Items.DoesNotExist:
            return JsonResponse({'error': 'This product is not in your cart'}, status=404)
    return JsonResponse({'error': 'Invalid parameters'}, status=400)

@csrf_exempt
@api_view(["POST"])
def Cancel_Order(request):
    lid = request.session.get('lid')
    token = request.session.get('token')
    username = request.session.get('username')
    oid = request.data.get('o_id')
    
    try:
        user = SignUpUser.objects.get(id=lid)
    except SignUpUser.DoesNotExist:
        if user:
            user.Actiive=False
            user.save()
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "you have to lof=gin first!!")
        return JsonResponse({"Status":False, "redirect_url":reverse('login')})
    
    if not token:
        if user:
            user.Active=False
            user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        messages.error(request, "Your token is missing Please login again!!")
        return JsonResponse({"Status":False, "redirect_url":reverse('login')})

    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'

    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        if user:
            user.Active=False
            user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your Token is expired please login again!!")
        return JsonResponse({"Status":False, "redirect_url":reverse('login')})
    except jwt.DecodeError:
        if user:
            user.Active=False
            user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Yiur token hase decode  error, please login again!!")
        return JsonResponse({"Status":False, "redirect_url":reverse('login')})

    if token != user.Token:
        if user:
            user.Active=False
            user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request,"Your token is incurrect Please login again!!")
        return JsonResponse({"Status":False, "redirect_url":reverse('login')})
    
    try:
        order = Order_Details.objects.get(o_id=oid)
    except Order_Details.DoesNotExist:
        messages.error(request, "Your Order id not found")
        return JsonResponse({"Status":False, "redirect_url":reverse('orders')})
    
    if order.o_Status == 'pending':
        order.o_Status='cancled'
        order.save()
         # Increase the stock for each item in the cancelled order
        for item in order.Cart_Items.all():
            try:
                # Get the stock details for the product
                stock_detail = Stock_Details.objects.get(p_id=item.p_id)
                # Increase the quantity
                stock_detail.sto_Quantity += item.c_QTY
                stock_detail.save()
            except Stock_Details.DoesNotExist:
                # Handle the case where there is no stock detail for the product
                pass
        messages.success(request, "Your order is cancled!!")
        return JsonResponse({"Status":True,"redirect_url":reverse('orders')})
    
    if order.o_Status == 'placed':
        if timezone.now() - order.o_DateTime > timedelta(days=7):
            messages.error(request, "Your order is not replaceable as it more than 7 days old.")
            return JsonResponse({"Status":False,"redirect_url":reverse('orders')})
    
        order.o_Status='inreplace'
        order.save()

        messages.success(request, "Your replace order request are sent, our delivery partner will take it soon!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('orders')})
    messages.error(request, "Something went wrong please try again!!")
    return JsonResponse({"Status":False,"redirect_url":reverse('orders')})

@csrf_exempt
@api_view(["POST"])
def Cancel_Replace(request):
    lid = request.session.get('lid')
    token = request.session.get('token')
    username = request.session.get('username')
    oid = request.data.get('o_id')
    try:
        user = SignUpUser.objects.get(id=lid)
    except SignUpUser.DoesNotExist:
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "You have to login first!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    if not token:
        if user:
            user.Active=False
            user.save()
        if lid:
            del request.session['lid']
        if username:
            del request.session['username']
        messages.error(request, "Your token is missing, Please login first!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})

    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        if user:
            user.Active =False
            user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your Token is expired, please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    except jwt.DecodeError:
        if user:
            user.Active=False
            user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your token has decode error, please login again!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('login')})
    
    if token != user.Token:

        if user:
            user.Active=False
            user.save()
        if lid:
            del request.session['lid']
        if token:
            del request.session['token']
        if username:
            del request.session['username']
        messages.error(request, "Your token is incurrect, please login again!!")
        return JsonResponse({"Status":False, "redirect_url":reverse('login')})
    
    try:
        order = Order_Details.objects.get(o_id=oid)
    except Order_Details.DoesNotExist:
        messages.error(request, "Your order id is not found!!")
        return JsonResponse({"Status":False,"redirect_url":reverse('orders')})
    
    if order.o_Status == 'inreplace':
        order.o_Status='placed'
        order.save()

        messages.success(request, "Your order replace was canceled!!")
        return JsonResponse({"Status":False, "redirect_url":reverse('orders')})
    
    messages.error(request, "Something went wrong!!")
    return JsonResponse({"Status":False,"redirect_url":reverse('orders')})

@api_view(["POST"])
def delivery_signup(request):
    mobile = request.data.get('Mobile')
    email = request.data.get('Email')
    pass1 = request.data.get('Password1')
    pass2 = request.data.get('Password2')

    if not mobile:
        return JsonResponse({"Status":False,"msg":"Please enter mobile mobile number!!"})
    
    if len(mobile)<10 or len(mobile)>10:
        return JsonResponse({"Status":False,"msg":"Please enter valid mopbile number!!"})
    
    if not email:
        return JsonResponse({"Status":False,"msg":"please enter email id!!"})
    
    if Delivery_Signup.objects.filter(Q(Email=email) | Q(Mobile=mobile)).exists():
        return JsonResponse({"Status":False,"msg":"Delivery Boy Already exist!!"})
    
    if (not any(char.isdigit() for char in pass1) or
        not any(char.isupper() for char in pass1) or
        not any(char.islower() for char in pass1) or 
        not any(char in '!@#$%^&*()' for char in pass1) or
        len(pass1)>16 or len(pass1)<8):
        return JsonResponse({"Status":False,"msg":"please enter strong password!!"})
    
    if pass1 != pass2:
        return JsonResponse({"Status":False,"msg":"Both password are not same please enter both same!!"})
    
    Delivery_Signup.objects.create(
        Mobile=mobile,
        Email=email,
        Password=pass1
    )
    return JsonResponse({"Status":True,"msg":"Your Profile is created successfully!!"})

@api_view(["POST"])
def delivery_login(request):
    mobile = request.data.get('Mobile')
    email = request.data.get('Email')
    pass1 = request.data.get('Password')

    try:
        if mobile:
            d_user = Delivery_Signup.objects.get(Mobile=mobile)
        if email:
            d_user = Delivery_Signup.objects.get(Email=email)
        else:
            return JsonResponse({"Status":False,"msg":"Please enter mobile number or email to login!!"})
    except Delivery_Signup.DoesNotExist:
        return JsonResponse({"Status":False,"msg":"Please enter currect details!!"})
    
    if not pass1:
        return JsonResponse({"Status":False,"msg":"Please enter password!!"})
    
    if pass1 != d_user.Password:
        return JsonResponse({"Status":False,"msg":"Wrong Password, Please enter currect password!!"})
    
    otp = randint(100000,999999)
    print(otp,'-->')
    from django.core.mail import send_mail
    send_mail(
        'Your OTP For login',
        f'Your OTP for login is {otp}',
        'divybavishi001@gmail.com',
        [d_user.Email],
        fail_silently=False
    )
    d_user.OTP=otp
    d_user.save()
    request.session['dlid']=d_user.d_id
    return JsonResponse({"Status":True,"msg":"OTP is sent to your mail please varify it!!"})

@api_view(["POST"])
def delivery_verifyotp(request):
    dlid = request.session.get('dlid')
    otp = request.data.get('OTP')
    try:
        d_user = Delivery_Signup.objects.get(d_id=dlid)
    except Delivery_Signup.DoesNotExist:
        return JsonResponse({"Status":False,"msg":"Please login first !!"})
    
    if otp != d_user.OTP:
        return JsonResponse({"Status":False,"msg":"your OTP is incurrect!!"})
    
    d_token = generate_delivery_token(d_user)
    print(d_token,'-->')
    d_user.Active=True
    d_user.Token=d_token
    d_user.save()
    request.session['dtoken']=d_token
    return JsonResponse({"Status":True,"msg":"You have logged in successfully!!"})

@api_view(["POST"])
def delivery_forgot_password(request):
    mobile = request.data.get('Mobile')
    email = request.data.get('Email')
    try:
        if mobile:
            d_user = Delivery_Signup.objects.get(Mobile=mobile)
        if email:
            d_user = Delivery_Signup.objects.get(Email=email)
        else:
            return JsonResponse({"Status":False,"Msg":"Please Enter mobile number or email for forgot password!!"})
    except:
        return JsonResponse({"Status":False,"Msg":"Please enter currect email or mobile!!"})
    
    otp = randint(100000, 999999)

    print(otp,'-->')
    from django.core.mail import send_mail
    send_mail(
        'Your OTP for forget password',
        f'Your OTP for forgot password is {otp}',
        'divybavihi001@gmail.com',
        [d_user.Email],
        fail_silently=False
    )
    d_user.OTP=otp
    d_user.save()
    request.session['dlid']=d_user.d_id
    return JsonResponse({"Status":True,"Msg":"OTP is sent to your mail please verify it!!"})

@api_view(["POST"])
def reset_password_delivery(request):
    dlid = request.session.get('dlid')
    dtoken = request.session.get('dtoken')
    try:
        d_user = Delivery_Signup.objects.get(d_id=dlid)
    except:
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"You have to login first!!"})
    
    if not dtoken:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        return JsonResponse({"Status":False,"Msg":"Your token is missing, Please login again!!"})
    
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'

    try:
        payload = jwt.decode(dtoken, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token is expired, Please login again!!"})
    except jwt.DecodeError:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token has decode error, Please login again!!"})

    pass1 = request.data.get('Password1')
    pass2 = request.data.get('Password2')

    if (not any(char.isdigit() for char in pass1) or
        not any(char.isupper() for char in pass1) or 
        not any(char.islower() for char in pass1) or 
        not any(char in '!@#$%^&*()' for char in pass1) or 
        len(pass1)>16 or len(pass1)<8):
        return JsonResponse({"Status":False,"Msg":"Please enter strong password!!"})
    
    if pass1 != pass2:
        return JsonResponse({"Status":False,"Msg":"Please enter both password same!!"})
    
    d_user.Password=pass1
    d_user.save()
    return JsonResponse({"Status":True,"Msg":"Your new password is generated successfully!!"})

@api_view(["POST"])
def delivery_logout(request):
    dlid = request.session.get('dlid')
    dtoken = request.session.get('dtoken')
    try :
        d_user = Delivery_Signup.objects.get(d_id=dlid)
    except Delivery_Signup.DoesNotExist:
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"msg":"Please login again!!"})
    
    if not dtoken:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        return JsonResponse({"Status":False,"msg":"Your token is missing, please login again!!"})
    
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(dtoken, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"msg":"Your token is expired,please login again!!"})
    except jwt.DecodeError:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"msg":"Your Token has decode error, Please login again!!"})
    
    dex_token = expire_delivery_token(d_user)
    d_user.Active=False
    d_user.Token=dex_token
    d_user.save()
    del request.session['dlid']
    del request.session['dtoken']
    return JsonResponse({"Status":True,"msg":"You are logged out successfully!!"})

@api_view(["POST"])
def edit_delivery_profile(request):
    dlid = request.session.get('dlid')
    dtoken = request.session.get('dtoken')
    try:
        d_user = Delivery_Signup.objects.get(d_id=dlid)
    except Delivery_Signup.DoesNotExist:
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"You have to login first!!"})
    if not dtoken:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        return JsonResponse({"Status":False,"Msg":"Your token is missing,Please login again!!"})
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(dtoken, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token is expired, Please login again!!"})
    except jwt.DecodeError:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token has decode error, Please login again!"})

    if dtoken != d_user.Token:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token is incurrect, please login again!!"})

    fname = request.data.get('First_Name')
    lname = request.data.get('Last_Name')
    dob = request.data.get('DOB')
    address = request.data.get('Address')
    area_id = request.data.get('Area_id')
    DP = request.data.get('DP')
    try:
        area = Area.objects.get(id=area_id)
    except:
        return JsonResponse({"Status":False,"Msg":"Please enter valid area id"})
    try:
        d_profiles = Deliery_Profile.objects.get(d_id=d_user)
    except Deliery_Profile.DoesNotExist:
        Deliery_Profile.objects.create(
            d_id=d_user,
            defaults={
                'First_Name': fname,
                'Last_Name': lname,
                'DOB': dob,
                'Address': address,
                'Area': area,
                'dp': DP
            }
        )
        return JsonResponse({"Status":True,"Msg":"Your profile is created!!"})
    
    d_profiles.First_Name=fname
    d_profiles.Last_Name=lname
    d_profiles.DOB=dob
    d_profiles.Address=address
    d_profiles.Area=area
    d_profiles.dp=DP
    d_profiles.save()
    return JsonResponse({"Status":True,"Msg":"Your Profile was updated!!"})

@api_view(["POST"])
def delivery_View_Orders(request):
    dlid = request.session.get('dlid')
    dtoken = request.session.get('dtoken')
    try:
        d_user = Delivery_Signup.objects.get(d_id=dlid)
    except Delivery_Signup.DoesNotExist:
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"msg":"Please login first!!"})
    if not dtoken:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        return JsonResponse({"Status":False,"msg":"Your token is missing please login again!!"})
    
    secret_key ='django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'

    try:
        payload = jwt.decode(dtoken, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"msg":"Your token is expired, please login again!!"})
    except jwt.DecodeError:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"msg":"Your token has decode error, Please login again!!"})

    orders = Order_Details.objects.filter(o_Status='pending')
    order_list = []
    for order in orders:
        cart_items = order.Cart_Items.all()
        cart_items_list = serializers.serialize('json', cart_items)
        order_dict = {
            "o_id": order.o_id,
            "lid": order.lid.id,
            "shipadd_id": order.shipadd_id.shipadd_id,
            "o_Status": order.o_Status,
            "o_DateTime": order.o_DateTime,
            "Grand_Total": str(order.Grand_Total),
            "Payment_Status": order.Payment_Status,
            "Cart_Items": cart_items_list
        }
        order_list.append(order_dict)
    return JsonResponse({"Status":True,"Orders": order_list})

@api_view(["POST"])
def Complate_Delivery(request):
    dlid = request.session.get('dlid')
    dtoken = request.session.get('dtoken')
    oid = request.data.get('o_id')
    try:
        d_user = Delivery_Signup.objects.get(d_id=dlid)
    except Delivery_Signup.DoesNotExist:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"You have to login first!!"})
    if not dtoken:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        return JsonResponse({"Status":False,"Msg":"Your token is missing,Please login again!!"})
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(dtoken, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dtoken:
            del request.session['dtoken']
        if dlid:
            del request.session['dlid']
        return JsonResponse({"Status":False,"msg":"Your token is expired,Please login again!!"})
    except jwt.DecodeError:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token has decode error,Please login again!!"})
    
    if dtoken != d_user.Token:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token is incurrect, Please login again!!"})
    
    try:
        order = Order_Details.objects.get(o_id=oid)
    except Order_Details.DoesNotExist:
        return JsonResponse({"Status":False,"Msg":"Order id not found!!"})
    
    order.o_Status='placed'
    order.save()
    return JsonResponse({"Status":True,"Msg":"Order is complpeted!!"})

@api_view(["POST"])
def delivery_View_replace_orders(request):
    dlid = request.session.get('dlid')
    dtoken = request.session.get('dtoken')
    try:
        d_user = Delivery_Signup.objects.get(d_id=dlid)
    except Delivery_Signup.DoesNotExist:
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"You have to login first!!"})
    if not dtoken:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token is missing,Please login again!!"})
    
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(dtoken, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token is expired, Please login again!!"})
    except jwt.DecodeError:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token has decode error, Please login again!!"})
    
    if dtoken != d_user.Token:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token is incurrect, please login again!!"})
    
    orders = Order_Details.objects.filter(o_Status='inreplace')
    order_list = []
    for order in orders:
        cart_items = order.Cart_Items.all()
        cart_items_list = serializers.serialize('json', cart_items)
        order_dict = {
            "o_id": order.o_id,
            "lid": order.lid.id,
            "shipadd_id": order.shipadd_id.shipadd_id,
            "o_Status": order.o_Status,
            "o_DateTime": order.o_DateTime,
            "Grand_Total": str(order.Grand_Total),
            "Payment_Status": order.Payment_Status,
            "Cart_Items": cart_items_list
        }
        order_list.append(order_dict)
    return JsonResponse({"Status":True,"Orders": order_list})

@api_view(["POST"])
def complete_replace_order(request):
    dlid = request.session.get('dlid')
    dtoken = request.session.get('dtoken')
    oid = request.data.get('o_id')
    try:
        d_user = Delivery_Signup.objects.get(d_id=dlid)
    except Delivery_Signup.DoesNotExist:
        if dtoken:
            del request.session['dlid']
        return JsonResponse({"Status":False,"Msg":"Please login first!!"})
    if not dtoken:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token is missing, Please login!!"})
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    try:
        payload = jwt.decode(dtoken, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token is expired, Please login again!!"})
    except jwt.DecodeError:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token has decode error,Please login again!!"})
    
    if dtoken != d_user.Token:
        if d_user:
            d_user.Active=False
            d_user.save()
        if dlid:
            del request.session['dlid']
        if dtoken:
            del request.session['dtoken']
        return JsonResponse({"Status":False,"Msg":"Your token is incurrect,Please login again!!"})
    
    try:
        order = Order_Details.objects.get(o_id=oid)
    except Order_Details.DoesNotExist:
        return JsonResponse({"Status":False,"Msg":"Order id is missing!!"})
    
    order.o_Status='replaced'
    order.save()
    return JsonResponse({"Status":True,"Msg":"Your order is replaced!!"})

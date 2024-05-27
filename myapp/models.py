from django.db import models

# Create your models here.
class SignUpUser(models.Model):
    id = models.AutoField(primary_key=True)
    Email = models.EmailField(max_length=100,null=True)
    Mobile = models.CharField(max_length=10,null=True)
    Password = models.CharField(max_length=16,null=True)
    OTP = models.CharField(max_length=6,null=True)
    Token = models.CharField(max_length=200,null=True)
    Active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

class State(models.Model):
    id = models.AutoField(primary_key=True)
    State_Name = models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.State_Name

class City(models.Model):
    id = models.AutoField(primary_key=True)
    City_Name = models.CharField(max_length=100,null=True)
    State_Name = models.ForeignKey(State, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.City_Name

class Area(models.Model):
    id = models.AutoField(primary_key=True)
    Area_Name = models.CharField(max_length=100,null=True)
    Pincode = models.CharField(max_length=6,null=True)
    City_Name = models.ForeignKey(City, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.Area_Name

class Customer_Profile(models.Model):
    id= models.AutoField(primary_key=True)
    lid = models.ForeignKey(SignUpUser, on_delete=models.CASCADE, null=True)
    First_Name = models.CharField(max_length=50,null=True)
    Last_Name = models.CharField(max_length=50,null=True)
    DOB = models.DateField(null=True)
    dp = models.ImageField(upload_to='myapp/media',null=True)
    Address = models.TextField(max_length=500,null=True)
    Area_Name = models.ForeignKey(Area, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return str(self.id)

class Category(models.Model):
    c_id = models.AutoField(primary_key=True)
    Category_Name = models.CharField(max_length=100,null=True)
    Category_Image = models.ImageField(upload_to='myapp/media',null=True)

    def __str__(self):
        return str(self.c_id)

class Subcategory(models.Model):
    s_id = models.AutoField(primary_key=True)
    Subcategory_Name = models.CharField(max_length=100,null=True)
    c_id = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    SubCategory_Image = models.ImageField(upload_to='myapp/media',null=True)
    def __str__(self):
        return str(self.s_id)
    
class Product(models.Model):
    p_id = models.AutoField(primary_key=True)
    s_id = models.ForeignKey(Subcategory, on_delete=models.CASCADE, null=True)
    Pro_Name = models.CharField(max_length=100,null=True)
    Pro_Price = models.DecimalField(max_digits=10,decimal_places=2)
    Pro_Image = models.ImageField(upload_to='myapp/media',null=True)
    Pro_Disc = models.TextField(max_length=500,null=True)
    
    def __str__(self):
        return str(self.p_id)
    
class Cart_Items(models.Model):
    cart_id = models.AutoField(primary_key=True)
    lid = models.ForeignKey(SignUpUser, on_delete=models.CASCADE, null=True)
    p_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    P_name = models.CharField(max_length=100,null=True)
    P_Price = models.DecimalField(max_digits=10,decimal_places=2)
    c_QTY = models.IntegerField(default=1)
    c_Total = models.DecimalField(max_digits=10,decimal_places=2)
    c_DateTime = models.DateTimeField(auto_now=True,editable=False)
    cartstatus = (
        ('pending','PENDING'),
        ('inorder','INORDER'),
    )
    c_Status = models.CharField(max_length=20,choices=cartstatus)

    def __str__(self):
        return str(self.cart_id)

class ShippingAddress(models.Model):
    shipadd_id = models.AutoField(primary_key=True)
    First_Name = models.CharField(max_length=100,null=True)
    Last_Name = models.CharField(max_length=100,null=True)
    Email = models.EmailField(max_length=150, null=True)
    Mobile = models.CharField(max_length=10,null=True)
    Address = models.TextField(max_length=1000,null=True)
    Area_Name = models.ForeignKey(Area, on_delete=models.CASCADE,null=True)
    lid = models.ForeignKey(SignUpUser, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.shipadd_id)
    
    
class Order_Details(models.Model):
    o_id = models.AutoField(primary_key=True)
    lid = models.ForeignKey(SignUpUser, on_delete=models.CASCADE,null=True)
    Cart_Items = models.ManyToManyField(Cart_Items)
    shipadd_id = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE,null=True)  
    orderstatus = (
        ('pending','PENDING'),
        ('placed','PLACED'),
        ('cancled','CANCLED'),
        ('inreplace','INREPLACE'),
        ('replaced','REPLACED') 
    )
    o_Status = models.CharField(max_length=20,choices=orderstatus)
    o_DateTime = models.DateTimeField(auto_now=True,editable=False)
    Grand_Total = models.DecimalField(max_digits=10,decimal_places=2)
    Payment_Status = models.CharField(max_length=20, null=True)

    def __str__(self):
        return str(self.o_id)


class Stock_Details(models.Model):
    sto_id = models.AutoField(primary_key=True)
    p_id = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    sto_Quantity = models.IntegerField(null=True)

    def __str__(self):
        return str(self.sto_id)
    

class Shipping(models.Model):
    Ship_id = models.AutoField(primary_key=True)
    Area_Name= models.ForeignKey(Area, on_delete=models.CASCADE, null=True)
    Ship_Charege = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return str(self.Ship_id)


class Wishlist(models.Model):
    W_id = models.AutoField(primary_key=True)
    lid = models.ForeignKey(SignUpUser , on_delete=models.CASCADE, null=True)
    p_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.W_id)

class Card_Details(models.Model):
    card_id = models.AutoField(primary_key=True)
    Card_Number = models.IntegerField(null=True)
    Card_Name = models.CharField(max_length=100,null=True)
    Cvv_Code = models.IntegerField( null=True)
    Expire_Date = models.IntegerField(null=True)
    Balance = models.DecimalField(max_digits=12,decimal_places=2,null=True)

    def __str__(self):
        return  str(self.card_id)
    
class Delivery_Signup(models.Model):
    d_id = models.AutoField(primary_key=True)
    Mobile = models.CharField(max_length=10,null=True)
    Email = models.EmailField(max_length=100,null=True)
    Password = models.CharField(max_length=16,null=True)
    OTP = models.CharField(max_length=6,null=True)
    Token = models.CharField(max_length=200,null=True)
    Active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.d_id)
    
class Deliery_Profile(models.Model):
    dp_id = models.AutoField(primary_key=True)
    d_id = models.ForeignKey(Delivery_Signup, on_delete=models.CASCADE, null=True)
    First_Name = models.CharField(max_length=50,null=True)
    Last_Name = models.CharField(max_length=50, null=True)
    DOB = models.DateField(null=True)
    Address = models.TextField(max_length=500, null=True)
    Area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True)
    dp = models.ImageField(upload_to='myapp/media',null=True)

    def __str__(self):
        return str(self.dp_id)
    

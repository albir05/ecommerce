from django.shortcuts import render,HttpResponse,redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import Product,Cart,Order
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail

# Create your views here.

def about(request):
    return HttpResponse("This is about page")


# def home(request):
#     return HttpResponse("This is Index page")

def edit(request,rid):
    print("Id to be edited: ",rid)
    print(type(rid))
    return HttpResponse("Id to be edited "+rid)

def addition(request,x1,x2):
    a=int(x1)+int(x2)
    print("Addition is: ",a)
    return HttpResponse("addition is : "+str(a))    

class SimpleView(View):
    def get(self,request):
        return HttpResponse("Hello from django class based views")

def hello(request):
    context={}
    context['greet']='Good evening,we are learning DTL'
    context['x']=20
    context['y']=100
    context['l']=[10,20,30,40,50]
    context['products']=[
        
           {'id':1,'name':'samsung','cat':'mobile','price':2000},
           {'id':2,'name':'jeans','cat':'clothes','price':750},
           {'id':3,'name':'woodland','cat':'shoes','price':4500},
           {'id':4,'name':'Tshirt','cat':'clothes','price':450},
         ]
    return render (request,'hello.html',context)    

    #========================================
def index(request):
    # userid=request.user.id
    # print("id is logged in: ",userid)
    #print(request.user.is_authenticated)
    context={}
    p=Product.objects.filter(is_active=True)
    print(p)
    context['products']=p
    return render(request,'index.html',context)
        

def product_details(request,pid):
    p=Product.objects.filter(id=pid) #[object]
    print(p)
    context={}
    context['products']=p
    return render(request,'product_details.html',context)    

def register(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        context={}
        if uname=="" or upass=="" or ucpass=="":
         context['errmsg']="Fields cannot be empty"
        elif upass!=ucpass:
            context['errmsg']="Password and Confirm password did not match"
        else: 
            try:
                u=User.objects.create(password=upass,username=uname,email=uname)
                u.set_password(upass)
                u.save()
                context['success']="User created successfully"
            except Exception:
                context['errmsg']="User with same name already exist"    
        return render(request,'register.html',context)
    else:    
        return render(request,'register.html')   

def user_login(request):
    if request.method=='POST':
         uname=request.POST['uname']
         upass=request.POST['upass']
        #  print(uname)
        #  print(upass)
         context={}
         if uname=="" or upass=="":
            context['errmsg']="Fields cannot be empty"
            return render(request,'login.html',context)
         else:
            u=authenticate(username=uname,password=upass)
            print(u)
            if u is not None:
                login(request,u)
                return redirect('/')
            else:
                context['errmsg']="Invalid Username and Password"
                return render(request,'login.html',context)    
               
    else:
        return render(request,'login.html') 

def user_logout(request):
    logout(request)
    return redirect('/')

def catfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(cat=cv)
    p=Product.objects.filter(q1 & q2)
    #print(p)
    context={}
    context['products']=p
    return render(request,'index.html',context)  

def sort(request,sv):
    if sv == '0':
        #ascending order
        col='price'
    else:
        #descending order
        col='-price'
    p=Product.objects.filter(is_active=True).order_by(col)    
    context={}
    context['products']=p
    return render(request,'index.html',context)              

def range(request):
    # min and max value by GET method
    min=request.GET['min']
    max=request.GET['max']
    q1=Q(is_active="True")
    q2=Q(price__gte=min)
    q3=Q(price__lte=max)
    p=Product.objects.filter(q1 & q2 & q3)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def addtocart(request,pid):
    if request.user.is_authenticated:
        userid=request.user.id
        # print(userid)
        #print(pid)  
        u=User.objects.filter(id=userid)
        p=Product.objects.filter(id=pid)
        #print(u[0],p[0])
        #check product exist or not
        q1=Q(uid=u[0]) #3
        q2=Q(pid=p[0]) #6
        c=Cart.objects.filter(q1 & q2) #[cart object 3]
        n=len(c) #1
        context={}
        context['products']=p
        if n==1:
            context['errmsg']="Product already exist in cart!!"
        else:
            c=Cart.objects.create(uid=u[0],pid=p[0])
            c.save()
            context['success']="Product added successfully to Cart!!"
        return render(request,'product_details.html',context) 
    else:
        return redirect('/login')    

def viewcart(request):
    c=Cart.objects.filter(uid=request.user.id)
    # print(c)   #[cart object 3,cart object 4]
    # print(c[0].uid)   #thirduser@gmail.com ->object of user
    # print(c[0].pid)    #product object (6) ->object of product
    # print(c[0].uid.email)
    # print(c[0].uid.username)
    # print(c[0].pid.name)
    # print(c[0].pid.price)
    context={}
    s=0
    np=len(c)
    for x in c:
        s=s+ x.pid.price*x.qty
    print(s)    
    context['data']=c
    context['total']=s
    context['n']=np
    return render(request,'cart.html',context)

def remove(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')    

def updateqty(request,qv,cid):
    c=Cart.objects.filter(id=cid)
    print(c)
    print(c[0].qty)
    if qv == '1':
        t=c[0].qty+1
        c.update(qty=t)
    else:
        if c[0].qty>1:
            t=c[0].qty-1
            c.update(qty=t)
    return redirect('/viewcart')            

def placeorder(request):
    userid=request.user.id
    c=Cart.objects.filter(uid=userid)
    # print(c)
    oid=random.randrange(1000,9999)
    print(oid)
    for x in c:
        # print(x.uid)
        o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()
        x.delete()   # from cart table
    orders=Order.objects.filter(uid=userid)
    context={}
    context['data']=orders
    s=0
    np=len(orders)
    for x in orders:
        s=s+ x.pid.price*x.qty    # 14000+700
    context['total']=s
    context['n']=np
    return render(request,'placeorder.html',context)

def premove(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/placeorder')  

def makepayment(request):
    orders=Order.objects.filter(uid=request.user.id)
    s=0
    np=len(orders)
    for x in orders:
        s=s+ x.pid.price*x.qty
        oid=x.order_id
    client = razorpay.Client(auth=("rzp_test_pjmfONoAV5hhRJ", "2qLFlWxOv0vaA1jxWEEHwbcA"))
    data = { "amount": s*100, "currency": "INR", "receipt": oid }
    payment = client.order.create(data=data)
    #print(payment)
    uemail=request.user.email
    #print(email)
    context={}
    context['data']=payment
    context['uemail']=uemail
    return render(request,'pay.html',context)

def sendusermail(request,uemail):
    #we cant access email directly here so we have to pass from above function
    msg="Order details are:......"
    send_mail(
        "Ekart order placed successfully!!",
        msg,
        "kauralbir@gmail.com",
        [uemail],
        fail_silently=False,
    )
    return HttpResponse("Mail sent successfully")
        
       
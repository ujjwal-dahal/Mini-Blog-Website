from django.shortcuts import render , redirect , get_object_or_404
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.models import User , Group
from django.contrib.auth import authenticate , login , logout
from .models import Post , ContactForm

def home_page(request):
    objects = Post.objects.all()
    return render(request,"blog/home.html",{"data":objects})

def about_us(request):
    return render(request,"blog/aboutus.html")

def contact_us(request):
    if request.method == "POST":
        fullname = request.POST["fname"]
        email_address = request.POST["email"]
        number = request.POST["number"]
        address = request.POST["address"]
        msg = request.POST["message"]
        
        if fullname =="" or email_address=="" or number =="" or address=="" or msg=="":
            messages.error(request,"All Input Must Filled !!")
            return redirect("contact_us")
        
        if len(number)!=10:
            messages.error(request,"Enter 10 Digits Number !!")
            return redirect("contact_us")
        
        else:
            ContactForm.objects.create(
                fullname = fullname,
                email = email_address,
                phone = number,
                address = address,
                message = msg
            )
            messages.success(request,"Form Submitted Successfully !!")
            return redirect("contact_us")
            
        
    return render(request,"blog/contact.html")

def dashboard(request):
    
    if request.user.is_authenticated:
        user = request.user
        full_name = user.get_full_name()
        gps = user.groups.all()
        
        if user.is_staff or user.is_superuser:
            posts = Post.objects.all() 
            return render(request,"blog/dashboard.html",{"posts":posts,"full_name":full_name,"groups":gps})
        else: 
            posts = Post.objects.filter(author = request.user)
            return render(request,"blog/dashboard.html",{"posts":posts,"full_name":full_name,"groups":gps})
            
    else:
        return redirect("login")

def logout_page(request):
    if request.method == "POST":
        logout(request)
        messages.error(request,"Loggout Successfully !!")
        return redirect("home_page")
    return render(request,"blog/logout.html")

def register(request):
    form = RegisterForm()
    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        pass1 = request.POST["password1"]
        pass2 = request.POST["password2"]
        
        if len(username)>15:
            messages.error(request,"Character of username can't be more than 15 !!")
            return redirect("register")
        if User.objects.filter(username = username):
            messages.error(request,"Username already exist !!")
            return redirect("register")
        if pass1 != pass2:
            messages.error(request,"Password didnot match !!")
            return redirect("register")
        if username =="":
            messages.error(request,"Username can't be Empty !!")
            return redirect("register")
            
        else:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name = last_name,
                email=email,
                password=pass1
            )
            group = Group.objects.get(name="Author")
            user.groups.add(group)
            messages.success(request,"Congratulation You are now an Author !!")
            return redirect("login")
    return render(request,"blog/register.html",{"form":form})


def login_page(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            user_name = request.POST["username"]
            user_pass = request.POST["password"]
            
            new_user = authenticate(request, username=user_name,password = user_pass)
            if new_user is not None:
                login(request,new_user)
                messages.success(request,"Logged In Successfully !!")
                return redirect("dashboard")
            else:
                messages.error(request,"Invalid Credentials !!")
                return redirect("login")
    else:
        return redirect("dashboard")
    return render(request,"blog/login.html")


def add_post(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            title = request.POST["title"]
            desc = request.POST["desc"]
            
            if title == "" or desc =="":
                messages.error(request,"Title or Description Can't be Empty !!")
                return redirect("addpost")
            
            else:
                post = Post.objects.create(title=title,description=desc,author=request.user)
                post.save();
                messages.success(request,"Post Added Successfully!! ")
                return redirect("dashboard")
        return render(request,"blog/addpost.html")
    else:
        return redirect("login")


def edit_post(request,id):
    
    '''Certain Id ko Post Paune Object Form ma'''
    post = get_object_or_404(Post,pk=id)
    
    if request.user.is_authenticated:
        
        if request.method == "GET":
            post = Post.objects.get(pk=id)
            return render(request,"blog/editpost.html",{"post":post})
        
        if request.method == "POST":
            title = request.POST["title"]
            description = request.POST["desc"]
            
            '''Update Post'''
            post.title = title
            post.description = description
            post.save()
            
            messages.success(request,"Post Edited Successfully !!")
            return redirect("dashboard")
    else:
        return redirect("login")
    
    
def delete_post(request,id):
    if request.user.is_authenticated:
        if request.method == "POST":
            post = get_object_or_404(Post,pk = id)
            post.delete()
            return redirect("dashboard")
    return render(request,"blog/dashboard.html")
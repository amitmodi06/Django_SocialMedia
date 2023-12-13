from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile

# Create your views here.
@login_required(login_url='signin')
def index(request):
    return render(request, 'index.html')


@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST": 
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST.get('bio')
            location = request.POST.get('location')

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST.get('bio')
            location = request.POST.get('location')

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect('settings')
        
    context = {
        "user_profile" : user_profile
    }
    return render(request, 'setting.html', context)


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already taken.')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already taken.')
                return redirect('signup')                
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #login user and redirect to setting page 
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a profile object for the user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password does not match...!!')
            return redirect('signup')

    else:
        return render(request, 'signup.html')
    


def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("/")
        elif not User.objects.filter(username=username).exists():
            messages.info(request, "User does not exists.")
            return redirect('signin')
        else:
            messages.info(request, "Invalid Credentials.")
            return redirect("signin")
    else:
        return render(request, 'signin.html')
    


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')
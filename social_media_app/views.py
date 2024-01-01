from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Post, LikePost, FollowerCount
from itertools import chain

# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    posts = Post.objects.all()

    user_following_list = []
    feed = []

    user_followers = FollowerCount.objects.filter(follower=request.user.username)

    for user_follower in user_followers:
        user_following_list.append(user_follower.user)

    for username in user_following_list:
        feed_list = Post.objects.filter(user=username)
        feed.append(feed_list)

    feed_lists = list(chain(*feed))

    context = {
        "user_profile" : user_profile,
        "posts" : feed_lists
    }
    return render(request, 'index.html', context)


@login_required(login_url='signin')
def upload(request):
    user_object = User.objects.get(username=request.user.username)

    if request.method == "POST":
        user = user_object.username
        image = request.FILES.get("image_upload")
        caption = request.POST.get("caption")

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect("/")
    else:
        return redirect("/")
    

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST.get('username')
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for user in username_object:
            username_profile.append(user.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))

    context ={
        "user_profile" : user_profile,
        "username_profile_list" : username_profile_list,
    }

    return render(request, 'search.html', context)


@login_required(login_url='signin')
def like_post(request, post_id):
    username = request.user.username
    post = Post.objects.get(id=post_id)

    if post:
        like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

        if like_filter == None:
            new_like = LikePost.objects.create(post_id=post_id, username=username)
            new_like.save()
            post.no_of_likes = post.no_of_likes+1
            post.save()
            return redirect('index')
        else:
            like_filter.delete()
            post.no_of_likes = post.no_of_likes-1
            post.save()
            return redirect('index')

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowerCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = "Follow"

    user_followers = len(FollowerCount.objects.filter(user=user))
    user_following = len(FollowerCount.objects.filter(follower=user))

    context = {
        "user_object" : user_object,
        "user_profile" : user_profile,
        "user_posts" : user_posts,
        "user_post_length" : user_post_length,
        "button_text" : button_text,
        "user_followers" : user_followers,
        "user_following" : user_following,
    }
    return render(request, "profile.html", context)


@login_required(login_url='signin')
def follow(request):
    if request.method == "POST":
        follower = request.POST.get('follower')
        user = request.POST.get('user')

        if FollowerCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowerCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect("profile", pk=user)
        else:
            new_follower = FollowerCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect("profile", pk=user)
    else:
        return redirect("/")


@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST": 
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
        else:
            image = request.FILES.get('image')

        if request.FILES.get('baner-image') == None:
            print("#"*100)
            image_banner = user_profile.profilebanner
        else:
            print("$"*100)
            image_banner = request.FILES.get("baner-image")

        bio = request.POST.get('bio')
        location = request.POST.get('location')  

        user_profile.profileimg = image
        user_profile.profilebanner = image_banner
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
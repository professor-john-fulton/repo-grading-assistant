from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, "socialprojapp/register.html", {"form": form})
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("post_list")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "socialprojapp/login.html")
def logout(request):
    auth_logout(request)
    messages.success(request, "You are logged out")
    return redirect("login")
   
def post_list(request):
    search = request.GET.get('q', '')
    if search:
        posts = Post.objects.filter(
        title__icontains=search
        ) | Post.objects.filter(
            content__icontains=search
        )
    else:
        posts = Post.objects.all().order_by('-id')
    return render(request, 'socialprojapp/post.html', {'posts': posts, 'search': search})
def post_content(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'socialprojapp/content.html', {'post': post})

@login_required   
def post_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        Post.objects.create(title=title, content=content)
        return redirect('post_list')
    return render(request, 'socialprojapp/post_form.html')
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        post.title = request.POST.get("title")
        post.content = request.POST.get("content")
        post.save()
        return redirect('post_list')
    return render(request, 'socialprojapp/post_form.html', {'post': post})
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        post.delete()
        return redirect('post_list')
    return render(request, 'socialprojapp/post_delete.html', {'post': post})
 


from django.shortcuts import render, get_object_or_404, redirect
# from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .models import Post, Group
from .forms import PostForm
from .utils import my_paginator

User = get_user_model()


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    page_obj = my_paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    page_obj = my_paginator(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.all().filter(author__exact=user)
    page_obj = my_paginator(request, post_list)
    context = {
        'author': user,
        'page_obj': page_obj,

    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    context = {
        'post': post,
        'author': author
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    context = {
        'form': form,
    }
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)
    return render(request, 'posts/create_post.html', context)


def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    is_edit = True if request.user == post.author else False
    context = {
        'post_id': post_id,
        'is_edit': is_edit,
        'form': form,
    }
    if not is_edit:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', context)

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post
from .utils import get_padginator

User = get_user_model()


@cache_page(settings.CACHE_TIMEOUT, key_prefix='index_page')
def index(request):
    """Выводим шаблон главной страницы."""
    posts = Post.objects.select_related(
        'author',
        'group',
    )
    page_obj = get_padginator(posts, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Выводим шаблон с группами постов."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related(
        'author',
        'group',
    )
    page_obj = get_padginator(posts, request)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Выводит шаблон профиля пользователя."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related(
        'author',
        'group'
    )
    page_obj = get_padginator(posts, request)
    user = request.user
    following = user.is_authenticated and author.following.filter(
        user=user
    ).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Выводим на страницу подробную информацию о посте."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создаем форму для создания поста."""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post_create = form.save(commit=False)
        post_create.author = request.user
        post_create.save()
        return redirect(
            'posts:profile', post_create.author
        )
    context = {
        'form': form
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def post_edit(request, post_id):
    """Создаем форму для редактирования поста."""
    edit_post = get_object_or_404(Post, id=post_id)
    if request.user != edit_post.author:
        return redirect(
            'posts:post_detail', post_id
        )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=edit_post
    )
    if form.is_valid():
        form.save()
        return redirect(
            'posts:post_detail', post_id
        )
    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post = Post.objects.select_related(
        'author'
    ).filter(
        author__following__user=request.user
    )
    page_obj = get_padginator(post, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect(
        reverse(
            'posts:profile',
            kwargs={'username': username}
        )
    )


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    )
    author.delete()
    return redirect(
        'posts:profile',
        username=username
    )

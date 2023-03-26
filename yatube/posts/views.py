from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post
from .utils import get_padginator

User = get_user_model()


def index(request):
    """Выводим шаблон главной страницы."""
    posts = Post.objects.select_related(
        'author',
        'group',
    )
    context = {}
    context.update(get_padginator(posts.all(), request))
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Выводим шаблон с группами постов."""
    group = get_object_or_404(Group, slug=slug)
    context = {
        'group': group,
    }
    context.update(get_padginator(group.posts.select_related(
        'author',
        'group'
    ), request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Выводит шаблон профиля пользователя."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related()
    context = {
        'author': author,
        'posts': posts
    }
    context.update(get_padginator(author.posts.select_related(), request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Выводим на страницу подробную информацию о посте."""
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    posts_count = author.posts.select_related().count()
    context = {
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создаем форму для создания поста."""
    form = PostForm(request.POST or None)
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
    form = PostForm(request.POST or None, instance=edit_post)
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

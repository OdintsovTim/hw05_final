from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .forms import PostForm, CommentForm
from .models import Post, Group, Comment
from users.forms import User


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "index.html", {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 4)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    title = 'Добавить запись'

    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect('index')

    return render(request, "new_post.html", {'form': form, 'title': title})


def profile(request, username):
    author = get_object_or_404(User.objects.prefetch_related('posts'), username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'profile.html', {'author': author, 'page': page, 'paginator': paginator})


def post_view(request, username, post_id):
    post = get_object_or_404(Post.objects.select_related('author'), id=post_id, author__username=username)
    author = post.author
    comments = Comment.objects.filter(post=post)
    form = CommentForm()

    return render(request, 'post.html', {'author': author, 'post': post, 'comments': comments, 'form': form})


@login_required
def post_edit(request, username, post_id):

    post = get_object_or_404(Post.objects.select_related('author'), id=post_id, author__username=username)
    author = post.author

    if request.user != author:
        return redirect(f'/{author.username}/{post.id}/')

    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)

    if request.POST and form.is_valid():
        form.save()
        return redirect(f'/{author.username}/{post.id}/')

    title = 'Редактировать запись'

    return render(request, 'new_post.html', {'form': form, 'title': title, 'post': post})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post.objects.select_related('author'), id=post_id, author__username=username)

    if request.method == 'POST' and form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post = post
        new_comment.save()
        form = CommentForm()

    return redirect('post', username=username, post_id=post_id)

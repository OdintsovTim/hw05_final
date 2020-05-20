from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Post, Group


def index(request):
    latest = Post.objects.order_by('-pub_date')[:11]
    output = []

    return render(request, "index.html", {"posts": latest})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.order_by("-pub_date")[:12]

    return render(request, "group.html", {"group": group, "posts": posts})

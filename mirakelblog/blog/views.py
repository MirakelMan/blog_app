from django.core.paginator import EmptyPage, Paginator
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from .models import Post


# Create your views here.
def post_list(request: HttpRequest):
    all_posts = Post.published.all()
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get("page", 1)
    try:
        posts_to_display = paginator.page(page_number)
    except EmptyPage:
        posts_to_display = paginator.page(paginator.num_pages)
    return render(request, "blog/post/list.html", {"posts": posts_to_display})


def post_detail(request: HttpRequest, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    return render(request, "blog/post/detail.html", {"post": post})

from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from mirakelblog.settings import EMAIL_HOST_USER

from .forms import EmailPostForm
from .models import Post


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 5
    template_name = "blog/post/list.html"


# Create your views here.
def post_list(request: HttpRequest):
    all_posts = Post.published.all()
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get("page", 1)
    try:
        posts_to_display = paginator.page(page_number)
    except PageNotAnInteger:
        posts_to_display = paginator.page(1)
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


def post_share(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}."
            message = f"""Read {post.title} at {post_url} \n\n
            {cd['name']}\'s comments: {cd['comments']}"""
            send_mail(
                subject,
                message,
                EMAIL_HOST_USER,
                [cd["to"]],
            )
            sent = True
    else:
        form = EmailPostForm()
    return render(
        request, "blog/post/share.html", {"post": post, "form": form, "sent": sent}
    )

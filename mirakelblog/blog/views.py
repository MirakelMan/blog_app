from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from taggit.models import Tag

from mirakelblog.settings import EMAIL_HOST_USER

from .forms import CommentForm, EmailPostForm
from .models import Comment, Post


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 5
    template_name = "blog/post/list.html"


# Create your views here.
def post_list(request: HttpRequest, tag_slug=None):
    all_posts = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        all_posts = all_posts.filter(tags__in=[tag])
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get("page", 1)
    try:
        posts_to_display = paginator.page(page_number)
    except PageNotAnInteger:
        posts_to_display = paginator.page(1)
    except EmptyPage:
        posts_to_display = paginator.page(paginator.num_pages)
    return render(
        request, "blog/post/list.html", {"posts": posts_to_display, "tag": tag}
    )


def post_detail(request: HttpRequest, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    # list of active comments
    comments = post.comments.filter(active=True)
    # form for users to comment
    form = CommentForm()
    # list of similar posts
    # post_tags_ids = post.tags.values_list("id", flat=True)
    # similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    # similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by(
    #     "-same_tags", "-publish"
    # )[:4]
    similar_posts = post.tags.similar_objects()
    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
        },
    )


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


@require_POST
def post_comment(request: HttpRequest, id: int):
    post = get_object_or_404(Post, id=id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment: CommentForm = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form, "comment": comment},
    )

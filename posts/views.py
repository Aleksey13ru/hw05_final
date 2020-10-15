from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm


@cache_page(20 * 1)
def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 
                                          'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:12]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
                                          'group': group,
                                          'posts': posts,
                                          'page': page,
                                          'paginator': paginator
                                          })


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
#        text = request.POST.get('text') # убрать
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('index')
    return render(request, 'posts/new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_records = Post.objects.filter(author=author)
    paginator = Paginator(post_records, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'posts/profile.html', {'author': author,
                                                  'page': page,
                                                  'paginator': paginator,
                                                  'post_records': post_records})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    post_records = post.author.posts.count()
    form_comment = CommentForm()
    comments = Comment.objects.all()[:10]
    return render(request, 'posts/post.html', {'author': post.author,
                                               'post': post,
                                               'post_records': post_records,
                                               'comments': comments,
                                               'form_comment': form_comment})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user != post.author:
        return redirect('index')
    form = PostForm(request.POST or None, 
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post = form.save()
        return redirect('post', username=request.user.username,
                        post_id=post_id)
    return render(request, 'posts/new.html', {'form': form, 'post': post})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form_comment = CommentForm(request.POST or None)
    if request.method == "POST":
        if form_comment.is_valid():
            new_comment = form_comment.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
            return redirect('post', username=request.user.username, post_id=post_id) # перенаправить
        return redirect('post', username=request.user.username, post_id=post_id) #
    form_comment = CommentForm()    
    return redirect('post', username=request.user.username, post_id=post_id) #   


@login_required
def follow_index(request):
    '''Функция страницы, куда будут выведены посты авторов, на которых подписан текущий пользователь'''
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/follow.html', {'page': page,
                                           'paginator': paginator})

    
@login_required
def profile_follow(request, username):
    '''Функция для подписки на интересного автора'''
    author = get_object_or_404(User, username=username) # author пользователь, на которого подписываются
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)
    

@login_required
def profile_unfollow(request, username):
    '''Функция для того, чтобы отписаться от надоевшего графомана'''
    author = get_object_or_404(User, username=username) # author пользователь, на которого подписываются
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
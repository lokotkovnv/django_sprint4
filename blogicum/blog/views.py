from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Count

from blog.models import Post, Category, Comment
from blog.forms import PostForm, UserProfileForm, CommentForm


def index(request):
    post_list = (
        Post.objects
            .filter(
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, id):
    template = 'blog/detail.html'
    current_time = timezone.now()

    if request.user.is_authenticated and Post.objects.filter(
        id=id, author=request.user
    ).exists():
        post = get_object_or_404(Post, id=id)
    else:
        post = get_object_or_404(
            Post.objects.filter(
                pub_date__lte=current_time,
                is_published=True,
                category__is_published=True
            ).annotate(comment_count=Count('comments')),
            id=id
        )

    comments = post.comments.all()
    comment_form = CommentForm()
    context = {'post': post, 'comments': comments, 'form': comment_form}
    return render(request, template, context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
        )
    now = timezone.now()
    category_posts = category.posts.filter(
        pub_date__lte=now,
        is_published=True
        )
    paginator = Paginator(category_posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


User = get_user_model()


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    if request.user == profile:
        user_posts = profile.posts.annotate(
            comment_count=Count('comments')
            ).order_by('-pub_date')
    else:
        user_posts = profile.posts.filter(
            is_published=True, pub_date__lte=timezone.now()
            ).annotate(comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    login_url = '/login/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
            )


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.request.user.pk)

    def form_valid(self, form):
        form.save()
        return redirect(reverse(
            'blog:profile', kwargs={'username': self.request.user.username})
            )


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('blog:post_detail', id=self.get_object().id)
        return super().handle_no_permission()

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'id': self.object.id})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'id': self.object.post.id}
        )


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'id': self.object.post.id}
            )


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'id': self.object.post.id})

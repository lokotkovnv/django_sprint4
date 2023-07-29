from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Count
from django.conf import settings
from django.http import HttpResponseRedirect

from blog.models import Post, Category, Comment, User
from blog.forms import PostForm, UserProfileForm, CommentForm


def index(request):
    post_list = (
        Post.published.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    )
    paginator = Paginator(post_list, settings.PAX_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, id):
    template = 'blog/detail.html'
    post = get_object_or_404(Post, id=id)
    if not request.user.is_authenticated or request.user != post.author:
        post = get_object_or_404(Post.published.filter(
            id=id,
        ).annotate(comment_count=Count('comments')))

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
    category_posts = Post.published.filter(
        category=category
    )
    paginator = Paginator(category_posts, settings.PAX_POSTS_PER_PAGE)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    if request.user == profile:
        user_posts = profile.posts.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    else:
        user_posts = Post.published.filter(
            author=profile.id
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    paginator = Paginator(user_posts, settings.PAX_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

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


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return HttpResponseRedirect(
                reverse('blog:post_detail', args=[obj.id])
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'id': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return HttpResponseRedirect(
                reverse('blog:post_detail', args=[obj.id])
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_delete'] = True
        context['post'] = self.get_object()
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'id': self.object.post.id}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return HttpResponseRedirect(
                reverse('blog:post_detail', args=[obj.post.id])
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'id': self.object.post.id}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return HttpResponseRedirect(
                reverse('blog:post_detail', args=[obj.post.id])
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'id': self.object.post.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_delete'] = True
        return context

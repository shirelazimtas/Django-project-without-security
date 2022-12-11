from django.shortcuts import render, get_object_or_404 ,redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db import connection
from django.utils import timezone
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'project/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'project/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'project/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


#class PostCreateView(LoginRequiredMixin, CreateView):
#    model = Post
#    fields = ['title', 'content']
#
#    def form_valid(self, form):
#        form.instance.author = self.request.user
#        return super().form_valid(form)

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'author']

    def form_valid(self,request, *args, **kwargs):
        title = self.request.POST.get("title")
        content = self.request.POST.get("content")
        author = self.request.POST.get("author")
        cursor = connection.cursor()
        query = "INSERT INTO project_post (title, content, author_id, " \
                "date_posted) VALUES ('%s', '%s', '%s', '%s')" \
                % (title, content, author,timezone.now)
        result = cursor.execute(query)
        return redirect('post-detail', result.lastrowid)



class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'project/about.html', {'title': 'About'})

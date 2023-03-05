from django.shortcuts import render
from .models import Post
from django.views.generic import ListView, DetailView, CreateView


class PostListView(ListView):
    model = Post
    ordering = ['-date_posted']

class PostDetailView(DetailView):
    model = Post

class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'content']
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

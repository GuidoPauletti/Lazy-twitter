import openai
import os
from .models import Post
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

openai.api_key = os.environ['OpenAI_SecretKey']

class PostListView(ListView):
    model = Post
    ordering = ['-date_posted']
    paginate_by = 5

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        return Post.objects.filter(author=user).order_by('-date_posted')

class PostDetailView(DetailView):
    model = Post

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title']
    success_url = '/'

    def form_valid(self, form):
        title = form.cleaned_data['title']
        prompt = f"Write content for a post with the following title: '{title}'."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = [
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5
        )
        post_text = response['choices'][0]['message']['content']
        post = form.save(commit=False)
        post.author = self.request.user
        post.content = post_text
        post.save()
        return super().form_valid(form)

    #def form_valid(self, form):
        #form.instance.author = self.request.user
        #return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user
    
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    
    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user
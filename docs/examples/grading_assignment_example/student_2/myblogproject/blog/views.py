from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Comment
from .forms import CommentForm
#from django.contrib.auth.mixins import LoginRequiredMixin 
from django.urls import reverse, reverse_lazy
from django.db.models import Q

# Home view with search functionality
class HomeView(ListView):
    model = Post
    template_name = 'home.html'
    ordering = ['-created_at']  # Newest posts first

    def get_queryset(self):
            # Start with the default queryset (all posts, ordered)
            queryset = super().get_queryset()
            
            # Get the search query from the GET parameters
            query = self.request.GET.get('q')
            
            # If a query exists, filter the queryset
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) | Q(content__icontains=query)
                )
                
            return queryset

# Detail view for a single post
class PostDetailView(DetailView):
    model = Post
    template_name = 'post_details.html'

# Create view for a new post
class PostCreateView(CreateView):
    model = Post
    template_name = 'post_new.html'
    fields = ['title', 'content']
    success_url = reverse_lazy('home')

    # Automatically set the author to the current user
    def form_valid(self, form):
            form.instance.author = self.request.user            
            return super().form_valid(form)

# Update view for an existing post
class PostUpdateView(UpdateView):
    model = Post
    template_name = 'post_update.html'
    fields = ['title', 'content']

# Delete view for a post
class PostDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('home')

# Create view for a new comment
class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comment_new.html'
    success_url = reverse_lazy('home')

    # Pre-fill the 'name' field if the user is authenticated
    def get_initial(self):
            initial = super().get_initial()
            
            if self.request.user.is_authenticated:
                full_name = f"{self.request.user.first_name} {self.request.user.last_name}"
                initial['name'] = full_name
                
            return initial

    # Link the comment to the correct post
    def form_valid(self, form):
        form.instance.post_id = self.kwargs['pk']           
        return super().form_valid(form)
    
    # Redirect to the post detail page after submitting a comment
    def get_success_url(self):
        post_pk = self.kwargs['pk'] 
        return reverse('post_details', kwargs={'pk': post_pk})
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.core.cache import cache

from .models import Post, User


class PostsCasesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="Useeer", 
                                             email="email@mail.ru", 
                                             password="qwerty")
        self.client.force_login(self.user)
        self.anonymous = Client()
        self.post = Post.objects.create(text=("Test post"), author=self.user)
        self.reverse_index = reverse('index')
        self.reverse_new = reverse('new_post')
        self.reverse_post = reverse('post', args=[self.user.username,
                                                     self.post.id])
        self.reverse_profile = reverse('profile', args=[self.user.username])                                             
        self.reverse_post_edit = reverse('post_edit', args=[self.user.username,
                                                            self.post.id])

    def test_user_post(self):
        """Авторизованный пользователь может опубликовать пост (new)"""        
        old_count = Post.objects.count()
        self.client.post(reverse('new_post'), {'text': 'Test post', 'author': self.user}, follow=True)
        self.assertEqual(Post.objects.count(), old_count + 1)    
   
    def test_logout_post(self):
        """Неавторизованный посетитель не может опубликовать пост (его редиректит на страницу входа)"""
        old_count = Post.objects.count()
        self.anonymous.post(reverse('new_post'), {'text': 'Test post', 'author': self.user}, follow=True)
        self.assertEqual(Post.objects.count(), old_count)       
    
    def plug_new(self, arg):
        response = self.client.get(arg)
        self.assertContains(response, self.post.text)   
    
    def test_new_post_index(self):
        """После публикации поста новая запись появляется на главной странице сайта (index)"""
        self.plug_new(self.reverse_index)
         
    def test_new_post_profile(self):
        """После публикации поста новая запись появляется на персональной странице пользователя (profile)"""
        self.plug_new(self.reverse_profile)
      
    def test_new_post_view(self):
        """После публикации поста новая запись появляется на отдельной странице поста (post)"""
        self.plug_new(self.reverse_post)
    
    def plug_edit(self, arg):
        self.new_text = "New Test"
        self.client.post(reverse('post_edit', args=[self.user.username, self.post.id]), {'text': self.new_text})
        response = self.client.get(arg)
        self.assertContains(response, self.new_text)
       
    def test_postedit_index(self):
        """Авторизованный пользователь может отредактировать свой пост
        и его содержимое изменится на главной странице сайта (index)"""
        cache.clear()
        self.plug_edit(self.reverse_index)

    def test_postedit_profile(self):
        """Авторизованный пользователь может отредактировать свой пост
           и его содержимое изменится на персональной странице пользователя (profile)"""
        self.plug_edit(self.reverse_profile)
    
    def test_postedit_view(self):
        """Авторизованный пользователь может отредактировать свой пост
           и его содержимое изменится на отдельной странице поста (post)"""
        self.plug_edit(self.reverse_post)

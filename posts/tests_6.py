from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.core.cache import cache

from .models import Post, User, Group


class Error404CaseTest(TestCase):
    """Возвращает ли сервер код 404"""
    def test_wrong_url_returns_404(self):
        response = self.client.get('/something/really/weird/')
        self.assertEqual(response.status_code, 404)

class ImgCaseTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="User", 
                                             email="email@mail.ru", 
                                             password="qwerty")
        self.client.force_login(self.user)
        self.post = Post.objects.create(text=("Test post"), author=self.user)
        self.group = Group.objects.create(title="TestGroup", slug="testgroup", description="TestDesc")
        self.reverse_index = reverse('index')
        #self.reverse_new = reverse('new_post')
        self.reverse_post = reverse('post', args=[self.user.username,
                                                     self.post.id])
        self.reverse_profile = reverse('profile', args=[self.user.username])                                             
        self.reverse_group = reverse('group_posts', args=[self.group.slug])          
        with open('C:/Users/saint/OneDrive/Рабочий стол/загруженное.jpg','rb') as img: 
            post = self.client.post(reverse('post_edit', args=[self.user.username, self.post.id]),
                                    {'author': self.user, 'group': '1', 'text': 'post with image', 'image': img})                                        

    def plug_img(self, arg):
        response = self.client.get(arg)
        self.assertContains(response, "<img")   
    
    def test_img_index(self):
        """При публикации поста с изображнием на главной странице есть тег <img>"""
        self.plug_img(self.reverse_index)        

    def test_img_profile(self):
        """При публикации поста с изображнием на странице профайла есть тег <img>"""
        self.plug_img(self.reverse_profile)

    def test_img_view(self):
        """При публикации поста с изображнием на отдельной странице поста (post) есть тег <img>"""
        self.plug_img(self.reverse_post)

    def test_img_group(self):
        """При публикации поста с изображнием на странице группы есть тег <img>"""
        self.plug_img(self.reverse_group)

    def test_no_img(self):
        """Срабатывает защита от загрузки файлов не-графических форматов"""
        with open('C:/Users/saint/OneDrive/Рабочий стол/Джанго.txt','rb') as img: 
            post = self.client.post(reverse('post_edit', args=[self.user.username, self.post.id]),
                                    {'author': self.user, 'group': '1', 'text': 'post with image', 'image': img})                                   
        response = self.client.get(self.reverse_index)
        cache.clear()
        self.assertNotContains(response, "<img")


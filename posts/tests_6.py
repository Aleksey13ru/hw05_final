from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.core.cache import cache

from .models import Post, User, Group, Comment


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
        self.group = Group.objects.create(title="TestGroup",
                                         slug="testgroup",
                                         description="TestDesc")
        self.reverse_index = reverse('index')
        self.reverse_post = reverse('post', args=[self.user.username,
                                                 self.post.id])
        self.reverse_profile = reverse('profile', args=[self.user.username])
        self.reverse_group = reverse('group_posts', args=[self.group.slug])

    def plug_img(self, arg):
        with open('fixtures/загруженное.jpg','rb') as img:
            post = self.client.post(reverse('post_edit', args=[self.user.username,
                                                              self.post.id]),
        {'author': self.user, 'group': '1', 'text': 'post with image', 'image': img})
        response = self.client.get(arg)
        self.assertContains(response, "<img")

    def test_img_index(self):
        """При публикации поста с изображнием на главной странице есть тег <img>"""
        self.plug_img(self.reverse_index)

    def test_img_profile(self):
        """При публикации поста с изображнием на странице профайла есть тег <img>"""
        self.plug_img(self.reverse_profile)

    def test_img_view(self):
        """При публикации поста с изображнием на отдельной странице поста
        (post) есть тег <img>"""
        self.plug_img(self.reverse_post)

    def test_img_group(self):
        """При публикации поста с изображнием на странице группы есть тег <img>"""
        self.plug_img(self.reverse_group)

    def test_no_img(self):
        """Срабатывает защита от загрузки файлов не-графических форматов"""
        cache.clear()
        self.post = Post.objects.create(text=("Test post"), author=self.user)
        with open('fixtures/Джанго.txt', 'rb') as img:
            post = self.client.post(reverse('post_edit', args=[self.user.username,
                                            self.post.id]),
            {'author': self.user, 'group': '1', 'text': 'post with image', 'image': img})
        response = self.client.get(self.reverse_index)
        self.assertNotContains(response, "<img")


class CacheCaseTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="User",
                                            email="email@mail.ru",
                                            password="qwerty")
        self.client.force_login(self.user)
        self.reverse_index = reverse('index')

    def test_cache_index(self):
        """Тестирование функции кэша"""
        cache.clear()
        self.client.get(self.reverse_index)
        self.post = Post.objects.create(text="Test post", author=self.user)
        self.new_text = "New Test"
        self.client.post(reverse('post_edit', args=[self.user.username,
                                                   self.post.id]),
                                                   {'text': self.new_text})
        response = self.client.get(self.reverse_index)
        self.assertNotContains(response, self.new_text)


class FollowCaseTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="User",
                                             email="email@mail.ru",
                                             password="qwerty")
        self.user2 = User.objects.create_user(username="User2",
                                             email="email2@mail.ru",
                                             password="qwertyu")
        self.user3 = User.objects.create_user(username="User3",
                                             email="email3@mail.ru",
                                             password="qwertyui")
        self.client.login(username="User", password="qwerty")
        self.post = Post.objects.create(text="Test post", author=self.user3)


    def test_follow(self):
        """Авторизованный пользователь может подписываться на других пользователей"""
        self.client.get(reverse('profile_follow', args=[self.user2]))
        response = self.client.get(reverse('profile', args=[self.user]))
        self.assertEqual(response.context["followed"], 1)

    def test_unfollow(self):
        """Авторизованный пользователь может удалять других пользователей из подписок."""
        self.client.get(reverse('profile_unfollow', args=[self.user2]))
        response = self.client.get(reverse('profile', args=[self.user]))
        self.assertEqual(response.context["followed"], 0)

    def test_news_lent(self):
        """Новая запись пользователя появляется в ленте тех, кто на него подписан"""
        self.client.get(reverse('profile_follow', args=[self.user3]))
        response = self.client.get(reverse('follow_index'))
        self.assertContains(response, "Test post")

    def test_no_news_lent(self):
        """Новая запись пользователя не появляется в ленте тех, кто не подписан на него"""
        self.client.get(reverse('profile_unfollow', args=[self.user3]))
        cache.clear()
        response = self.client.get(reverse('follow_index'))
        self.assertNotContains(response, "Test post")


class CommentCaseTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="User",
                                             email="email@mail.ru",
                                             password="qwerty")
        self.client.force_login(self.user)
        self.anonymous = Client()
        self.post = Post.objects.create(text="Test post", author=self.user)
        self.reverse_post = reverse('post', args=[self.user.username,
                                                      self.post.id])
        self.reverse_add_comment = reverse('add_comment', args=[self.user.username,
                                                             self.post.id])

    def test_comment_authorized(self):
        """Авторизированный пользователь может комментировать посты."""
        self.client.post(self.reverse_add_comment, {'text': 'Test comment'})
        response = self.client.get(self.reverse_post)
        self.assertContains(response, "Test comment")

    def test_comment_not_authorized(self):
        """Не авторизированный пользователь не может комментировать посты."""
        self.anonymous.post(self.reverse_add_comment, {"text": "Test comment"})
        response = self.client.get(self.reverse_post)
        self.assertNotContains(response, "Test comment")

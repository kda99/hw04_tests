from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User

INDEX = reverse('posts:index', None)
POST_CREATE = reverse('posts:post_create')


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
        )
        cls.user = User.objects.create_user(username='HasNoName')

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author.force_login(self.author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            INDEX: 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.author}):
                'posts/profile.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            POST_CREATE: 'posts/create_post.html',
        }

        for address, template in templates_url_names.items():
            if address not in (reverse('posts:post_edit', kwargs={
                    'post_id': self.post.pk}), POST_CREATE):
                with self.subTest(address=address):
                    response = self.guest_client.get(address)
                    self.assertTemplateUsed(response, template)

        for address, template in templates_url_names.items():
            if address not in (reverse('posts:post_edit', kwargs={
                    'post_id': self.post.pk}),):
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)
                    self.assertTemplateUsed(response, template)

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)

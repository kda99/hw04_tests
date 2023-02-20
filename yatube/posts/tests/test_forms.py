import tempfile
from http import HTTPStatus

from ..forms import PostForm
from ..models import Group, Post
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


User = get_user_model()


class TaskPostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='test_post',
            author=cls.author,
            group=cls.group
        )
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.user = User.objects.create_user(username='User')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Task
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }

        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(text='Тестовый текст').count())

    def test_edit_post(self):
        """Валидная форма редактирует пост"""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', args=({self.post.id})),
            data=form_data,
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            "posts:post_detail", kwargs={"post_id": self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            text='Отредактированный текст').count())

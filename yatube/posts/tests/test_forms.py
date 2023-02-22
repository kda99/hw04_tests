from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

POST_CREATE = reverse('posts:post_create')


class PostFormTest(TestCase):
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

    def setUp(self):
        self.user = User.objects.create_user(username='User')
        self.anonim_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post_anonim(self):
        """аноним не может создать пост"""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }

        response = self.anonim_client.post(
            POST_CREATE,
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            POST_CREATE,
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        last_post = Post.objects.order_by('-id')[0]

        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.author, self.author)

    def test_edit_post_anonim(self):
        """аноним не может отредактировать пост"""
        posts_count = Post.objects.count()
        POST_EDIT = reverse('posts:post_edit', args=({self.post.id}))
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id,
        }

        self.anonim_client.post(
            POST_EDIT,
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(not Post.objects.filter(
            text='Отредактированный текст').count())

    def test_edit_post(self):
        """Валидная форма редактирует пост"""
        posts_count = Post.objects.count()
        POST_EDIT = reverse('posts:post_edit', args=({self.post.id}))
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            POST_EDIT,
            data=form_data,
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            "posts:post_detail", kwargs={"post_id": self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            text='Отредактированный текст').count())

        last_post = Post.objects.order_by('-id')[0]

        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.author, self.author)

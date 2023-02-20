from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
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
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_pages_uses_correct_template_quest(self):
        """URL-адрес использует соответствующий шаблон для guest_users"""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index', None),
            'posts/group_list.html':
                reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            'posts/profile.html':
                reverse('posts:profile', kwargs={'username': self.author}),
            'posts/post_detail.html':
                reverse('posts:post_detail', kwargs={'post_id': self.post.pk}
                        ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_uses_correct_template_user(self):
        """URL-адрес использует соответствующий шаблон для auth_users"""
        templates_pages_names = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def assert_post_response(self, response):
        """Проверяем Context"""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse('posts:post_create'))
        self.assert_post_response(response)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        self.assert_post_response(response)

    def test_post_list_page_show_correct_context(self):
        """Шаблон post_list сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.id
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, self.post.pk)
        self.assertEqual(post_author_0, self.author)
        self.assertEqual(post_group_0, self.group)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_author = Client()
        cls.author = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test-slug'
        )

    def setUp(self):
        for post_temp in range(13):
            Post.objects.create(
                text=f'text{post_temp}', author=self.author, group=self.group
            )

    def test_first_page_contains_ten_records(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
                reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            'posts/profile.html':
                reverse('posts:profile', kwargs={'username': self.author}),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), 10
                )

    def test_second_page_contains_three_records(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index') + '?page=2',
            'posts/group_list.html':
                reverse('posts:group_list',
                        kwargs={'slug': self.group.slug}) + '?page=2',
            'posts/profile.html':
                reverse('posts:profile',
                        kwargs={'username': self.author}) + '?page=2',
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(
                    response.context['page_obj']), 3
                )

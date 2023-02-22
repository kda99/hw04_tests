from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post, User

INDEX = reverse('posts:index')
GROUP_LIST = reverse('posts:group_list', kwargs={'slug': 'test-slug'})
POST_CREATE = reverse('posts:post_create')
PAGE_IN_PAGINATOR = 10


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

    def assert_form_context(self, response):
        """Проверяем Context в form"""
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
        response = self.authorized_author.get(POST_CREATE)
        self.assert_form_context(response)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        self.assert_form_context(response)

    def test_post_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_author.get(GROUP_LIST)
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.id
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, self.post.pk)
        self.assertEqual(post_author_0, self.author)
        self.assertEqual(post_group_0, self.group)

    def test_post_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_author.get(GROUP_LIST)
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.id
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, self.post.pk)
        self.assertEqual(post_author_0, self.author)
        self.assertEqual(post_group_0, self.group)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_author.get(INDEX)
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.id
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, self.post.pk)
        self.assertEqual(post_author_0, self.author)
        self.assertEqual(post_group_0, self.group)

    def test_post_another_group(self):
        another_group = Group.objects.create(
            title='another_group',
            description='another_group_description',
            slug='1'
        )
        Post.objects.create(
            text='another_group_test_post',
            author=self.author,
            group=another_group
        )
        response = self.authorized_author.get(GROUP_LIST)
        for post in response.context['page_obj']:
            self.assertNotEqual(post.group, another_group)


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
        for post_temp in range(13):
            Post.objects.create(
                text=f'text{post_temp}', author=cls.author, group=cls.group
            )

    def test_first_page_contains_ten_records(self):
        templates_pages_names = {
            'posts/index.html': INDEX,
            'posts/group_list.html':
                reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            'posts/profile.html':
                reverse('posts:profile', kwargs={'username': self.author}),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), PAGE_IN_PAGINATOR
                )

    def test_second_page_contains_three_records(self):
        templates_pages_names = {
            'posts/index.html': INDEX + '?page=2',
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

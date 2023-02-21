from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        self.assertEqual(post.text[:15], str(post),
                         'некорректно работает Post.__str__()')
        group = PostModelTest.group
        self.assertEqual(group.title, str(group),
                         'некорректно работает Group.__str__()')

    def test_verbose_name(self):
        post = PostModelTest.post
        self.assertEqual(post._meta.get_field(
            'text').verbose_name, 'Текст'
            ' поста', 'некорректно работает Group verbose_name Post')

    def test_help_text(self):
        post = PostModelTest.post
        self.assertEqual(post._meta.get_field(
            'text').help_text, 'Введите текст'
            ' поста', 'некорректно работает help_text Group')

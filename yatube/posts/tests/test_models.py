from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        list_models = [
            (
                PostModelTest.post.text[:settings.FIRST_CHAR_POST],
                self.post.text
            ),
            (
                PostModelTest.group.title,
                self.group.title
            )
        ]
        for model, value in list_models:
            with self.subTest(model=model):
                self.assertEqual(model, value)

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_author = User.objects.create_user(username='auth_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )
        cls.comment = Comment.objects.create(
            text='Комментарий поста',
            author=cls.user,
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user_author
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        list_models = (
            (
                PostModelTest.post.text[:settings.FIRST_CHAR_POST],
                self.post.text
            ),
            (
                PostModelTest.group.title,
                self.group.title
            ),
            (
                PostModelTest.comment.text,
                self.comment.text
            ),
            (
                PostModelTest.follow.user,
                self.follow.user
            ),
            (
                PostModelTest.follow.author,
                self.follow.author
            )
        )
        for model, value in list_models:
            with self.subTest(model=model):
                self.assertEqual(model, value)

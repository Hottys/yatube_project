from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='auth'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в базе."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст формы',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'auth'}
        ))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст формы',
                group=self.group.id,
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирования изменяет пост в базе данных."""
        previous_post = self.post
        form_data = {
            'text': 'Новый редактированный тестовый текст',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:edit',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        current_post = Post.objects.get(id=self.post.id)
        self.assertNotEqual(previous_post.text, current_post.text)
        self.assertTrue(
            Post.objects.filter(
                text='Новый редактированный тестовый текст',
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

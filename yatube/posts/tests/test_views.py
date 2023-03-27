from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='auth',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug',
        )

        for count in range(settings.TOTAL_POSTS):
            cls.post = Post.objects.create(
                text='Тестовый текст',
                group=cls.group,
                author=cls.user,
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse(
                'posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): 'posts/post_detail.html',
            reverse(
                'posts:edit',
                kwargs={'post_id': self.post.id}): 'posts/post_create.html',
            reverse(
                'posts:post_create'): 'posts/post_create.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """index, group_list, profile сформирован с правильным контекстом."""
        pages_names = {
            reverse('posts:index'),
            reverse(
                'posts:profile',
                kwargs={'username': self.user}),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug})
        }
        for template in pages_names:
            with self.subTest(template=template):
                response = self.guest_client.get(template)
                first_object = response.context['page_obj'][0]
                post_text = first_object.text
                post_group = first_object.group.title
                post_author = first_object.author.username
                self.assertEqual(post_text, 'Тестовый текст')
                self.assertEqual(post_group, 'Тестовая группа')
                self.assertEqual(post_author, 'auth')

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id})
        )
        post = response.context['post']
        self.assertEqual(post, self.post)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_create(edit) сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:edit',
            kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_first_page_contains_ten_posts(self):
        """10 постов на первой и 3 поста на второй странице шаблонов."""
        pages_names = (
            reverse('posts:index'),
            reverse(
                'posts:profile',
                kwargs={'username': self.user}),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug})
        )
        for page in pages_names:
            with self.subTest(page=page):
                response_1 = self.authorized_client.get(page)
                response_2 = self.authorized_client.get(page + '?page=2')
                self.assertEqual(
                    len(response_1.context['page_obj']),
                    settings.TEN_POST_PAGE
                )
                self.assertEqual(
                    len(response_2.context['page_obj']),
                    settings.THREE_POST_PAGE
                )

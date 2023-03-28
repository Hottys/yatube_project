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
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def posts_check(self, post):
        """Проверка полей поста."""
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.group.id, self.post.group.id)
            self.assertEqual(post.author, self.post.author)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        self.posts_check(response.context['page_obj'][0])

    def test_groups_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'], self.group)
        self.posts_check(response.context['page_obj'][0])

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            )
        )
        self.assertEqual(response.context['author'], self.user)
        self.posts_check(response.context['page_obj'][0])

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context['post'], self.post)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post и edit сформированы с правильным контекстом."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response_1 = self.authorized_client.get(reverse(
                    'posts:post_create')
                )
                response_2 = self.authorized_client.get(reverse(
                    'posts:edit',
                    kwargs={'post_id': self.post.id})
                )
                form_field_1 = response_1.context.get('form').fields.get(value)
                self.assertIsInstance(form_field_1, expected)
                form_field_2 = response_2.context.get('form').fields.get(value)
                self.assertIsInstance(form_field_2, expected)

        def test_post_after_create_in_templates(self):
            """Пост появился в шаблонах index, group_list, profile."""
            pages_names = {
                reverse(
                    'posts:index'): self.group.slug,
                reverse(
                    'posts:group_list',
                    kwargs={'slug': self.group.slug}): self.group.slug,
                reverse(
                    'posts:profile',
                    kwargs={'username': self.user}): self.group.slug,
            }
            for value, expected in pages_names.items():
                response = self.authorized_client.get(value)
                for object in response.context['page_obj']:
                    post_group = object.group.slug
                    with self.subTest(value=value):
                        self.assertEqual(post_group, expected)

        def test_post_not_get_someone_else_group(self):
            """Созданный пост не попал в чужую группу"""
            response = self.authorized_client.get(
                reverse('posts:group_list')
            )
            self.assertEqual(
                response.context['page_obj'][0].group, self.group
            )


class PostsPaginatorViewsTests(TestCase):
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
        cls.post = [
            Post.objects.bulk_create([
                Post(
                    text='Тестовый текст' + str(post_plus),
                    group=cls.group,
                    author=cls.user,
                ),
            ])
            for post_plus in range(settings.TOTAL_POSTS)
        ]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        """10 постов на первой и 3 поста на второй странице шаблонов."""
        test_pages = [
            (settings.TEN_POST_PAGE, 1),
            (settings.THREE_POST_PAGE, 2)
        ]
        for posts_on_page, page_nubmer in test_pages:
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
                    response = self.authorized_client.get(
                        page + '?page=' + str(page_nubmer)
                    )
                    self.assertEqual(
                        len(response.context['page_obj']),
                        posts_on_page
                    )

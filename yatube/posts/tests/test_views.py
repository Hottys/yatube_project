import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
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
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def posts_check(self, post):
        """Проверка полей поста."""
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.group, self.post.group)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.image, self.post.image)

    def test_check_image_context(self):
        """Картинка передается в словаре context
        в шаблоны index, profile, group_list и post_detail."""
        templates_list = {
            reverse('posts:index'),
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        }
        for templates in templates_list:
            with self.subTest(templates=templates):
                response = self.authorized_client.get(templates)
                self.assertEqual(
                    response.context['post'].image, self.post.image
                )

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
                kwargs={'slug': self.group.slug}
            )
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
        self.assertEqual(response.context['following'], False)
        self.posts_check(response.context['page_obj'][0])

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(response.context['post'], self.post)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post и edit сформированы с правильным контекстом."""
        test_pages = [
            reverse('posts:post_create'),
            reverse(
                'posts:edit',
                kwargs={'post_id': self.post.id}
            )
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField
        }
        for page_name in test_pages:
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    response = self.authorized_client.get(page_name)
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_post_after_create_in_templates(self):
        """Пост появился в шаблонах index, group_list, profile."""
        post_test_create = Post.objects.create(
            text='Тестовый текст',
            group=self.group,
            author=self.user,
        )
        pages_names = {
            reverse(
                'posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': self.user}),
        }
        for template in pages_names:
            with self.subTest(template=template):
                response = self.authorized_client.get(template)
                self.assertIn(post_test_create, response.context['page_obj'])

    def test_post_not_get_someone_else_group(self):
        """Созданный пост не попал в чужую группу."""
        group = Group.objects.create(
            title='Тестовая группа 2',
            description='Тестовое описание 2',
            slug='test-slug-2',
        )
        post = Post.objects.create(
            text='Тестовый текст 2',
            group=group,
            author=self.user,
        )
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            )
        )
        post_object = response.context['page_obj']
        self.assertNotIn(post.group, post_object)

    def test_index_page_cache(self):
        """Список записей в index хранится в кеше."""
        response_first = self.authorized_client.get(
            reverse('posts:index')
        )
        Post.objects.all().delete()
        response_second = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(
            response_first.content,
            response_second.content
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
        pages_names = (
            reverse('posts:index'),
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        for posts_on_page, page_nubmer in test_pages:
            for page in pages_names:
                with self.subTest(page=page):
                    response = self.authorized_client.get(
                        page + '?page=' + str(page_nubmer)
                    )
                    self.assertEqual(
                        len(response.context['page_obj']),
                        posts_on_page
                    )


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(
            username='auth_author',
        )
        cls.user_follow = User.objects.create(
            username='auth_follow',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author,
        )

    def setUp(self):
        cache.clear()
        self.author_client = Client()
        self.author_client.force_login(self.user_follow)
        self.follow_client = Client()
        self.follow_client.force_login(self.user_author)

    def test_follow_on_user(self):
        """Проверка подписки на автора."""
        follow_count = Follow.objects.count()
        response = self.follow_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_follow}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user_follow}
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_author, author=self.user_follow
            ).exists()
        )

    def test_unfollow_on_user(self):
        """Проверка отписки от автора."""
        follow_count = Follow.objects.count()
        self.follow_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_follow}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user_author, author=self.user_follow
            ).exists()
        )

    def test_posts_on_followers(self):
        """Проверка появления записей избранных авторов у подписчиков."""
        post = Post.objects.create(
            author=self.user_author,
            text="Тестовый текст"
        )
        Follow.objects.create(
            user=self.user_follow,
            author=self.user_author
        )
        response = self.author_client.get(
            reverse('posts:follow_index')
        )
        post_object = response.context['page_obj']
        self.assertIn(post, post_object)

    def test_posts_on_unfollowers(self):
        """Проверка записей у тех кто не подписан на авторов."""
        post = Post.objects.create(
            author=self.user_author,
            text="Тестовый текст"
        )
        response = self.author_client.get(
            reverse('posts:follow_index')
        )
        post_object = response.context['page_obj']
        self.assertNotIn(post, post_object)

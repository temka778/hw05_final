import shutil
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from posts.models import Group, Post, Follow, User
from posts.tests.constants import (
    INDEX,
    GROUP_LIST,
    PROFILE,
    POST_CREATE,
    USERNAME,
    SLUG,
    SMALL_GIF,
    TEMP_MEDIA_ROOT
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        uploaded = SimpleUploadedFile(
            name='small.gif', content=SMALL_GIF, content_type='image/gif'
        )
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание тестовой группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
            group=cls.group,
            image=uploaded
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.POST_DETAIL = reverse("posts:post_detail", args=[cls.post.id])
        cls.POST_EDIT = reverse("posts:post_edit", args=[cls.post.id])
        cls.templates_pages_names = [
            (INDEX, 'posts/index.html'),
            (GROUP_LIST, 'posts/group_list.html'),
            (PROFILE, 'posts/profile.html'),
            (PostsViewsTests.POST_DETAIL, 'posts/post_detail.html'),
            (PostsViewsTests.POST_EDIT, 'posts/create_post.html'),
            (POST_CREATE, 'posts/create_post.html')
        ]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """Шаблон главной страницы сформирован с правильным контекстом."""
        response = self.guest_client.get(INDEX)
        first_object = response.context['page_obj'][0]
        text_0 = first_object.text
        author_0 = first_object.author
        image_0 = first_object.image
        self.assertEqual(text_0, self.post.text)
        self.assertEqual(author_0, self.user)
        self.assertEqual(image_0, self.post.image)

    def test_group_list_context(self):
        """Шаблон страницы с постами определённой
        группы сформирован с правильным контекстом.
        """
        response = self.guest_client.get(GROUP_LIST)
        first_object = response.context['page_obj'][0]
        text_0 = first_object.text
        author_0 = first_object.author
        group_0 = first_object.group
        image_0 = first_object.image
        self.assertEqual(text_0, self.post.text)
        self.assertEqual(author_0, self.user)
        self.assertEqual(group_0, self.group)
        self.assertEqual(image_0, self.post.image)

    def test_profile_context(self):
        """Шаблон профиля сформирован с правильным контекстом."""
        response = self.guest_client.get(PROFILE)
        first_object = response.context['page_obj'][0]
        text_0 = first_object.text
        author_0 = first_object.author
        image_0 = first_object.image
        self.assertEqual(text_0, self.post.text)
        self.assertEqual(author_0, self.user)
        self.assertEqual(image_0, self.post.image)

    def test_post_detail_context(self):
        """Шаблон подробной инфы поста сформирован с правильным контекстом.
        """
        response = self.guest_client.get(PostsViewsTests.POST_DETAIL)
        first_object = response.context['post']
        text_0 = first_object.text
        author_0 = first_object.author
        group_0 = first_object.group
        image_0 = first_object.image
        self.assertEqual(text_0, self.post.text)
        self.assertEqual(author_0, self.user)
        self.assertEqual(group_0, self.group)
        self.assertEqual(image_0, self.post.image)

    def test_create_post_context(self):
        """Шаблон добавления(изменения) поста сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(POST_CREATE)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added(self):
        """Пост при создании отображается на нужных страничках"""
        post = Post.objects.create(
            text=self.post.text, author=self.user, group=self.group)
        index = self.authorized_client.get(INDEX).context['page_obj']
        group = self.authorized_client.get(GROUP_LIST).context['page_obj']
        profile = self.authorized_client.get(PROFILE).context['page_obj']
        self.assertIn(post, index, 'Пост не отобразился на главной странице')
        self.assertIn(post, group, 'Пост не отобразился на странице группы')
        self.assertIn(post, profile, 'Пост не отобразился на страние профиля')

    def test_post_is_in_the_right_group(self):
        """Пост попадает в нужную группу при создании"""
        group2 = Group.objects.create(
            title='Тестовая группа 2', slug='test-slug_2')
        count_1 = Post.objects.filter(group=group2).count()
        Post.objects.create(
            text='Тестовый пост для группы 2.', author=self.user, group=group2)
        count_2 = Post.objects.filter(group=group2).count()
        self.assertEqual(count_1 + 1, count_2, 'Пост не попал в нужную группу')

    def test_cache(self):
        """Тест кэширования главной страницы."""
        post_cache = Post.objects.create(
            text=self.post.text, author=self.user
        )
        first = self.authorized_client.get(INDEX)
        post_cache.delete()
        second = self.authorized_client.get(INDEX)
        self.assertEqual(first.content, second.content)
        cache.clear()
        third = self.authorized_client.get(INDEX)
        self.assertNotEqual(third.content, second.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тeстовая группа ', slug=SLUG)
        Post.objects.bulk_create(
            [Post(
                text=f'Тестовый текст {i} поста',
                group=cls.group,
                author=cls.user
            ) for i in range(13)]
        )

    def test_paginator(self):
        """Проверяем пагинатор. Вывод по 10 постов на странице."""
        pages = [INDEX, GROUP_LIST, PROFILE]
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(len(response.context['page_obj']), 10)
            with self.subTest(page=page + '?page=2'):
                response = self.client.get(page + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)

    def test_return_post(self):
        """Проверяем последовательность постов на странице."""
        self.assertEqual(
            Post.objects.latest('id').text,
            'Тестовый текст 12 поста',
            'Неправильная последовательность.'
        )


class FollowTests(TestCase):
    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create(username='follower')
        self.user_following = User.objects.create(username='following')
        self.post = Post.objects.create(
            author=self.user_following,
            text='Тестовая запись для тестирования ленты'
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_follow(self):
        self.client_auth_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_following.username}
            )
        )
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        self.client_auth_follower.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.client_auth_follower.get(reverse('posts:profile_unfollow',
                                      kwargs={'username':
                                              self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscription(self):
        """Запись появляется в ленте подписчиков."""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        response = self.client_auth_follower.get('/follow/')
        post_text_0 = response.context['page_obj'][0].text
        self.assertEqual(post_text_0, 'Тестовая запись для тестирования ленты')
        # проверка, что запись не появилась у неподписанного пользователя
        response = self.client_auth_following.get('/follow/')
        self.assertNotEqual(response, 'Тестовая запись для тестирования ленты')

    def test_add_comment(self):
        """Проверка добавления комментария."""
        self.client_auth_following.post(f'/posts/{self.post.pk}/comment/',
                                        {'text': 'тестовый комментарий'},
                                        follow=True)
        response = self.client_auth_following.get(f'/posts/{self.post.pk}/')
        self.assertContains(response, 'тестовый комментарий')
        self.client_auth_following.logout()
        self.client_auth_following.post(f'/posts/{self.post.pk}/comment/',
                                        {'text': 'комментарий от гостя'},
                                        follow=True)
        response = self.client_auth_following.get(f'/posts/{self.post.pk}/')
        self.assertNotContains(response, 'комментарий от гостя')

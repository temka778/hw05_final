from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User
from posts.tests.constants import (
    INDEX, GROUP_LIST, PROFILE, POST_CREATE, USERNAME, USERNAME_2, SLUG
)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username=USERNAME)
        cls.user2 = User.objects.create(username=USERNAME_2)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_2 = Client()
        cls.authorized_client_2.force_login(cls.user2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG,
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст тестового поста',
            id=1
        )
        cls.POST_DETAIL = reverse("posts:post_detail", args=[cls.post.id])
        cls.POST_EDIT = reverse("posts:post_edit", args=[cls.post.id])
        cls.list_urls_status_template = [
            (INDEX, HTTPStatus.OK, "posts/index.html", cls.guest_client),
            (GROUP_LIST, HTTPStatus.OK,
             "posts/group_list.html", cls.guest_client),
            (PROFILE, HTTPStatus.OK, "posts/profile.html", cls.guest_client),
            (PostURLTests.POST_DETAIL, HTTPStatus.OK,
             "posts/post_detail.html", cls.guest_client),
            (PostURLTests.POST_EDIT, HTTPStatus.FOUND,
             "posts/create_post.html", cls.guest_client),
            (POST_CREATE, HTTPStatus.FOUND,
             "posts/create_post.html", cls.guest_client),
            (POST_CREATE, HTTPStatus.OK,
             "posts/create_post.html", cls.authorized_client)
        ]

    def test_posts_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, _, template, _ in self.list_urls_status_template:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    f"неверный шаблон - {template} для адреса {url}"
                )

    def test_posts_status(self):
        """URL-адрес возвращает должный HTTP-статус."""
        for url, status, _, client in self.list_urls_status_template:
            with self.subTest(url=url):
                self.assertEqual(
                    client.get(url).status_code,
                    status,
                    f"{url} вернул другой статус код. Нежели {status}",
                )

    def test_unexisting_page_url(self):
        """Адрес несуществующей странички."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_redirect(self):
        """
        Гостя редиректит на страницу входа.
        Не автора редиректит на пост_детайл.
        """
        address_redirect = [
            (POST_CREATE,
             f"/auth/login/?next={POST_CREATE}",
             self.guest_client),
            (PostURLTests.POST_EDIT,
             f"/auth/login/?next={PostURLTests.POST_EDIT}",
             self.guest_client),
            (PostURLTests.POST_EDIT,
             PostURLTests.POST_DETAIL,
             self.authorized_client_2)
        ]
        for url, redirect, client in address_redirect:
            with self.subTest(url=url, client=client):
                response = client.get(url, follow=True)
                self.assertRedirects(response, redirect)

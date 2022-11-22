import shutil
from http import HTTPStatus
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Post, Group, User
from posts.tests.constants import (
    PROFILE, POST_CREATE, USERNAME, SLUG, SMALL_GIF, TEMP_MEDIA_ROOT
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        uploaded = SimpleUploadedFile(
            name='small.gif', content=SMALL_GIF, content_type='image/gif')
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG,
            description='Описание тестовой группы')
        cls.group_2 = Group.objects.create(
            title='Вторая тест_группа',
            slug='test-slug_2',
            description='Описание второй тестовой группы')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
            group=cls.group,
            image=uploaded)
        cls.form = PostForm()
        cls.POST_EDIT = reverse("posts:post_edit", args=[cls.post.id])
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()
        cls.URL_POST_COMMENT = reverse(
            "posts:add_comment", args=[cls.post.id])
        cls.URL_POST_DETAIL = reverse(
            "posts:post_detail", args=[cls.post.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
            'image': self.post.image
        }
        response = self.authorized_client.post(
            POST_CREATE, data=form_data, follow=True)
        self.assertRedirects(response, PROFILE)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post_create = Post.objects.latest('id')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post_create.text, form_data['text'])
        self.assertEqual(post_create.author, self.user)
        self.assertEqual(post_create.group.pk, form_data['group'])
        self.assertEqual('posts/small.gif', form_data['image'])

    def test_edit_post(self):
        """Редактирование записи создателем поста"""
        form_data = {'text': self.post.text, 'group': self.group.pk}
        self.authorized_client.post(POST_CREATE, data=form_data, follow=True)
        post_edit = Post.objects.get(pk=self.group.pk)
        self.client.get(PostFormTests.POST_EDIT)
        form_data = {
            'text': 'Изменённый пост', 'group': self.group_2.pk
        }
        response_edit = self.authorized_client.post(
            PostFormTests.POST_EDIT, data=form_data, follow=True)
        post_edit = Post.objects.get(pk=self.group.pk)
        self.assertEqual(response_edit.status_code, HTTPStatus.OK)
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(post_edit.group.pk, form_data['group'])

    def test_comment_posts(self):
        """Проверка невозможности коментить неавторизованному пользователю
        и в случае таких попыток - редирект на страницу входа.
        При создании комента авторизованным пользователем
        - в БД появляется соответствующая запись + редирект на детали поста.
        Содержимое поля "text" последней записи в таблице "Comment"
        эквивалентен тексту созданного тестового коммента.
        """
        comment = PostFormTests.post.comments.count()
        form_data = {"text": "Тестовый текст комментария"}
        response = self.guest_client.post(
            PostFormTests.URL_POST_COMMENT, data=form_data, follow=True)
        if True:
            self.assertEqual(
                PostFormTests.post.comments.count(), comment)
            self.assertRedirects(
                response,
                f"/auth/login/?next={PostFormTests.URL_POST_COMMENT}")
        response = self.authorized_client.post(
            PostFormTests.URL_POST_COMMENT, data=form_data, follow=True)
        self.assertEqual(
            PostFormTests.post.comments.count(), comment + 1)
        self.assertRedirects(response, PostFormTests.URL_POST_DETAIL)
        added_comment = PostFormTests.post.comments.latest("id")
        self.assertEqual(added_comment.text, form_data["text"])

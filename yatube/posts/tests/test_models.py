from django.test import TestCase
from posts.models import Group, Post, User
from posts.tests.constants import USERNAME, SLUG


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG,
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый посттттттттттттттттттттттттттттттттттттт'
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделеk корректно работает __str__."""
        post = PostModelTest.post
        expected_object_post = post.text[:15]
        self.assertEqual(expected_object_post, str(post))

        group = PostModelTest.group
        expected_object_group = group.title
        self.assertEqual(expected_object_group, str(group))

    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'текст поста',
            'author': 'Автор',
            'group': 'группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text, expected_value)

from django.test import TestCase, Client
from django.urls import reverse

from .models import User, Group, Post


class TestPosts(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name='Tim',
            last_name='Odin',
            username='Timod',
            email='timodin@yandex.ru',
            password='Zxcvb12345'
        )
        self.client = Client()
        self.unauth_user_client = Client()
        self.text = '12345zxcvbbn'
        self.new_text = '123456zxc23243'

        self.group = Group.objects.create(
            title='test_group',
            slug='test_group',
            description='group for test'
        )

        self.client.force_login(self.user)

    def test_profile_existence(self):
        user = User.objects.get(username=self.user.username)
        self.assertEqual(user.username, self.user.username)

        response = self.client.get(reverse('profile', kwargs={'username': user.username}))
        self.assertEqual(response.status_code, 200)

    def test_new_post_authorized(self):

        response = self.client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

        self.client.post(reverse('new_post'), {'text': self.text, 'group': self.group.id}, follow=True)
        self.assertEqual(Post.objects.count(), 1)

    def test_post_existence(self):
        post = Post.objects.create(
            text=self.text,
            group=self.group,
            author=self.user,
        )
        self.assertEqual(Post.objects.count(), 1)

        urls = (
            reverse('index'),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('post', kwargs={'username': self.user.username, 'post_id': post.id}),
            reverse('groups', kwargs={'slug': self.group.slug}),
        )

        for url in urls:
            response = self.client.get(url)
            self.assertContains(response, self.text)

    def test_edit_post(self):
        post = Post.objects.create(
            text=self.text,
            group=self.group,
            author=self.user,
        )
        new_group = Group.objects.create(
            title='new_group',
            slug='new_group',
            description='new_group'
        )
        self.assertEqual(Post.objects.count(), 1)

        urls = (
            reverse('index'),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('post', kwargs={'username': self.user.username, 'post_id': post.id}),
            reverse('groups', kwargs={'slug': new_group.slug}),
        )

        self.client.post(
            reverse('post_edit', kwargs={'username': self.user.username, 'post_id': post.id}),
            {'text': self.new_text, 'group': new_group.id},
            follow=True
        )

        for url in urls:
            response = self.client.get(url)
            self.assertContains(response, self.new_text)

    def test_new_post_unauthorized(self):
        response = self.unauth_user_client.get('/new/')
        self.assertRedirects(
            response,
            expected_url='/auth/login/?next=/new/',
            status_code=302,
            target_status_code=200
        )

        self.unauth_user_client.post(reverse('new_post'), {'text': self.text, 'group': self.group.id}, follow=True)
        self.assertEqual(Post.objects.count(), 0)

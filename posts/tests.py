from django.test import TestCase, Client
from django.urls import reverse

from .models import User, Group


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
        self.new_group = Group.objects.create(
            title='new_group',
            slug='new_group',
            description='new_group'
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

    def test_create_post(self):
        self.client.post(reverse('new_post'), {'text': self.text, 'group': self.group.id}, follow=True)
        post = self.user.posts.get(text=self.text)
        self.assertEqual(post.text, self.text)

        urls = (
            reverse('index'),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('post', kwargs={'username': self.user.username, 'post_id': post.id}),
        )

        for url in urls:
            response = self.client.get(url)
            self.assertContains(response, self.text)

        group_response = self.client.get(reverse('groups', kwargs={'slug': self.group.slug}))
        self.assertContains(group_response, self.text)

    def test_edit_post(self):
        self.client.post(reverse('new_post'), {'text': self.text, 'group': self.group.id}, follow=True)
        post = self.user.posts.get(text=self.text)
        self.assertEqual(post.text, self.text)

        urls = (
            reverse('index'),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('post', kwargs={'username': self.user.username, 'post_id': post.id}),
        )

        self.client.post(
            reverse('post_edit', kwargs={'username': self.user.username, 'post_id': post.id}),
            {'text': self.new_text, 'group': self.new_group.id},
            follow=True
        )

        for url in urls:
            response = self.client.get(url)
            self.assertContains(response, self.new_text)

        group_response = self.client.get(reverse('groups', kwargs={'slug': self.new_group.slug}))
        self.assertContains(group_response, self.new_text)

    def test_new_post_unauthorized(self):
        response = self.unauth_user_client.get('/new/')
        self.assertRedirects(
            response,
            expected_url='/auth/login/?next=/new/',
            status_code=302,
            target_status_code=200
        )

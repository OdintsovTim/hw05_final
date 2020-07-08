from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from .models import User, Group, Post, Follow, Comment


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
            reverse('group', kwargs={'slug': self.group.slug}),
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
            reverse('group', kwargs={'slug': new_group.slug}),
        )

        self.client.post(
            reverse('post_edit', kwargs={'username': self.user.username, 'post_id': post.id}),
            {'text': self.new_text, 'group': new_group.id},
            follow=True
        )

        cache.clear()

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

    def test_page_not_found(self):
        response = self.client.get(reverse('profile', kwargs={'username': 'sdfsdf'}))
        self.assertEqual(response.status_code, 404)

    def test_image_existence(self):
        with open('posts/test_image.jpg', 'rb') as img:
            self.client.post(
                reverse('new_post'),
                {'text': self.text, 'group': self.group.id, 'image': img},
                follow=True,
            )

        self.assertEqual(Post.objects.filter(image__isnull=False).count(), 1)

        post = Post.objects.all()[0]
        urls = (
            reverse('index'),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('post', kwargs={'username': self.user.username, 'post_id': post.id}),
            reverse('group', kwargs={'slug': self.group.slug}),
        )

        cache.clear()

        for url in urls:
            response = self.client.get(url)
            self.assertContains(response, '<img')

    def test_wrong_image_format(self):
        with open('posts/__init__.py', 'rb') as img:
            self.client.post(
                reverse('new_post'),
                {'text': self.text, 'group': self.group.id, 'image': img},
                follow=True,
            )

        self.assertEqual(Post.objects.filter(image__isnull=False).count(), 0)

    def test_cashe(self):
        response = self.client.get(reverse('index'))
        with open('posts/test_image.jpg', 'rb') as img:
            self.client.post(
                reverse('new_post'),
                {'text': self.text, 'group': self.group.id, 'image': img},
                follow=True,
            )
        response = self.client.get(reverse('index'))

        self.assertNotContains(response, '<img')
        self.assertNotContains(response, self.text)

    def test_authorized_follow_unfollow(self):
        new_user = User.objects.create_user(
            first_name='Van',
            last_name='Damm',
            username='Vandamm',
            email='vandamm@yandex.ru',
            password='Zxcvb12345'
        )
        new_user2 = User.objects.create_user(
            first_name='Ter',
            last_name='Minator',
            username='Terminator',
            email='terminator@yandex.ru',
            password='Zxcvb12345'
        )
        new_client = Client()
        new_client2 = Client()
        new_client.force_login(new_user)
        new_client2.force_login(new_user2)

        new_client.get(reverse('profile_follow', kwargs={'username': self.user.username}))
        self.assertEqual(Follow.objects.count(), 1)

        post = Post.objects.create(
            text=self.text,
            group=self.group,
            author=self.user,
        )
        cache.clear()
        response = new_client.get(reverse('follow_index'))
        self.assertContains(response, self.text)
        response = new_client2.get(reverse('follow_index'))
        self.assertNotContains(response, self.text)

        new_client.get(reverse('profile_unfollow', kwargs={'username': self.user.username}))
        self.assertEqual(Follow.objects.count(), 0)

    def test_authorized_comment(self):
        post = Post.objects.create(
            text=self.text,
            group=self.group,
            author=self.user,
        )
        comment = Comment.objects.create(
            text=self.text,
            author=self.user,
            post=post,
        )
        self.assertEqual(Comment.objects.count(), 1)

        self.unauth_user_client.post(
            reverse('post', kwargs={'username': self.user.username, 'post_id': post.id}),
            {'text': self.text},
            follow=True
        )
        self.assertEqual(Comment.objects.count(), 1)

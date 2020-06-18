from django.test import TestCase

from .models import User


class TestProfile(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name='Tim',
            last_name='Odin',
            username='Timod',
            email='timodin@yandex.ru',
            password='Zxcvb12345'
        )
        self.client.force_login(self.user)

    def test_profile(self):
        response = self.client.get(f'/{self.user.username}/')
        self.assertEqual(response.status_code, 200)


class TestNewPost(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            first_name='Tim',
            last_name='Odin',
            username='Timod',
            email='timodin@yandex.ru',
            password='Zxcvb12345'
        )
        self.client.force_login(self.user)

    def test_new_post_authorized(self):
        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        text = '12345zxcvbbn'
        self.client.post('/new/', {'text': text}, follow=True)
        post_id = self.user.posts.get(text=text).id

        for url in ('/', f'/{self.user.username}/', f'/{self.user.username}/{post_id}/'):
            response = self.client.get(url)
            self.assertContains(response, text)

    def test_edit_post(self):
        text = '12345zxcvbbn'
        self.client.post('/new/', {'text': text}, follow=True)
        post_id = self.user.posts.get(text=text).id

        new_text = '123456zxc23243'
        self.client.post('/Timod/1/edit/', {'text': new_text}, follow=True)

        for url in ('/', f'/{self.user.username}/', f'/{self.user.username}/{post_id}/'):
            response = self.client.get(url)
            self.assertContains(response, new_text)

    def test_new_post_unauthorized(self):
        self.client.logout()

        response = self.client.get('/new/')
        self.assertRedirects(
            response,
            expected_url='/auth/login/?next=/new/',
            status_code=302,
            target_status_code=200
        )

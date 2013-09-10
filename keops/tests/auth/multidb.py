from django.conf import settings
from django.test import TestCase, Client

class AuthTestCase(TestCase):
    from keops.modules.base import app_info
    fixtures = app_info['fixtures']

    def setUp(self):
        # add test user
        from keops.modules.base import models
        u = models.User(username='test')
        u.set_password('test')
        u.save()
        self.client = Client()
        # add db2 alias
        dbs = settings.DATABASES
        dbs['my_db'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'my_db',
            'USER': 'postgres',
            'SCHEMA': '',
            'PASSWORD': '1',
            'HOST': 'localhost',
            'PORT': '',
        }
        self.settings(DATABASES=dbs)

    def test_multi_db(self):
        response = self.client.get('/db/?alias=default')
        # /admin/ have to redirect
        self.assertRedirects(response, settings.LOGIN_URL + '?next=/admin/')
        # try to login
        response = self.client.post(settings.LOGIN_URL + '?next=/admin/', {'username': 'admin', 'password': 'admin'})
        assert response.status_code == 302
        response = self.client.get('/admin/?db=default')
        response = self.client.get(settings.LOGOUT_URL)

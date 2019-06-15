from datetime import datetime, timedelta
import unittest
from app import create_app, mongo
from app.models import Usuario, Post
from mockupdb import MockupDB, go, Command
from flask import current_app
from config import Config


class TestConfig(Config):
    TESTING = True
    #MONGO_URI = "mongodb://localhost:27017/testando"

class UserModelCase(unittest.TestCase):

    def setUp(self):
        self.server = MockupDB(auto_ismaster=True, verbose=True)
        self.server.run()

        self.app = create_app(TestConfig)

        self.app_context = self.app.app_context()
        self.app_context.push()
        current_app.config[' MONGO_URI'] = self.server.uri

    def tearDown(self):
        self.server.stop()
        self.app_context.pop()

    def text_password_hashing(self):
        u = Usuario.mock()
        u.set_password('t')
        self.assertFalse(u.check_password('g'))
        self.assertTrue(u.check_password('t'))

    def test_avatar(self):
        u = Usuario.mock()
        self.assertEqual(u.avatar(128),
                         'http://www.gravatar.com/avatar/b642b4217b34b1e8d3bd915fc65c4452?d=identicon&s=128')


if __name__ == '__main__':
    unittest.main(verbosity=2)



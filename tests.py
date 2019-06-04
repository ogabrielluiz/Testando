from datetime import datetime, timedelta
import unittest
from app import App, mongo
from app.models import Usuario, Post
from mockupdb import MockupDB, go, Command

class UserModelCase(unittest.TestCase):

    def setUp(self):
        self.server = MockupDB(auto_ismaster=True, verbose=True)
        self.server.run()

        App.testing = True
        App.config[' MONGO_URI'] = self.server.uri
        self.App = App.test_client()

    def tearDown(self):
        self.server.stop()

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



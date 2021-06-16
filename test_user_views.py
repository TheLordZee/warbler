import os
from unittest import TestCase
from flask.globals import session

from werkzeug.utils import html

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)

        db.session.commit()

    def tearDown(self):
        """Cleansup"""
        db.session.rollback()

    
    def test_signup_form(self):
        """Tests sign up form"""

        with self.client as c:
            res = c.get('/signup')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Join Warbler today", html)

    def test_signup(self):
        """Tests signup"""
        with self.client as c:
            data = {
                "username" : "new testuser",
                "password":"testpass",
                "email":"testemail@site.com",
                "image_url": None
            }
            res = c.post("/signup", data=data)
            query = User.query.filter(User.username == "new testuser").first()

            self.assertEqual(query.username, data["username"])
            self.assertEqual(query.email, data["email"])
            self.assertEqual(query.image_url,'/static/images/default-pic.png')
            self.assertNotEqual(query.password, data["password"])
            self.assertEqual(res.status_code, 302)
            self.assertEqual(session[CURR_USER_KEY], query.id)

    def test_login_form(self):
        """Tests login form"""
        with self.client as c:
            res = c.get('/login')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Welcome back", html)

    def test_login(self):
        """Tests login"""
        with self.client as c:
            data = {
                "username" : "testuser",
                "password" : "testuser",
            }
            res = c.post("/login", data=data)

            self.assertEqual(res.status_code, 302)
            self.assertEqual(session[CURR_USER_KEY], self.testuser.id)

    def test_logout(self):
        """Tests logout"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.get('/logout')

            self.assertEqual(res.status_code, 302)
            self.assertNotIn(CURR_USER_KEY, session)

    
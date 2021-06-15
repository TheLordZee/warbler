"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from werkzeug.utils import html

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def tearDown(self):
        """Cleansup"""
        db.session.rollback()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_anon_home(self):
        """Do messages display on the homepage if is not logged in?"""
        
        with self.client as c:
            res = c.get("/")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("<h4>New to Warbler?</h4>", html)
            self.assertNotIn('<ul class="list-group" id="messages">', html)

    def test_logged_in_home(self):
        with self.client as c:
            with c.session_transaction() as sess:
                 sess[CURR_USER_KEY] = self.testuser.id

            res = c.get("/")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertNotIn("<h4>New to Warbler?</h4>", html)
            self.assertIn('<ul class="list-group" id="messages">', html)

    def test_anon_new_message(self):
        with self.client as c:
            res = c.get('/messages/new')
            self.assertEqual(res.status_code, 302)

    def test_logged_in_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                 sess[CURR_USER_KEY] = self.testuser.id

            res = c.get('/messages/new')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Add my message!", html)

    def test_show_message(self):
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            m = Message(text="Sample Text", user_id=self.testuser.id)
            db.session.add(m)
            db.session.commit()

            res = c.get(f'/messages/{m.id}')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(m.text, html)
   
    def test_anon_delete_message(self):
        with self.client as c:
            m = Message(text="Sample Text", user_id=self.testuser.id)
            db.session.add(m)
            db.session.commit()

            res = c.post(f'/messages/{m.id}/delete')
            query = Message.query.get(m.id)

            self.assertEqual(m, query)
            self.assertEqual(res.status_code, 302)

    def test_delete_message(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            m = Message(text="Sample Text", user_id=self.testuser.id)
            db.session.add(m)
            db.session.commit()

            res = c.post(f'/messages/{m.id}/delete')
            query = Message.query.get(m.id)

            self.assertEqual(query, None)
            self.assertEqual(res.status_code, 302)
import os
from unittest import TestCase

from werkzeug.utils import html

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """Test model for message"""
    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        u = User.signup('user1', 'email1@site.com', 'password1', 'img1')
        
        db.session.add(u)
        db.session.commit()

        self.u = u

    def tearDown(self):
        """Cleans up"""
        db.session.rollback()

    def test_message(self):
        m = Message(text='This is a test message', user_id=self.u.id)
        db.session.add(m)
        db.session.commit()
        self.assertIn(m, self.u.messages)

        m2 = Message()
        db.session.add(m2)
        with self.assertRaises(Exception):
            db.session.commit()

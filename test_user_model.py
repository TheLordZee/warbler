"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from werkzeug.utils import html

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test model for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        u1 = User.signup('user1', 'email1@site.com', 'password1', 'img1')
        u2 = User.signup('user2', 'email2@site.com', 'password2', 'img2')

        db.session.add_all([u1,u2])
        db.session.commit()

        self.u1 = u1
        self.u2 = u2

    def tearDown(self):
        """Cleans up"""
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_signup(self):
        """Does sign up work?"""
        res = User.signup('OceanMan', 'aemail@asite.com', 'Spongbob', 'https://upload.wikimedia.org/wikipedia/en/thumb/3/3b/SpongeBob_SquarePants_character.svg/1200px-SpongeBob_SquarePants_character.svg.png')

        db.session.add(res)
        db.session.commit()

        self.assertEqual(res.username, 'OceanMan')
        self.assertEqual(res.email, 'aemail@asite.com')
        self.assertNotEqual(res.password, 'Spongbob')
        self.assertEqual(res.image_url, 'https://upload.wikimedia.org/wikipedia/en/thumb/3/3b/SpongeBob_SquarePants_character.svg/1200px-SpongeBob_SquarePants_character.svg.png')
        self.assertIn(res, db.session)
       
        new_res = User.signup('OceanMan', 'aemail@asite.com', 'Spongbob', 'https://upload.wikimedia.org/wikipedia/en/thumb/3/3b/SpongeBob_SquarePants_character.svg/1200px-SpongeBob_SquarePants_character.svg.png')
        db.session.add(new_res)
        with self.assertRaises(Exception):
            db.session.commit()
        
        with self.assertRaises(Exception):
            User.signup()

        with self.assertRaises(Exception):
            User.signup('Ocean')

        with self.assertRaises(Exception):
            User.signup('Man', 'password')

    def test_is_following(self):
        self.assertFalse(self.u1.is_following(self.u2))
        self.u1.following.append(self.u2)
        self.assertTrue(self.u1.is_following(self.u2))

    def test_is_followed_by(self):
        self.assertFalse(self.u1.is_followed_by(self.u2))
        self.u1.following.append(self.u2)
        self.assertTrue(self.u2.is_followed_by(self.u1))

    def test_repr_(self):
        u_repr = f'<User #{self.u1.id}: user1, email1@site.com>'
        self.assertEqual(self.u1.__repr__(), u_repr)

    def test_authenticate(self):
        res = User.authenticate('user1', 'password1')
        res2 = User.authenticate('user1', 'BAD_PASSWORD')
        res3 = User.authenticate('NotAUser', 'password1')

        self.assertEqual(res, self.u1)
        self.assertFalse(res2)
        self.assertFalse(res3)
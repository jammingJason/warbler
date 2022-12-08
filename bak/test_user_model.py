"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, g, CURR_USER_KEY
app.config['WTF_CSRF_ENABLED'] = False
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        # Follows.query.delete()

        self.client = app.test_client()
        self.testuser = User.signup(username="test_user2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser2 = User.signup(username="testing_new_user",
                                    email="testing_new_user@test.com",
                                    password="testuser",
                                    image_url=None)
        
        db.session.commit()

        follows = Follows(user_being_followed_id=self.testuser.id, user_following_id=self.testuser2.id)
        db.session.add(follows)
        db.session.commit()
        
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
    
    def test_repr_method(self):
        """  Testing repr method"""
        repr = User.__repr__(self.testuser)
        self.assertEqual(repr, f'<User #{self.testuser.id}: test_user2, test2@test.com>')

    def test_following(self):
        """Testing following user(s)"""
        
        self.assertNotEqual(self.testuser.id, self.testuser2.id)
        self.assertEqual(User.is_following(self.testuser2, self.testuser), True)
        self.assertEqual(User.is_following(self.testuser, self.testuser2), False)

    def test_is_followed_by(self):
        """Testing is_followed_by"""

        self.assertEqual(User.is_followed_by(self.testuser, self.testuser2), True)
        self.assertEqual(User.is_followed_by(self.testuser2, self.testuser), False)

    def test_create_new_user(self):
        """Testing create new user"""
        with self.client as c:
            # New user with correct info
            resp = c.post("/signup", data={"username": "create_new_user",
                            "email" : "cnu@testing.com",
                            "password" : "HASHED_PASSWORD",
                            "image_url": None})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302, "This is redirecting")
            
            # New user with duplicate info
            # resp = c.post("/signup", data={"username": "create_new_user",
            #                 "email" : "cnu@testing.com",
            #                 "password" : "HASHED_PASSWORD",
            #                 "image_url": None})
            

        # New user with duplicate info
            # Duplicate info produces an error because of the unique being true

    def test_authenticate_user(self):
        """Testing authentication with correct and incorrect credentials """
        
        # With CORRECT credentials
        test_auth = User.authenticate('test_user2', 'testuser')
        self.assertTrue(test_auth)

        #  Incorrect password being used
        test_again = User.authenticate('test_user2', 'password')
        self.assertFalse(test_again)

        #  Incorrect username being used
        testing_again = User.authenticate('VJC', 'testuser')
        self.assertFalse(testing_again)

        
#
#
# Public Archive of Days Since Timers
# Helper Base Class Unit Tests
#
#

from django.test import TestCase
from django.utils import timezone
from padsweb.helpers import PADSHelper
from padsweb.models import PADSUser
from padsweb.settings import defaults

settings = defaults

class PADSHelperTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_id_fake = -9999
        # Place a test User in the database
        cls.user = PADSUser()
        cls.user.nickname_short = 'test-dave'
        cls.user.nickname = 'Read Test User'
        cls.user.last_login_date_time = timezone.now()
        cls.user.password_hash = ''
        cls.user.sign_up_date_time = timezone.now()
        cls.user.timezone = 'UTC'
        cls.user.save()
        # Get Test User id
        cls.user_id = cls.user.id
    
    def test_set_user_id_valid(self):
        helper = PADSHelper()
        helper.set_user_id(self.user_id)
        self.assertEqual(self.user_id, helper.user_id, 'User id should be set')
    
    def test_set_user_id_fake_user(self):
        user_id = self.user_id_fake
        helper = PADSHelper(user_id)
        self.assertEquals(helper.user_id, settings['user_id_signed_out'],
                'Default User id should be assigned for Users not signed up')
        
    def test_user_is_present(self):
        helper = PADSHelper()
        helper.set_user_id(self.user_id)
        self.assertTrue(helper.user_is_present(),
                        'User should be indicated as present if signed up')

    def test_user_is_present_fake_user(self):
        user_id = self.user_id_fake
        helper = PADSHelper(user_id)
        self.assertFalse(helper.user_is_present(),
                      'User Is Present flag should be False if not signed up')
        
    def test_user_is_not_present(self):
        helper = PADSHelper()
        self.assertFalse(helper.user_is_present(), 
                         'User Is Present flag should be false by default')        
    

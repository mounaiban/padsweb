#
#
# Public Archive of Days Since Timers
# Helper Base Class Unit Tests
#
#

from django.test import TestCase
from padsweb.helpers import PADSHelper

class PADSHelperTests(TestCase):
    def test_set_user_id(self):
        user_id = 64
        helper = PADSHelper()
        helper.set_user_id(user_id)
        self.assertEqual(helper.user_id, user_id, 'User id should be set')
        
    def test_user_is_not_present(self):
        helper = PADSHelper()
        self.assertFalse(helper.user_is_present(), 
                         'User Is Present flag should be false by defaul')
        
    def test_user_is_present(self):
        user_id = 64
        helper = PADSHelper(user_id)
        self.assertTrue(helper.user_is_present(),
                        'User Is Present flag should be True')
    
    def test_user_is_present_after_set_user_id(self):
        user_id = 64
        helper = PADSHelper()
        helper.set_user_id(user_id)
        self.assertTrue(helper.user_is_present(), 
                'User Is Present flag should be True after it is manually set')

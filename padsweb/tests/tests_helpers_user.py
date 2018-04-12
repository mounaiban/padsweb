#
#
# Public Archive of Days Since Timers
# User Account Model Helper Unit Tests
#
#

from django.test import TestCase
from django.utils import timezone
from padsweb.helpers import PADSUserHelper, PADSWriteUserHelper
from padsweb.models import PADSUser
from padsweb.settings import defaults
import secrets  # For token_urlsafe()

settings = defaults

#
# Shared Test Data
#
blank_inputs = {
        # These inputs are in a dictionary, so that they can be cycled through
        # automatically with the dict.values() iterable. The keys are an
        # alternative to comments.
        'newlines_only_8' : '\n\n\n\n\n\n\n\n',
        'whitespace_mix' : '\f\n\r\t\v ',
        'none' : None,
        'spaces_only_8' : '        ',
        'tabs_only_8' : '\t\t\t\t\t\t\t\t',
        'zero_length_string' : '',
        }

#
# User Account Retrieval Helper Tests
#

# TODO: PADSUserHelper.set_user_id() Tests
# TODO: PADSUserHelper.set_user_id_by_username() Tests
# TODO: PADSUserHelper.check_ql_password() Tests
class PADSUserHelperCheckPasswordTests(TestCase):
    """Unit tests for PADSUserHelper.check_password()"""
    @classmethod
    def setUpTestData(cls):
        # Sign up test User
        cls.username = 'test-dave'
        cls.password = '    wxyzWXYZ_12345678'
        cls.write_user_helper = PADSWriteUserHelper()
        cls.write_user_helper.new(cls.username, cls.password)
        # Prepare User Helper for test User
        cls.read_user_helper = PADSUserHelper()
        cls.read_user_helper.set_user_id_by_username(cls.username)
    
    def test_check_password_valid(self):
        # Assertions
        self.assertTrue(self.read_user_helper.check_password(self.password),
                        'The correct password must validate')
    
    def test_check_password_wrong_password(self):
        password_wrong = secrets.token_urlsafe(
                settings['message_max_length_short'])
        # Assertions
        self.assertFalse(self.read_user_helper.check_password(password_wrong),
                         'An incorrect password must fail to validate')
    
    def test_check_password_blank_input(self):
        # Multi-Assertion
        for p in blank_inputs.values():
            self.assertFalse(self.read_user_helper.check_password(p),
                             'A blank password must fail to validate')

    def test_check_password_no_user(self):
        read_user_helper_orphan = PADSUserHelper()
        # Assertions
        self.assertFalse(read_user_helper_orphan.check_password(self.password),
                  'A User Helper with no User must fail to validate passwords')

#
# User Account Creation and Configuration Helper Tests
#

# Write Helper Tests
# TODO: PADSWriteUserHelper.merge_users_by_id() tests (valid, invalid ids)
# TODO: PADSWriteUserHelper.set_timezone() tests (valid, invalid timezones)
class PADSWriteUserHelperDeleteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Sign up Test Users
        cls.username_a = 'test_jess_d'
        cls.password_a = '    uiopUIOP-9999'
        cls.username_b = 'not_jess'
        # Both users unknowingly have the same password
        cls.password_b = cls.password_a
        cls.write_user_helper = PADSWriteUserHelper()
        cls.write_user_helper.new(cls.username_a, cls.password_a)
        cls.write_user_helper.new(cls.username_b, cls.password_b)
            
    def test_delete_valid(self):
        user_a = PADSUser.objects.get(nickname_short=self.username_a)
        self.write_user_helper.set_user_id(user_a.id)
        op_result = self.write_user_helper.delete()
        # Assertions
        user_a_is_in = PADSUser.objects.filter(
                nickname_short=self.username_a).exists()
        user_b_is_in = PADSUser.objects.filter(
                nickname_short=self.username_b).exists()
        self.assertFalse(user_a_is_in, 
                         'Test User must no longer exist after deletion')
        self.assertTrue(user_b_is_in,
                     'User not targeted for deletion must remain in database')
        self.assertTrue(op_result,
                        'Helper must indicate success of User deletion')
    
    def test_delete_no_such_user(self):
        write_user_helper_x = PADSWriteUserHelper(-99999) # Invalid user id
        op_result = write_user_helper_x.delete()
        # Assertions
        user_a_is_in = PADSUser.objects.filter(
                nickname_short=self.username_a).exists()
        user_b_is_in = PADSUser.objects.filter(
                nickname_short=self.username_b).exists()
        self.assertTrue(user_a_is_in, 
                     'Test User must remain in database after failed deletion')
        self.assertTrue(user_b_is_in,
                    'Other User must remain in database after failed deletion')
        self.assertFalse(op_result,
                        'Helper must indicate failure of User deletion')
    

class PADSWriteUserHelperNewTests(TestCase):
    """Unit tests for PADSWriteUserHelper.new() which creates user accounts"""
    @classmethod
    def setUpTestData(cls):
        cls.write_user_helper = PADSWriteUserHelper()
        cls.read_user_helper = PADSUserHelper()
    
    def test_new_valid(self):
        username = 'test_jess_nv'
        password = '   asdfASDF1234!@#$()&;'
        self.write_user_helper.new(username, password)
        # Assertions
        user_test = PADSUser.objects.get(nickname_short=username)
        self.assertEquals(user_test.nickname_short, username, 
                             'User must be in database after account creation')
    
    def test_new_ql_valid(self):
        ql_password = self.write_user_helper.new() # Sign up to get password
        ql_user_id = self.read_user_helper.split_ql_password(ql_password)[0]
        # Assertions
        ql_user_test = PADSUser.objects.get(pk=ql_user_id)
        self.assertEquals(str(ql_user_test.id), ql_user_id,
          'Quick List user must be in database with correct id after creation')
    
    def test_new_blank_usernames(self):
        password = '    abcdABCD1234-5678'
        usernames = blank_inputs.values()
        # Multi-Assertion
        for u in usernames:
            op_result = self.write_user_helper.new(u, password)
            user_is_in = PADSUser.objects.filter(nickname_short=u).exists()
            self.assertIsNone(op_result,
                          'Helper must fail creating User with blank username')
            self.assertFalse(user_is_in)
    
    def test_new_fake_ql_user(self):
        username = ''.join( (settings['ql_user_name_prefix'], '1234') )
        password = '    abcdABCD1234-5678'
        # Assertions
        op_result = self.write_user_helper.new(username, password)
        user_is_in = PADSUser.objects.filter(nickname_short=username).exists()
        self.assertFalse(user_is_in,
                          'Fake Quick List User must not be in database')
        self.assertIsNone(op_result,
                          'Helper must fail creating fake Quick List account')
    
    def test_new_long_username(self):
        name_length = settings['name_max_length_short'] + 1
        username = secrets.token_urlsafe(name_length) # Random long username
        password = '    abcdABCD1234-5678'
        op_result = self.write_user_helper.new(username, password)
        user_is_in = PADSUser.objects.filter(nickname_short=username).exists()
        # Assertions
        self.assertFalse(user_is_in, 
                 'User with excessively long username must not be in database')
        self.assertIsNone(op_result, 
               'Helper must fail creating User with excessively long username')
    
    def test_taken_username_different_case(self):
        username_a = 'test_jess_tu'
        password_a = '    abcdABCD1234-5678'
        username_b = 'TEST_JESS_TU' # Username A but in all caps
        password_b = '    lolol1234-5678'
        # Sign up User A
        self.write_user_helper.new(username_a, password_a)
        # Assertions
        op_result = self.write_user_helper.new(username_b, password_b)
        user_is_in = PADSUser.objects.filter(
                nickname_short=username_b).exists()
        self.assertIsNone(op_result,
           'Helper must fail adding User with taken username (different case)')
        self.assertFalse(user_is_in,
            'User with taken username (differnt case) must not be in database')

class PADSWriteUserHelperSetNicknameTests(TestCase):
    """Unit tests for PADSWriteUserHelper.set_nickname_long()"""
    @classmethod
    def setUpTestData(cls):
        # Sign up test User
        cls.username = 'test_jess_snl'
        password = '     hjklHJKL-246810'
        cls.write_user_helper = PADSWriteUserHelper()
        cls.write_user_helper.new(cls.username, password)
        # Get and assign User id to Write User Helper
        cls.user = PADSUser.objects.get(nickname_short=cls.username)
        cls.write_user_helper.set_user_id(cls.user.id)
        # Reminder: The default long nickname for a new User is the same as the
        # username (or short nickname)
    
    def test_set_nickname_long_valid(self):
        nickname_long_new = 'Jessica the Test User'
        op_result = self.write_user_helper.set_nickname_long(nickname_long_new)
        user_reloaded = PADSUser.objects.get(pk=self.user.id)
        # Assertions
        self.assertEquals(user_reloaded.nickname, nickname_long_new,
                          'User must be able to set a valid nickname')
        self.assertTrue(op_result,
                        'Helper must indicate success in long nickname change')
    
    def test_set_nickname_long_blank_input(self):
        # Multi-Assertions
        for n in blank_inputs.values():
            op_result = self.write_user_helper.set_nickname_long(n)
            user_reloaded = PADSUser.objects.get(pk=self.user.id)
            self.assertEquals(user_reloaded.nickname, self.username,
              'User\'s nickname must not change after failure to set nickname')
            self.assertFalse(op_result,
                    'Helper must indicate failure to set blank long nicknames')
    
    def test_set_nickname_long_too_long(self):
        length = settings['name_max_length_long'] + 1
        nickname_too_long = ''.join( ['Jessica the Test User',
                                      secrets.token_urlsafe(length)] )
        op_result = self.write_user_helper.set_nickname_long(
                nickname_too_long)
        user_reloaded = PADSUser.objects.get(pk=self.user.id)
        # Assertions
        self.assertEquals(user_reloaded.nickname, self.username,
              'User\'s nickname must not change after failure to set nickname')
        self.assertFalse(op_result,
               'Helper must indicate failure to set excessively long nickname')
        

class PADSWriteUserHelperSetPasswordTests(TestCase):
    """Unit tests for PADSWriteUserHelper.set_password()"""
    @classmethod
    def setUpTestData(cls):
        # Sign up test User, get details
        cls.username = 'test_jess_sp'
        cls.password = '    zxcvZXCV-54321'
        cls.write_user_helper = PADSWriteUserHelper()
        cls.write_user_helper.new(cls.username, cls.password)
        cls.user = PADSUser.objects.get(nickname_short=cls.username)
        # Set User Write Helper User id to test User's
        cls.write_user_helper.set_user_id(cls.user.id)
        
    def test_set_password_valid(self):
        password_new = ''.join( [self.password, secrets.token_urlsafe(7)] )
        op_result = self.write_user_helper.set_password(password_new)
        # Reload user info
        # Beginner's PROTIP: After making changes to the database via the
        # Django database model objects, the model object still contains old
        # information. Thus, it is necessary to reload the record from the
        # database.
        user_reloaded = PADSUser.objects.get(nickname_short=self.username)
        # Assertions
        self.assertFalse(self.write_user_helper.password_hasher.verify(
                self.password, user_reloaded.password_hash),
                'User\'s old valid password must fail to validate')
        self.assertTrue(self.write_user_helper.password_hasher.verify(
                password_new, user_reloaded.password_hash),
                'User\'s new valid password must validate')
        self.assertTrue(op_result, 
                  'Helper must indicate success in password change')

    def test_set_password_blank_input(self):
        # Multi-Assertion
        for p in blank_inputs.values():
            user_reloaded = PADSUser.objects.get(nickname_short=self.username)
            op_result = self.write_user_helper.set_password(p)
            if p is None:
                # Workaround PBKDF2PasswordHasher not accepting None as input
                p = '' 
            self.assertFalse(self.write_user_helper.password_hasher.verify(
                    p, user_reloaded.password_hash),
                    'Blank password must fail to validate for User')
            self.assertTrue(self.write_user_helper.password_hasher.verify(
                    self.password, user_reloaded.password_hash),
                    'User\'s old password must continue to validate')            
            self.assertFalse(op_result, 
               'Helper must indicate failure to change to blank password')
        
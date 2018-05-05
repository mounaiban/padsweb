#
#
# Public Archive of Days Since Timers
# Timer-related Model Helper Unit Tests
#
#

from django.test import TestCase
from django.utils import timezone
from padsweb.helpers import PADSReadTimerHelper, PADSWriteTimerHelper
from padsweb.helpers import PADSWriteUserHelper
from padsweb.models import PADSTimer
from padsweb.settings import defaults

#
# Shared Test Items
#
write_user_helper = PADSWriteUserHelper()
#
# Shared Test Data
#
bad_str_inputs = {
        # Blank and non-string inputs expected to be encountered by PADS
        # during normal operation
        'newlines_only_8' : '\n\n\n\n\n\n\n\n',
        'whitespace_mix' : '\f\n\r\t\v ',
        'spaces_only_8' : '        ',
        'tabs_only_8' : '\t\t\t\t\t\t\t\t',
        'zero_length_string' : '',
        'none' : None,
        # The following are expected to be encountered via JSON requests
        'int' : -9999,
        'float' : 3.141592654,
        'list' : [],
        'tuple' : (),
        'dict' : {},
        }

#
# Retrieval Helper Tests
class PADSReadTimerHelperGetAllFromDbTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Sign Up Main Test User
        username_a = 'test-dave'
        password_a = '    abcdABCD1234'
        cls.user_a = write_user_helper.prepare_user_in_db(
                username_a, password_a)
        cls.user_a.save()
        
        # Create Timers for Main Test User
        write_timer_helper_a = PADSWriteTimerHelper(cls.user_a.id)
        #  Timer A1: Private
        cls.timer_a1_desc = 'User A Timer 1 (Private)'
        write_timer_helper_a.new(cls.timer_a1_desc)
        #  Timer A2: Public
        cls.timer_a2_desc = 'User A Timer 2 (Public)'
        write_timer_helper_a.new(cls.timer_a2_desc, public=True)
                
        # Sign Up Second Test User
        username_b = 'NOT-test-dave'
        password_b = '    wxyzWXYZ7890'
        cls.user_b = write_user_helper.prepare_user_in_db(
                username_b, password_b)
        cls.user_b.save()
        
        # Create Timers for Second Test User
        write_timer_helper_b = PADSWriteTimerHelper(cls.user_b.id)
        #  Timer B1: Private
        cls.timer_b1_desc = 'User B Timer 1 (Private)'
        write_timer_helper_b.new(cls.timer_b1_desc)

    def test_get_all_from_db(self):
        read_timer_helper = PADSReadTimerHelper()
        
        # Assertion routine
        def check_timer_access(timer, user):
            own_private_visible = (timer.creator_user_id == user.id)
            others_public_visible = (timer.public is True)
            self.assertTrue( (own_private_visible | others_public_visible),
             'User must be able to get own private and all public Timers only')                    
            
        # Get all timers available to User A and check access
        read_timer_helper.set_user_id(self.user_a.id)
        timers_user_a = read_timer_helper.get_all_from_db()
        #  Assertions
        for t in timers_user_a:
            check_timer_access(t, self.user_a)
            
        # Get all timers available to User B and check access
        read_timer_helper.set_user_id(self.user_b.id)
        timers_user_b = read_timer_helper.get_all_from_db()
        #  Assertions
        for t in timers_user_b:
            check_timer_access(t, self.user_b)
    
    def test_get_all_from_db_signed_out(self):
        read_timer_helper = PADSReadTimerHelper() # No User id set
        timers = read_timer_helper.get_all_from_db()
        # Assertions
        for t in timers:
            self.assertTrue(t.public,
              'Helper not assigned to any User must only access public timers')
    

class PADSReadTimerHelperGetFromDbTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Sign Up Main Test User
        username_a = 'test-dave'
        password_a = '    abcdABCD1234'
        cls.user_a = write_user_helper.prepare_user_in_db(
                username_a, password_a)
        cls.user_a.save()
        
        # Create Timers for Main Test User
        write_timer_helper_a = PADSWriteTimerHelper(cls.user_a.id)
        #  Timer A1: Private
        cls.timer_a1_desc = 'Test Timer'
        cls.timer_a1_id = write_timer_helper_a.new(cls.timer_a1_desc)
        #  Timer A2: Public
        cls.timer_a2_desc = cls.timer_a1_desc
        cls.timer_a2_id = write_timer_helper_a.new(
                cls.timer_a2_desc, public=True)

        # Sign Up Second Test User
        username_b = 'NOT-test-dave'
        password_b = '    wxyzWXYZ7890'
        cls.user_b = write_user_helper.prepare_user_in_db(
                username_b, password_b)
        cls.user_b.save()
        
        # Create Timers for Second Test User
        write_timer_helper_b = PADSWriteTimerHelper(cls.user_b.id)
        #  Timer B1: Private
        cls.timer_b1_desc = cls.timer_a1_desc
        cls.timer_b1_id = write_timer_helper_b.new(cls.timer_b1_desc)

    def test_get_from_db_valid_a(self):
        read_timer_helper = PADSReadTimerHelper(self.user_a.id)
        timer = read_timer_helper.get_from_db(self.timer_a1_id)
        # Assertions
        self.assertEqual(timer.id, self.timer_a1_id, 
                         'User A must get a Timer of a matching id')
    
    def test_get_from_db_valid_b(self):
        read_timer_helper = PADSReadTimerHelper(self.user_b.id)
        timer = read_timer_helper.get_from_db(self.timer_b1_id)
        # Assertions
        self.assertEqual(timer.id, self.timer_b1_id, 
                         'User B must get a Timer of a matching id')

    def test_get_from_db_valid_public(self):
        read_timer_helper = PADSReadTimerHelper()
        timer = read_timer_helper.get_from_db(self.timer_a2_id)
        # Assertions
        self.assertEqual(timer.id, self.timer_a2_id, 
                   'User not signed in must get a public Timer of matching id')

    def test_get_from_db_wrong_user_a(self):
        read_timer_helper = PADSReadTimerHelper(self.user_a.id)
        timer = read_timer_helper.get_from_db(self.timer_b1_id)
        # Assertions
        self.assertIsNone(timer, 'User A must not get another User\'s Timers')
    
    def test_get_from_db_wrong_user_b(self):
        read_timer_helper = PADSReadTimerHelper(self.user_b.id)
        timer = read_timer_helper.get_from_db(self.timer_a1_id)
        # Assertions
        self.assertIsNone(timer, 'User B must not get another User\'s Timers')
    
    def test_get_from_db_wrong_user_signed_out(self):
        read_timer_helper = PADSReadTimerHelper()
        timer = read_timer_helper.get_from_db(self.timer_a1_id)
        # Assertions
        self.assertIsNone(timer, 
                'User not signed in must not be able to access private Timers')

    def test_get_from_db_invalid_id_a(self):
        read_timer_helper = PADSReadTimerHelper(self.user_a.id)
        timer = read_timer_helper.get_from_db(-9999)
        # Assertions
        self.assertIsNone(timer, 
                    'User A must not get any Timer without a valid Timer id')

    def test_get_from_db_invalid_id_s(self):
        read_timer_helper = PADSReadTimerHelper()
        timer = read_timer_helper.get_from_db(-9999)
        # Assertions
        self.assertIsNone(timer, 
          'User not signed in must not get any Timer without a valid Timer id')


class PADSReadTimerHelperGetByPermalinkCodeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        
        def new_timer_get_permalink(user_id, description, **kwargs):
            write_timer_helper = PADSWriteTimerHelper(user_id)
            timer_id = write_timer_helper.new(user_id, **kwargs)
            timer = PADSTimer.objects.get(pk=timer_id)
            return timer.permalink_code
            
        # Sign Up Main Test User
        username_a = 'test-dave'
        password_a = '    abcdABCD1234'
        cls.user_a = write_user_helper.prepare_user_in_db(
                username_a, password_a)
        cls.user_a.save()
        
        # Create Timers for Main Test User
        #  Timer A1: Private
        cls.timer_a1_desc = 'Test Timer'
        cls.timer_a1_plink = new_timer_get_permalink(
                cls.user_a.id, cls.timer_a1_desc)
        #  Timer A2: Public
        cls.timer_a2_desc = cls.timer_a1_desc
        cls.timer_a2_plink = new_timer_get_permalink(
                cls.user_a.id, cls.timer_a2_desc, public=True)

        # Sign Up Second Test User
        username_b = 'NOT-test-dave'
        password_b = '    wxyzWXYZ7890'
        cls.user_b = write_user_helper.prepare_user_in_db(
                username_b, password_b)
        cls.user_b.save()
        
        # Create Timers for Second Test User
        #  Timer B1: Private
        cls.timer_b1_desc = cls.timer_a1_desc
        cls.timer_b1_plink = new_timer_get_permalink(
                cls.user_b.id, cls.timer_b1_desc)

    def test_get_from_db_by_permalink_code_valid_a(self):
        read_timer_helper = PADSReadTimerHelper(self.user_a.id)
        timer = read_timer_helper.get_from_db_by_permalink_code(
                self.timer_a1_plink)
        # Assertions
        self.assertEqual(timer.permalink_code, self.timer_a1_plink, 
                        'User A must get a Timer of a matching permalink code')
    
    def test_get_from_db_by_permalink_code_valid_b(self):
        read_timer_helper = PADSReadTimerHelper(self.user_b.id)
        timer = read_timer_helper.get_from_db_by_permalink_code(
                self.timer_b1_plink)
        # Assertions
        self.assertEqual(timer.permalink_code, self.timer_b1_plink, 
                        'User B must get a Timer of a matching permalink code')

    def test_get_from_db_by_permalink_code_valid_signed_out(self):
        read_timer_helper = PADSReadTimerHelper()
        timer = read_timer_helper.get_from_db_by_permalink_code(
                self.timer_a2_plink)
        # Assertions
        self.assertEqual(timer.permalink_code, self.timer_a2_plink, 
            'User not signed in must get a public Timer of matching permalink')

    def test_get_from_db_by_permalink_code_wrong_user_a(self):
        read_timer_helper = PADSReadTimerHelper(self.user_a.id)
        timer = read_timer_helper.get_from_db_by_permalink_code(
                self.timer_b1_plink)
        # Assertions
        self.assertIsNone(timer, 'User A must not get another User\'s Timers')
    
    def test_get_from_db_by_permalink_code_wrong_user_b(self):
        read_timer_helper = PADSReadTimerHelper(self.user_b.id)
        timer = read_timer_helper.get_from_db_by_permalink_code(
                self.timer_a1_plink)
        # Assertions
        self.assertIsNone(timer, 'User B must not get another User\'s Timers')
    
    def test_get_from_db_by_permalink_code_wrong_user_signed_out(self):
        read_timer_helper = PADSReadTimerHelper()
        timer = read_timer_helper.get_from_db_by_permalink_code(
                self.timer_a1_plink)
        # Assertions
        self.assertIsNone(timer, 
                'User not signed in must not be able to access private Timers')

    def test_get_from_db_by_permalink_code_invalid_id_a(self):
        read_timer_helper = PADSReadTimerHelper(self.user_a.id)
        for b in bad_str_inputs:
            timer = read_timer_helper.get_from_db_by_permalink_code(b)
            # Assertions
            self.assertIsNone(timer, 
                       'User A must not get any Timer without valid permalink')

    def test_get_from_db_by_permalink_code_invalid_id_signed_out(self):
        read_timer_helper = PADSReadTimerHelper()
        for b in bad_str_inputs:
            timer = read_timer_helper.get_from_db_by_permalink_code(b)
            # Assertions
            self.assertIsNone(timer, 
               'User not signed in musn\'t get Timers without valid permalink')

class PADSReadTimerGetGroupsByTimerIdTests(TestCase):
    def setUpTestData(self):
        raise NotImplementedError
        
    def test_get_groups_by_timer_id_valid_a(self):
        raise NotImplementedError

    def test_get_groups_by_timer_id_valid_b(self):
        raise NotImplementedError

    def test_get_groups_by_timer_id_valid_public(self):
        raise NotImplementedError
        
    def test_get_groups_by_timer_id_wrong_user_a(self):
        raise NotImplementedError
    
    def test_get_groups_by_timer_id_invalid_id(self):
        raise NotImplementedError
    

class PADSReadTimerGetResetsByTimerIdTests(TestCase):
# TODO: PADSReadTimerHelper.get_resets_by_timer_id() (valid, wrong user, not signed in)
    def setUpTestData(self):
        raise NotImplementedError
    
    

#
# Write Helper Tests
#
# TODO: PADSWriteTimerHelper.new() (valid, not signed in, bad input)
# TODO: PADSWriteTimerHelper.delete() (valid, not signed in, wrong user, bad input)
# TODO: PADSWriteTimerHelper.set_description() (valid, not signed in, wrong user, bad input)
# TODO: PADSWriteTimerHelper.stop_by_id() (valid, not signed in, wrong user, bad input)
# TODO: PADSWriteTimerHelper.restart_by_id() (valid, not signed in, wrong user, bad input)


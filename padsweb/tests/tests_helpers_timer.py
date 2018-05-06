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

    def test_get_from_db_valid_signed_out(self):
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

class PADSReadTimerHelperGetGroupsByTimerIdTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        
        # Sign Up Main Test User and Write Timer Helper
        username_a = 'test-dave-ggbt'
        password_a = '     mnbvcMNBVC-98765'
        cls.user_a = write_user_helper.prepare_user_in_db(
                username_a, password_a)
        cls.user_a.save()
        write_timer_helper = PADSWriteTimerHelper(cls.user_a.id)        
        
        # Create Timer Groups for Test User
        cls.tgroup_a1_desc = 'Test Timer Group A1'
        cls.tgroup_a1_id = write_timer_helper.new_group(cls.tgroup_a1_desc)
        cls.tgroup_a2_desc = 'Test Timer Group A2'
        cls.tgroup_a2_id = write_timer_helper.new_group(cls.tgroup_a2_desc)        
        
        # Set Up Timers for Main Test User
        cls.timer_a1_desc = 'Test Timer A1'
        cls.timer_a1_id = write_timer_helper.new(cls.timer_a1_desc)
        #  Add Timers to Groups
        #  Timer A1 is added to Group A1. Group A2 is left without a Timer.
        write_timer_helper.add_to_group(cls.timer_a1_id, cls.tgroup_a1_id)
        
    def test_get_groups_by_timer_id_valid_a(self):
        read_timer_helper = PADSReadTimerHelper(self.user_a.id)
        # Get ids of all groups associated with Test Timer A1
        timer_groups = read_timer_helper.get_groups_by_timer_id(
                self.timer_a1_id)
        timer_group_ids = []
        for tg in timer_groups:
            timer_group_ids.append(tg.id)
        # Assertions
        self.assertIn(self.tgroup_a1_id, timer_group_ids,
                      'A Timer must be included in a Group it was added to')
        self.assertNotIn(self.tgroup_a2_id, timer_group_ids,
                 'A Timer must be excluded from a Group it was never added to')

    def test_get_groups_by_timer_id_valid_ql(self):
        # Note: This test differs from test_get_groups_by_timer_id_valid().
        #  It tests the behaviour of multiple Timers sharing the same 
        #  Group instead.
        # Sign up Quick List User and Timer Helper
        user_q = write_user_helper.prepare_ql_user_in_db()[0]
        user_q.save()
        read_timer_helper = PADSReadTimerHelper(user_q.id)
        write_timer_helper = PADSWriteTimerHelper(user_q.id)
        # Create Timers for Test QL User
        timer_q1_desc = 'Test Timer Q1'
        timer_q1_id = write_timer_helper.new(timer_q1_desc)
        timer_q2_desc = 'Test Timer Q2'
        timer_q2_id = write_timer_helper.new(timer_q2_desc)
        # Create Timer Group
        tgroup_q1_desc = 'Timer Group Q1'
        tgroup_q1_id = write_timer_helper.new_group(tgroup_q1_desc)
        # Add both Timers to the Timer Group
        write_timer_helper.add_to_group(timer_q1_id, tgroup_q1_id)
        write_timer_helper.add_to_group(timer_q2_id, tgroup_q1_id)
        # Get Timer Group ids associated with Timers
        timer_groups_q1 = read_timer_helper.get_groups_by_timer_id(timer_q1_id)
        timer_q1_group_ids = []
        for tg in timer_groups_q1:
            timer_q1_group_ids.append(tg.id)
        timer_groups_q2 = read_timer_helper.get_groups_by_timer_id(timer_q2_id)
        timer_q2_group_ids = []
        for tg in timer_groups_q2:
            timer_q2_group_ids.append(tg.id)
        # Assertions
        self.assertIn(tgroup_q1_id, timer_q1_group_ids,
                      'Timer Q1 must be present in Timer Group Q1')
        self.assertIn(tgroup_q1_id, timer_q2_group_ids,
                      'Timer Q2 must be present in Timer Group Q1')

    def test_get_groups_by_timer_id_valid_signed_out(self):
        read_timer_helper = PADSReadTimerHelper()
        tgroups = read_timer_helper.get_groups_by_timer_id(self.timer_a1_id)
        # Assertions
        self.assertIsNone(tgroups,
                  'Timer Groups must not be returned while user is signed out')
        
    def test_get_groups_by_timer_id_wrong_user_a(self):
        # Set up second Test User
        username_b = 'not-test-dave'
        password_b = '     fghjFGHJ4567'
        user_b = write_user_helper.prepare_user_in_db(username_b, password_b)
        user_b.save()
        # Get Timer Groups
        read_timer_helper = PADSReadTimerHelper(user_b.id)
        tgroups = read_timer_helper.get_groups_by_timer_id(self.timer_a1_id)
        # Assertions
        self.assertIsNone(tgroups,
                          'A User cannot load another User\'s Timer Groups')
    
    def test_get_groups_by_timer_id_invalid_id(self):
        read_timer_helper = PADSReadTimerHelper(self.user_a.id)
        tgroups = read_timer_helper.get_groups_by_timer_id(-9999)
        # Assertions
        self.assertIsNone(tgroups,
               'Timer Groups must not be returned with an invalid Timer id')

class PADSReadTimerHelperGetResetsByTimerIdTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Sign Up Test Users and Timer Helpers
        #  User A
        username_a = 'test-dave-grbt'
        password_a = '     yuiopYUIOP1212121212'
        cls.user_a = write_user_helper.prepare_user_in_db(username_a, 
                                                          password_a)
        cls.user_a.save()
        write_timer_helper_a = PADSWriteTimerHelper(cls.user_a.id)
        cls.read_timer_helper_a = PADSReadTimerHelper(cls.user_a.id)
        #  User B
        username_b = 'not-test-dave'
        password_b = password_a
        cls.user_b = write_user_helper.prepare_user_in_db(username_b,
                                                          password_b)
        cls.user_b.save()        
        write_timer_helper_b = PADSWriteTimerHelper(cls.user_b.id)
        cls.read_timer_helper_b = PADSReadTimerHelper(cls.user_b.id)
        #  Quick List User
        cls.user_q = write_user_helper.prepare_ql_user_in_db()[0]
        cls.user_q.save()
        write_timer_helper_q = PADSWriteTimerHelper(cls.user_q.id)
        cls.read_timer_helper_q = PADSReadTimerHelper(cls.user_q.id)
        # Create Timers and Log Entries for Test Users
        #  User A
        cls.timer_a1_desc = 'Test Timer A1 by User A'
        cls.timer_a1_id = write_timer_helper_a.new(cls.timer_a1_desc)
        cls.logent_a1_desc = 'Log Entry for Timer A1 by User A'
        cls.logent_a1_id = write_timer_helper_a.new_log_entry(
                cls.timer_a1_id, cls.logent_a1_desc)
        cls.timer_a2_desc = 'Test Timer A2 by User A (Public)'
        cls.timer_a2_id = write_timer_helper_a.new(cls.timer_a2_desc, 
                                                   public=True)
        cls.logent_a2_desc = 'Log Entry for Timer A2 by User A (Public)'
        cls.logent_a2_id = write_timer_helper_a.new_log_entry(
                cls.timer_a2_id, cls.logent_a2_desc)
        #  User B
        cls.timer_b1_desc = 'Test Timer B1 by User B'
        cls.timer_b1_id = write_timer_helper_b.new(cls.timer_b1_desc)
        cls.logent_b1_desc = 'Log Entry B1 for Timer B1 by User B'
        cls.logent_b1_id = write_timer_helper_b.new_log_entry(
                cls.timer_b1_id, cls.logent_b1_desc)
        #  Quick List User
        cls.timer_q1_desc = 'Test Timer Q1 by QL User'
        cls.timer_q1_id = write_timer_helper_q.new(cls.timer_q1_desc)
        cls.logent_q1_desc = 'Log Entry Q1 for Timer Q1 by QL User'
        cls.logent_q1_id = write_timer_helper_q.new_log_entry(
                cls.timer_q1_id, cls.logent_q1_desc)
    
    def get_reset_reason_list(self, timer_id, read_timer_helper):
        resets = read_timer_helper.get_resets_from_db_by_timer_id(timer_id)
        if resets is None:
            return None
        reasons = []
        for r in resets:
            reasons.append(r.reason)
        return reasons
            
    def get_reset_id_list(self, timer_id, read_timer_helper):
        resets = read_timer_helper.get_resets_from_db_by_timer_id(timer_id)
        if resets is None:
            return None
        ids = []
        for r in resets:
            ids.append(r.id)
        return ids
    
    def test_get_resets_by_timer_id_valid_a(self):
        logent_ids = self.get_reset_id_list(self.timer_a1_id, 
                                            self.read_timer_helper_a)
        logent_descs = self.get_reset_reason_list(self.timer_a1_id, 
                                                  self.read_timer_helper_a)
        # Asserts
        self.assertIn(self.logent_a1_id, logent_ids)
        self.assertIn(self.logent_a1_desc, logent_descs)
        self.assertNotIn(self.logent_b1_id, logent_ids)
        self.assertNotIn(self.logent_q1_id, logent_ids)
        
    def test_get_resets_by_timer_id_valid_public_a(self):
        logent_ids = self.get_reset_id_list(self.timer_a2_id, 
                                            self.read_timer_helper_a)
        logent_descs = self.get_reset_reason_list(self.timer_a2_id, 
                                                  self.read_timer_helper_a)
        # Asserts
        self.assertIn(self.logent_a2_id, logent_ids)
        self.assertIn(self.logent_a2_desc, logent_descs)
        self.assertNotIn(self.logent_b1_id, logent_ids)
        self.assertNotIn(self.logent_q1_id, logent_ids)
            
    def test_get_resets_by_timer_id_valid_ql(self):
        logent_ids = self.get_reset_id_list(self.timer_q1_id, 
                                            self.read_timer_helper_q)
        logent_descs = self.get_reset_reason_list(self.timer_q1_id, 
                                                  self.read_timer_helper_q)
        # Asserts
        self.assertIn(self.logent_q1_id, logent_ids)
        self.assertIn(self.logent_q1_desc, logent_descs)
        self.assertNotIn(self.logent_a1_id, logent_ids)
        self.assertNotIn(self.logent_b1_id, logent_ids)
        
    def test_get_resets_by_timer_id_valid_public_ql(self):
        logent_ids = self.get_reset_id_list(self.timer_a2_id, 
                                            self.read_timer_helper_q)
        logent_descs = self.get_reset_reason_list(self.timer_a2_id, 
                                                  self.read_timer_helper_q)
        # Asserts
        self.assertIn(self.logent_a2_id, logent_ids)
        self.assertIn(self.logent_a2_desc, logent_descs)
        self.assertNotIn(self.logent_a1_id, logent_ids)
        self.assertNotIn(self.logent_b1_id, logent_ids)
        self.assertNotIn(self.logent_q1_id, logent_ids)
        
    def test_get_resets_by_timer_id_valid_public_signed_out(self):
        read_timer_helper = PADSReadTimerHelper()
        logent_ids = self.get_reset_id_list(self.timer_a2_id,read_timer_helper)
        logent_descs = self.get_reset_reason_list(self.timer_a2_id,
                                                  read_timer_helper)
        # Asserts
        self.assertIn(self.logent_a2_id, logent_ids)
        self.assertIn(self.logent_a2_desc, logent_descs)
        self.assertNotIn(self.logent_a1_id, logent_ids)
        self.assertNotIn(self.logent_b1_id, logent_ids)
        self.assertNotIn(self.logent_q1_id, logent_ids)

    def test_get_resets_by_timer_id_signed_out(self):
        read_timer_helper = PADSReadTimerHelper()
        logent_ids = self.get_reset_id_list(self.timer_a1_id,read_timer_helper)
        logent_descs = self.get_reset_reason_list(self.timer_a1_id,
                                                  read_timer_helper)
        # Asserts
        self.assertIsNone(logent_descs)
        self.assertIsNone(logent_ids)
    
    def test_get_resets_by_timer_id_wrong_user_a(self):
        logent_ids = self.get_reset_id_list(self.timer_a1_id,
                                            self.read_timer_helper_b)
        logent_descs = self.get_reset_reason_list(self.timer_a1_id,
                                            self.read_timer_helper_b)
        # Asserts
        self.assertIsNone(logent_descs)
        self.assertIsNone(logent_ids)
    
    def test_get_groups_by_timer_id_invalid_id(self):
        logent_ids = self.get_reset_id_list(-9999, self.read_timer_helper_a)
        logent_descs = self.get_reset_reason_list(-9999, 
                                                  self.read_timer_helper_a)
        # Asserts
        self.assertIsNone(logent_descs)
        self.assertIsNone(logent_ids)

    def test_get_groups_by_timer_id_invalid_id_signed_out(self):
        read_timer_helper = PADSReadTimerHelper()
        logent_ids = self.get_reset_id_list(-9999, read_timer_helper)
        logent_descs = self.get_reset_reason_list(-9999, read_timer_helper)
        # Asserts
        self.assertIsNone(logent_descs)
        self.assertIsNone(logent_ids)


#
# Write Helper Tests
#
class PADSWriteTimerHelperNewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        raise NotImplementedError
    
    def test_new_valid(self):
        raise NotImplementedError
        
    def test_new_valid_opening_message(self):
        raise NotImplementedError
    
    def test_new_valid_historical(self):
        raise NotImplementedError
        
    def test_new_valid_historical_not_running(self):
        raise NotImplementedError
    
    def test_new_valid_public(self):
        raise NotImplementedError
    
    def test_new_signed_out(self):
        raise NotImplementedError
    
    def test_new_bad_description(self):
        raise NotImplementedError
    
class PADSWriteTimerHelperNewLogEntryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        raise NotImplementedError

class PADSWriteTimerHelperAddToGroupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        raise NotImplementedError

class PADSWriteTimerHelperNewGroupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        raise NotImplementedError

class PADSWriteTimerHelperDeleteGroupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        raise NotImplementedError

class PADSWriteTimerHelperRemoveFromGroupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        raise NotImplementedError

class PADSWriteTimerHelperDeleteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        raise NotImplementedError
    
    def test_delete_valid_a(self):
        raise NotImplementedError

    def test_delete_valid_b(self):
        raise NotImplementedError
    
    def test_delete_signed_out(self):
        raise NotImplementedError
    
    def test_delete_invalid_wrong_user_a(self):
        raise NotImplementedError

    def test_delete_invalid_id(self):
        raise NotImplementedError

class PADSWriteTimerHelperSetDescriptionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        raise NotImplementedError
    
    def test_set_description_valid_a(self):
        raise NotImplementedError

    def test_set_description_valid_b(self):
        raise NotImplementedError
    
    def test_set_description_signed_out(self):
        raise NotImplementedError

    def test_set_description_bad_description(self):
        raise NotImplementedError
    
    def test_set_description_wrong_user_a(self):
        raise NotImplementedError

class PADSWriteTimerHelperResetByIdTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        raise NotImplementedError
    
    def test_reset_by_id_valid_a(self):
        raise NotImplementedError

    def test_reset_by_id_valid_b(self):
        raise NotImplementedError
    
    def test_reset_by_id_signed_out(self):
        raise NotImplementedError

    def test_reset_by_id_bad_reason_a(self):
        raise NotImplementedError

    def test_reset_by_id_invalid_id(self):
        raise NotImplementedError

class PADSWriteTimerHelperStopByIdTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        raise NotImplementedError

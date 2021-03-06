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
from padsweb.models import GroupInclusion
from padsweb.models import PADSTimer, PADSTimerGroup, PADSTimerReset 
from padsweb.settings import defaults
import time
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
            timer_id = write_timer_helper.new(description, **kwargs)
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
        # Sign Up Test User and Timer Helpers
        username_a = 'test-jess-hnt'
        password_a = '    ertyERTY553-355'
        cls.user_a = write_user_helper.prepare_user_in_db(username_a, 
                                                          password_a)
        cls.user_a.save()
        cls.write_timer_helper_a = PADSWriteTimerHelper(cls.user_a.id)
        cls.read_timer_helper_a = PADSReadTimerHelper(cls.user_a.id)
        
    def test_new_valid(self):
        timer_a_desc = 'Test Timer A by Test User A'
        timer_a_id = self.write_timer_helper_a.new(timer_a_desc)
        #  Assertions
        timer_assert = PADSTimer.objects.get(pk=timer_a_id)
        self.assertEquals(timer_a_desc, timer_assert.description,
                      'Timer Description must be the same as declared by User')
        self.assertEquals(timer_assert.creator_user_id, self.user_a.id,
                          'Creator User id must be correctly assigned')
        self.assertFalse(timer_assert.historical,
                         'Timer must be non-historical by default')
        self.assertFalse(timer_assert.public, 
                         'Timer must be private by default')    
        self.assertTrue(timer_assert.running, 
                        'Timer must be running by default')
    
    def test_new_valid_ql(self):
        # Sign Up Test Quick List User and Timer Helper
        user_ql = write_user_helper.prepare_ql_user_in_db()[0]
        user_ql.save()
        write_timer_helper_q = PADSWriteTimerHelper(user_ql.id)
        # Create Timers as QL User
        timer_q_desc = 'Test Timer by Quick List User'
        timer_q_id = write_timer_helper_q.new(timer_q_desc)
        # Assertions
        timer_assert= PADSTimer.objects.get(pk=timer_q_id)
        self.assertEquals(timer_assert.creator_user_id, user_ql.id,
                          'Creator User id must be correctly assigned')
                
    def test_new_valid_opening_message(self):
        timer_am_desc = 'Test Timer A by Test User A with Message'
        timer_am_opmesg = 'Opening Message by Test User A'
        timer_am_id = self.write_timer_helper_a.new(
                    timer_am_desc,message=timer_am_opmesg)
        # Assertions
        logent = PADSTimerReset.objects.filter(timer_id=timer_am_id)[0]
        self.assertIn(logent.reason, timer_am_opmesg)
        
    
    def test_new_valid_historical(self):
        timer_ah_desc = 'Test Historical Timer A by Test User A'
        timer_ah_id = self.write_timer_helper_a.new(
                timer_ah_desc,historical=True)
        # Assertions
        timer_assert = PADSTimer.objects.get(pk=timer_ah_id)
        self.assertEquals(timer_ah_id, timer_assert.id,
                              'Correct Timer id must be returned on creation')
        self.assertTrue(timer_assert.historical,
                     'Helper must be able to set Historical flag on creation')
        
    def test_new_valid_public(self):
        timer_ap_desc = 'Test Public Timer A by Test User A'
        timer_ap_id = self.write_timer_helper_a.new(
                timer_ap_desc,public=True)
        # Assertions
        timer_assert = PADSTimer.objects.get(pk=timer_ap_id)
        self.assertEquals(timer_ap_id, timer_assert.id,
                              'Correct Timer id must be returned on creation')
        self.assertTrue(timer_assert.public,
                            'Helper must be able to create new public Timers')

    def test_new_historical_not_running(self):
        timer_ahn_desc = 'Test Non-running Historical Timer A by Test User A'
        timer_ahn_id = self.write_timer_helper_a.new(
                timer_ahn_desc,historical=True,running=False)
        # Assertions
        #  Reminder: Historical Timers cannot be reset, so creating a 
        #  non-running Historical Timer is not allowed.
        timer_exists = PADSTimer.objects.filter(
                description=timer_ahn_desc).exists()
        self.assertIsNone(timer_ahn_id,
                             'Historical Timers cannot be created non-running')
        self.assertFalse(timer_exists,
                    'New non-running Historical Timer must not be in database')
    
    def test_new_signed_out(self):
        write_timer_helper_s = PADSWriteTimerHelper()
        timer_s_desc = 'Test Timer by Signed Out User'
        timer_s_id = write_timer_helper_s.new(timer_s_desc)
        timer_created = PADSTimer.objects.filter(
                description=timer_s_desc).exists()
        # Assertions
        self.assertIsNone(timer_s_id,
             'Helper must indicate failure to save Timers for signed-out User')
        self.assertFalse(timer_created, 
                      'Timer created by signed-out User cannot be in database')
    
    def test_new_bad_description(self):
        # Multi-assertion
        for s in bad_str_inputs.values():
            timer_id = self.write_timer_helper_a.new(s)
            timer_created = PADSTimer.objects.filter(description=s).exists()
            if timer_created is True:
                print('Timer Desc: {0}'.format(s))                
            self.assertIsNone(timer_id,
                 'Must indicate Timer creation failure (signed in, bad desc.)')
            self.assertFalse(timer_created,
                       'Timers with a bad description must not be in database')
        
    def test_new_bad_description_signed_out(self):
        write_timer_helper_s = PADSWriteTimerHelper()
        # Multi-assertion
        for s in bad_str_inputs.values():
            timer_id = write_timer_helper_s.new(s)
            timer_created = PADSTimer.objects.filter(description=s).exists()
            self.assertIsNone(timer_id,
                 'Must indicate Timer creation failure (signed in, bad desc.)')
            self.assertFalse(timer_created,
                       'Timers with a bad description must not be in database')


class PADSWriteTimerHelperNewLogEntryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set Up Test Users and Write Timer Helpers
        #  Test User A
        username_a = 'test-jess-nlet'
        password_a = '       plusPLUS+1111111'
        cls.user_a = write_user_helper.prepare_user_in_db(
                username_a, password_a)
        cls.user_a.save()
        cls.write_timer_helper_a = PADSWriteTimerHelper(cls.user_a.id)
        # Test Quick List User
        cls.user_q = write_user_helper.prepare_ql_user_in_db()[0]
        cls.user_q.save()
        cls.write_timer_helper_q = PADSWriteTimerHelper(cls.user_q.id)
        
        # Set Up Test Timers
        #  Test User A's Timer
        timer_a1_p_desc = 'Test Timer A1 by Test User A (Public)'
        cls.timer_a1_p_id = cls.write_timer_helper_a.new(
                timer_a1_p_desc, public=True)
        #  Test QL User's Timer
        timer_q1_p_desc = 'Test Timer Q1 by Test QL User (Public)'
        cls.timer_q1_p_id = cls.write_timer_helper_q.new(
                timer_q1_p_desc, public=True)
    
    def test_new_log_entry_valid_a(self):
        reason = 'Event for Test Timer A1'
        entry_id = self.write_timer_helper_a.new_log_entry(
                self.timer_a1_p_id, reason)
        entry_created = PADSTimerReset.objects.filter(
                timer_id=self.timer_a1_p_id, reason=reason).exists()
        # Assertions
        self.assertTrue(entry_created)
        self.assertIsNotNone(entry_id)
    
    def test_new_log_entry_valid_q(self):
        reason = 'Event for Test Timer Q1'
        entry_id = self.write_timer_helper_q.new_log_entry(
                self.timer_q1_p_id, reason)
        entry_created = PADSTimerReset.objects.filter(
                timer_id=self.timer_q1_p_id, reason=reason).exists()
        # Assertions
        self.assertTrue(entry_created)
        self.assertIsNotNone(entry_id)

    def test_new_log_entry_wrong_user_a(self):
        reason = 'Attempt by User A to add log entry to Timer Q1'
        entry_id = self.write_timer_helper_a.new_log_entry(
                self.timer_q1_p_id, reason)
        entry_created = PADSTimerReset.objects.filter(
                timer_id=self.timer_q1_p_id, reason=reason).exists()
        # Assertions
        self.assertFalse(entry_created)
        self.assertIsNone(entry_id)

    def test_new_log_entry_wrong_user_q(self):
        reason = 'Attempt by QL User to add log entry to Timer A1'
        entry_id = self.write_timer_helper_q.new_log_entry(
                self.timer_a1_p_id, reason)
        entry_created = PADSTimerReset.objects.filter(
                timer_id=self.timer_a1_p_id, reason=reason).exists()
        # Assertions
        self.assertFalse(entry_created)
        self.assertIsNone(entry_id)

    def test_new_log_entry_bad_description_a(self):
        # Multi-assertion
        for i in bad_str_inputs.values():
            entry_id = self.write_timer_helper_a.new_log_entry(
                    self.timer_a1_p_id, i)
            entry_created = PADSTimerReset.objects.filter(
                    timer_id=self.timer_a1_p_id, reason=i).exists()
            self.assertFalse(entry_created)
            self.assertIsNone(entry_id)
            
    def test_new_log_entry_bad_description_q(self):
        # Multi-assertion
        for i in bad_str_inputs.values():
            entry_id = self.write_timer_helper_q.new_log_entry(
                    self.timer_q1_p_id, i)
            entry_created = PADSTimerReset.objects.filter(
                    timer_id=self.timer_q1_p_id, reason=i).exists()
            self.assertFalse(entry_created)
            self.assertIsNone(entry_id)

    def test_new_log_entry_invalid_id_a(self):
        reason = 'Attempt by Test User to add log event to non-existing Timer'
        entry_id = self.write_timer_helper_a.new_log_entry(
            -9999, reason)
        entry_created = PADSTimerReset.objects.filter(reason=reason).exists()
        # Assertions
        self.assertFalse(entry_created)
        self.assertIsNone(entry_id)
        
    def test_new_log_entry_signed_out(self):
        write_timer_helper = PADSWriteTimerHelper()
        reason = 'Attempt by Test User to add log event to non-existing Timer'
        entry_id = write_timer_helper.new_log_entry(self.timer_a1_p_id, reason)
        entry_created = PADSTimerReset.objects.filter(reason=reason).exists()
        # Assertions
        self.assertFalse(entry_created)
        self.assertIsNone(entry_id)
        
class PADSWriteTimerHelperNewGroupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set Up Test Users and Write Timer Helpers
        #  Test User A
        username_a = 'test-jess-thng'
        password_a = '       <>^v<>^vwazsWAZS42684268'
        cls.user_a = write_user_helper.prepare_user_in_db(
                username_a, password_a)
        cls.user_a.save()
        cls.write_timer_helper_a = PADSWriteTimerHelper(cls.user_a.id)
        # Test Quick List User
        cls.user_q = write_user_helper.prepare_ql_user_in_db()[0]
        cls.user_q.save()
        cls.write_timer_helper_q = PADSWriteTimerHelper(cls.user_q.id)
    
    def test_new_group_valid_a(self):
        group_name= 'test_group_ga1_user_a'
        group_ga1_id = self.write_timer_helper_a.new_group(group_name)
        group_ga1 = PADSTimerGroup.objects.get(pk=group_ga1_id) # ga1, not gaL
        # Assertions
        self.assertIsNotNone(group_ga1_id)
        self.assertEquals(group_ga1.name, group_name)
        self.assertEquals(group_ga1.creator_user_id, self.user_a.id)
        
    def test_new_group_valid_q(self):
        group_name= 'test_group_gq1_user_q'
        group_gq1_id = self.write_timer_helper_q.new_group(group_name)
        group_gq1 = PADSTimerGroup.objects.get(pk=group_gq1_id) # gq1, not gaL
        # Assertions
        self.assertIsNotNone(group_gq1_id)
        self.assertEquals(group_gq1.name, group_name)
        self.assertEquals(group_gq1.creator_user_id, self.user_q.id)
    
    def test_new_group_same_name_a(self):
        group_name = 'test_group_ga2_dup_user_a'
        # Attempt to create a group with the same name twice for User A
        self.write_timer_helper_a.new_group(group_name)
        group_ga2_dup_id = self.write_timer_helper_a.new_group(group_name)
        # Assertions
        self.assertIsNone(group_ga2_dup_id)

    def test_new_group_same_name_q(self):
        group_name = 'test_group_gq2_dup_user_q'
        # Attempt to create a group with the same name twice for QL User
        self.write_timer_helper_q.new_group(group_name)
        group_gq2_dup_id = self.write_timer_helper_q.new_group(group_name)
        # Assertions
        self.assertIsNone(group_gq2_dup_id)
    
    def test_new_group_bad_name_a(self):
        # Multi-assertions
        for i in bad_str_inputs.values():
            bad_group_id = self.write_timer_helper_a.new_group(i)
            if i is not None:
                # Beginner's PROTIP: None is not an accepted value for Django
                # database queries.
                bad_group_created = PADSTimerGroup.objects.filter(
                        name__icontains=i).exists()
            else:
                bad_group_created = False
            self.assertIsNone(bad_group_id)
            self.assertFalse(bad_group_created)

    def test_new_group_bad_name_q(self):
        # Multi-assertions
        for i in bad_str_inputs.values():
            bad_group_id = self.write_timer_helper_q.new_group(i)
            if i is not None:
                bad_group_created = PADSTimerGroup.objects.filter(
                        name__icontains=i).exists()
            else:
                bad_group_created = False
            self.assertIsNone(bad_group_id)
            self.assertFalse(bad_group_created)
        
    def test_new_group_signed_out(self):
        write_timer_helper = PADSWriteTimerHelper()
        group_name = 'test_group_gs1_signed_out_user'
        group_gs1_id = write_timer_helper.new_group(group_name)
        group_created = PADSTimerGroup.objects.filter(
                name__icontains=group_name)
        # Assertions
        self.assertIsNone(group_gs1_id)
        self.assertFalse(group_created)

class PADSWriteTimerHelperAddToGroupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set Up Test Users and Write Timer Helpers
        #  Test User A
        username_a = 'test-jess-atgt'
        password_a = '       mnbvcxzMNBVVCXZ12345'
        cls.user_a = write_user_helper.prepare_user_in_db(
                username_a, password_a)
        cls.user_a.save()
        cls.write_timer_helper_a = PADSWriteTimerHelper(cls.user_a.id)
        #  Test Quick List User
        cls.user_q = write_user_helper.prepare_ql_user_in_db()[0]
        cls.user_q.save()
        cls.write_timer_helper_q = PADSWriteTimerHelper(cls.user_q.id)
        # Set up Test Timers for Test Users
        #  Test User A
        timer_a1_desc = 'Test Timer A1 by Test User A'
        cls.timer_a1_id = cls.write_timer_helper_a.new(timer_a1_desc)
        timer_a2_p_desc = 'Test Timer A2 (Public) by Test User A'
        cls.timer_a2_p_id = cls.write_timer_helper_a.new(
                timer_a2_p_desc, public=True)
        #  Test QL User
        timer_q1_desc = 'Test Timer Q1 by Test QL User'
        cls.timer_q1_id = cls.write_timer_helper_q.new(timer_q1_desc)        
        timer_q2_p_desc = 'Test Timer A2 (Public) by Test User A'
        cls.timer_q2_p_id = cls.write_timer_helper_q.new(
                timer_q2_p_desc, public=True)
        # Set up Test Timer Groups for Test Users
        #  Test User A
        cls.tgroup_ga1_name = 'test_group_ga1_user_a'
        cls.tgroup_ga1_id = cls.write_timer_helper_a.new_group(
                cls.tgroup_ga1_name)
        #  Test QL User
        cls.tgroup_gq1_name = 'test_group_gq1_user_q'
        cls.tgroup_gq1_id = cls.write_timer_helper_q.new_group(
                cls.tgroup_ga1_name)
        
    def test_add_to_group_valid_private_a(self):
        add_result = self.write_timer_helper_a.add_to_group(
                self.timer_a1_id, self.tgroup_ga1_id)
        a1_ga1_exists = GroupInclusion.objects.filter(
                timer_id=self.timer_a1_id, group_id=self.tgroup_ga1_id)
        # Assertions
        self.assertTrue(add_result)
        self.assertTrue(a1_ga1_exists)
    
    def test_add_to_group_valid_private_q(self):
        add_result = self.write_timer_helper_q.add_to_group(
                self.timer_q1_id, self.tgroup_gq1_id)
        q1_gq1_exists = GroupInclusion.objects.filter(
                timer_id=self.timer_q1_id, group_id=self.tgroup_gq1_id)
        # Assertions
        self.assertTrue(add_result)
        self.assertTrue(q1_gq1_exists)
        
    def test_add_to_group_valid_public_other_user_a(self):
        # A User may add another User's public Timer to own Groups.
        add_result = self.write_timer_helper_a.add_to_group(
                self.timer_q2_p_id, self.tgroup_ga1_id)
        q2_p_ga1_exists = GroupInclusion.objects.filter(
                timer_id=self.timer_q2_p_id,
                group_id=self.tgroup_ga1_id).exists()
        # Assertions
        self.assertTrue(add_result)
        self.assertTrue(q2_p_ga1_exists)

    def test_add_to_group_valid_public_other_user_q(self):
        # A QL User may add another User's public Timer to own Groups.
        add_result = self.write_timer_helper_q.add_to_group(
                self.timer_a2_p_id, self.tgroup_gq1_id)
        a2_p_gq1_exists = GroupInclusion.objects.filter(
                timer_id=self.timer_a2_p_id,
                group_id=self.tgroup_gq1_id).exists()
        # Assertions
        self.assertTrue(add_result)
        self.assertTrue(a2_p_gq1_exists)
    
    def test_add_to_group_private_other_user_a(self):
        # A User must fail to add another User's private Timers to own Groups.
        add_result = self.write_timer_helper_a.add_to_group(
                self.timer_q1_id, self.tgroup_ga1_id)
        q1_ga1_exists = GroupInclusion.objects.filter(
                timer_id=self.timer_q1_id,
                group_id=self.tgroup_ga1_id).exists()
        # Assertions
        self.assertFalse(add_result)
        self.assertFalse(q1_ga1_exists)

    def test_add_to_group_private_other_user_q(self):
        # A QL User must fail to add other Users' private Timers to own Groups.
        add_result = self.write_timer_helper_q.add_to_group(
                self.timer_a1_id, self.tgroup_gq1_id)
        a1_gq1_exists = GroupInclusion.objects.filter(
                timer_id=self.timer_a1_id,
                group_id=self.tgroup_gq1_id).exists()
        # Assertions
        self.assertFalse(add_result)
        self.assertFalse(a1_gq1_exists)
    
    def test_add_to_group_wrong_user_a(self):
        # A User must fail to add any Timer to another User's Groups.
        add_result_a1_gq1 = self.write_timer_helper_a.add_to_group(
                self.timer_a1_id, self.tgroup_gq1_id)
        add_result_a2_p_gq1 = self.write_timer_helper_a.add_to_group(
                self.timer_a2_p_id, self.tgroup_gq1_id)
        add_result_q1_gq1 = self.write_timer_helper_a.add_to_group(
                self.timer_q1_id, self.tgroup_gq1_id)
        add_result_q2_p_gq1 = self.write_timer_helper_a.add_to_group(
                self.timer_q2_p_id, self.tgroup_gq1_id)        
        inclusions_created = GroupInclusion.objects.all().count()
        # Assertions
        self.assertFalse(add_result_a1_gq1)
        self.assertFalse(add_result_a2_p_gq1)
        self.assertFalse(add_result_q1_gq1)
        self.assertFalse(add_result_q2_p_gq1)
        self.assertEquals(inclusions_created, 0)
    
    def test_add_to_group_wrong_user_q(self):
        # A QL User must fail to add any Timer to another User's Groups.
        add_result_a1_ga1 = self.write_timer_helper_q.add_to_group(
                self.timer_a1_id, self.tgroup_ga1_id)
        add_result_a2_p_ga1 = self.write_timer_helper_q.add_to_group(
                self.timer_a2_p_id, self.tgroup_ga1_id)
        add_result_q1_ga1 = self.write_timer_helper_q.add_to_group(
                self.timer_q1_id, self.tgroup_ga1_id)
        add_result_q2_p_ga1 = self.write_timer_helper_q.add_to_group(
                self.timer_q2_p_id, self.tgroup_ga1_id)        
        inclusions_created = GroupInclusion.objects.all().count()
        # Assertions
        self.assertFalse(add_result_a1_ga1)
        self.assertFalse(add_result_a2_p_ga1)
        self.assertFalse(add_result_q1_ga1)
        self.assertFalse(add_result_q2_p_ga1)
        self.assertEquals(inclusions_created, 0)

    def test_add_to_group_invalid_timer_id_a(self):
        add_result = self.write_timer_helper_a.add_to_group(
                -9999, self.tgroup_ga1_id)
        inclusions_created = GroupInclusion.objects.all().count()
        # Assertions
        self.assertFalse(add_result)
        self.assertEquals(inclusions_created, 0)

    def test_add_to_group_invalid_timer_id_q(self):
        add_result = self.write_timer_helper_q.add_to_group(
                -9999, self.tgroup_ga1_id)
        inclusions_created = GroupInclusion.objects.all().count()
        # Assertions
        self.assertFalse(add_result)
        self.assertEquals(inclusions_created, 0)
    
    def test_add_to_group_invalid_group_id_a(self):
        add_result = self.write_timer_helper_a.add_to_group(
                self.timer_a1_id, -9999)
        add_result_p = self.write_timer_helper_a.add_to_group(
                self.timer_a2_p_id, -9999)
        inclusions_created = GroupInclusion.objects.all().count()
        # Assertions
        self.assertFalse(add_result)
        self.assertFalse(add_result_p)
        self.assertEquals(inclusions_created, 0)

    def test_add_to_group_invalid_group_id_q(self):
        add_result = self.write_timer_helper_q.add_to_group(
                self.timer_a1_id, -9999)
        add_result_p = self.write_timer_helper_q.add_to_group(
                self.timer_a2_p_id, -9999)
        inclusions_created = GroupInclusion.objects.all().count()
        # Assertions
        self.assertFalse(add_result)
        self.assertFalse(add_result_p)
        self.assertEquals(inclusions_created, 0)
    
    def test_add_to_group_invalid_ids_a(self):
        add_result = self.write_timer_helper_a.add_to_group(
                -9999, -9999)
        inclusions_created = GroupInclusion.objects.all().count()
        # Assertions
        self.assertFalse(add_result)
        self.assertEquals(inclusions_created, 0)

    def test_add_to_group_invalid_ids_q(self):
        add_result = self.write_timer_helper_q.add_to_group(
                -9999, -9999)
        inclusions_created = GroupInclusion.objects.all().count()
        # Assertions
        self.assertFalse(add_result)
        self.assertEquals(inclusions_created, 0)
 
class PADSWriteTimerHelperDeleteGroupByIdTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set Up Test Users and Write Timer Helpers
        #  Test User A'
        username_a = 'test-jess-thdgbi'
        password_a = '       +-/*+-/*fghjFGHJ99999'
        cls.user_a = write_user_helper.prepare_user_in_db(
                username_a, password_a)
        cls.user_a.save()
        cls.write_timer_helper_a = PADSWriteTimerHelper(cls.user_a.id)
        #  Test Quick List User
        cls.user_q = write_user_helper.prepare_ql_user_in_db()[0]
        cls.user_q.save()
        cls.write_timer_helper_q = PADSWriteTimerHelper(cls.user_q.id)
        # Set up Test Timer Groups for Test Users
        #  Test User A'
        cls.tgroup_ga1_name = 'test_group_ga1_user_a'
        cls.tgroup_ga1_id = cls.write_timer_helper_a.new_group(
                cls.tgroup_ga1_name)
        cls.tgroup_ga1 = PADSTimerGroup.objects.get(pk=cls.tgroup_ga1_id)
        #  Test QL User
        cls.tgroup_gq1_name = 'test_group_gq1_user_q'
        cls.tgroup_gq1_id = cls.write_timer_helper_q.new_group(
                cls.tgroup_ga1_name)
        cls.tgroup_gq1 = PADSTimerGroup.objects.get(pk=cls.tgroup_gq1_id)
    
    def all_tgroups_in_database(self):
        '''Checks if the test Timer Groups are still in the database
        '''
        tgroup_ga1_exists = PADSTimerGroup.objects.filter(
                pk=self.tgroup_ga1_id).exists()
        tgroup_gq1_exists = PADSTimerGroup.objects.filter(
                pk=self.tgroup_ga1_id).exists()
        return tgroup_ga1_exists & tgroup_gq1_exists
        
    def test_delete_group_by_id_valid_a(self):
        del_result = self.write_timer_helper_a.delete_group_by_id(
                self.tgroup_ga1_id)
        tgroup_ga1_exists = PADSTimerGroup.objects.filter(
                pk=self.tgroup_ga1_id)
        # Assertions
        self.assertTrue(del_result)
        self.assertFalse(tgroup_ga1_exists)

    def test_delete_group_by_id_valid_q(self):
        del_result = self.write_timer_helper_q.delete_group_by_id(
                self.tgroup_gq1_id)
        tgroup_gq1_exists = PADSTimerGroup.objects.filter(
                pk=self.tgroup_gq1_id)
        # Assertions
        self.assertTrue(del_result)
        self.assertFalse(tgroup_gq1_exists)

    def test_delete_group_by_id_wrong_user_a(self):
        del_result = self.write_timer_helper_a.delete_group_by_id(
                self.tgroup_gq1_id)
        tgroup_gq1_exists = PADSTimerGroup.objects.filter(
                pk=self.tgroup_gq1_id)
        # Assertions
        self.assertFalse(del_result)
        self.assertTrue(tgroup_gq1_exists)

    def test_delete_group_by_id_wrong_user_q(self):
        del_result = self.write_timer_helper_q.delete_group_by_id(
                self.tgroup_ga1_id)
        tgroup_ga1_exists = PADSTimerGroup.objects.filter(
                pk=self.tgroup_ga1_id)
        # Assertions
        self.assertFalse(del_result)
        self.assertTrue(tgroup_ga1_exists)
    
    def test_delete_group_by_id_invalid_id_a(self):
        del_result = self.write_timer_helper_a.delete_group_by_id(-9999)
        # Assertions
        self.assertFalse(del_result)
        self.assertTrue(self.all_tgroups_in_database())

    def test_delete_group_by_id_invalid_id_q(self):
        del_result = self.write_timer_helper_q.delete_group_by_id(-9999)
        # Assertions
        self.assertFalse(del_result)
        self.assertTrue(self.all_tgroups_in_database())
    
    def test_delete_group_by_id_signed_out(self):
        write_timer_helper = PADSWriteTimerHelper()
        del_result = write_timer_helper.delete_group_by_id(
                self.tgroup_ga1.id)
        # Assertions
        self.assertFalse(del_result)
        self.assertTrue(self.all_tgroups_in_database)
    
class PADSWriteTimerHelperRemoveFromGroupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set Up Test Users and Write Timer Helpers
        #  Test User A
        username_a = 'test-jess-rfgt'
        password_a = '       54321YTREytre'
        cls.user_a = write_user_helper.prepare_user_in_db(
                username_a, password_a)
        cls.user_a.save()
        cls.write_timer_helper_a = PADSWriteTimerHelper(cls.user_a.id)
        #  Test Quick List User
        cls.user_q = write_user_helper.prepare_ql_user_in_db()[0]
        cls.user_q.save()
        cls.write_timer_helper_q = PADSWriteTimerHelper(cls.user_q.id)
        # Set up Test Timers for Test Users
        #  Test User A
        timer_a1_desc = 'Test Timer A1 by Test User A'
        cls.timer_a1_id = cls.write_timer_helper_a.new(timer_a1_desc)
        timer_a2_p_desc = 'Test Timer A2 (Public) by Test User A'
        cls.timer_a2_p_id = cls.write_timer_helper_a.new(
                timer_a2_p_desc, public=True)
        #  Test QL User
        timer_q1_desc = 'Test Timer Q1 by Test QL User'
        cls.timer_q1_id = cls.write_timer_helper_q.new(timer_q1_desc)        
        timer_q2_p_desc = 'Test Timer A2 (Public) by Test User A'
        cls.timer_q2_p_id = cls.write_timer_helper_q.new(
                timer_q2_p_desc, public=True)
        # Set up Test Timer Groups for Test Users
        #  Test User A
        cls.tgroup_ga1_name = 'test_group_ga1_user_a'
        cls.tgroup_ga1_id = cls.write_timer_helper_a.new_group(
                cls.tgroup_ga1_name)
        #  Test QL User
        cls.tgroup_gq1_name = 'test_group_gq1_user_q'
        cls.tgroup_gq1_id = cls.write_timer_helper_q.new_group(
                cls.tgroup_gq1_name)
        # Set up Test Group Inclusions (add Timers to Groups)
        #  Test User A, Permitted
        cls.write_timer_helper_a.add_to_group(
                cls.timer_a1_id, cls.tgroup_ga1_id)
        cls.write_timer_helper_a.add_to_group(
                cls.timer_a2_p_id, cls.tgroup_ga1_id)
        cls.write_timer_helper_a.add_to_group(
                cls.timer_q2_p_id, cls.tgroup_ga1_id) # Other Users' public
        #  Test User A, Not Permitted
        incl_q1_ga1 = GroupInclusion(
                timer_id=cls.timer_q1_id, group_id=cls.tgroup_ga1_id)
        incl_q1_ga1.save()
        #  Test QL User, Permitted
        cls.write_timer_helper_q.add_to_group(
                cls.timer_q1_id, cls.tgroup_gq1_id)
        cls.write_timer_helper_q.add_to_group(
                cls.timer_q2_p_id, cls.tgroup_gq1_id)
        cls.write_timer_helper_q.add_to_group(
                cls.timer_a2_p_id, cls.tgroup_gq1_id) # Other Users' public
        #  Test QL User, Not Permitted                
        incl_a1_gq1 = GroupInclusion(
                timer_id=cls.timer_a1_id, group_id=cls.tgroup_gq1_id)
        incl_a1_gq1.save()

    def user_a_group_inclusions_unchanged(self):
        a1_ga1_exists = GroupInclusion.objects.filter(
            timer_id=self.timer_a1_id, group_id=self.tgroup_ga1_id).exists()
        a2_p_ga1_exists = GroupInclusion.objects.filter(
            timer_id=self.timer_a2_p_id, group_id=self.tgroup_ga1_id).exists()
        q1_ga1_exists = GroupInclusion.objects.filter(
            timer_id=self.timer_q1_id, group_id=self.tgroup_ga1_id).exists()
        q2_p_ga1_exists = GroupInclusion.objects.filter(
            timer_id=self.timer_q2_p_id, group_id=self.tgroup_ga1_id).exists()
        return a1_ga1_exists & a2_p_ga1_exists & q1_ga1_exists & q2_p_ga1_exists

    def user_q_group_inclusions_unchanged(self):
        a1_gq1_exists = GroupInclusion.objects.filter(
            timer_id=self.timer_a1_id, group_id=self.tgroup_gq1_id).exists()
        a2_p_gq1_exists = GroupInclusion.objects.filter(
            timer_id=self.timer_a2_p_id, group_id=self.tgroup_gq1_id).exists()
        q1_gq1_exists = GroupInclusion.objects.filter(
            timer_id=self.timer_q1_id, group_id=self.tgroup_gq1_id).exists()
        q2_p_gq1_exists = GroupInclusion.objects.filter(
            timer_id=self.timer_q2_p_id, group_id=self.tgroup_gq1_id).exists()
        return a1_gq1_exists & a2_p_gq1_exists & q1_gq1_exists & q2_p_gq1_exists

    def test_remove_from_group_valid_private_a(self):
        remove_result = self.write_timer_helper_a.remove_from_group(
                self.timer_a1_id, self.tgroup_ga1_id)
        timer_in_group = GroupInclusion.objects.filter(
              timer_id=self.timer_a1_id, group_id=self.tgroup_ga1_id).exists()
        # Assertions
        self.assertTrue(remove_result)
        self.assertFalse(timer_in_group)
    
    def test_remove_from_group_valid_private_q(self):
        remove_result = self.write_timer_helper_q.remove_from_group(
                self.timer_q1_id, self.tgroup_gq1_id)
        timer_in_group = GroupInclusion.objects.filter(
              timer_id=self.timer_q1_id, group_id=self.tgroup_gq1_id).exists()
        # Assertions
        self.assertTrue(remove_result)
        self.assertFalse(timer_in_group)
        
    def test_remove_from_group_valid_other_user_timers_a(self):
        # A User may remove another User's Timer (public or private) 
        # from own Groups.
        remove_result_other = self.write_timer_helper_a.remove_from_group(
                self.timer_q1_id, self.tgroup_ga1_id)
        remove_result_other_p = self.write_timer_helper_a.remove_from_group(
                self.timer_q2_p_id, self.tgroup_ga1_id)        
        timer_in_group = GroupInclusion.objects.filter(
              timer_id=self.timer_q1_id, group_id=self.tgroup_ga1_id).exists()
        timer_pub_in_group = GroupInclusion.objects.filter(
             timer_id=self.timer_q2_p_id, group_id=self.tgroup_ga1_id).exists()
        # Assertions
        self.assertTrue(remove_result_other)
        self.assertTrue(remove_result_other_p)
        self.assertFalse(timer_in_group)
        self.assertFalse(timer_pub_in_group)

    def test_remove_from_group_valid_other_user_timers_q(self):
        # A QL User may remove another User's Timer, public or private,
        # from own Groups. This is to aid recovery from potential errors
        remove_result_other = self.write_timer_helper_q.remove_from_group(
                self.timer_a1_id, self.tgroup_gq1_id)
        remove_result_other_p = self.write_timer_helper_q.remove_from_group(
                self.timer_a2_p_id, self.tgroup_gq1_id)        
        timer_in_group = GroupInclusion.objects.filter(
              timer_id=self.timer_a1_id, group_id=self.tgroup_gq1_id).exists()
        timer_pub_in_group = GroupInclusion.objects.filter(
             timer_id=self.timer_a2_p_id, group_id=self.tgroup_gq1_id).exists()
        # Assertions
        self.assertTrue(remove_result_other)
        self.assertTrue(remove_result_other_p)
        self.assertFalse(timer_in_group)
        self.assertFalse(timer_pub_in_group)

    def test_remove_from_group_no_inclusion_a(self):
        # Helper should indicate an error if an attempt is made to remove
        #  an existing Timer from an existing Group it doesn't belong to.
        self.write_timer_helper_a.remove_from_group(
                self.timer_a1_id, self.tgroup_ga1_id)
        remove_result_2 = self.write_timer_helper_a.remove_from_group(
                self.timer_a1_id, self.tgroup_ga1_id)
        # Assertions
        self.assertFalse(remove_result_2)
        self.assertTrue(self.user_q_group_inclusions_unchanged)

    def test_remove_from_group_no_inclusion_q(self):    
        # Helper should indicate an error if an attempt is made to remove
        #  an existing Timer from an existing Group it doesn't belong to.
        self.write_timer_helper_q.remove_from_group(
                self.timer_q1_id, self.tgroup_gq1_id)
        remove_result_2 = self.write_timer_helper_q.remove_from_group(
                self.timer_q1_id, self.tgroup_gq1_id)
        # Assertions
        self.assertFalse(remove_result_2)
        self.assertTrue(self.user_a_group_inclusions_unchanged)
        
    def test_remove_from_group_wrong_user_a(self):
        # A User must fail to remove any Timer from another User's Groups.
        remove_result_own = self.write_timer_helper_a.remove_from_group(
                self.timer_a1_id, self.tgroup_gq1_id)
        remove_result_own_pub = self.write_timer_helper_a.remove_from_group(
                self.timer_a2_p_id, self.tgroup_gq1_id)
        remove_result_other = self.write_timer_helper_a.remove_from_group(
                self.timer_q1_id, self.tgroup_gq1_id)
        remove_result_other_pub = self.write_timer_helper_a.remove_from_group(
                self.timer_q2_p_id, self.tgroup_gq1_id)
        # Assertions
        self.assertFalse(remove_result_own)
        self.assertFalse(remove_result_own_pub)
        self.assertFalse(remove_result_other)
        self.assertFalse(remove_result_other_pub)
        self.assertTrue(self.user_a_group_inclusions_unchanged)
        self.assertTrue(self.user_q_group_inclusions_unchanged)
    
    def test_remove_to_group_wrong_user_q(self):
        # A QL User must fail to remove any Timer from another User's Groups.
        remove_result_own = self.write_timer_helper_q.remove_from_group(
                self.timer_q1_id, self.tgroup_ga1_id)
        remove_result_own_pub = self.write_timer_helper_q.remove_from_group(
                self.timer_q2_p_id, self.tgroup_ga1_id)
        remove_result_other = self.write_timer_helper_q.remove_from_group(
                self.timer_a1_id, self.tgroup_ga1_id)
        remove_result_other_pub = self.write_timer_helper_q.remove_from_group(
                self.timer_a2_p_id, self.tgroup_ga1_id)
        # Assertions
        self.assertFalse(remove_result_own)
        self.assertFalse(remove_result_own_pub)
        self.assertFalse(remove_result_other)
        self.assertFalse(remove_result_other_pub)
        self.assertTrue(self.user_a_group_inclusions_unchanged)
        self.assertTrue(self.user_q_group_inclusions_unchanged)

    def test_remove_from_group_invalid_timer_id_a(self):
        remove_result = self.write_timer_helper_a.remove_from_group(
                -9999, self.tgroup_ga1_id)
        # Assertions
        self.assertFalse(remove_result)
        self.assertTrue(self.user_a_group_inclusions_unchanged)
        self.assertTrue(self.user_q_group_inclusions_unchanged)
    
    def test_remove_from_group_invalid_group_id_a(self):
        remove_result = self.write_timer_helper_a.remove_from_group(
                self.timer_a1_id, -9999)
        # Assertions
        self.assertFalse(remove_result)
        self.assertTrue(self.user_a_group_inclusions_unchanged)
        self.assertTrue(self.user_q_group_inclusions_unchanged)
    
    def test_remove_from_group_invalid_ids_a(self):
        remove_result = self.write_timer_helper_a.remove_from_group(
                -9999, -9999)
        # Assertions
        self.assertFalse(remove_result)
        self.assertTrue(self.user_a_group_inclusions_unchanged)
        self.assertTrue(self.user_q_group_inclusions_unchanged)

class PADSWriteTimerHelperDeleteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set Up Test Users and Write Timer Helpers
        #  Test User A
        username_a = 'test-jess-thdt'
        password_a = '       ^^^^opopoOPOPOP1234'
        cls.user_a = write_user_helper.prepare_user_in_db(
                username_a, password_a)
        cls.user_a.save()
        cls.write_timer_helper_a = PADSWriteTimerHelper(cls.user_a.id)
        #  Test User B
        username_b = 'not-jess'
        password_b = password_a
        cls.user_b = write_user_helper.prepare_user_in_db(
                username_b, password_b)
        cls.user_b.save()
        cls.write_timer_helper_b = PADSWriteTimerHelper(cls.user_b.id)
        # Test Quick List User
        cls.user_q = write_user_helper.prepare_ql_user_in_db()[0]
        cls.user_q.save()
        cls.write_timer_helper_q = PADSWriteTimerHelper(cls.user_q.id)
        
        # Set Up Test Timers
        #  Public Timers are used in this test to ensure that the Helpers
        #  are able to tell between granting write and read access.
        #  Test User A's Timer
        timer_a1_p_desc = 'Test Timer A1 by Test User A (Public)'
        cls.timer_a1_p_id = cls.write_timer_helper_a.new(
                timer_a1_p_desc, public=True)
        #  Test User B's Timer
        timer_b1_p_desc = 'Test Timer B1 by Test User B (Public)'
        cls.timer_b1_p_id = cls.write_timer_helper_b.new(
                timer_b1_p_desc, public=True)
        #  Test QL User's Timer
        timer_q1_p_desc = 'Test Timer Q1 by Test QL User (Public)'
        cls.timer_q1_p_id = cls.write_timer_helper_q.new(
                timer_q1_p_desc, public=True)
        
    def test_delete_valid_a(self):
        del_result = self.write_timer_helper_a.delete(self.timer_a1_p_id)
        timer_a1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_a1_p_id).exists()
        timer_b1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_b1_p_id).exists()
        timer_q1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_q1_p_id).exists()
        # Assertions
        self.assertTrue(
                del_result, 'Must indicate success of deletion by User A.')
        self.assertFalse(
                timer_a1_p_exists, 'Timer A1 must no longer exist in database')
        self.assertTrue(
                timer_b1_p_exists, 'Timer B1 must remain in database')
        self.assertTrue(
                timer_q1_p_exists, 'Timer Q1 must remain in database')
        
    def test_delete_valid_b(self):
        del_result = self.write_timer_helper_b.delete(self.timer_b1_p_id)
        timer_a1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_a1_p_id).exists()
        timer_b1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_b1_p_id).exists()
        timer_q1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_q1_p_id).exists()
        # Assertions
        self.assertTrue(
                del_result, 'Must indicate success of deletion by User B.')
        self.assertTrue(
                timer_a1_p_exists, 'Timer A1 must remain in database')
        self.assertFalse(
                timer_b1_p_exists, 'Timer B1 must no longer exist in database')
        self.assertTrue(
                timer_q1_p_exists, 'Timer Q1 must remain in database')
    
    def test_delete_valid_q(self):
        del_result = self.write_timer_helper_q.delete(self.timer_q1_p_id)
        timer_a1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_a1_p_id).exists()
        timer_b1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_b1_p_id).exists()
        timer_q1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_q1_p_id).exists()
        # Assertions
        self.assertTrue(
                del_result, 'Must indicate success of deletion by QL User')
        self.assertTrue(
                timer_a1_p_exists, 'Timer A1 must remain in database')
        self.assertTrue(
                timer_b1_p_exists, 'Timer B1 must remain in database')
        self.assertFalse(
                timer_q1_p_exists, 'Timer Q1 must no longer exist in database')
    
    def test_delete_signed_out(self):
        write_timer_helper = PADSWriteTimerHelper()
        del_a_result = write_timer_helper.delete(self.timer_a1_p_id)
        del_b_result = write_timer_helper.delete(self.timer_b1_p_id)
        del_q_result = write_timer_helper.delete(self.timer_q1_p_id)
        timer_a1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_a1_p_id).exists()
        timer_b1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_b1_p_id).exists()
        timer_q1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_q1_p_id).exists()
        # Assertions
        self.assertFalse(del_a_result,
                 'Must indicate failure to delete Timer A1 by signed out User')
        self.assertFalse(del_b_result,
                 'Must indicate failure to delete Timer B1 by signed out User')
        self.assertFalse(del_q_result,
                 'Must indicate failure to delete Timer Q1 by signed out User')
        self.assertTrue(
                timer_a1_p_exists, 'Timer A1 must remain in database')
        self.assertTrue(
                timer_b1_p_exists, 'Timer B1 must remain in database')
        self.assertTrue(
                timer_q1_p_exists, 'Timer Q1 must remain in database')
        
    def test_delete_invalid_id_a(self):
        # Multi-assertion
        for i in bad_str_inputs.values():    
            del_result = self.write_timer_helper_a.delete(i)
            timer_a1_p_exists = PADSTimer.objects.filter(
                    pk=self.timer_a1_p_id).exists()
            timer_b1_p_exists = PADSTimer.objects.filter(
                    pk=self.timer_b1_p_id).exists()
            timer_q1_p_exists = PADSTimer.objects.filter(
                    pk=self.timer_q1_p_id).exists()
            self.assertFalse(
                    del_result, 
                    'Must indicate failure by User A to delete invalid Timer')
            self.assertTrue(
                    timer_a1_p_exists, 'Timer A1 must remain in database')
            self.assertTrue(
                    timer_b1_p_exists, 'Timer B1 must remain in database')
            self.assertTrue(
                    timer_q1_p_exists, 'Timer Q1 must remain in database')        

    def test_delete_wrong_user_a(self):
        del_result_a_nb = self.write_timer_helper_a.delete(self.timer_b1_p_id)
        del_result_a_nq = self.write_timer_helper_a.delete(self.timer_q1_p_id)
        timer_a1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_a1_p_id).exists()
        timer_b1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_b1_p_id).exists()
        timer_q1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_q1_p_id).exists()
        # Assertions
        self.assertFalse(del_result_a_nb, 
                         'User A must fail to delete User B\'s Timer')
        self.assertFalse(del_result_a_nq,
                         'User A must fail to delete QL User\'s Timer')
        self.assertTrue(timer_a1_p_exists, 'Timer A1 must remain in database')
        self.assertTrue(timer_b1_p_exists, 'Timer B1 must remain in database')
        self.assertTrue(timer_q1_p_exists, 'Timer Q1 must remain in database')

    def test_delete_wrong_user_b(self):
        del_result_b_na = self.write_timer_helper_b.delete(self.timer_a1_p_id)
        del_result_b_nq = self.write_timer_helper_b.delete(self.timer_q1_p_id)
        timer_a1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_a1_p_id).exists()
        timer_b1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_b1_p_id).exists()
        timer_q1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_q1_p_id).exists()
        # Assertions
        self.assertFalse(del_result_b_na, 
                         'User B must fail to delete User A\'s Timer')
        self.assertFalse(del_result_b_nq,
                         'User B must fail to delete QL User\'s Timer')
        self.assertTrue(timer_a1_p_exists, 'Timer A1 must remain in database')
        self.assertTrue(timer_b1_p_exists, 'Timer B1 must remain in database')
        self.assertTrue(timer_q1_p_exists, 'Timer Q1 must remain in database')

    def test_delete_wrong_user_q(self):
        del_result_q_na = self.write_timer_helper_q.delete(self.timer_a1_p_id)
        del_result_q_nb = self.write_timer_helper_q.delete(self.timer_b1_p_id)
        timer_a1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_a1_p_id).exists()
        timer_b1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_b1_p_id).exists()
        timer_q1_p_exists = PADSTimer.objects.filter(
                pk=self.timer_q1_p_id).exists()
        # Assertions
        self.assertFalse(del_result_q_na, 
                         'QL User must fail to delete User A\'s Timer')
        self.assertFalse(del_result_q_nb,
                         'QL User must fail to delete User B\'s Timer')
        self.assertTrue(timer_a1_p_exists, 'Timer A1 must remain in database')
        self.assertTrue(timer_b1_p_exists, 'Timer B1 must remain in database')
        self.assertTrue(timer_q1_p_exists, 'Timer Q1 must remain in database')
        
        
class PADSWriteTimerHelperSetDescriptionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up test Users and Timer Helpers
        # Set Up Test Users and Write Timer Helpers
        #  Test User A
        username_a = 'test-jess-sdt'
        password_a = '       ;;;;;?????huhHUH1'
        cls.user_a = write_user_helper.prepare_user_in_db(
                username_a, password_a)
        cls.user_a.save()
        cls.write_timer_helper_a = PADSWriteTimerHelper(cls.user_a.id)
        #  Test User B
        username_b = 'not-jess'
        password_b = password_a
        cls.user_b = write_user_helper.prepare_user_in_db(
                username_b, password_b)
        cls.user_b.save()
        cls.write_timer_helper_b = PADSWriteTimerHelper(cls.user_b.id)
        # Test Quick List User
        cls.user_q = write_user_helper.prepare_ql_user_in_db()[0]
        cls.user_q.save()
        cls.write_timer_helper_q = PADSWriteTimerHelper(cls.user_q.id)
        
        # Set Up Test Timers, remember original count-from date time.
        #  Public Timers are used in this test to ensure that the Helpers
        #  are able to tell between granting write and read access.
        #  Test User A's Timer
        cls.timer_a1_p_desc = 'Test Timer A1 by Test User A (Public)'
        cls.timer_a1_p_id = cls.write_timer_helper_a.new(
                cls.timer_a1_p_desc, public=True)
        cls.timer_a1_p = PADSTimer.objects.get(pk=cls.timer_a1_p_id)
        cls.orig_count_time_a1_p = cls.timer_a1_p.count_from_date_time
        #  Test User B's Timer
        cls.timer_b1_p_desc = 'Test Timer B1 by Test User B (Public)'
        cls.timer_b1_p_id = cls.write_timer_helper_b.new(
                cls.timer_b1_p_desc, public=True)
        cls.timer_b1_p = PADSTimer.objects.get(pk=cls.timer_b1_p_id)
        cls.orig_count_time_b1_p = cls.timer_b1_p.count_from_date_time
        #  Test QL User's Timer
        cls.timer_q1_p_desc = 'Test Timer Q1 by Test QL User (Public)'
        cls.timer_q1_p_id = cls.write_timer_helper_q.new(
                cls.timer_q1_p_desc, public=True)
        cls.timer_q1_p = PADSTimer.objects.get(pk=cls.timer_q1_p_id)
        cls.orig_count_time_q1_p = cls.timer_q1_p.count_from_date_time
    
    def test_timers_descs_unchanged(self):
        '''Returns True if the descriptions of all Test Timers in the 
        Timer Write Helper Set Description Test Case have remained unchanged.
        '''
        # Beginner's PROTIP: Timers must be reloaded to ensure any changes
        # that may have been made are accounted for
        timer_rel_a1 = PADSTimer.objects.get(pk=self.timer_a1_p_id)
        timer_a_desc_same = (self.timer_a1_p_desc == timer_rel_a1.description)
        timer_rel_b1 = PADSTimer.objects.get(pk=self.timer_b1_p_id)
        timer_b_desc_same = (self.timer_b1_p_desc == timer_rel_b1.description)
        timer_rel_q1 = PADSTimer.objects.get(pk=self.timer_q1_p_id)
        timer_q_desc_same = (self.timer_q1_p_desc == timer_rel_q1.description)
        return (timer_a_desc_same & timer_b_desc_same & timer_q_desc_same)
    
    def test_timers_cfdts_unchanged(self):
        '''Returns True if the count-from date times of all Test Timers in the 
        Timer Write Helper Set Description Test Case have remained unchanged.
        '''
        timer_rel_a1 = PADSTimer.objects.get(pk=self.timer_a1_p_id)
        timer_a_cfdt_same = (
                self.orig_count_time_a1_p == timer_rel_a1.count_from_date_time)
        timer_rel_b1 = PADSTimer.objects.get(pk=self.timer_b1_p_id)
        timer_b_cfdt_same = (
             self.orig_count_time_b1_p == timer_rel_b1.count_from_date_time)
        timer_rel_q1 = PADSTimer.objects.get(pk=self.timer_q1_p_id)
        timer_q_cfdt_same = (
             self.orig_count_time_q1_p == timer_rel_q1.count_from_date_time)
        return (timer_a_cfdt_same & timer_b_cfdt_same & timer_q_cfdt_same)
        
    def test_set_description_valid_a(self):
        new_desc_a1 = 'New Timer Description A1'
        desc_changed = self.write_timer_helper_a.set_description(
                self.timer_a1_p_id, new_desc_a1)
        ref_timestamp = timezone.now().timestamp()
        timer_rel = PADSTimer.objects.get(pk=self.timer_a1_p_id)
        # Assertions
        self.assertEquals(timer_rel.description, new_desc_a1, 
                          'User A\'s Timer description must be changed')
        self.assertTrue(desc_changed, 
                  'Timer helper must indicate success in changing description')
        self.assertAlmostEquals(timer_rel.count_from_date_time.timestamp(), 
                                ref_timestamp, 
                                delta=1.0,
                                msg='Changing description must reset Timer')
        self.assertEquals(self.timer_b1_p.description, self.timer_b1_p_desc,
                      'User B\'s Timer description must remain unchanged.')
        self.assertEquals(self.timer_b1_p.count_from_date_time, 
              self.orig_count_time_b1_p,
              'User B\'s Timer count-from date time must remain unchanged')
        self.assertEquals(self.timer_q1_p.description, self.timer_q1_p_desc,
                   'QL User\'s Timer description must remain unchanged.')
        self.assertEquals(self.timer_q1_p.count_from_date_time, 
              self.orig_count_time_q1_p,
              'QL User\'s Timer count-from date time must remain unchanged')
            
    def test_set_description_valid_q(self):
        new_desc_q1 = 'New Timer Description Q1'
        desc_changed = self.write_timer_helper_q.set_description(
                self.timer_q1_p_id, new_desc_q1)
        ref_timestamp = timezone.now().timestamp()
        timer_rel = PADSTimer.objects.get(pk=self.timer_q1_p_id)
        # Assertions
        self.assertEquals(timer_rel.description, new_desc_q1, 
                          'QL User\'s Timer description must be changed')
        self.assertTrue(desc_changed,
                  'Timer helper must indicate success in changing description')
        self.assertAlmostEquals(timer_rel.count_from_date_time.timestamp(),
                            ref_timestamp,
                            delta=1.0,
                            msg='Description change must reset Timer')
        self.assertEquals(self.timer_a1_p.description, self.timer_a1_p_desc,
                         'User A\'s Timer\'s description must remain the same')
        self.assertEquals(self.timer_a1_p.count_from_date_time, 
                  self.orig_count_time_a1_p,
                  'User A\'s Timer\'s count-from date time must be unchanged')
        self.assertEquals(self.timer_b1_p.description, self.timer_b1_p_desc,
                      'User B\'s Timer Description must remain the same')
        self.assertEquals(self.timer_b1_p.count_from_date_time, 
                  self.orig_count_time_b1_p,
                  'User B\'s Timer count-from date time must remain the same')
        
    def test_set_description_valid_stopped_b(self):
        # Set up a Historical Timer for Test User A
        timer_b2_pnr_desc = 'Test Timer B2 by Test User A (Public/Stopped)'
        timer_b2_pnr_id= self.write_timer_helper_a.new(
                timer_b2_pnr_desc, public=True, running=False)
        timer_b2_pnr = PADSTimer.objects.get(pk=timer_b2_pnr_id)
        orig_count_time_b2_pnr = timer_b2_pnr.count_from_date_time
        # Attempt to change Historical Timer's description
        new_desc_b2_pnr = 'Test Timer B2 New Description'
        desc_changed = self.write_timer_helper_a.set_description(
                timer_b2_pnr_id, new_desc_b2_pnr)
        timer_b2_pnr_rel = PADSTimer.objects.get(pk=timer_b2_pnr_id) # Reload
        # Assertions
        self.assertTrue(desc_changed)
        self.assertFalse(timer_b2_pnr.running)
        self.assertEquals(timer_b2_pnr_desc, timer_b2_pnr.description)
        self.assertEquals(orig_count_time_b2_pnr, 
                          timer_b2_pnr_rel.count_from_date_time)
    
    def test_set_description_bad_description(self):
        # Multi-Assertion
        for i in bad_str_inputs.values():
            desc_changed = self.write_timer_helper_a.set_description(
                    self.timer_q1_p_id, i)
            self.assertFalse(desc_changed,
                 'Timer helper must indicate failure to set a bad description')
            self.assertTrue(self.test_timers_cfdts_unchanged(),
                       'Descriptions of all Test Timers must remain unchanged')
            self.assertTrue(self.test_timers_descs_unchanged(),
                    'Count-from date times of all Test Timers must not change')
        
    def test_set_description_historical(self):
        # Set up a Historical Timer for Test User A
        timer_a2_ph_desc = 'Test Timer A2 by Test User A (Public/Historical)'
        timer_a2_ph_id= self.write_timer_helper_a.new(
                timer_a2_ph_desc, public=True, historical=True)
        timer_a2_ph = PADSTimer.objects.get(pk=timer_a2_ph_id)
        orig_count_time_a2_ph = timer_a2_ph.count_from_date_time
        # Attempt to change Historical Timer's description
        new_desc_a2_ph = 'Test User A editing own historical Timer'
        desc_changed = self.write_timer_helper_a.set_description(
                timer_a2_ph_id, new_desc_a2_ph)
        # Assertions
        self.assertFalse(desc_changed)
        self.assertEqual(timer_a2_ph.description, timer_a2_ph_desc)
        self.assertEqual(timer_a2_ph.count_from_date_time, 
                         orig_count_time_a2_ph)

    def test_set_description_invalid_id(self):
        new_desc_b1_a = 'User A attempting to modify non-existent Timer'
        desc_changed = self.write_timer_helper_a.set_description(
                -9999, new_desc_b1_a)
        self.assertFalse(desc_changed, 
                    'Timer helper must indicate failure to change description')
        self.assertTrue(self.test_timers_cfdts_unchanged(),
                   'Descriptions of all Test Timers must remain unchanged')
        self.assertTrue(self.test_timers_descs_unchanged(),
                'Count-from date times of all Test Timers must not change')

    def test_set_description_signed_out(self):
        write_timer_helper = PADSWriteTimerHelper()
        new_desc_a1_s = 'Signed out User attempting to modify User A\'s Timer'
        desc_changed = write_timer_helper.set_description(
                self.timer_a1_p_id, new_desc_a1_s)
        self.assertFalse(desc_changed, 
                    'Timer helper must indicate failure to change description')
        self.assertTrue(self.test_timers_cfdts_unchanged(),
                   'Descriptions of all Test Timers must remain unchanged')
        self.assertTrue(self.test_timers_descs_unchanged(),
                'Count-from date times of all Test Timers must not change')
            
    def test_set_description_wrong_user_a(self):
        new_desc_b1_a = 'User A attempting to modify User B\'s Timer'
        desc_changed = self.write_timer_helper_a.set_description(
                self.timer_b1_p_id, new_desc_b1_a)
        self.assertFalse(desc_changed, 
                    'Timer helper must indicate failure to change description')
        self.assertTrue(self.test_timers_cfdts_unchanged(),
                   'Descriptions of all Test Timers must remain unchanged')
        self.assertTrue(self.test_timers_descs_unchanged(),
                'Count-from date times of all Test Timers must not change')
        
class PADSWriteTimerHelperResetByIdTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up test Users and Timer Helpers
        # Set Up Test Users and Write Timer Helpers
        #  Test User A
        username_a = 'test-jess-thrbi'
        password_a = '       +-+-+-trewqTREWQ4321'
        cls.user_a = write_user_helper.prepare_user_in_db(
                username_a, password_a)
        cls.user_a.save()
        cls.write_timer_helper_a = PADSWriteTimerHelper(cls.user_a.id)
        #  Test User B
        username_b = 'not-jess'
        password_b = password_a
        cls.user_b = write_user_helper.prepare_user_in_db(
                username_b, password_b)
        cls.user_b.save()
        cls.write_timer_helper_b = PADSWriteTimerHelper(cls.user_b.id)
        # Test Quick List User
        cls.user_q = write_user_helper.prepare_ql_user_in_db()[0]
        cls.user_q.save()
        cls.write_timer_helper_q = PADSWriteTimerHelper(cls.user_q.id)
        
        # Set Up Test Timers, remember original count-from date time
        #  Public Timers are used in this test to ensure that the Helpers
        #  are able to tell between granting write and read access.
        #  Test User A's Timer
        timer_a1_p_desc = 'Test Timer A1 by Test User A (Public)'
        cls.timer_a1_p_id = cls.write_timer_helper_a.new(
                timer_a1_p_desc, public=True)
        cls.timer_a1_p = PADSTimer.objects.get(pk=cls.timer_a1_p_id)
        cls.orig_count_time_a1_p = cls.timer_a1_p.count_from_date_time
        #  Test User B's Timer
        timer_b1_p_desc = 'Test Timer B1 by Test User B (Public)'
        cls.timer_b1_p_id = cls.write_timer_helper_b.new(
                timer_b1_p_desc, public=True)
        cls.timer_b1_p = PADSTimer.objects.get(pk=cls.timer_b1_p_id)
        cls.orig_count_time_b1_p = cls.timer_b1_p.count_from_date_time
        #  Test QL User's Timer
        timer_q1_p_desc = 'Test Timer Q1 by Test QL User (Public)'
        cls.timer_q1_p_id = cls.write_timer_helper_q.new(
                timer_q1_p_desc, public=True)
        cls.timer_q1_p = PADSTimer.objects.get(pk=cls.timer_q1_p_id)
        cls.orig_count_time_q1_p = cls.timer_q1_p.count_from_date_time
    
    def timers_cfdts_unchanged(self):
        '''Returns True if the count-from date times of all Test Timers in the 
        Timer Write Helper Set Description Test Case have remained unchanged.
        '''
        timer_rel_a1 = PADSTimer.objects.get(pk=self.timer_a1_p_id)
        timer_a_cfdt_same = (
                self.orig_count_time_a1_p == timer_rel_a1.count_from_date_time)
        timer_rel_b1 = PADSTimer.objects.get(pk=self.timer_b1_p_id)
        timer_b_cfdt_same = (
             self.orig_count_time_b1_p == timer_rel_b1.count_from_date_time)
        timer_rel_q1 = PADSTimer.objects.get(pk=self.timer_q1_p_id)
        timer_q_cfdt_same = (
             self.orig_count_time_q1_p == timer_rel_q1.count_from_date_time)
        return (timer_a_cfdt_same & timer_b_cfdt_same & timer_q_cfdt_same)

    
    def test_reset_by_id_valid_a(self):
        reset_reason = 'Test User A Resetting Timer A1'
        timer_reset = self.write_timer_helper_a.reset_by_id(
                self.timer_a1_p_id, reset_reason)
        # Beginner's PROTIP: Timers must be reloaded after reset in order to
        #  get the new count-from date times.
        timer_a1_p_rel = PADSTimer.objects.get(pk=self.timer_a1_p_id)
        count_time_a = timer_a1_p_rel.count_from_date_time
        log_entry_a = PADSTimerReset.objects.filter(
                timer_id=self.timer_a1_p_id).order_by('-date_time')[0]
        timer_b1_p_rel = PADSTimer.objects.get(pk=self.timer_b1_p_id)
        count_time_b = timer_b1_p_rel.count_from_date_time
        timer_q1_p_rel = PADSTimer.objects.get(pk=self.timer_q1_p_id)
        count_time_q = timer_q1_p_rel.count_from_date_time
        ref_timestamp = timezone.now().timestamp()
        # Assertions
        self.assertTrue(timer_reset, 
                        'Helper must indicate success resetting timer')
        self.assertTrue(timer_a1_p_rel.running,
                        'Timer A1 must be running after reset')
        self.assertIn(reset_reason, log_entry_a.reason, 
                      'Timer A1\'s reset must be logged')
        self.assertAlmostEqual(count_time_a.timestamp(),
               ref_timestamp, 
               delta=1.0,
              msg='Timer A1 count-from date time must be advanced after reset')
        self.assertEquals(count_time_b, self.orig_count_time_b1_p,
                          'Timer B1 count-from date time must remain the same')
        self.assertEquals(count_time_q, self.orig_count_time_q1_p,
                          'Timer Q1 count-from date time must remain the same')

    def test_reset_by_id_valid_b(self):
        reset_reason = 'Test User B Resetting Timer B1'
        timer_reset = self.write_timer_helper_b.reset_by_id(
                self.timer_b1_p_id, reset_reason)
        # Reload Timers
        timer_b1_p_rel = PADSTimer.objects.get(pk=self.timer_b1_p_id)
        count_time_b = timer_b1_p_rel.count_from_date_time
        log_entry_b = PADSTimerReset.objects.filter(
                timer_id=self.timer_b1_p_id).order_by('-date_time')[0]
        timer_a1_p_rel = PADSTimer.objects.get(pk=self.timer_a1_p_id)
        count_time_a = timer_a1_p_rel.count_from_date_time
        timer_q1_p_rel = PADSTimer.objects.get(pk=self.timer_q1_p_id)
        count_time_q = timer_q1_p_rel.count_from_date_time
        ref_timestamp = timezone.now().timestamp()
        # Assertions
        self.assertTrue(timer_reset,
                        'Helper must indicate success resetting timer')
        self.assertTrue(timer_b1_p_rel.running,
                        'Timer B1 must be running after reset')
        self.assertIn(reset_reason, log_entry_b.reason, 
                      'Timer B1\'s reset must be logged')
        self.assertAlmostEqual(count_time_b.timestamp(),
               ref_timestamp,
               delta=1.0,
              msg='Timer B1 count-from date time must be advanced after reset')
        self.assertEquals(count_time_a, self.orig_count_time_a1_p,
                          'Timer A1 count-from date time must remain the same')
        self.assertEquals(count_time_q, self.orig_count_time_q1_p,
                          'Timer Q1 count-from date time must remain the same')
        
    def test_reset_by_id_wrong_user_q(self):
        reset_reason = 'Test User Q Resetting Timer A1'
        timer_reset = self.write_timer_helper_q.reset_by_id(
                self.timer_a1_p_id, reset_reason)
        reset_logged = PADSTimerReset.objects.filter(
                timer_id=self.timer_a1_p_id,
                reason__icontains=reset_reason).exists()
        # Assertions
        self.assertFalse(timer_reset,
                  'Helper must indicate failure to reset other Users\' Timers')
        self.assertTrue(self.timers_cfdts_unchanged(),
                    'Count-from date times of all Test Timers must not change')
        self.assertFalse(reset_logged, 'Failed Timer reset must not be logged')
        
    def test_reset_by_id_signed_out(self):
        write_timer_helper = PADSWriteTimerHelper()
        reset_reason = 'Signed Out User Resetting Timer A1'
        timer_reset = write_timer_helper.reset_by_id(
                self.timer_a1_p_id, reset_reason)
        reset_logged = PADSTimerReset.objects.filter(
                reason__icontains=reset_reason).exists()
        # Assertions
        self.assertFalse(timer_reset,
                        'Helper must indicate failure to reset Timer')
        self.assertTrue(self.timers_cfdts_unchanged(),
                    'Count-from date times of all Test Timers must not change')
        self.assertFalse(reset_logged, 'Failed Timer reset must not be logged')

    def test_reset_by_id_bad_reason_a(self):
        # First-stage Assertions
        for i in bad_str_inputs.values():
            timer_reset = self.write_timer_helper_a.reset_by_id(
                    self.timer_a1_p_id, i)
            self.assertFalse(timer_reset,
                 'Helper must indicate failed Timer reset with invalid reason')
        # Second-stage Assertions
        self.assertTrue(self.timers_cfdts_unchanged(),
                    'Count-from date times of all Test Timers must not change')
    
    def test_reset_by_id_historical(self):
        # Create new historical Timer for Test QL User
        timer_q2_ph_desc = 'Test Timer Q2 by QL User (Pub/Historical)'
        reset_reason = 'Test QL User attempting to reset historical Timer'
        timer_q2_id = self.write_timer_helper_q.new(
                timer_q2_ph_desc, historical=True)
        timer_q2 = PADSTimer.objects.get(pk=timer_q2_id)
        timer_reset = self.write_timer_helper_q.reset_by_id(
                timer_q2_id, reset_reason)
        orig_count_time_q2 = timer_q2.count_from_date_time
        timer_q2_rel = PADSTimer.objects.get(pk=timer_q2_id) # Reload
        reset_logged = PADSTimerReset.objects.filter(
                timer_id=timer_q2_id, reason__icontains=reset_reason).exists()
        # Assertions
        self.assertFalse(timer_reset)
        self.assertEquals(timer_q2_rel.count_from_date_time,
                          orig_count_time_q2)
        self.assertFalse(reset_logged,'Failed Timer resets must not be logged')

    def test_reset_by_id_invalid_id(self):
        reset_reason = 'Test User A resetting non-existent Timer'
        # First-stage Assertions
        for i in bad_str_inputs.values():
            timer_reset = self.write_timer_helper_a.reset_by_id(
                    i, reset_reason)
            self.assertFalse(timer_reset,
                     'Helper must indicate failed reset with invalid Timer id')
        reset_logged = PADSTimerReset.objects.filter(
                reason__icontains=reset_reason).exists()
        # Second-stage Assertions
        self.assertTrue(self.timers_cfdts_unchanged(),
                    'Count-from date times of all Test Timers must not change')
        self.assertFalse(reset_logged, 
                         'Failed Timer resets must not be logged')

class PADSWriteTimerHelperStopByIdTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up test Users and Timer Helpers
        # Set Up Test Users and Write Timer Helpers
        #  Test User A
        username_a = 'test-jess-thsbi'
        password_a = '       ///?????huyyuhHYUUH534435'
        cls.user_a = write_user_helper.prepare_user_in_db(
                username_a, password_a)
        cls.user_a.save()
        cls.write_timer_helper_a = PADSWriteTimerHelper(cls.user_a.id)
        #  Test User B
        username_b = 'not-jess'
        password_b = password_a
        cls.user_b = write_user_helper.prepare_user_in_db(
                username_b, password_b)
        cls.user_b.save()
        cls.write_timer_helper_b = PADSWriteTimerHelper(cls.user_b.id)
        # Test Quick List User
        cls.user_q = write_user_helper.prepare_ql_user_in_db()[0]
        cls.user_q.save()
        cls.write_timer_helper_q = PADSWriteTimerHelper(cls.user_q.id)
        
        # Set Up Test Timers, remember original count-from date time
        #  Public Timers are used in this test to ensure that the Helpers
        #  are able to tell between granting write and read access.
        #  Test User A's Timer
        timer_a1_p_desc = 'Test Timer A1 by Test User A (Public)'
        cls.timer_a1_p_id = cls.write_timer_helper_a.new(
                timer_a1_p_desc, public=True)
        cls.timer_a1_p = PADSTimer.objects.get(pk=cls.timer_a1_p_id)
        cls.orig_count_time_a1_p = cls.timer_a1_p.count_from_date_time
        #  Test User B's Timer
        timer_b1_p_desc = 'Test Timer B1 by Test User B (Public)'
        cls.timer_b1_p_id = cls.write_timer_helper_b.new(
                timer_b1_p_desc, public=True)
        cls.timer_b1_p = PADSTimer.objects.get(pk=cls.timer_b1_p_id)
        cls.orig_count_time_b1_p = cls.timer_b1_p.count_from_date_time
        #  Test QL User's Timer
        timer_q1_p_desc = 'Test Timer Q1 by Test QL User (Public)'
        cls.timer_q1_p_id = cls.write_timer_helper_q.new(
                timer_q1_p_desc, public=True)
        cls.timer_q1_p = PADSTimer.objects.get(pk=cls.timer_q1_p_id)
        cls.orig_count_time_q1_p = cls.timer_q1_p.count_from_date_time
    
    def timers_cfdts_unchanged(self):
        '''Returns True if the count-from date times of all Test Timers in the 
        Timer Write Helper Set Description Test Case have remained unchanged.
        '''
        timer_rel_a1 = PADSTimer.objects.get(pk=self.timer_a1_p_id)
        timer_a_cfdt_same = (
                self.orig_count_time_a1_p == timer_rel_a1.count_from_date_time)
        timer_rel_b1 = PADSTimer.objects.get(pk=self.timer_b1_p_id)
        timer_b_cfdt_same = (
             self.orig_count_time_b1_p == timer_rel_b1.count_from_date_time)
        timer_rel_q1 = PADSTimer.objects.get(pk=self.timer_q1_p_id)
        timer_q_cfdt_same = (
             self.orig_count_time_q1_p == timer_rel_q1.count_from_date_time)
        return (timer_a_cfdt_same & timer_b_cfdt_same & timer_q_cfdt_same)
            
    def test_stop_by_id_valid_a(self):
        reason = 'User A Stopping Timer A1'
        timer_stopped = self.write_timer_helper_a.stop_by_id(
                self.timer_a1_p_id, reason)
        ref_timestamp = timezone.now().timestamp()
        stop_logged = PADSTimerReset.objects.filter(
                timer_id=self.timer_a1_p_id, reason__icontains=reason).exists()
        timer_a1_p_rel = PADSTimer.objects.get(pk=self.timer_a1_p_id)
        # Assertions
        self.assertTrue(timer_stopped,
                        'Helper must indicate success stopping timer')
        self.assertFalse(timer_a1_p_rel.running, 'Timer must be stopped')
        self.assertTrue(
             timer_a1_p_rel.count_from_date_time > self.orig_count_time_a1_p,
             'Timer count-from date time must have advanced')
        self.assertAlmostEquals(
                timer_a1_p_rel.count_from_date_time.timestamp(),
                ref_timestamp,
                delta=0.1,
                msg='Timer count-from date time must be close to system time'
                )
        self.assertTrue(stop_logged, 'Successful timer stops must be logged')
        self.assertEquals(self.timer_b1_p.count_from_date_time, 
                  self.orig_count_time_b1_p,
                  'Other User\'s (B) Timer count-from time must not change')
        self.assertEquals(self.timer_q1_p.count_from_date_time, 
                   self.orig_count_time_q1_p,
                   'Other User\'s (QL) Timer count-from time must not change')
    
    def test_stop_by_id_valid_q(self):
        reason = 'QL User Stopping Timer Q1'
        timer_stopped = self.write_timer_helper_q.stop_by_id(
                self.timer_q1_p_id, reason)
        ref_timestamp = timezone.now().timestamp()
        stop_logged = PADSTimerReset.objects.filter(
                timer_id=self.timer_q1_p_id, reason__icontains=reason).exists()
        timer_q1_p_rel = PADSTimer.objects.get(pk=self.timer_q1_p_id)
        # Assertions
        self.assertTrue(timer_stopped,
                        'Helper must indicate success stopping Timer')
        self.assertFalse(timer_q1_p_rel.running, 'Timer must not be running')
        self.assertTrue(
             timer_q1_p_rel.count_from_date_time > self.orig_count_time_q1_p,
             'Timer count-from date time must have advanced')
        self.assertAlmostEquals(
             timer_q1_p_rel.count_from_date_time.timestamp(),
             ref_timestamp,
             delta=0.1,
             msg= 'Timer\'s count-from date time must be close to system time'
             )
        self.assertTrue(stop_logged, 'Successful Timer stops must be logged')
        self.assertEquals(self.timer_a1_p.count_from_date_time, 
                     self.orig_count_time_a1_p,
                     'Other User\'s (A) Timer count-from time must not change')
        self.assertEquals(self.timer_b1_p.count_from_date_time, 
                      self.orig_count_time_b1_p,
                     'Other User\'s (B) Timer count-from time must not change')
        
    def test_stop_by_id_valid_historical_a(self):
        # Create new historical Timer for Test QL User
        timer_q2_ph_desc = 'Test Timer Q2 by QL User (Pub/Historical)'
        reset_reason = 'Test QL User attempting to stop historical Timer'
        timer_q2_ph_id = self.write_timer_helper_q.new(
                timer_q2_ph_desc, historical=True)
        timer_q2_ph = PADSTimer.objects.get(pk=timer_q2_ph_id)
        # Stop test Timer
        timer_stopped = self.write_timer_helper_q.stop_by_id(
                timer_q2_ph_id, reset_reason)
        orig_count_time_q2 = timer_q2_ph.count_from_date_time
        timer_q2_rel = PADSTimer.objects.get(pk=timer_q2_ph_id) # Reload
        stop_logged = PADSTimerReset.objects.filter(timer_id=timer_q2_ph_id, 
                                reason__icontains=reset_reason).exists()
        ref_timestamp = timezone.now().timestamp()
        # Assertions
        self.assertTrue(timer_stopped,
                        'Helper must indicate success stopping Timer')
        self.assertTrue(timer_q2_rel.count_from_date_time > orig_count_time_q2,
                        'Timer count-from date time must have advanced')
        self.assertAlmostEquals(timer_q2_ph.count_from_date_time.timestamp(), 
                 ref_timestamp,
                 delta=0.1,
                 msg='Timer count-from date time must be close to system time')
        self.assertTrue(stop_logged,
                        'Successful stop of a Historical Timer must be logged')
    
    def test_stop_by_id_wrong_user_b(self):
        reason = 'User B attempting to stop User A\'s Timer A1'
        timer_stopped = self.write_timer_helper_b.stop_by_id(
                self.timer_a1_p_id, reason)
        stop_logged = PADSTimerReset.objects.filter(
                timer_id=self.timer_a1_p_id, reason__icontains=reason)
        # Assertions
        self.assertFalse(timer_stopped,
                         'Helper must indicate failure to stop timer')
        self.assertTrue(self.timers_cfdts_unchanged(),
                   'Count-from date time on test Timers must remain unchanged')
        self.assertFalse(stop_logged,
                         'Failed Timer stops must not be logged')
    
    def test_stop_by_id_signed_out(self):
        reason = 'Signed out User attempting to stop QL User\'s Timer'
        write_timer_helper = PADSWriteTimerHelper()
        timer_stopped = write_timer_helper.stop_by_id(
                self.timer_q1_p_id, reason)
        stop_logged = PADSTimerReset.objects.filter(
                timer_id=self.timer_a1_p_id, reason__icontains=reason).exists()
        # Assertions
        self.assertFalse(timer_stopped,
                         'Helper must indicate failure to stop Timer')
        self.assertTrue(self.timers_cfdts_unchanged(),
                   'Count-from date time on test Timers must remain unchanged')
        self.assertFalse(stop_logged,
                         'Failed Timer stops must not be logged')
    
    def test_stop_by_id_bad_reason_a(self):
        # First-stage Multi-assertion
        for i in bad_str_inputs.values():
            timer_stopped = self.write_timer_helper_a.stop_by_id(
                    self.timer_a1_p_id, i)
            self.assertFalse(timer_stopped)
        # Second-stage Assertions
        self.assertTrue(self.timers_cfdts_unchanged())
    
    def test_stop_by_id_invalid_id(self):
        reason = 'User A attempting to reset non-existent Timer'
        timer_stopped = self.write_timer_helper_a.stop_by_id(-9999, reason)
        stop_logged = PADSTimerReset.objects.filter(
                timer_id=self.timer_a1_p_id, reason__icontains=reason).exists()
        # Assertions
        self.assertFalse(timer_stopped,
               'Timer helper must indicate failure to stop non-existent Timer')
        self.assertTrue(self.timers_cfdts_unchanged(),
                   'Count-from date time on test Timers must remain unchanged')
        self.assertFalse(stop_logged,
                         'Failed Timer stops must not be logged')
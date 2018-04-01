#
#
# Public Archive of Days Since Timers
# View-Level Essential Integration Tests
#
#

# Imports
from django.test import TestCase
from django.test import Client
from django.utils import timezone
from django.urls import reverse
from padsweb.settings import *
from padsweb.strings import labels, messages
from padsweb.user import PADSUserHelper
from padsweb.timers import PADSEditingTimerHelper, PADSTimerHelper
from padsweb.views import PADSTimerEditView, PADSView
import datetime

#
# Shared Test Data
#

## URLs
shared_uncovered_test_urls = (
    # Only URLs that are currently not covered by any other test
    #  are to be included here.
    reverse('padsweb:index_group', kwargs={'timer_group_id':1}),
    reverse('padsweb:index_longest_running'),
    reverse('padsweb:index_recent_resets'),
    reverse('padsweb:sign_up_intro'),
    reverse('padsweb:sign_up_user'),
    reverse('padsweb:sign_up_quicklist'),    
    reverse('padsweb:session_quicklist'),
    reverse('padsweb:settings_set_password'),
    reverse('padsweb:settings_import_ql'),
    )

## Helpers
user_helper = PADSUserHelper()

#
# View Test Helper Classes
#

class TestUser:
    # Class for simulating User interaction with Views

    #
    # Class Variables
    #
    user_helper = PADSUserHelper()   #  For more direct access to DB
    
    # URLs
    url_delete_timer_group = reverse('padsweb:settings_delete_timer_group')
    url_import_ql = reverse('padsweb:settings_import_ql')
    url_new_timer_group = reverse('padsweb:settings_new_timer_group')
    url_personal_timer_groups = reverse('padsweb:index_personal_groups')
    url_set_password = reverse('padsweb:settings_set_password')
    url_settings_info = reverse('padsweb:settings_info')
    url_sign_in = reverse('padsweb:session')
    url_sign_in_ql = reverse('padsweb:session_quicklist')
    url_sign_out = reverse('padsweb:session_end')
    url_sign_out_ql = url_sign_out
    url_sign_up = reverse('padsweb:sign_up_user')
    url_sign_up_ql = reverse('padsweb:sign_up_quicklist')
    url_timer_group_delete = reverse('padsweb:settings_delete_timer_group')
    url_timer_index = reverse('padsweb:index')
    url_timer_index_personal = reverse('padsweb:index_personal')
    url_timer_new = reverse('padsweb:timer_new')

    #
    # View Methods    
    #
    
    # These methods invoke the different functions of the PADS through 
    # simulated HTTP requests using the Django Test Client.
    
    def timer_group_index_personal(self):
        # Requests the Personal Timer Groups index
        
        response = self.client.get(self.url_personal_timer_groups)
        self.last_response = response
        return response
        
    def settings_delete_timer_group(self, timer_group_id):
        # Deletes a Timer Group
        
        req_body_dtg = {'timer_group' : timer_group_id,}
        response = self.client.post(self.url_delete_timer_group, req_body_dtg)
        self.last_response = response
        return response
        
    def settings_info(self):
        # Requests the setup screen
        response = self.client.get(self.url_settings_info)
        self.last_response = response
        return response

    def settings_import_ql(self, quick_list_password, timer_group_id=''):
        # Imports a Quick List's timer into a regular User account.
        # All timers from the Quick List will be under the control of the
        # User. The Quick List will be deleted.
        
        # An optional Timer Group id may be supplied, if the User chooses
        # to import the Timers into an existing Group instead.
        
        req_body_imp_ql = {
                'password' : quick_list_password,
                'timer_group' : timer_group_id,
                }
        self.settings_info()
        response = self.client.post(self.url_import_ql, req_body_imp_ql)
        self.last_response = response
        return response
    
    def settings_new_timer_group(self, timer_group_name):
        # Creates a new timer group
        
        req_body_ng = {'name' : timer_group_name,}
        response = self.client.post(self.url_new_timer_group, req_body_ng)
        self.last_repsonse = response
        return response
        
    def settings_set_password(self, password_old, password_new):
        # Changes the password for a User who is signed in
        req_body_setpass = {
            'user_id' : self.get_id_via_helper(),
            'old_password' : password_old,
            'new_password' : password_new,
            'new_password_confirm' : password_new,
            }
        response = self.client.post(self.url_set_password, req_body_setpass)
        self.last_response = response
        return response

    def sign_up(self):
        # Creates a User account
        req_body_su = { 
            'username' : self.username,
            'password' : self.password,
            'password_confirm' : self.password,
            }
        response = self.client.post(self.url_sign_up, req_body_su)
        self.last_response = response
        return response
        
    def sign_in(self):
        # Attempts to start a session for the User
        
        req_body_si = {
            'username' : self.username,
            'password' : self.password,
            }
        response = self.client.post(self.url_sign_in, req_body_si)
        self.last_response = response
        return response
    
    def sign_out(self):
        # Signs out the User
        
        response = self.client.get(self.url_sign_out)
        self.last_response = response
        return response

    def timer_add_to_group(self, timer_id, timer_group_id):
        # Adds a Timer to a Timer Group

        url_timer_add_to_group = reverse(
            'padsweb:timer_add_to_group',
            kwargs={'timer_id':timer_id})
        req_body_tg_add = {'timer_group' : timer_group_id}
        response = self.client.post(url_timer_add_to_group, req_body_tg_add)
        self.last_response = response
        return response

    def timer_set_groups(self, timer_id, timer_group_names):
        # Assigns a Timer to Timer Groups specified by name. Groups should be
        # automatically created if they have not been so. The Timer will also
        # be removed from unspecified Groups if there are existing inclusions.
        
        url_timer_set_groups = reverse(
                'padsweb:timer_set_groups', kwargs={'timer_id':timer_id})
        req_body_tg_set = {'group_names' : timer_group_names}
        response = self.client.post(url_timer_set_groups, req_body_tg_set)
        self.last_response = response
        return response

    def timer_delete(self, timer_id):
        # Deletes a Timer
        
        url_delete = reverse(
            'padsweb:timer_del',
            kwargs={'timer_id' : timer_id})
        response = self.client.post(url_delete)
        self.last_response = response
        return response
    
    def timer_detail(self, timer_id):
        # Opens a Timer's detail page

        url_timer_detail = reverse(
            'padsweb:timer',
            kwargs={'timer_id' : timer_id}
            )
        response = self.client.get(url_timer_detail)
        self.last_response = response
        return response

    def timer_index(self):
        # Requests the Timer Index

        response = self.client.get(self.url_timer_index)
        self.last_response = response
        return response

    def timer_index_personal(self):
        # Requests the Personal Index

        response = self.client.get(self.url_timer_index_personal)
        self.last_response = response
        return response
        
    def timer_new(self, description, date_time, **kwargs):
        # Creates a Timer        
        
        # Note 1: Timers are always Private when created (0.5x).
        # Note 2: The date_time object is broken down into its individual 
        #  components only to be recombined in the view method.
        # Note 3: It is alright to supply a naive date_time, because
        #  the Time Zone of the timer is intended to be specified
        #  separately.
        
        first_history_message = kwargs.get(
            'first_history_message',
            labels['TIMER_DEFAULT_CREATION_REASON'])
        historical = kwargs.get('historical', False)
        use_current_date_time = kwargs.get('use_current_date_time', False)
        
        req_body_nt = {
            'description' : description,
            'first_history_message' : first_history_message,
            'year' : date_time.year,
            'month' : date_time.month,
            'day' : date_time.day,
            'hour' : date_time.hour,
            'minute' : date_time.minute,
            'second' : date_time.second,
            'historical' : historical,
            'use_current_date_time' : use_current_date_time,
            }
        response = self.client.post(self.url_timer_new, req_body_nt)
        self.last_response = response
        return response
    
    def timer_remove_from_group(self, timer_id, timer_group_id):
        # Removes a Timer from a Timer Group

        url_remove_from_group = reverse(
            'padsweb:timer_remove_from_group',
            kwargs = {'timer_id':timer_id})
        req_body_tg_remove = {'timer_group' : timer_group_id}
        response = self.client.post(url_remove_from_group, req_body_tg_remove)
        self.last_response = response
        return response    
    
    def timer_rename(self, timer_id, description):
        # Renames a Timer

        url_rename_timer = reverse(
            'padsweb:timer_rename',
            kwargs = {'timer_id' : timer_id })
        req_body_rt = {'description' : description}
        response = self.client.post(url_rename_timer, req_body_rt)
        self.last_response = response
        return response
    
    def timer_reset(self, timer_id, reason):
        # Resets a Timer

        url_reset_timer = reverse(
            'padsweb:timer_reset',
            kwargs = { 'timer_id' : timer_id })
        req_body_res = { 'reason' : reason }
        response = self.client.post(url_reset_timer, req_body_res)
        self.last_response = response
        return response
    
    def timer_share(self, timer_id):
        # Makes a Timer visible to other Users and the general public

        url_timer_share = reverse(
            'padsweb:timer_share',
            kwargs = { 'timer_id' : timer_id })
        response = self.client.post(url_timer_share)
        self.last_response = response
        return response
        
    def timer_unshare(self, timer_id):
        # Makes a Timer private and only visible to the creator User

        url_timer_unshare = reverse(
            'padsweb:timer_unshare',
            kwargs = { 'timer_id' : timer_id })
        response = self.client.post(url_timer_unshare)
        self.last_response = response
        return response
        
    #
    # Test Helper Methods
    #
    def get_id_via_helper(self):
        # Looks up the User's id using the User Helper

        user = self.user_helper.get_user_by_nickname_short(self.username)
        if(user):
            return user.id()
        else:
            return INVALID_SESSION_ID
                
    #
    # Special Methods
    #
    def __init__(self, username, password):
        # Constructor and Instance Variables

        self.last_response = None
        self.password = password
        self.username = username
        self.client = Client()  # This is not a TestCase, so it's needed

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'Test User ({0}:{1})'.format(self.username, self.password)
        # The output format was inspired by Unix Password Files
        # See: man7.org/linux/man-pages/man5/passwd.5.html

class TestQuickListUser(TestUser):
    # Class for simulating Quick List User interactions with views

    def sign_in(self):
        url_sign_in_ql = reverse('padsweb:session_quicklist')
        req_body_siql = {
            'password' : self.password,
            }
        response = self.client.post(url_sign_in_ql, req_body_siql)
        self.last_response = response
        return response
    
    def sign_up(self):
        url_sign_up_ql = reverse('padsweb:sign_up_quicklist')
        response = self.client.post(url_sign_up_ql)
        
        # Extract the Quick List password from the banner shown
        # when a QL is created.
        bann_text = get_session_value(response, 'banner_text')
        self.password = bann_text.lstrip(
            messages['USER_SIGN_UP_QL_SUCCESS'])
        
        self.last_response = response
        return response
    
    def __init__(self):
        # A Quick List User does not have a username.
        #  Signing in is performed only with a password which is not
        #  known until the Quick List is created.
        # So for now, the username and password will be None.
        super().__init__(None, None)

    #
    # Test Helper Methods
    #
    def get_id_via_helper(self):
        # Looks up the QL User's id using the User Helper
        user_creds = self.user_helper.split_anon_user_password(
            self.password)
        user_id = user_creds[0]
        user = self.user_helper.get_user_for_view_by_id(user_id)
        
        if(user):
            return user.id()
        else:
            return INVALID_SESSION_ID

#
#
# Tests
#
#

class PADSViewTests(TestCase):
    # Unit Tests for the PADS View Class
    
    @classmethod
    def setUpTestData(cls):
        # Setup and Sign Up Test User
        cls.user_pvt = TestUser('test_jess_pvt', 'secure8765')
        cls.user_pvt.sign_up()

    def test_user_present(self):
        # When a user is signed in, user_present must be True

        # Actions
        #  Sign in the test user, capture response and original request
        resp_sign_in_pvt = self.user_pvt.sign_in()
        req_sign_in_pvt = resp_sign_in_pvt.wsgi_request

        #  Create a PADSView Instance
        view = PADSView(req_sign_in_pvt)
        
        # Assertions
        self.assertTrue(view.user_present())

    def test_user_not_present(self):
        # When a user is signed out, user_present must be False

        # Actions
        #  Make a request as without signing in, capture its request
        resp_get_index = self.client.get(TestUser.url_timer_index)
        req_get_index = resp_get_index.wsgi_request
        
        #  Create a PADSView Instance
        view = PADSView(req_get_index)
        
        # Assertions
        self.assertFalse(view.user_present())

class PADSTimerEditViewTests(TestCase):
    # Unit Tests for the PADS Edit View Class
    
    @classmethod
    def setUpTestData(cls):
        # Setup, Sign Up and Sign In the Test User
        cls.test_user_ptevt = TestUser('test_jess_ptevt', 'secure7006')
        cls.test_user_ptevt.sign_up()
        cls.test_user_ptevt.sign_in()
        
        # Create a Timer dated to test run time
        #  Capture the id of the new Timer.
        timer_test_desc = 'Test Timer'
        resp_timer_test_ptevt = cls.test_user_ptevt.timer_new(
            timer_test_desc, timezone.now())
        cls.timer_test_id = get_session_value(
            resp_timer_test_ptevt, 'last_new_item_id')
        
        #  Sign Out the Test User
        cls.test_user_ptevt.sign_out() 
            
    def test_timer_edit_helper_present(self):
        # When a user is signed in, and a Timer assigned to the Edit View,
        # an Editing Helper must be present.

        # Actions
        #  Sign in the test user, capture response and original request
        resp_sign_in_ptevt = self.test_user_ptevt.sign_in()
        req_sign_in_ptevt = resp_sign_in_ptevt.wsgi_request

        #  Create a PADSView Instance
        view = PADSTimerEditView(req_sign_in_ptevt, self.timer_test_id)
        
        # Assertions
        #  An Editing Helper must be present
        self.assertTrue(isinstance(view.timer_helper, PADSEditingTimerHelper))

    def test_user_present(self):
        # When a user is signed in, user_present must be True

        # Actions
        #  Sign in the test user, capture response and original request
        resp_sign_in_ptevt = self.test_user_ptevt.sign_in()
        req_sign_in_ptevt = resp_sign_in_ptevt.wsgi_request

        #  Create a PADSView Instance
        #   This is functionally equivalent to opening a new timer in
        #    a PADSTimerEditView.
        view = PADSTimerEditView(req_sign_in_ptevt, self.timer_test_id)
        
        # Assertions
        self.assertTrue(view.user_present())
        
    def test_user_not_present(self):
        # When a user is signed out, user_present must be False

        # Actions
        #  Make a request as without signing in, capture its request
        response = self.client.get(TestUser.url_timer_index)
        request = response.wsgi_request
        
        #  Create a PADSView Instance
        view = PADSTimerEditView(request, self.timer_test_id)
        
        # Assertions
        self.assertFalse(view.user_present())
    

class PublicMiscGETNavigationTests(TestCase):
    # Public Miscellaneous Navigation Tests verify the correct operation
    # of views that are accessible (either by entering the URL directly
    # or through links on pages) by non-signed in users andvie
    # not covered by the Account and Timer tests.
    # 
    # At the moment, these tests ensure that no not-found errors
    # (HTTP 404), and server errors arising from Django exceptions 
    # (HTTP 500), happen during casual navigation by relatively 
    # non-technical users.

    def test_views_accessible_by_public(self):
        # Actions
        #  Get a responses from each of the selected URLs in the
        #   uncovered URLs list
        test_url_responses = []
        for url in shared_uncovered_test_urls:
            test_url_responses.append(self.client.get(url))
        
        # Assertions
        #  Ensure that each of the responses are not 404s or 500s.
        for r in test_url_responses:
            self.assertNotEqual(r.status_code, 404)            
            self.assertNotEqual(r.status_code, 500)
    
class QuickListTests(TestCase):
    # Quick List Tests verify the correctness of Quick List-related
    # operations that are not covered by the Account and Timer tests.
    
    @classmethod
    def setUpTestData(cls):
        # Timer Helper Setup
        cls.timer_helper = PADSTimerHelper()
        
        # Quick List Setup
        cls.user_ql = TestQuickListUser()
        cls.user_ql.sign_up()

        # Regular User Setup
        cls.user_reg = TestUser('test_jess_qlt', 'secure126837')
        cls.user_reg.sign_up()
    
    def test_import_quick_list(self):
        # A user who has signed in should succeed in importing a valid
        # Quick List

        # Actions
        #  Create a new Quick List and open it
        user_ql_import_test = TestQuickListUser()
        user_ql_import_test.sign_up()
        user_ql_import_test.sign_in()
        
        #  Create a new Timer under the test Quick List
        timer_qli_name = 'Quick List Timer Import'
        resp_timer_new = user_ql_import_test.timer_new(
            timer_qli_name, datetime.datetime.now())
        timer_qli_id = get_session_value(resp_timer_new, 'last_new_item_id')

        #  Close the Quick List
        user_ql_import_test.sign_out()

        #  Sign in as the regular Test User
        self.user_reg.sign_in()
        
        #  Import the Quick List
        self.user_reg.settings_import_ql(user_ql_import_test.password)

        #  Open the Personal Timer Index as the regular Test User
        self.user_reg.timer_index_personal()
        view_timer_groups = self.user_reg.last_response.context.get(
            'index_groups')
        view_timer_ids = get_timer_ids(view_timer_groups)
        
        #  Attempt to open the Quick List again
        resp_ql_re_entry = user_ql_import_test.sign_in()
        bann_ql_entry_type = get_session_value(
            resp_ql_re_entry, 'banner_type') 
        bann_ql_entry_text = get_session_value(
            resp_ql_re_entry, 'banner_text') 
        
        # Assertions
        #  All timers must be accessible by the Test User
        self.assertIn(timer_qli_id, view_timer_ids)
        
        #  The Quick List should no longer be accessible
        self.assertEqual(
            user_ql_import_test.get_id_via_helper(), INVALID_SESSION_ID)
        
        #  Failure to open the Quick List has been indicated
        self.assertEqual(bann_ql_entry_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_ql_entry_text, messages['USER_SIGN_IN_QL_WRONG_PASSWORD'])        

    def test_import_quick_list_default_group(self):
        # A user who has signed in should succeed in importing a valid
        # Quick List while choosing to add all imported timers to a 
        # default Timer Group.

        # Actions
        #  Create a new Quick List and open it
        user_ql_import_test = TestQuickListUser()
        user_ql_import_test.sign_up()
        user_ql_import_test.sign_in()
        
        #  Create a new Timer under the test Quick List
        timer_qli_name = 'Quick List Timer Import (into a group)'
        resp_timer_new = user_ql_import_test.timer_new(
            timer_qli_name, timezone.now())
        timer_qli_id = get_session_value(resp_timer_new, 'last_new_item_id')

        #  Close the Quick List
        user_ql_import_test.sign_out()

        #  Sign in as the regular Test User
        self.user_reg.sign_in()
        
        #  Create a Timer Group
        timer_group_name = 'test_group_ql_import'
        resp_new_timer_group = self.user_reg.settings_new_timer_group(
            timer_group_name)
        timer_group_id = get_session_value(
            resp_new_timer_group, 'last_new_item_id')
        
        #  Import the Quick List
        self.user_reg.settings_import_ql(
            user_ql_import_test.password, timer_group_id)

        #  Open the Personal Timer Index as the regular Test User
        resp_index_groups = self.user_reg.timer_group_index_personal()
        
        #  Get ids for all Timers in the Test Timer Group only 
        view_timer_groups = resp_index_groups.context.get('index_groups')
        view_timer_dg_ids = []
        for tg in view_timer_groups:
            if tg.id() == timer_group_id:
                view_timer_dg_ids.extend(get_timer_ids_from_group(tg))
        
        #  Attempt to open the Quick List again
        resp_ql_re_entry = user_ql_import_test.sign_in()
        bann_ql_entry_type = get_session_value(
            resp_ql_re_entry, 'banner_type') 
        bann_ql_entry_text = get_session_value(
            resp_ql_re_entry, 'banner_text') 
        
        # Assertions
        #  All timers must be accessible by the Test User
        self.assertIn(timer_qli_id, view_timer_dg_ids)
        
        #  The Quick List should no longer be accessible
        self.assertEqual(
            user_ql_import_test.get_id_via_helper(), INVALID_SESSION_ID)        

        #  Failure to open the Quick List has been indicated
        self.assertEqual(bann_ql_entry_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_ql_entry_text, messages['USER_SIGN_IN_QL_WRONG_PASSWORD'])

    def test_settings_restricted(self):
        # A Quick List user should be correctly identified in the
        # setup view as a QL user and therefore be shown only a 
        # restricted number of options.
        
        # Actions
        #  Sign in and Open the Setup screen, capture important info
        self.user_ql.sign_in()
        resp_setup = self.user_ql.settings_info()
        session_user = resp_setup.context.get('user')
        
        # Assertions
        self.assertTrue(session_user.is_anonymous)

    def test_new_timer_group_quick_list(self):
        # A Quick List user should fail to create a Timer Group

        # Actions
        #  Open the Test Quick List
        self.user_ql.sign_in()
        
        #  Attempt to create a new Timer Group, capture response
        timer_group_name = 'ql_user_timer_group'
        resp_ql_new_timer_group = self.user_ql.settings_new_timer_group(
            timer_group_name)
        
        #  Attempt to look up group directly from PADS Timer Group Model
        timer_groups_ql = self.timer_helper.get_timer_groups_for_view_by_name(
            timer_group_name)
        
        # Assertions
        #  Failure of Timer Group creation indicated
        banner = get_session_value(resp_ql_new_timer_group, 'banner_type')
        self.assertEqual(banner, BANNER_FAILURE_DENIAL)
        
        #  Verify that the timer was never created.
        #  Within the test database, there should be no timers bearing a name
        #   that sounds like the test timer's at all.
        self.assertEquals(len(timer_groups_ql), 0)
        
    
    def test_sign_in_quick_list(self):
        # A user who has not signed in should succeed in creating a new
        # Quick List and opening it.

        # Actions
        #  Sign in as the Quick List User
        resp_sign_in_ql = self.user_ql.sign_in()
        user_ql_id = get_session_value(resp_sign_in_ql, 'user_id')
        
        # Assertions
        #  Verify that the sign in was successful. This also verifies
        #  that the correct password to the new QL is accessible from
        #  the view.
        self.assertNotEquals(user_ql_id, INVALID_SESSION_ID)
        self.assertEquals(user_ql_id, self.user_ql.get_id_via_helper())
    
    def test_sign_out_quick_list(self):
        # A user who has opened a Quick List should succeed in closing it
        # cleanly

        # Actions
        #  Open the Test Quick List 
        self.user_ql.sign_in()

        #  Close the Test Quick List and capture response
        resp_sign_out_ql = self.user_ql.sign_out()
        
        #  Get QL id
        session_id = get_session_value(resp_sign_out_ql, 'user_id')
        
        # Assertions
        self.assertEquals(session_id, INVALID_SESSION_ID)
        self.assertNotEquals(session_id, self.user_ql.get_id_via_helper())

class RegularAccountSettingsTests(TestCase):
    # Regular Account Options Tests verify that Users are able to
    # successfully update settings associated with their accounts
    # where available.

    @classmethod
    def setUpTestData(cls):
        # Helper Setup
        cls.user_helper = PADSUserHelper()

        # Test User Setup
        cls.password_old = 'secure0000!@#$'
        cls.user_s = TestUser('test_jess_rast', cls.password_old)
        cls.user_s.sign_up()

    def test_change_password_valid(self):
        # A User should be able to change sign in passwords

        # Actions
        #  Sign in the Test User
        self.user_s.sign_in()
        
        #  Change the password for the Test User
        password_new = 'secure*#$%&120'
        resp = self.user_s.settings_set_password(
            self.user_s.password, password_new)
        
        #  Sign Out the Test User
        self.user_s.sign_out()
        
        #  Attempt to sign in with the old password, then sign out
        self.user_s.password = self.password_old
        resp_sign_in_old_pass = self.user_s.sign_in()
        user_id_old_pass = get_session_value(
            resp_sign_in_old_pass, 'user_id')
        self.user_s.sign_out()

        #  Attempt to sign in with the new password, then sign out
        self.user_s.password = password_new
        resp_sign_in_new_pass = self.user_s.sign_in()
        user_id_new_pass = get_session_value(
            resp_sign_in_new_pass, 'user_id')
        self.user_s.sign_out()
        
        # Assertions
        #  Verify that the old password can no longer be used
        self.assertEqual(user_id_old_pass, INVALID_SESSION_ID)
    
        #  Verify that the new password logs into the same account
        self.assertEqual(user_id_new_pass, self.user_s.get_id_via_helper())


class RegularAccountSignUpTests(TestCase):
    # Regular Account Signup Tests verify that account creation (and
    # incidentially, sign-in) functions are working correctly, and that
    # they are rejecting the most common kinds of invalid input.
    
    def test_sign_up_password_blank(self):    
        # Users should fail to sign up for an account with a
        # valid username but a blank or empty password.
        
        # Arrangements
        #  Invalid Credentials
        user_blank_password = TestUser('test_dave_pb', '')
        user_null_password = TestUser('test_dave_pn', None)

        # Actions
        #  Attempt to sign up with blank username and password
        resp_sign_up_blank_password = user_blank_password.sign_up()
        resp_sign_up_null_password = user_null_password.sign_up()
        
        # Attempt to sign in with blank username and password
        resp_sign_in_blank_password = user_blank_password.sign_in()
        resp_sign_in_null_password = user_null_password.sign_in()
        
        # Assertions
        #  Failure of sign up indicated when empty string is specified for password
        bann_sign_up_empty_type = get_session_value(
            resp_sign_up_blank_password, 'banner_type')
        bann_sign_up_empty_text = get_session_value(
            resp_sign_up_blank_password, 'banner_text')
        self.assertEqual(bann_sign_up_empty_type, BANNER_FAILURE_DENIAL)
        self.assertIn(
            bann_sign_up_empty_text, messages['USER_NAME_INVALID_CHARACTERS'])
        
        #  Failure of sign up indicated when None is specified for password
        bann_sign_up_none_type = get_session_value(
            resp_sign_up_null_password, 'banner_type')
        bann_sign_up_none_text = get_session_value(
            resp_sign_up_null_password, 'banner_text')
        self.assertEqual(bann_sign_up_none_type, BANNER_FAILURE_DENIAL)
        self.assertIn(
            bann_sign_up_none_text, messages['USER_NAME_INVALID_CHARACTERS'])
        
        #  Failure of sign in indicated when empty string is specified for password
        bann_sign_in_empty_type = get_session_value(
            resp_sign_in_blank_password, 'banner_type')
        bann_sign_in_empty_text = get_session_value(
            resp_sign_in_blank_password, 'banner_text')
        self.assertEqual(bann_sign_in_empty_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_empty_text, messages['USER_SIGN_IN_INVALID_CREDS'])

        #  Failure of sign in indicated when None is specified for password
        bann_sign_in_none_type = get_session_value(
            resp_sign_in_null_password, 'banner_type')
        bann_sign_in_none_text = get_session_value(
            resp_sign_in_null_password, 'banner_text')
        self.assertEqual(bann_sign_in_none_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_none_text, messages['USER_SIGN_IN_WRONG_PASSWORD'])
        
        #  Confirm that no session user id has been assigned
        user_id_empty = get_session_value(
            resp_sign_in_blank_password, 'user_id')
        user_id_none = get_session_value(
            resp_sign_in_null_password, 'user_id')
        self.assertEqual(user_id_empty, INVALID_SESSION_ID)
        self.assertEqual(user_id_none, INVALID_SESSION_ID)
        
        #  Confirm that the users are not in the DB
        self.assertEqual(
            user_blank_password.get_id_via_helper(), INVALID_SESSION_ID)
        self.assertEqual(
            user_null_password.get_id_via_helper(), INVALID_SESSION_ID)

    def test_sign_up_username_blank(self):
        # Users should fail to sign up for an account with a
        # blank or empty username yet with a valid password.

        # Arrangements
        user_empty = TestUser('', 'secure9999_876543')
        user_none = TestUser(None, 'secure9999_876543')
                
        # Actions
        #  Attempt to sign up using a blank username
        resp_sign_up_empty = user_empty.sign_up()
        resp_sign_up_none = user_none.sign_up()
        
        #  Attempt to sign in using a blank username
        resp_sign_in_empty = user_empty.sign_in()
        resp_sign_in_none = user_none.sign_in()
        
        # Assertions
        #  Failure of sign up indicated when an empty string is specified 
        #   for username
        bann_sign_up_empty_type = get_session_value(
            resp_sign_up_empty, 'banner_type')
        bann_sign_up_empty_text = get_session_value(
            resp_sign_up_empty, 'banner_text')
        self.assertEqual(bann_sign_up_empty_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_up_empty_text, 
            messages['USER_NAME_INVALID_CHARACTERS'])
                
        #  Failure of sign up indicated when None is specified for username
        bann_sign_up_none_type = get_session_value(
            resp_sign_up_none, 'banner_type')
        bann_sign_up_none_text = get_session_value(
            resp_sign_up_none, 'banner_text')
        self.assertEqual(bann_sign_up_empty_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_up_empty_text, messages['USER_NAME_INVALID_CHARACTERS'])
        
        #  Failure of sign in indicated when empty string is specified 
        #   for username
        bann_sign_in_empty_type = get_session_value(
            resp_sign_in_empty, 'banner_type')
        bann_sign_in_empty_text = get_session_value(
            resp_sign_in_empty, 'banner_text')
        self.assertEqual(bann_sign_in_empty_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_empty_text, messages['USER_SIGN_IN_INVALID_CREDS'])
                
        #  Failure of sign in indicated when None is specified for username
        bann_sign_in_none_type = get_session_value(
            resp_sign_in_none, 'banner_type')
        bann_sign_in_none_text = get_session_value(
            resp_sign_in_none, 'banner_text')
        self.assertEqual(bann_sign_in_none_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_none_text, messages['USER_SIGN_IN_WRONG_PASSWORD'])
        
        #  Confirm that session user ids have not been assigned
        user_id_empty = get_session_value(resp_sign_in_empty, 'user_id')
        user_id_none = get_session_value(resp_sign_in_none, 'user_id')
        self.assertEqual(user_id_empty, INVALID_SESSION_ID)
        self.assertEqual(user_id_none, INVALID_SESSION_ID)
        
        #  Confirm that the users are not in the database
        self.assertEqual(user_empty.get_id_via_helper(), INVALID_SESSION_ID)
        self.assertEqual(user_none.get_id_via_helper(), INVALID_SESSION_ID)

    def test_sign_up_password_username_blank(self):
        """Users should fail to sign up with a blank (None or 
        empty string) username and password are supplied
        """
        # Arrangements
        user_empty = TestUser('', '')
        user_none = TestUser(None, None)
                
        # Actions
        #  Attempt to sign up an account using a blank username and password
        resp_sign_up_empty = user_empty.sign_up()
        resp_sign_up_none = user_none.sign_up()
        #  Attempt to sign in with blank username and password
        resp_sign_in_empty = user_empty.sign_in()
        resp_sign_in_none = user_none.sign_in()
        
        # Assertions
        #  Failure of sign up indicated when empty string is specified
        #   for both username and password.
        bann_sign_up_empty_type = get_session_value(
            resp_sign_up_empty, 'banner_type')
        bann_sign_up_empty_text = get_session_value(
            resp_sign_up_empty, 'banner_text')
        self.assertEqual(bann_sign_up_empty_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_up_empty_text, 
            messages['USER_NAME_INVALID_CHARACTERS'])
        
        #  Failure of sign in indicated when empty string is specified
        #   for both username and password.
        bann_sign_up_none_type = get_session_value(
            resp_sign_up_none, 'banner_type')
        bann_sign_up_none_text = get_session_value(
            resp_sign_up_none, 'banner_text')
        self.assertEqual(bann_sign_up_none_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_up_none_text, 
            messages['USER_NAME_INVALID_CHARACTERS'])
        
        #  Failure of sign in indicated when empty string is specified 
        #   for both username and password.
        bann_sign_in_empty_type = get_session_value(
            resp_sign_in_empty, 'banner_type')
        bann_sign_in_empty_text = get_session_value(
            resp_sign_in_empty, 'banner_text')
        user_id_empty = get_session_value(resp_sign_in_empty, 'user_id')
        self.assertEqual(bann_sign_in_empty_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_empty_text, messages['USER_SIGN_IN_INVALID_CREDS'])
        self.assertEqual(user_id_empty, INVALID_SESSION_ID)
        
        #  Failure of sign in indicated when None is specified for 
        #   both username and password.
        bann_sign_in_none_type = get_session_value(
            resp_sign_in_none, 'banner_type')
        bann_sign_in_none_text = get_session_value(
            resp_sign_in_none, 'banner_text')
        user_id_none = get_session_value(resp_sign_in_none, 'user_id')
        self.assertEqual(bann_sign_in_none_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_none_text, messages['USER_SIGN_IN_WRONG_PASSWORD'])
        self.assertEqual(user_id_none, INVALID_SESSION_ID)
        
        #  Confirm that users are not in the DB
        self.assertEqual(user_empty.get_id_via_helper(), INVALID_SESSION_ID)
        self.assertEqual(user_none.get_id_via_helper(), INVALID_SESSION_ID)
            
    
    def test_sign_up_password_invalid(self):
        """Users should fail to sign in when the wrong password is entered
        after an account is created. This is part of the verification
        process to ensure that the account password is set properly.
        """ 
        # Arrangements
        user_correct = TestUser('test_dave_pi', '123secure')
        user_wrong = TestUser('test_dave_pi', '456secure')
        #  The Wrong User has the same username, but different password.

        # Actions
        #  Sign up the User with the correct password
        user_correct.sign_up()
        
        #  However, sign in with the wrong user
        resp_sign_in = user_wrong.sign_in()  # Simulates sign in with wrong password
        
        # Assertions
        #  Failure of signing into new account indicated, 
        #  invalid user id returned
        bann_sign_in_type = get_session_value(resp_sign_in, 'banner_type')
        bann_sign_in_text = get_session_value(resp_sign_in, 'banner_text')
        user_id = get_session_value(resp_sign_in, 'user_id')
        self.assertEqual(bann_sign_in_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_text, messages['USER_SIGN_IN_WRONG_PASSWORD'])        
        self.assertEqual(user_id, INVALID_SESSION_ID)

    def test_sign_up_password_leading_space(self):
        """Users should succeed in signing up, then signing in with a
        password that begin with spaces
        """
        # Arrangements
        user_pls = TestUser('test_dave_pls', '   secure7878')
        
        # Actions
        #  Sign up and sign in the test User
        resp_sign_up_pwls = user_pls.sign_up()
        resp_sign_in_pwls = user_pls.sign_in()
        
        # Assertions
        #  Success of signing up new account indicated
        bann_sign_in_type = get_session_value(
            resp_sign_up_pwls, 'banner_type')
        bann_sign_in_text = get_session_value(
            resp_sign_up_pwls, 'banner_text')        
        self.assertEqual(bann_sign_in_type, BANNER_SUCCESS)
        self.assertIn(bann_sign_in_text, messages['USER_SIGN_UP_SUCCESS'])
        
        #  Success of signing into new account indicated
        bann_sign_in_type = get_session_value(
            resp_sign_in_pwls, 'banner_type')
        bann_sign_in_text = get_session_value(
            resp_sign_in_pwls, 'banner_text')
        self.assertEqual(bann_sign_in_type, BANNER_INFO)
        self.assertIn(
            bann_sign_in_text, 
            messages['USER_SIGN_IN_SUCCESS'].format(user_pls.username) )

        #  Valid user id returned
        user_id = get_session_value(resp_sign_in_pwls, 'user_id')
        self.assertEqual(user_id, user_pls.get_id_via_helper())

    def test_sign_up_password_trailing_space(self):
        """Users should succeed in signing up, then signing in with a
        password that end with spaces
        """
        # Arrangements
        user_pts = TestUser('test_dave_pts', 'secure7878          ')
        
        # Actions
        #  Attempt to sign up and sign in the User
        resp_sign_up = user_pts.sign_up()
        resp_sign_in = user_pts.sign_in()
        
        # Assertions
        #  Success of signing up new account indicated
        bann_sign_up_type = get_session_value(resp_sign_up, 'banner_type')
        bann_sign_up_text = get_session_value(resp_sign_up, 'banner_text')
        self.assertEqual(bann_sign_up_type, BANNER_SUCCESS)
        self.assertIn(bann_sign_up_text, messages['USER_SIGN_UP_SUCCESS'])
        
        #  Success of signing into new account indicated
        bann_sign_in_type = get_session_value(resp_sign_in, 'banner_type')
        bann_sign_in_text = get_session_value(resp_sign_in, 'banner_text')
        self.assertEqual(bann_sign_in_type, BANNER_INFO)
        self.assertIn(
            bann_sign_in_text, 
            messages['USER_SIGN_IN_SUCCESS'].format(user_pts.username) )

        #  Correct user id returned
        user_id = get_session_value(resp_sign_in, 'user_id')
        self.assertEqual(user_id, user_pts.get_id_via_helper())

    def test_sign_up_valid(self):
        """A User should succeed in signing up with an available username
        and a reasonable password.
        """
        # Arrangements
        #  Set up a new user
        user = TestUser('test_dave', 'secure!@#$1234')
        
        # Actions
        #  Sign up the test user
        sign_up_response = user.sign_up()
        #  Sign in the test user
        sign_in_response = user.sign_in()
        
        # Assertions
        #  Valid user id returned
        sign_in_user_id = get_session_value(sign_in_response, 'user_id')
        self.assertEqual(sign_in_user_id, user.get_id_via_helper())
        

    def test_sign_up_username_taken(self):
        """Users should fail to be able to sign up with a username 
        that has been taken.
        """
        # Arrangements
        user_original = TestUser('test_dave', 'secure7890_12345')
        user_reject = TestUser('test_dave', 'notthesame1254<>')
        
        # Actions
        #  Sign up the original user
        user_original.sign_up()

        #  Attempt to sign up a second user with the same username 
        #   but different password
        resp_sign_up_reject = user_reject.sign_up()

        #  Attempt to sign in as second user
        resp_sign_in_reject = user_reject.sign_in()
        
        #  Attempt to sign in as the original user
        resp_sign_in_original = user_original.sign_in()
        
        # Assertions
        #  Failure of account creation indicated
        bann_sign_up_reject_type = get_session_value(
            resp_sign_up_reject, 'banner_type')
        bann_sign_up_reject_text = get_session_value(
            resp_sign_up_reject, 'banner_text')
        self.assertEqual(bann_sign_up_reject_type, BANNER_FAILURE_DENIAL)
        self.assertIn(
            messages['USER_SIGN_UP_NAME_NOT_AVAILABLE'], 
            bann_sign_up_reject_text)
        
        #  Failure of signing into existing account by rejected user
        #   indicated
        bann_sign_in_reject_type = get_session_value(
            resp_sign_in_reject, 'banner_type')
        bann_sign_in_reject_text = get_session_value(
            resp_sign_in_reject, 'banner_text')
        self.assertEqual(bann_sign_in_reject_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_reject_text, messages['USER_SIGN_IN_WRONG_PASSWORD'])
        
        #  Confirm that rejected user did was not assigned a session
        #   user id
        user_id_reject = get_session_value(resp_sign_in_reject, 'user_id')
        self.assertEqual(user_id_reject, INVALID_SESSION_ID)

        #  Confirm integrity of original account, indicated by successful
        #   sign-in with original password, and matching user ids
        #   in session and in the database.
        user_id_original = get_session_value(resp_sign_in_original, 'user_id')
        self.assertEqual(user_original.get_id_via_helper(), user_id_original)
        
        #  Success of signing into original account indicated
        bann_sign_in_original_type = get_session_value(
            resp_sign_in_original, 'banner_type')
        bann_sign_in_original_text = get_session_value(
            resp_sign_in_original, 'banner_text')
        self.assertEqual(bann_sign_in_original_type, BANNER_INFO)
        self.assertEqual(
            bann_sign_in_original_text, 
            messages['USER_SIGN_IN_SUCCESS'].format(user_original.username) )

    def test_sign_up_username_taken_different_case(self):
        """Users should fail to be able to sign up with a username 
        that has been taken, even if said username is in a different 
        alphabetical case.
        """
        # Arrangements
        user_original = TestUser('test_dave_dc', 'secure7890')
        user_reject = TestUser('TEST_DAVE_DC', 'notthesame1254<>')
        
        # Actions
        #  Sign up the original user
        user_original.sign_up()

        #  Attempt to sign up a second user with the same username 
        #   but different password
        resp_sign_up_reject = user_reject.sign_up()

        #  Attempt to sign in as second user
        resp_sign_in_reject = user_reject.sign_in()
        
        #  Attempt to sign in as the original user
        resp_sign_in_original = user_original.sign_in()
        
        # Assertions
        #  Failure of account creation indicated
        bann_sign_up_reject_type = get_session_value(
            resp_sign_up_reject, 'banner_type')
        bann_sign_up_reject_text = get_session_value(
            resp_sign_up_reject, 'banner_text')
        self.assertEqual(bann_sign_up_reject_type, BANNER_FAILURE_DENIAL)
        self.assertIn(
            messages['USER_SIGN_UP_NAME_NOT_AVAILABLE'], 
            bann_sign_up_reject_text)
        
        #  Failure of signing into existing account by rejected user
        #   indicated
        bann_sign_in_reject_type = get_session_value(
            resp_sign_in_reject, 'banner_type')
        bann_sign_in_reject_text = get_session_value(
            resp_sign_in_reject, 'banner_text')
        self.assertEqual(bann_sign_in_reject_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_reject_text, 
            messages['USER_SIGN_IN_WRONG_PASSWORD'])
        
        #  Confirm that rejected user did was not assigned a session
        #   user id
        user_id_reject = get_session_value(resp_sign_in_reject, 'user_id')
        self.assertEqual(user_id_reject, INVALID_SESSION_ID)

        #  Confirm integrity of original account, indicated by successful
        #   sign-in with original password, and matching user ids
        #   in session and in the database.
        user_id_original = get_session_value(resp_sign_in_original, 'user_id')
        self.assertEqual(user_original.get_id_via_helper(), user_id_original)
        
        #  Success of signing into original account indicated
        bann_sign_in_original_type = get_session_value(
            resp_sign_in_original, 'banner_type')
        bann_sign_in_original_text = get_session_value(
            resp_sign_in_original, 'banner_text')
        self.assertEqual(bann_sign_in_original_type, BANNER_INFO)
        self.assertEqual(
            bann_sign_in_original_text, 
            messages['USER_SIGN_IN_SUCCESS'].format(user_original.username) )
    

class RegularAccountSignOutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Prepare data for Regular Account Sign Out Tests
        """        
        # Test User Setup
        cls.user_so_1 = TestUser('test_jess', '1234!@#$secure')
        cls.user_so_2 = TestUser('adversary', '5678%^&*secure')
        cls.user_public = TestUser(None,None)
        
        #  Sign Up The Users
        cls.user_so_1.sign_up()
        cls.user_so_2.sign_up()
        
    def test_sign_out_user_id_removed(self):
        """A user who has just signed out should succeed in removing
        the session user id.
        """
        # Actions
        #  Sign in as Test User 1
        self.user_so_1.sign_in()
        
        #  Sign out Test User 1
        resp_sign_out = self.user_so_1.sign_out()
        
        #  Get a response from the personal index and new timer views
        #   as a public user
        resp_personal_index_signed_out = self.user_public.timer_index_personal()
        resp_timer_signed_out = self.client.get(TestUser.url_timer_new)

        # Assertions
        #  Verify that the sign out has been indicated
        bann_sign_out_type = get_session_value(
            resp_sign_out, 'banner_type')
        bann_sign_out_text = get_session_value(
            resp_sign_out, 'banner_text')
        self.assertEquals(bann_sign_out_type, BANNER_INFO)
        self.assertEquals(bann_sign_out_text, 
            messages['USER_SIGN_OUT_SUCCESS'])
        
        #  Verify that the session has been flushed
        with self.assertRaises(NameError):
            get_session_value(resp_personal_index_signed_out, user_id)
            get_session_value(resp_timer_signed_out, user_id)
    
    def test_sign_out_user_switch(self):
        """Subsequent sign-ins by other users should be assigned with the
        correct user ids. A previously signed-out user should have
        their user ids rendered inaccessible.
        """
        # Arrangements
        #  Prepare sign-in credentials
        sign_in_creds_1 = {
            'username' : self.user_so_1.username, 
            'password' : self.user_so_1.password,
            }
        sign_in_creds_2 = {
            'username' : self.user_so_2.username, 
            'password' : self.user_so_2.password,
            }
        
        # Actions
        #   Note: The Test Client will be reused for signing in both
        #    test users to simulate a user switch on the same system.
        #    This is because when using TestUser's, separate Test Clients
        #    are set up for each TestUser.

        #  Sign in as Test User 1 using a shared Test Client
        url_sign_in = reverse('padsweb:session')
        resp_sign_in_user_1 = self.client.post(url_sign_in, sign_in_creds_1)
        
        #  Sign out Test User 1
        self.client.get(TestUser.url_sign_out)
        
        #  Sign in as Test User 2
        resp_sign_in_user_2 = self.client.post(url_sign_in, sign_in_creds_2)        
                
        # Assertions
        #  Verify that the correct user ids have been assigned to each user
        user_id_1 = get_session_value(resp_sign_in_user_1, 'user_id')
        user_id_2 = get_session_value(resp_sign_in_user_2, 'user_id')
        self.assertEqual(user_id_1, self.user_so_1.get_id_via_helper())
        self.assertEqual(user_id_2, self.user_so_2.get_id_via_helper())
        self.assertNotEqual(user_id_1, user_id_2)
        
class RegularAccountSignInTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Prepare data for Regular Account Sign In Tests
        """
        # Test Helper Setup
        cls.user_si = TestUser('test_jess', '5678%^&*secure')
        cls.user_si.sign_up()
        
    def test_sign_in_username_blank(self):
        """Users should fail to sign in when a blank (None or empty string)
        username but valid password are entered
        """
        # Arrangements
        #  Use the Test User's password, but with a blank username
        user_si_empty = TestUser('', self.user_si.password)
        user_si_none = TestUser(None, self.user_si.password)
        
        # Actions
        #  Attempt to sign in with empty and null usernames
        resp_sign_in_empty = user_si_empty.sign_in()
        resp_sign_in_none = user_si_none.sign_in()

        # Assertions
        #  Failure of sign in indicated when empty string is specified
        #   as username
        bann_sign_in_empty_type = get_session_value(
            resp_sign_in_empty, 'banner_type')
        bann_sign_in_empty_text = get_session_value(
            resp_sign_in_empty, 'banner_text')
        self.assertEqual(bann_sign_in_empty_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_empty_text, messages['USER_SIGN_IN_INVALID_CREDS'])

        #  Failure of sign in indicated when null is specified as username
        bann_sign_in_none_type = get_session_value(
            resp_sign_in_none, 'banner_type')
        bann_sign_in_none_text = get_session_value(
            resp_sign_in_none, 'banner_text')
        self.assertEqual(bann_sign_in_empty_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_empty_text, 
            messages['USER_SIGN_IN_INVALID_CREDS'])

        #  Verify that no session user id has been assigned
        user_id_empty = get_session_value(resp_sign_in_empty, 'user_id')
        user_id_none = get_session_value(resp_sign_in_none, 'user_id')
        self.assertEqual(user_id_empty, INVALID_SESSION_ID)
        self.assertEqual(user_id_none, INVALID_SESSION_ID)
    
    def test_sign_in_password_blank(self):
        """Users should fail to sign in when a valid username but blank
        password (None or empty string) are entered
        """
        # Arrangements
        #  Use Test User's name, but with a blank password
        user_sip_empty = TestUser(self.user_si.username, '')
        user_sip_none = TestUser(self.user_si.username, None)
        
        # Actions
        #  Attempt to sign in with empty and null usernames
        resp_sign_in_empty = user_sip_empty.sign_in()
        resp_sign_in_none = user_sip_none.sign_in()

        # Assertions
        #  Failure of sign in indicated when empty string is specified
        #   as password
        bann_sign_in_empty_type = get_session_value(
            resp_sign_in_empty, 'banner_type')
        bann_sign_in_empty_text = get_session_value(
            resp_sign_in_empty, 'banner_text')
        self.assertEqual(bann_sign_in_empty_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_empty_text, messages['USER_SIGN_IN_INVALID_CREDS'])

        #  Failure of sign in indicated when null is specified as password
        bann_sign_in_none_type = get_session_value(
            resp_sign_in_none, 'banner_type')
        bann_sign_in_none_text = get_session_value(
            resp_sign_in_none, 'banner_text')
        self.assertEqual(bann_sign_in_empty_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_empty_text, 
            messages['USER_SIGN_IN_INVALID_CREDS'])

        #  Verify that no session user id has been assigned
        user_id_empty = get_session_value(resp_sign_in_empty, 'user_id')
        user_id_none = get_session_value(resp_sign_in_none, 'user_id')
        self.assertEqual(user_id_empty, INVALID_SESSION_ID)
        self.assertEqual(user_id_none, INVALID_SESSION_ID)
        
        
    def test_sign_in_username_password_blank(self):
        """Users should fail to sign in when a blank (None or empty string)
        username and password are supplied.
        """
        # Arrangements
        #  Prepare blank credentials
        user_siup_empty = TestUser('', '')
        user_siup_none = TestUser(None, None)
        
        # Actions
        #  Attempt to sign in with empty and null credentials
        resp_sign_in_empty = user_siup_empty.sign_in()
        resp_sign_in_none = user_siup_none.sign_in()

        # Assertions
        #  Failure of sign in with empty string credentials indicated
        bann_sign_in_empty_type = get_session_value(
            resp_sign_in_empty, 'banner_type')
        bann_sign_in_empty_text = get_session_value(
            resp_sign_in_empty, 'banner_text')
        self.assertEqual(bann_sign_in_empty_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_empty_text, messages['USER_SIGN_IN_INVALID_CREDS'])

        #  Failure of sign in with null credentials indicated
        bann_sign_in_none_type = get_session_value(
            resp_sign_in_none, 'banner_type')
        bann_sign_in_none_text = get_session_value(
            resp_sign_in_none, 'banner_text')
        self.assertEqual(bann_sign_in_empty_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_empty_text, 
            messages['USER_SIGN_IN_INVALID_CREDS'])

        #  Verify that no session user id has been assigned
        user_id_empty = get_session_value(resp_sign_in_empty, 'user_id')
        user_id_none = get_session_value(resp_sign_in_none, 'user_id')
        self.assertEqual(user_id_empty, INVALID_SESSION_ID)
        self.assertEqual(user_id_none, INVALID_SESSION_ID)

    def test_sign_in_username_password_bogus(self):
        """Users should fail to sign in when a bogus username
        and password is entered.
        """
        # Arrangements
        #  Prepare bogus credentials
        user_bogus = TestUser('asdfghjkl', '+_)(*&^%secure')
        
        # Actions
        #  Attempt to sign in with empty and null usernames
        resp_sign_in_bogus = user_bogus.sign_in()

        # Assertions
        #  Failure of sign in indicated when credentials for a user
        #   who has not signed up are presented
        bann_sign_in_bogus_type = get_session_value(
            resp_sign_in_bogus, 'banner_type')
        bann_sign_in_bogus_text = get_session_value(
            resp_sign_in_bogus, 'banner_text')
        self.assertEqual(bann_sign_in_bogus_type, BANNER_FAILURE_DENIAL)
        self.assertEqual(
            bann_sign_in_bogus_text, messages['USER_SIGN_IN_WRONG_PASSWORD'])

        #  Verify that no user id has been assigned
        user_id_bogus = get_session_value(resp_sign_in_bogus, 'user_id')
        self.assertEqual(user_id_bogus, INVALID_SESSION_ID)
        self.assertNotEqual(user_id_bogus, self.user_si.get_id_via_helper())
    
    def test_sign_in_valid(self):
        """Users should be able to sign in with a regular account, 
        using a valid username and password.
        """
        # Actions
        #  Test User has already been signed up in Test Setup
        resp_sign_in = self.user_si.sign_in()

        # Assertions
        #  Success of signing into new account indicated
        bann_sign_in_type = get_session_value(resp_sign_in, 'banner_type')
        bann_sign_in_text = get_session_value(resp_sign_in, 'banner_text')
        self.assertEqual(bann_sign_in_type, BANNER_INFO)
        self.assertIn(
            messages['USER_SIGN_IN_SUCCESS'].format(self.user_si.username), 
            bann_sign_in_text)
        
        #  Verify that the correct session user id has been assigned
        user_id = get_session_value(resp_sign_in, 'user_id')
        self.assertEqual(user_id, self.user_si.get_id_via_helper() )
    
    def test_sign_in_valid_different_case(self):
        """Users should be able to sign in with a regular account, 
        using a valid username in a different case and the correct
        password.
        """
        # Arrangements
        #  Prepare credentials, Test User with username in uppercase
        user_si_uppercase = TestUser(
            self.user_si.username.upper(), self.user_si.password)
        
        # Actions
        #  Test User has already been signed up in Test Setup
        resp_sign_in = user_si_uppercase.sign_in()

        # Assertions
        #  Success of signing into new account indicated
        bann_sign_in_type = get_session_value(resp_sign_in, 'banner_type')
        bann_sign_in_text = get_session_value(resp_sign_in, 'banner_text')
        self.assertEqual(bann_sign_in_type, BANNER_INFO)
        self.assertIn(
            messages['USER_SIGN_IN_SUCCESS'].format(self.user_si.username), 
            bann_sign_in_text)
        
        #  Verify that the correct session user id has been assigned,
        #   and that all user id's match
        user_id_uppercase = get_session_value(resp_sign_in, 'user_id')
        self.assertEqual(user_id_uppercase, self.user_si.get_id_via_helper() )
        self.assertEqual(user_si_uppercase.get_id_via_helper(), self.user_si.get_id_via_helper() )


# For all the other Timer View tests, see TimerTests
class TimerGroupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Arrangements for all Timer Group tests
        
        Test Scenario:
        There are two Test Users.
        Test User 1 has two Timers and two Timer Groups
        Test User 2 has one Timer and one Timer Group        
        """
        # Arrangements
        
        # Timer Helper Setup
        cls.timer_helper = PADSTimerHelper()
        
        # Test User Setup
        #  Prepare and Sign Up Test Users
        cls.user_test_tg_1 = TestUser('test_jess_tgt', '1234!@#$secure')
        cls.user_test_tg_1.sign_up()
        cls.user_test_tg_2 = TestUser('adversary', '456secure')
        cls.user_test_tg_2.sign_up()
        cls.user_public = TestUser(None, None) # Public user who has not signed up
        
        #  Sign In Test Users
        cls.user_test_tg_1.sign_in()
        cls.user_test_tg_2.sign_in()
        
        # Test Timer Setup
        #  Put Test Timers into the Database and get ids
        #   For User 1
        cls.timer_u1t1_name = 'Timer Group Test: Timer I by User 1'
        resp_new_timer = cls.user_test_tg_1.timer_new(
            cls.timer_u1t1_name, timezone.now() )
        cls.timer_u1t1_id = get_session_value(
            resp_new_timer, 'last_new_item_id')

        cls.timer_u1t2_name = 'Timer Group Test: Timer II by User 1'
        resp_new_timer = cls.user_test_tg_1.timer_new(
            cls.timer_u1t2_name, timezone.now() )
        cls.timer_u1t2_id = get_session_value(
            resp_new_timer, 'last_new_item_id')
        
        #   For User 2
        cls.test_timer_u2t1_name = 'Timer Group Test: Timer i by User 2'
        resp_new_timer = cls.user_test_tg_1.timer_new(
            cls.test_timer_u2t1_name, timezone.now() )
        cls.test_timer_u2t1_id = get_session_value(
            resp_new_timer, 'last_new_item_id')

        # Test Timer Group Setup
        #  Put Test Timer Groups into the Database and get ids
        #   For User 1
        cls.timer_group_u1g1_name = 't_group_u1_a'
        resp_new_timer_group = cls.user_test_tg_1.settings_new_timer_group(
            cls.timer_group_u1g1_name)
        cls.timer_group_u1g1_id = get_session_value(
            resp_new_timer_group, 'last_new_item_id')
        
        cls.timer_group_u1g2_name = 't_group_u1_b'
        resp_new_timer_group = cls.user_test_tg_1.settings_new_timer_group(
            cls.timer_group_u1g2_name)
        cls.timer_group_u1g2_id = get_session_value(
            resp_new_timer_group, 'last_new_item_id')

        #   Add User 1's Test Timer 2 to User 1's Group B
        cls.user_test_tg_1.timer_add_to_group(
            cls.timer_u1t2_id, cls.timer_group_u1g2_id)

        #  For User 2
        cls.timer_group_u2g1_name = 't_group_u2_a'
        resp_new_timer_group = cls.user_test_tg_2.settings_new_timer_group(
            cls.timer_group_u2g1_name)
        cls.timer_group_u2g1_id = get_session_value(
            resp_new_timer_group, 'last_new_item_id')
        
    
    def test_new_group(self):
        """A signed-in User should succeed in creating a Timer Group.
        """    
        # Actions
        #  Create a new Timer Group as Test User 1 and get its id
        timer_group_u1n_name = 'new_timer_group_test'
        resp_new_timer_group = self.user_test_tg_1.settings_new_timer_group(
            timer_group_u1n_name)
        timer_group_u1n_id = get_session_value(
            resp_new_timer_group, 'last_new_item_id')
        
        #  Get a response from the Personal Timer Groups view as
        #   Test User 1
        resp_timer_groups = self.user_test_tg_1.timer_group_index_personal()
        
        #  Get names of all groups loaded
        timer_group_ids = []
        timer_groups = resp_timer_groups.context.get('index_groups')
        for tg in timer_groups:
            timer_group_ids.append(tg.id())
        
        # Assertions
        #  The new Timer Group should be present i Test User 1's
        #  Personal Timer Groups view
        self.assertIn(timer_group_u1n_id, timer_group_ids)
        
    def test_new_group_by_public(self):
        """A User who has not signed in should fail to create a Timer Group.
        """
        # Actions
        #  Attempt to add a Timer Group without signing in
        timer_group_np_name = 'timer_group_new_pub'
        self.user_public.settings_new_timer_group(timer_group_np_name)
        
        #  Get a count of new Timer Groups in the Test Database
        view_group_list = self.timer_helper.get_timer_groups_for_view_by_name(
            timer_group_np_name)
        new_group_count = len(view_group_list)
        
        # Assertions
        #  There should be no new Timer Groups in the Database
        self.assertEqual(new_group_count, 0)
        
    def test_delete_group(self):
        """A signed-in User should succeed in deleting a group timer owned
        by the User.
        """    
        # Actions
        #  Create a new Timer Group as Test User 1
        timer_group_temp_name = 'timer_group_delete_test'
        resp_new_timer_group = self.user_test_tg_1.settings_new_timer_group(
            timer_group_temp_name)
        timer_group_temp_id = get_session_value(
            resp_new_timer_group, 'last_new_item_id')
        
        #  Delete Timer Group as Test User 1
        self.user_test_tg_1.settings_delete_timer_group(timer_group_temp_id)
        
        #  Open up the Timer Groups Personal Index as Test User 1
        resp_timer_index = self.user_test_tg_1.timer_group_index_personal()

        #  Get names of all groups loaded
        timer_group_ids = []
        timer_groups = resp_timer_index.context.get('index_groups')
        for tg in timer_groups:
            timer_group_ids.append(tg.id())
        
        # Assertions
        #  Test Group should not be present in Test User 1's Timer Groups view
        self.assertNotIn(timer_group_temp_id, timer_group_ids)

    def test_delete_group_by_public(self):
        """A User who has not signed in should fail to delete any timer
        group.
        """
        # Actions
        #  Create a new Timer Group as Test User 1
        timer_group_temp_name = 'timer_group_delete_test_p'
        resp_new_timer_group = self.user_test_tg_1.settings_new_timer_group(
            timer_group_temp_name)
        timer_group_temp_id = get_session_value(
            resp_new_timer_group, 'last_new_item_id')

        #  Attempt to Delete Timer Group without Signing In
        self.user_public.settings_delete_timer_group(timer_group_temp_id)
        
        #  Get a response from the Personal Timer Groups view
        #  for Test User 1
        resp_timer_index = self.user_test_tg_1.timer_group_index_personal()
        
        #  Get id's of all groups loaded
        timer_group_ids = []
        timer_groups = resp_timer_index.context.get('index_groups')
        for tg in timer_groups:
            timer_group_ids.append(tg.id())
        
        # Assertions
        #  Test Group should remain in Test User 1's Timer Groups view
        self.assertIn(timer_group_temp_id, timer_group_ids)

    def test_delete_group_other_user(self):
        """A signed-in User should fail to delete a timer group owned
        by another User.
        """    
        # Actions
        #  Create a new Timer Group as Test User 1
        timer_group_temp_name = 'timer_group_delete_test_ou'
        resp_new_timer_group = self.user_test_tg_1.settings_new_timer_group(
            timer_group_temp_name)
        timer_group_temp_id = get_session_value(
            resp_new_timer_group, 'last_new_item_id')
        
        #  Delete Timer Group as Test User 2
        self.user_test_tg_2.settings_delete_timer_group(timer_group_temp_id)
        
        #  Open up the Timer Groups Personal Index as Test User 1
        resp_timer_index = self.user_test_tg_1.timer_group_index_personal()

        #  Get names of all groups loaded
        timer_group_ids = []
        timer_groups = resp_timer_index.context.get('index_groups')
        for tg in timer_groups:
            timer_group_ids.append(tg.id())
        
        # Assertions
        #  Test Group should remain in Test User 1's Timer Groups view
        self.assertIn(timer_group_temp_id, timer_group_ids)
    
    def test_add_to_group(self):
        """A signed-in user should succeed in adding a timer owned or
        created by the user to an existing timer group.
        """
        # Actions
        #  Add Test User's Timer I to Group A, as Test User 1
        self.user_test_tg_1.timer_add_to_group(
            self.timer_u1t1_id, self.timer_group_u1g1_id)
        
        #  Open up the Personal Timers Group Index as Test User 1
        resp_timer_index = self.user_test_tg_1.timer_group_index_personal()
        
        #  Get the ids of all Timers in Test Timer Group A from the 
        #  response
        timer_group_u1g1_ids = []
        timer_groups = resp_timer_index.context.get('index_groups')
        for tg in timer_groups:
            if tg.id() == self.timer_group_u1g1_id:
                timer_group_u1g1_ids.extend(get_timer_ids_from_group(tg))
        
        # Assertions
        #  Timer 1 should appear in Test User's Group A
        self.assertIn(self.timer_u1t1_id, timer_group_u1g1_ids)
        
    def test_add_to_group_by_public(self):
        """A user who has not signed in should fail to add any timer
        to any existing timer group.
        """
        # Actions
        #  Attempt to add Test User 1's Timer I to Test User 2's Group A
        #   as the public user
        self.user_public.timer_add_to_group(
            self.timer_u1t1_id, self.timer_group_u2g1_id)

        #  Get a response from the Personal Timers By Group View
        #   as Test User 2
        resp_timer_index = self.user_test_tg_2.timer_group_index_personal()

        #  Get the ids of all Timers in Test Timer Group A from 
        #   the response as Test User 1
        timer_group_u2g1_ids = []
        timer_groups = resp_timer_index.context.get('index_groups')
        for tg in timer_groups:
            if tg.id() == self.timer_group_u2g1_id:
                timer_group_u2g1_ids.extend(get_timer_ids_from_group(tg))
        
        # Assertions
        #  Verify that the User 1's Timer I has not been added 
        #   to User 2's Group A. 
        self.assertNotIn(self.timer_u1t1_id, timer_group_u2g1_ids)

    def test_add_to_group_other_user(self):
        """A signed-in user should fail in adding a timer owned or
        created by another user to an existing timer group.
        """
        # Actions
        #  Attempt to add Test User 1's Timer I to Test User 2's Group A
        #   as Test User 2
        self.user_test_tg_2.timer_add_to_group(
            self.timer_u1t1_id, self.timer_group_u2g1_id)
        
        #  Get a response from the Personal Timers By Group View as Test User 2
        resp_timer_groups = self.user_test_tg_2.timer_group_index_personal()
        
        #  Get the ids of all Timers in Test Timer Group A from the 
        #  response as Test User 2
        timer_groups = resp_timer_groups.context.get('index_groups')
        timer_group_u2g1_ids = []
        for tg in timer_groups:
            if tg.id() == self.timer_group_u2g1_id:
                timer_group_u2g1_ids.extend(get_timer_ids_from_group(tg))
        
        # Assertions
        #  Verify that the User 1's Timer I has not been added to
        #    User 2's Group A. 
        self.assertNotIn(self.timer_u1t1_id, timer_group_u2g1_ids)
        
    def test_remove_from_group(self):
        """A signed-in User should succeed in removing a timer which
        the User created or owns, from an existing group.
        """
        # Actions
        #  Remove Test User 1's Timer II from Group B as Test User 1
        self.user_test_tg_1.timer_remove_from_group(
            self.timer_u1t2_id, self.timer_group_u1g2_id)

        #  Get a response from the Personal Timers By Group View 
        #   as Test User 1
        resp_timer_group_index = self.user_test_tg_1.timer_group_index_personal()
        
        #  Get the ids of all Timers in Test Timer Group A from the 
        #  response as Test User 1
        timer_group_u1g2_ids = []
        timer_groups = resp_timer_group_index.context.get('index_groups')
        for tg in timer_groups:
            if tg.id() == self.timer_group_u1g2_id:
                timer_group_u1g2_ids.extend(get_timer_ids_from_group(tg))
        
        # Assertions
        #  Verify that the Test User 1's Timer II has been removed
        #   from Group B. 
        self.assertNotIn(self.timer_u1t1_id, timer_group_u1g2_ids)
        
    def test_remove_from_group_by_public(self):
        """A user who has not signed in should fail in removing a 
        timer from an existing timer group.
        """
        #  Attempt to Test User 1's Remove Timer II from 
        #   Group B as the public user
        self.user_public.timer_remove_from_group(
            self.timer_u1t2_id, self.timer_group_u1g2_id)

        #  Get a response from the Personal Timers By Group View
        #   as Test User 1
        resp_timer_group_index = self.user_test_tg_1.timer_group_index_personal()
                
        #  Get the ids of all Timers in Test Timer Group B 
        #   as seen by Test User 1
        timer_groups = resp_timer_group_index.context.get('index_groups')
        timer_group_u1g2_ids = []
        for tg in timer_groups:
            if tg.id() == self.timer_group_u1g2_id:
                timer_group_u1g2_ids.extend(get_timer_ids_from_group(tg))
        
        # Assertions
        #  Verify that the Test User 1's Timer II remains in Group B
        self.assertIn(self.timer_u1t2_id, timer_group_u1g2_ids)
    
    def test_remove_from_group_other_user(self):
        """A signed-in user should fail in removing a timer owned or
        created by another user to an existing timer group.
        """
        #  Attempt to Test User 1's Remove Timer II from 
        #   Group B as the Test User 2
        self.user_test_tg_2.timer_remove_from_group(
            self.timer_u1t2_id, self.timer_group_u1g2_id)

        #  Get a response from the Personal Timers By Group View
        #   as Test User 1
        resp_timer_group_index = self.user_test_tg_1.timer_group_index_personal()
                
        #  Get the ids of all Timers in Test Timer Group B 
        #   as seen by Test User 1
        timer_groups = resp_timer_group_index.context.get('index_groups')
        timer_group_u1g2_ids = []
        for tg in timer_groups:
            if tg.id() == self.timer_group_u1g2_id:
                timer_group_u1g2_ids.extend(get_timer_ids_from_group(tg))
        
        # Assertions
        #  Verify that the Test User 1's Timer II remains in Group B
        self.assertIn(self.timer_u1t2_id, timer_group_u1g2_ids)
        
class TimerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Arrangements for all Timer View Tests
        """    
        # Test User Setup
        #  Setup and Sign Up Test Users
        cls.user_test_t_1 = TestUser('test_jess_tt', '90-=()_+secure')
        cls.user_test_t_1.sign_up()
        cls.user_test_t_2 = TestUser('adversary', '987pefectly_secure')
        cls.user_test_t_2.sign_up()
        #  A TestUser with None for username and password cannot be
        #  signed up, and thus acts as an unregistered public user.
        cls.user_public = TestUser(None, None)
        
        #  Sign In Test Users
        cls.user_test_t_1.sign_in()
        cls.user_test_t_2.sign_in()
        
        #  Create Test Timers as Test User 1 and capture Timer id's
        #   Test Timers id's are:
        #    timer_lpv_1_id : Private Timer
        #    timer_lpub_2_id : Public Timer 
        #    timer_dpub_3_id : Public Timer for Deletion
        #    timer_rpub_4_id : Public Timer for Reset Tests
        
        #   Private Test Timer
        resp_1 = cls.user_test_t_1.timer_new(
            'Test Private Timer by Test User 1', timezone.now() )
        cls.timer_lpv_1_id = get_session_value(resp_1, 'last_new_item_id')

        #   Public Test Timer
        resp_2 = cls.user_test_t_1.timer_new(
            'Test Public Timer by Test User 1', timezone.now() )
        cls.timer_lpub_2_id = get_session_value(resp_2, 'last_new_item_id')
        cls.user_test_t_1.timer_share(cls.timer_lpub_2_id)

        #   Public Test Timer For Deletion
        resp_3 = cls.user_test_t_1.timer_new(
            'Test Public Timer for deletion by Test User 1', timezone.now() )
        cls.timer_dpub_3_id = get_session_value(resp_3, 'last_new_item_id')
        cls.user_test_t_1.timer_share(cls.timer_dpub_3_id)
        
        #   Public Test Timer For Reset
        resp_4 = cls.user_test_t_1.timer_new(
            'Test Public Timer for reset tests by Test User 1', timezone.now() )
        cls.timer_rpub_4_id = get_session_value(resp_4, 'last_new_item_id')
        cls.user_test_t_1.timer_share(cls.timer_rpub_4_id)
        
    def test_list_private_timer(self):
        """Any user should be able to see own private timers on the 
        personal timer index.
        """
        # Actions
        #  Open the Timer Personal Index as Test User 1
        #   Test User 1 signed in during Test Setup
        resp_inp = self.user_test_t_1.timer_index_personal()
        view_timer_groups = resp_inp.context.get('index_groups')
        
        # Assertions
        #  Get all ids of visible timers on the timer index view, then search 
        #  for the presence of the Existing Private Timer in the
        #  timer groups in the personal index view.
        visible_timer_ids = get_timer_ids(view_timer_groups)
        
        #  Test User 1's Private Time should be visible
        self.assertIn(self.timer_lpv_1_id, visible_timer_ids)
            
    def test_list_private_timer_other_user(self):
        """Another registered and signed-in User must fail to see a 
        private timer owned by someone else on the personal and public
        timer indices.
        """
        # Actions        
        #  Open the Public and Personal Timer Index Views as Test User 2
        #  Test User 2 signed in during test setup
        resp_pvidx_user_2 = self.user_test_t_2.timer_index_personal()
        resp_pubidx_user_2 = self.user_test_t_2.timer_index()
        
        #  Get a list of Timers id's that appear in Test User 2's
        #  Timer Indexes
        view_timer_groups_private = resp_pvidx_user_2.context.get(
            'index_groups')
        view_timer_groups_public = resp_pubidx_user_2.context.get(
            'index_groups')
        
        # Assertions
        #  Get all ids of visible timers on the timer index view, then search 
        #  for the presence of the Existing Private Timer in the
        #  timer groups in the personal index view.
        visible_timer_ids_private = get_timer_ids(view_timer_groups_private)
        visible_timer_ids_public = get_timer_ids(view_timer_groups_public)
        
        #  Test User 1's Private Timer should be hidden from Test User 2
        self.assertNotIn(self.timer_lpv_1_id, visible_timer_ids_public)
        self.assertNotIn(self.timer_lpv_1_id, visible_timer_ids_private)
        
    def test_list_private_timer_by_public(self):
        """A user who has not signed in should fail to see the presence 
        of a private timer on the public timer index.
        """
        # Actions        
        #  Get a response from the timer public index view
        resp_unreg_index = self.user_public.timer_index()
        view_timer_groups = resp_unreg_index.context.get('index_groups')
        
        # Assertions
        #  Get all ids of visible timers on the timer index view, then 
        #  search for the presence of the Existing Private Timer in the
        #  timer groups in the public index view.
        visible_timer_ids = get_timer_ids(view_timer_groups)
        
        #  Test User 1's Private Time should be hidden
        self.assertNotIn(self.timer_lpv_1_id, visible_timer_ids)

    def test_list_public_timer(self):
        """ Any signed-in user should succeed in seeing public timers that 
        they are the owner/creator of on the Personal Timer Index.        
        """
        # Actions
        #  Get a response from the timer Public Index view as
        #   Test User 1. The Test User has already signed in during
        #   Test Setup
        resp_pv_idx = self.user_test_t_1.timer_index()
        view_timer_groups = resp_pv_idx.context.get('index_groups')
        
        # Assertions
        #  Get all ids of visible timers on the timer index view, then
        #  search for the presence of the User 1' s Existing Public Timer
        #  in the timer groups in the public index view.
        visible_timer_ids = get_timer_ids(view_timer_groups)
        
        # Test User 1's Public Timer should be visible
        self.assertIn(self.timer_lpub_2_id, visible_timer_ids)
        
    def test_list_public_timer_by_public(self):
        """A user who is not signed in (regular account or quick list)
        should succeed in listing public timers shared by a registered
        user on the public timer index.
        """
        # Actions
        #  Get a response from the timer public index view
        resp_unreg_index = self.user_public.timer_index()
        view_timer_groups = resp_unreg_index.context.get('index_groups')

        # Assertions
        #  Get all ids of visible timers on the timer index view, then
        #  search for the presence of the User 1' s Existing Public Timer
        #  in the timer groups in the public index view.
        visible_timer_ids = get_timer_ids(view_timer_groups)
        
        # Test User 1's Public Timer should be visible
        self.assertIn(self.timer_lpub_2_id, visible_timer_ids)
                
    def test_list_public_timer_other_user(self):
        """A user who is signed in should succeed in listing public timers
        shared by another registered user on the public timer index.
        """
        # Actions
        #  Get a response from the timer public Timer Index View
        #   as Test User 2, who signed in during Test Setup
        resp_idx_user_2 = self.user_test_t_2.timer_index()
        view_timer_groups = resp_idx_user_2.context.get('index_groups')

        # Assertions
        #  Get all ids of visible timers on the timer index view, then
        #  search for the presence of the User 1' s Existing Public Timer
        #  in the timer groups in the public index view.
        visible_timer_ids = get_timer_ids(view_timer_groups)
        
        #  Test User 1's Public Timer should be visible
        self.assertIn(self.timer_lpub_2_id, visible_timer_ids)    

    def test_open_public_timer(self):
        """A signed-in user should succeed in accessing the details of a
        public timer owned or created by the user. Edit options must
        be enabled.
        """
        # Actions
        #  Open up the Test Public Timer's detail page as Test User 1.
        #   Capture edit enabled flags in the View's response.
        resp_timer_detail = self.user_test_t_1.timer_detail(
            self.timer_lpub_2_id)
        view_timer = resp_timer_detail.context.get('timer')
        edit_enabled = resp_timer_detail.context.get('edit_enabled')
        
        # Assertions
        #  Verify that the correct timer is opened
        self.assertIsNotNone(view_timer)
        self.assertEqual(view_timer.id(), self.timer_lpub_2_id)
        
        #  Edit options should be enabled
        self.assertTrue(edit_enabled)

    def test_open_public_timer_other_user(self):
        """A signed-in user should succeed in accessing the details of
        another user's public timer.
        """
        # Actions
        #  Open up the Test Public Timer's detail page as Test User 2.
        #   Capture edit enabled flags in the View's response.
        resp_timer_detail = self.user_test_t_2.timer_detail(self.timer_lpub_2_id)
        view_timer = resp_timer_detail.context.get('timer')
        edit_enabled = resp_timer_detail.context.get('edit_enabled')
        
        # Assertions
        #  Extra Assertion: Verify that it really wasn't Test User 2
        #   who created the timer
        self.assertNotEqual(view_timer.creator_user_id(), self.user_test_t_2)
        
        #  Verify that the correct timer is opened
        self.assertIsNotNone(view_timer)
        self.assertEqual(view_timer.id(), self.timer_lpub_2_id)
        
        #  Edit options should be disabled
        self.assertFalse(edit_enabled)
        
    def test_open_public_timer_by_public(self):
        """A user who is not signed in should succeed in accessing the 
        details of a public timer.
        """
        # Actions
        #  Open up the Test Public Timer's detail page as the public
        #   test user and capture its edit enabled flags
        resp_timer_detail = self.user_public.timer_detail(self.timer_lpub_2_id)
        timer = resp_timer_detail.context.get('timer')
        edit_enabled = resp_timer_detail.context.get('edit_enabled')
        
        # Assertions
        #  Verify that the correct timer is opened
        self.assertEqual(timer.id(), self.timer_lpub_2_id)
        
        #  Edit options should be disabled
        self.assertFalse(edit_enabled)

    def test_open_private_timer(self):
        """A regular user who is signed in must succeed in accessing the 
        detai view of a private timer under the user's ownership.
        """
        # Actions
        #  Get the details of an existing private Timer as Test User 1
        resp_timer_detail = self.user_test_t_1.timer_detail(self.timer_lpv_1_id)
        timer = resp_timer_detail.context.get('timer')
        edit_enabled = resp_timer_detail.context.get('edit_enabled')
        
        # Assertions
        #  Verify that the correct timer is opened.
        self.assertEqual(timer.id(), self.timer_lpv_1_id)
        
        #  Edit options should be enabled
        self.assertTrue(edit_enabled)
        
    def test_open_private_timer_by_public(self):
        """A user who is not signed in must fail to access the details 
        of a private timer.
        """
        # Actions
        #  Get a response from the timer detail view as the public user
        resp_timer_detail = self.user_public.timer_detail(self.timer_lpv_1_id)
        
        # Assertions
        #  Verify that no context was created
        self.assertIsNone(resp_timer_detail.context)
        
        #  Verify that a redirect was performed
        self.assertEqual(resp_timer_detail.status_code, 302)

    def test_open_private_timer_other_user(self):
        """A user who is signed in (regular account) must fail to access
        the details of another user's private timer.
        """
        # Actions
        #  Attempt to get the details of Test User 1's Private Timer
        #   as Test User 2
        resp_timer_detail = self.user_test_t_2.timer_detail(
            self.timer_lpv_1_id)
        
        # Assertions
        #  Verify that no context was created
        self.assertIsNone(resp_timer_detail.context)
        
        #  Verify that a redirect was performed
        self.assertEqual(resp_timer_detail.status_code, 302)

    # NOTE: For Timer Edit Tests
    #  Only public timers are tested at this time. 
    #  Testing just the public timers is expected to be sufficient 
    #  for now, as private timers are currently believe to behave 
    #  exactly like public timers, with the exception of being 
    #  accessible only to the creator or owner user.
    #
    #  Assertions of these tests are carried out from the point of view
    #  of non-registered users.
    
    def test_change_description_public_timer(self):
        """A User who is signed in should succeed in changing the
        description of a public    timer that the User is an owner of.
        """
        # Actions
        
        #  Create a Timer as Test User 1, capture timer id
        timer_r_desc = 'Test Renameable Timer by Test User 1'
        #   Capture datetime for use with the new timer before the
        #    method call, as this will make testing a lot easier.
        date_time_test_start = timezone.now()
        resp_new_timer = self.user_test_t_1.timer_new(timer_r_desc, date_time_test_start)
        timer_r_id = get_session_value(resp_new_timer, 'last_new_item_id')
        
        #  Make the Timer public
        self.user_test_t_1.timer_share(timer_r_id)
        
        #  Change the description on the public timer
        timer_r_desc_new = 'Test Timer Renamed by Test User 1'
        self.user_test_t_1.timer_rename(timer_r_id, timer_r_desc_new)

        #  Open up the timer detail view, as the public user
        #   and get timer details
        resp_timer_r_detail = self.user_public.timer_detail(timer_r_id)
        view_timer = resp_timer_r_detail.context.get('timer')
        
        # Assertions
        #  Verify that the timer description has changed
        self.assertEqual(view_timer.get_description(), timer_r_desc_new)

        #  Verify that the timer has been reset, and that the 
        #  accompanying reset history entry has been recorded.
        self.assertLess(date_time_test_start, view_timer.count_from_date_time())
        timer_reset_reason = view_timer.reset_history_latest().reason
        self.assertIn(timer_r_desc_new, timer_reset_reason)
    
    def test_change_description_public_timer_other_user(self):
        """A User who is signed in should fail to change the description
        of a timer owned by another User
        """
        # Actions
        
        #  Create a Timer as Test User 1, capture timer id
        timer_rx_desc = 'Test Off-limits Timer A by Test User 1'
        #   Capture datetime for use with the new timer before the
        #    method call, as this will make testing a lot easier.
        date_time = datetime.datetime.now()
        resp_new_timer = self.user_test_t_1.timer_new(timer_rx_desc, date_time)
        timer_rx_id = get_session_value(resp_new_timer, 'last_new_item_id')

        #  Make the Timer public
        self.user_test_t_1.timer_share(timer_rx_id)
        
        #  Open up the timer detail view as the public user before
        #   attempted reset and get timer details
        resp_timer_detail = self.user_public.timer_detail(timer_rx_id)
        view_timer_before = resp_timer_detail.context.get('timer')
        
        #  Attempt to change the description on the public timer
        #   as Test User 2
        timer_rx_desc_2 = 'Timer Renamed by Test User 2'
        resp_rename_timer = self.user_test_t_2.timer_rename(
            timer_rx_id, timer_rx_desc_2)
        
        #  Open up the timer detail view as the public user after
        #   attempted reset and get timer details
        resp_timer_detail = self.user_public.timer_detail(timer_rx_id)
        view_timer_after = resp_timer_detail.context.get('timer')

        # Assertions
        #  Verify that the timer description remains the same
        self.assertEqual(view_timer_after.get_description(), timer_rx_desc)
        
        #  Verify that the timer date time remains the same, and that
        #   no new history entry has been written.
        timer_reset_reason = view_timer_after.reset_history_latest().reason
        self.assertEqual(
            view_timer_before.count_from_date_time(), 
            view_timer_after.count_from_date_time())
        self.assertNotIn(timer_rx_desc_2, timer_reset_reason)
        
        
    def test_change_description_public_timer_by_public(self):
        """A user who is not signed in should fail to change the description
        of a public timer.
        """
        #  Create a Timer as Test User 1, capture timer id
        timer_rx_desc = 'Test Off-limits Timer B by Test User 1'
        #   Capture datetime for use with the new timer before the
        #    method call, as this will make testing a lot easier.
        date_time_test_start = datetime.datetime.now()
        resp_new_timer = self.user_test_t_1.timer_new(
            timer_rx_desc, date_time_test_start)
        timer_rx_id = get_session_value(resp_new_timer, 'last_new_item_id')

        #  Make the Timer public
        self.user_test_t_1.timer_share(timer_rx_id)
        
        #  Open up the timer detail view and get timer details
        #   before attempted changes as the public user
        resp_timer_detail = self.user_public.timer_detail(timer_rx_id)
        view_timer_before = resp_timer_detail.context.get('timer')

        #  Attempt to change the description on the public timer
        timer_rx_desc_2 = 'Timer Renamed by Test User 2'
        resp_rename_timer = self.user_public.timer_rename(
            timer_rx_id, timer_rx_desc_2)
        
        #  Open up the timer detail view and get timer details
        #   as the public user
        resp_timer_detail = self.user_public.timer_detail(timer_rx_id)
        view_timer_after = resp_timer_detail.context.get('timer')

        # Assertions
        #  Verify that the timer description remains the same
        self.assertEqual(view_timer_after.get_description(), timer_rx_desc)
        
        #  Verify that the timer date time remains the same, and that
        #   no new history entry has been written.
        timer_reset_reason = view_timer_after.reset_history_latest().reason
        self.assertEqual(
            view_timer_before.count_from_date_time(), 
            view_timer_after.count_from_date_time())
        self.assertNotIn(timer_rx_desc_2, timer_reset_reason)

    def test_delete_public_timer(self):
        """A user who is signed in should succeed in deleting a timer that
        is owned or created by the user.
        """
        # Actions
        #  Delete the Test Timer as Test User 1
        self.user_test_t_1.timer_delete(self.timer_dpub_3_id)

        #  Attempt to open the deleted timer as the public user
        resp_timer_detail = self.user_public.timer_detail(self.timer_dpub_3_id)
        
        # Assertions
        #  Verify timer deletion through the lack of a context
        self.assertIsNone(resp_timer_detail.context)
        #  Verify timer deletion through the presence of a redirect
        self.assertEquals(resp_timer_detail.status_code, 302)
    
    def test_delete_public_timer_by_public(self):
        """A user who is not signed in should fail to delete a 
        public timer.
        """
        #  Attempt to Delete the Deletable Timer as the public user
        self.user_public.timer_delete(self.timer_dpub_3_id)

        #  Attempt to open up the timer as the public user
        resp_timer_detail = self.user_public.timer_detail(self.timer_dpub_3_id)
        view_timer = resp_timer_detail.context.get('timer')
        
        # Assertions
        #  Verify that the timer is still present
        self.assertIsNotNone(view_timer)
        self.assertEquals(view_timer.id(), self.timer_dpub_3_id)
    
    def test_delete_public_timer_other_user(self):
        """A User who is signed in should fail to delete a public timer
        that is not owned by the User.
        """
        #  Attempt to delete the Deletable Timer as Test User 2
        self.user_test_t_2.timer_delete(self.timer_dpub_3_id)

        #  Attempt to open up the deleted timer as the public user
        resp_timer_detail = self.user_public.timer_detail(self.timer_dpub_3_id)
        view_timer = resp_timer_detail.context.get('timer')

        # Assertions
        #  Verify that the timer is still present
        self.assertIsNotNone(view_timer)
        self.assertEquals(view_timer.id(), self.timer_dpub_3_id)

    def test_reset_public_timer(self):
        """A User who is signed in should succeed in resetting a timer that
        is created or owned by the User.
        """
        # Actions
        
        #  Open up the timer detail view and get timer details as
        #   the public user before the reset
        resp_timer_detail = self.user_public.timer_detail(self.timer_rpub_4_id)
        view_timer_before = resp_timer_detail.context.get('timer')
        
        #  Reset the test timer as Test User 1
        timer_reset_reason = 'Test User 1 Resetting Resettable Timer'
        self.user_test_t_1.timer_reset(self.timer_rpub_4_id, timer_reset_reason)
        
        #  Open up the timer detail view and get timer details as
        #   the public user after the reset
        resp_timer_detail = self.user_public.timer_detail(self.timer_rpub_4_id)
        view_timer_after = resp_timer_detail.context.get('timer')

        # Assertions
        #  Verify that the timer has been reset.
        #   The timer should be set to a later date time than the original 
        self.assertGreater(
            view_timer_after.count_from_date_time(), 
            view_timer_before.count_from_date_time())
        
        #  Verify that the accompanying reset history entry 
        #  has been recorded.
        timer_reset_latest_reason = view_timer_after.reset_history_latest().reason
        self.assertIn(timer_reset_reason, timer_reset_latest_reason)
    
    def test_reset_public_timer_other_user(self):
        """A user who is signed in should fail to reset a public timer
        owned or created by another user.
        """
        # Actions
                
        #  Open up the timer detail view, get timer details before
        #   attempted reset
        resp_timer_detail = self.user_public.timer_detail(self.timer_rpub_4_id)
        view_timer_before = resp_timer_detail.context.get('timer')

        #  Attempt to reset the test timer as Test User 2
        timer_reset_reason = 'Test User 2 Attempting to Reset Resettable Timer'
        self.user_test_t_2.timer_reset(self.timer_rpub_4_id, timer_reset_reason)
        
        #  Open up the timer detail view, get timer details after
        #   attempted reset
        resp_timer_detail = self.user_public.timer_detail(self.timer_rpub_4_id)
        view_timer_after = resp_timer_detail.context.get('timer')
        
        # Assertions
        #  Verify that the timer date time has remained the same
        self.assertEqual(
            view_timer_before.count_from_date_time(), 
            view_timer_after.count_from_date_time())
        #  Verify that a reset history entry has not been created
        self.assertNotIn(
            view_timer_after.reset_history_latest().reason, 
            timer_reset_reason)
        
        
    def test_reset_public_timer_by_public(self):
        """A user who is not signed in should fail to reset a public timer
        """
        # Actions
                
        #  Open up the timer detail view, get timer details before
        #   attempted reset
        resp_timer_detail = self.user_public.timer_detail(self.timer_rpub_4_id)
        view_timer_before = resp_timer_detail.context.get('timer')

        #  Attempt to reset the test timer as the public user
        timer_reset_reason = 'Public User Attempting to Reset Resettable Timer'
        self.user_public.timer_reset(self.timer_rpub_4_id, timer_reset_reason)
        
        #  Open up the timer detail view, get timer details after
        #   attempted reset
        resp_timer_detail = self.user_public.timer_detail(self.timer_rpub_4_id)
        view_timer_after = resp_timer_detail.context.get('timer')
        
        # Assertions
        #  Verify that the timer date time has remained the same
        self.assertEqual(
            view_timer_before.count_from_date_time(), 
            view_timer_after.count_from_date_time())
        #  Verify that a reset history entry has not been created
        self.assertNotIn(view_timer_after.reset_history_latest().reason, timer_reset_reason)
    
    def test_share_private_timer(self):
        """A user who is signed in should succeed in making a private
        timer viewable to the public.
        """
        # Actions
        #   Create a Private Timer as Test User 1
        resp = self.user_test_t_1.timer_new(
            'Existing Shareable Private Timer', timezone.now())
        timer_spv_id = get_session_value(resp, 'last_new_item_id')
        
        #  Set the Private Timer as Public as Test User 1
        self.user_test_t_1.timer_share(timer_spv_id)
        
        #  Get a response from the timer public index view as the
        # public user and get all visible timer ids.
        resp_timer_index_pu = self.user_public.timer_index()
        view_timer_groups_pu = resp_timer_index_pu.context.get(
            'index_groups')
        timer_ids_pu = get_timer_ids(view_timer_groups_pu)
        
        #  Get a response from the timer public index view as
        #  Test User 2 and get all visible timer ids.
        resp_timer_index_u2 = self.user_test_t_2.timer_index()
        view_timer_groups_u2 = resp_timer_index_u2.context.get(
            'index_groups')
        timer_ids_u2 = get_timer_ids(view_timer_groups_u2)
        
        # Assertions
        #  The shared timer should be visible by other users, including
        #  those who have not signed in.
        self.assertIn(timer_spv_id, timer_ids_pu) # Public User can view timer
        self.assertIn(timer_spv_id, timer_ids_u2) # Test User 2 can view timer
    
    def test_unshare_public_timer(self):
        """A user who is signed in should succeed in making a public
        timer hidden from the public.
        """
        # Actions
        #   Create a Timer as Test User 1
        resp = self.user_test_t_1.timer_new(
            'Existing Hideable Public Timer', timezone.now())
        timer_hpu_id = get_session_value(resp, 'last_new_item_id')
        
        #   Share the Public Timer as Test User 1
        self.user_test_t_1.timer_share(timer_hpu_id)
        
        #  Set the Private Timer as Public as Test User 1
        self.user_test_t_1.timer_unshare(timer_hpu_id)
        
        #  Get a response from the timer public index view as the
        # public user and get all visible timer ids.
        resp_timer_index_pu = self.user_public.timer_index()
        view_timer_groups_pu = resp_timer_index_pu.context.get(
            'index_groups')
        timer_ids_pu = get_timer_ids(view_timer_groups_pu)
        
        #  Get a response from the timer public index view as
        #  Test User 2 and get all visible timer ids.
        resp_timer_index_u2 = self.user_test_t_2.timer_index()
        view_timer_groups_u2 = resp_timer_index_u2.context.get(
            'index_groups')
        timer_ids_u2 = get_timer_ids(view_timer_groups_u2)
        
        # Assertions
        #  The shared timer should be visible by other users, including
        #  those who have not signed in.
        self.assertNotIn(timer_hpu_id, timer_ids_pu) # Public User can view timer
        self.assertNotIn(timer_hpu_id, timer_ids_u2) # Test User 2 can view timer

#    
# Miscellaneous Functions
#
def get_session_value(response, key):
    """Get a session variable from an HttpResponse object directly
    """
    return response.wsgi_request.session.get(key)

def get_timer_ids(view_timer_groups):
    """Get the id's of every timer visible on an index view's timer groups
    list.
    """
    timer_ids = []
    for tg in view_timer_groups:
        timer_ids.extend(get_timer_ids_from_group(tg))
    return timer_ids

def get_timer_ids_from_group(view_timer_group):
    """Get the id's of every timer in a timer group
    """
    timer_ids = []
    for t in view_timer_group.get_timers():
        timer_ids.append(t.id())
    return timer_ids

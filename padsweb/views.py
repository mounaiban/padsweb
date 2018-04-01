#
#
# Public Archive of Days Since Timers
# Views
#
#

#
# Imports
#

from django.db import IntegrityError, models
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import TemplateView
from padsweb.forms import *
from padsweb.settings import *
from padsweb.strings import messages
from padsweb.timers import *
from padsweb.user import PADSUserHelper, PADSViewUser
import pytz  # For pytz.timezone() tzinfo object lookup
import json  # For json.dumps()

#
# Constants
#

# View-Global Objects
settings = defaults
timer_helper = PADSTimerHelper()
public_timer_helper = PADSPublicTimerHelper()
user_helper = PADSUserHelper()

#
# View Classes
#

class PADSView(TemplateView):
    def get_session_user_id(self):
        session_user_id = (
            self.request.session.get('user_id', INVALID_SESSION_ID))
        if session_user_id:
            return session_user_id
        return INVALID_SESSION_ID

    def get_session_user(self):
        if self.user_present():
            return self.user_helper.get_user_for_view_by_id(
                self.get_session_user_id())
        else:
            return None

    def set_banner_empty(self):
        # TODO: Investigate why the pop() method was not reliable in
        # clearing the banners.
        try:
            del self.request.session['banner_type']
            del self.request.session['banner_text']
        except:
            pass
    
    def get_app_version(self):
        return PADS_CURRENT_VERSION
    
    def get_banner_type(self):
        if self.request.session:
            return self.request.session.get('banner_type')
    
    def get_banner_text(self):
        if self.request.session:
            return self.request.session.get('banner_text')
    
    def add_context_item(self, key, item):
        self.context[key] = item
    
    def user_present(self):
        session_user_id = self.get_session_user_id()
        if session_user_id:
            return session_user_id != INVALID_SESSION_ID
        else:
            return False    
    
    def prepare_context(self):
        self.add_context_item('user_id',self.get_session_user_id())

        self.add_context_item("signed_in", self.user_present())

        if self.user_present():
            self.add_context_item("user", self.get_session_user())
        
        if self.user_present():
            self.add_context_item('time_zone', 
                         self.get_session_user().get_timezone())
        else:
            self.add_context_item('time_zone', 
                         timezone.get_current_timezone_name())
        
        self.add_context_item("app_version", self.get_app_version())
        self.add_context_item("banner_text", self.get_banner_text())
        self.add_context_item("banner_type", self.get_banner_type())
        # Quick way of generating the first part of the URL (scheme and
        # host) adapted from answer by Levi Velazquez on Stack Overflow
        # See: https://stackoverflow.com/a/37740812
        self.add_context_item("permalink_prefix",
                    '{0}://{1}'.format(
                            self.request.scheme, self.request.get_host()))
        
        # Erase banners
        self.set_banner_empty()
    
    def render_template(self, template):
        self.prepare_context()
        return render(self.request, template, self.context)
    
    def __init__(self, request, context=dict(), user_helper=PADSUserHelper()):
        self.request = request
        self.context = context
        self.user_helper = user_helper
        self.search_term = request.GET.get('q')

class PADSTimerView(PADSView):
    
    def set_timer_helpers(self):
        if self.user_present():
            self.timer_helper = PADSTimerHelper(
                self.get_session_user_id())
            self.personal_shared_timer_helper = PADSPublicTimerHelper(
                self.get_session_user_id())
        self.public_timer_helper = PADSPublicTimerHelper()
                
    def __init__(self, request, timer_id):
        super().__init__(request)    
        self.timer_id = timer_id
        self.timer_helper = None
        self.public_timer_helper = None
        self.personal_shared_timer_helper = None
        self.set_timer_helpers()

class PADSTimerDetailView(PADSTimerView):
    TEMPLATE_INDEX_VIEW = 'padsweb/timer.html'

    def get_creator_user_id(self):
        if self.timer:
            return self.timer.creator_user_id()

    def edit_enabled(self):
        session_user_id = self.get_session_user_id()
        creator_user_id = self.get_creator_user_id()
        
        if ((session_user_id != INVALID_SESSION_ID) 
            & (creator_user_id != INVALID_SESSION_ID)):
                
            return self.get_session_user_id() == self.get_creator_user_id()
        
        else:
            return False
    
    def get_timer(self):
        timer = None
        if self.timer_helper:
            timer = self.timer_helper.get_timer_for_view_by_id(self.timer_id)
        if timer == None:
            timer = self.public_timer_helper.get_timer_for_view_by_id(self.timer_id)
        return timer
        
    def prepare_context(self):
        if self.timer:
            self.add_context_item('timer', self.timer)
            self.add_context_item(
                'reset_history', self.timer.reset_history())
            self.add_context_item('edit_enabled', self.edit_enabled())
            if self.edit_enabled():
                self.add_context_item('reason_form', ReasonForm())
        super().prepare_context()
                
    def render_template(self):
        self.prepare_context()
        if self.context.get('timer'):
            return render(self.request, self.TEMPLATE_INDEX_VIEW, self.context)
        else:
            return None
        
    def __init__(self, request, timer_id):
        super().__init__(request, timer_id)
        self.timer_id = timer_id
        self.timer = self.get_timer()

class PADSTimerEditView(PADSTimerDetailView):
    """Dummy view for making requests to change a Timer's configuration.

    NOTE: PADS Timer Edit Views are intended for use with operations
    that change the details of a Timer. They are *not* intended for 
    use with templates.
    """
    
    def set_timer_helpers(self):
        if self.user_present():
            self.timer_helper = PADSEditingTimerHelper(
                self.get_session_user_id())
        else:
            self.timer_helper = None
        self.public_timer_helper = None
    
    def get_timer(self):
        if self.timer_helper:
            return self.timer_helper.get_timer_for_view_by_id(
                self.timer_id)
        else:
            return None
        
    def redirect_to_index(self):
        if self.user_present():
            if self.get_timer():
                if self.get_timer().is_public():
                    return HttpResponseRedirect(reverse('padsweb:index'))
        
        return HttpResponseRedirect(reverse('padsweb:index_personal'))

    def redirect_to_timer(self):
        return HttpResponseRedirect(
            reverse('padsweb:timer', kwargs={'timer_id' : self.timer_id} ))

    def __init__(self, request, timer_id):
        super().__init__(request, timer_id)
        if self.user_present():
            self.set_timer_helpers()

class PADSTimerGroupIndexView(PADSTimerView):
    """View class for management of the rendering of an index of 
    Timer Groups
    """
    
    TEMPLATE_INDEX_VIEW = 'padsweb/index.html'
    
    def add_timer_group(self, group):
        if self.natural_page_number:
            group.set_natural_page_number(int(self.natural_page_number))
        if self.get_search_term():
            group.set_description_filter(self.get_search_term())
            group.set_title('{0} Containing "{1}"'.format(
                group.get_title(), self.get_search_term()) )
        self.timer_groups.append(group)

    def get_search_term(self):
        if self.search_term:
            if len(self.search_term) <= 0:
                return None
            elif len(self.search_term) < MIN_SEARCH_TERMS_LEN:
                # Pad a space on short search terms as a quick and dirty 
                # method of forcing a whole word search, as users may be 
                # searching for short words if they are entering a short
                # search string.
                return ' ' + self.search_term
            else:
                return self.search_term
        
        # No search terms found
        else:
            return None

    def prepare_context(self):
        self.add_context_item('index_groups', self.timer_groups)
        super().prepare_context()

    def render_template(self):
        self.prepare_context()
        return render(self.request, self.TEMPLATE_INDEX_VIEW, self.context)

    def __init__(self, request, timer_groups):
        self.timer_groups = timer_groups
        self.natural_page_number = request.GET.get('p')
        super().__init__(request, dict())

class PADSPaginatedView(TemplateView):
    """Main View Class for PADS. Contains methods for user session detection,
    banner display, pagination and version information.
    """
    
    # By default, only the GET method is permitted
    http_method_names = ['get']

    #
    # User session identification and management methods
    #
    def set_user_id_from_session(self, request):
        """Returns User information from the session if the User is already 
        signed in, and assigns the user to the View object. A default user id
        is assigned if no user has signed in.
        """
        user_id = request.session.get('user_id', 
                                      settings('user_id_signed_out'))
        self.user_id = user_id
    
    def get_user_id(self):
        """Returns the User Id assigned to the view
        """
        return self.user_id
        
    def user_present(self):
        """Checks if a user id has been assigned
        """
        return self.current_user_id != settings['user_id_signed_out']

    # 
    # Banner management methods
    #
    def set_banner_empty_in_session(self):
        """Clears the banner from the session variables of the request 
        associated with this view
        """
        del self.request.session['banner_type']
        del self.request.session['banner_text']
        
    def set_banner_from_session(self, request):
        """Attempts to set up a banner on the view from session data in the 
        incoming HTTP request. Banners are contained in the 'banner_type' 
        (CSS formatting class) and 'banner_text' (text content) key values in 
        the session.
        """
        self.banner_type = request.session.get('banner_type')
        self.banner_text = request.session.get('banner_text')
        self.set_banner_empty_in_session()
            
    #
    # Pagination and data display methods
    # These methods are to be implemented by the view object
    #
    def get_page(self, page=0):
        return self.view_object.get_page(page)

    def get_first_page(self):
        return self.view_object.page()

    def get_natural_page(self, page=1):
        # First page is 1, get the first page by default
        if page <= 0:
            # Automatically get the first page if 0 is entered
            req_page = self.get_first_page() 
        else:
            req_page = self.get_page(page - 1)
        return req_page               

    def get_previous_page_url(self):
        if len(self.view_object.get_url_prefix()) > 0:
            return self.get_page_url(self.get_previous_page_number())
        else:
            return None
    
    def get_previous_page_label(self):
        if self.at_first_page():
            return None
        else:
            return '<'

    def get_previous_natural_page_number(self):
        if self.is_at_first_page():
            return 0
        else:
            return self.view_object.get_current_natural_page_number() - 1
    
    def get_url_prefix(self):
        return self.view_object.get_url_prefix()
    
    def get_page_url(self, n):
        return self.view_object.get_page_url()

    def get_next_natural_page(self):
        if self.at_last_page():
            return self.max_page()
        else:
            return self.current_natural_page_number() + 1

    def get_next_page_url(self):
        tg_url = self.get_pagination_url()
        if len(tg_url) > 0:
            return '{0}?p={1}'.format(
                tg_url, self.get_next_natural_page())
        else:
            return None

    def get_next_page_label(self):
        if self.is_at_last_page():
            return None
        else:
            return '>'

    #
    # Status query methods
    #
    def count(self):
        """Returns the number of items in the view object bound to the view
        """
        return self.view_object.count()
    
    def get_max_page_number(self):
        return self.view_object.get_max_page_number()

    def get_max_natural_page_number(self):
        return self.view_object.max_page_number() + 1
    
    def is_at_last_page(self):
        return self.current_page == 0
    
    def is_at_first_page(self):
        return self.current_page == self.view_object.get_max_page_number()

    def is_multi_page(self):
        return self.view_object.is_multi_page()
    
    def has_small_last_page(self):
        """Determines if the last page will contain less than a third of the 
        page size's number of items.
        """
        return (self.count() % self.page_size) <= int(self.page_size / 3)
    
    #
    # App metadata retrieval methods
    #
    def get_app_version(self):
        return app_metadata['current_version']
    
    def get_permalink_prefix(self, request):
        # Quick way of generating the first part of the URL (scheme and
        # host) adapted from answer by Levi Velazquez on Stack Overflow
        # See: https://stackoverflow.com/a/37740812
        return '{0}://{1}'.format(
                self.request.scheme, self.request.get_host())

    #
    # HTTP request and response methods
    #
    def get(self, request, *args, **kwargs):
        self.set_user_id_from_session()
    
    # TODO: Implement custom error handler in http_method_not_allowed()
    
    #
    # View Object Context Management stuff and Local Variables
    #
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.get_user_id()
        context['signed_in'] = self.user_present()
        if self.user_present():
            vuser = self.user_helper.get_user_for_view_by_id(
                    self.get_user_id())
            context['user'] = vuser
            context['time_zone'] = vuser.get_timezone()
        else:
            self.add_context_item('time_zone', 
                         timezone.get_current_timezone_name())
        
        context['app_version'] = self.get_app_version()
        context['banner_text'] = self.banner_text()
        context['banner_type'] = self.get_banner_type()
        context["permalink_prefix"] = self.get_permalink_prefix()
        
        return context

    def __init__(self, **kwargs):
        """View superclass from which other PADS View Classes are derived.
        At a minimum, PADSPaginatedView requires the following for proper 
        operation:
            
            1. A PADSUserHelper object, for getting user information.
            2. A view object that contains information to show to the User,
               controllable using the Pagination Methods defined in this 
               class.
        """
        self.banner_text = None
        self.banner_type = None
        self.current_page = 0
        self.current_user_id = settings['user_id_signed_out']
        self.items_per_page = settings['view_items_per_page']
        self.request = None
        self.user_helper = kwargs.get('user_helper', PADSUserHelper())
        self.view_object = kwargs.get('view_object')

#
# View Functions
#

# Default Index View without Search Filters
def index(request):
    """Django View to load the Public Timer Index
    """
    index_view = PADSTimerGroupIndexView(request, list())
    # Prepare a Public Timer Helper
    # Only show public Timers
    public_timer_helper = PADSPublicTimerHelper()
    
    #  Load Public Timer Index features
    index_view.add_timer_group(
        PADSLongestRunningTimerGroup(public_timer_helper))
    index_view.add_timer_group(
        PADSRecentlyResetTimerGroup(public_timer_helper))
    index_view.add_timer_group(
        PADSNewestTimerGroup(public_timer_helper))
    
    return index_view.render_template()

def index_personal(request):
    """Django View to load timers created by a User
    """
    index_view_personal = PADSTimerGroupIndexView(request, list())
    
    # Only show Personal Index when User is signed in
    if index_view_personal.user_present():
        user_id = int(index_view_personal.get_session_user_id())
        
        # Get timers for signed-in user, load timers
        private_timers = PADSPrivateTimerGroup(
            index_view_personal.get_session_user_id())
        index_view_personal.add_timer_group(private_timers)
        
        public_timers = PADSSharedTimerGroup(
            index_view_personal.get_session_user_id())
        public_timers.set_title(labels['TIMER_GROUP_DEFAULT_PUBLIC_TITLE'])
        index_view_personal.add_timer_group(public_timers)
        return index_view_personal.render_template()
    
    # Redirect non signed-in users to the Sign Up/Sign In forms
    else:
        return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))

def index_personal_groups(request):
    """Django View to display the Personal Timer Groups Index
    """
    index_view_personal = PADSTimerGroupIndexView(request, list())
    
    if index_view_personal.user_present():
        user_id = index_view_personal.get_session_user_id()
        private_timer_helper = index_view_personal.timer_helper
        
        # Get timer groups for signed-in user
        timer_groups_from_db = private_timer_helper.get_timer_groups_for_view_all()
        for tg in timer_groups_from_db:
            index_view_personal.add_timer_group(tg)
        
        return index_view_personal.render_template()
    
    # Redirect non signed-in Users to the Sign In/Sign Up Form
    else:
        return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))

def index_shared_by_user(request, user_id):
    """Django View to display Timers shared by a User.
    This view is also accessible to users who have not signed in.
    """
    index_view = PADSTimerGroupIndexView(request, list())
    user = user_helper.get_user_for_view_by_id(user_id)

    if user:
        shared_timers = PADSSharedTimerGroup(user_id)
        # Beginner's PROTIP: This is how you concatenate strings in 
        # Python using join().
        # Correct: ''.join([string,string])
        # Wrong: string.join(string)
        timer_group_title = ''.join(
            [shared_timers.title, ': ', user.username()])
        shared_timers.set_title(timer_group_title)
        index_view.add_timer_group(shared_timers)        
        return index_view.render_template()
        
    # User Does Not Exist
    else:
        set_banner(
            request, messages['USER_NOT_FOUND'], BANNER_FAILURE_ERROR)
        
    # Return to the Index View if anything fails
    return HttpResponseRedirect(reverse('padsweb:index'))

def index_private_by_user(request):
    """Django View to display Personal Timers by a signed in User
    """
    index_view = PADSTimerGroupIndexView(request, list())
    
    # Display personal timers when User is signed in
    if index_view.user_present():
        user_id = index_view.get_session_user_id()
        user = user_helper.get_user_for_view_by_id(user_id)
        private_timers = PADSPrivateTimerGroup(user_id)
        index_view.add_timer_group(private_timers)
        timer_group_title = ''.join(
            [private_timers.title, ': ', user.username()])
        private_timers.set_title(timer_group_title)
        return index_view.render_template()
        
    # Redirect non signed-in Users to the Sign In/Sign Up form
    return HttpResponseRedirect(
        reverse('padsweb:sign_up_sign_in_intro'))

def index_group(request, timer_group_id):
    """Django View to display Timers from a Timer Group.
    """
    index_view_personal = PADSTimerGroupIndexView(request, list())
    
    # Display Timer Groups when User is signed in
    if index_view_personal.user_present():
        user_id = index_view_personal.get_session_user_id()
        timer_helper = PADSTimerHelper(user_id)
        
        # Get single timer group for signed-in user
        personal_group = timer_helper.get_timer_group_by_id(timer_group_id)
        if personal_group.timer_group_from_db.creator_user_id == user_id:
            index_view_personal.add_timer_group(personal_group)
            return index_view_personal.render_template()

        # If signed-in User does not own the Timer Group, redirect 
        #  to the Public Index View
        else:
            return HttpResponseRedirect(reverse('padsweb:index'))            
    
    # Redirect non signed-in Users to the Sign In/Sign Up form
    return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))

def index_longest_running(request):
    """Django View to display the longest running Public Timers
    """
    index_view = PADSTimerGroupIndexView(request, list())
    
    longest_running_timers = PADSLongestRunningTimerGroup(
        public_timer_helper)
    index_view.add_timer_group(longest_running_timers)
    return index_view.render_template()

def index_recent_resets(request):
    """Django View to display the most recently reset Public Timers
    """
    index_view = PADSTimerGroupIndexView(request, list())
    
    recent_resets = PADSRecentlyResetTimerGroup(public_timer_helper)
    index_view.add_timer_group(recent_resets)
    return index_view.render_template()

def index_newest(request):
    """Django View to display the newest Public Timers
    """
    index_view = PADSTimerGroupIndexView(request, list())
    
    recent_resets = PADSNewestTimerGroup(public_timer_helper)
    index_view.add_timer_group(recent_resets)
    return index_view.render_template()

def quicklist_new(request):
    """Django View to create Quick Lists. Quick Lists are User accounts
     with a randomly generated    password and no username.
    """
    # POST Requests set up a new Quick List
    if request.method == "POST":
        # Attempt to create a Quick List
        user_ql_new = user_helper.new_anon_user_in_db()
        
        # Success
        if user_ql_new:
            quick_list_password = user_ql_new
            #  Note: string concatenation is performed here instead of
            #  substitution with the format() method, for testability
            #  purposes.
            banner_text = ''.join(
                [messages['USER_SIGN_UP_QL_SUCCESS'], 
                quick_list_password])
            set_banner(request, banner_text, BANNER_INFO)

        # Failure
        else:
            set_banner(
                request, messages['USER_SIGN_UP_QL_ERROR'],
                BANNER_FAILURE_ERROR)
        
        return HttpResponseRedirect(reverse('padsweb:index'))
        
    # GET Requests redirect users to the Sign In/Sign Up screen
    else:
        return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))


def session_end(request):
    """Django View to sign out a User.
    """
    request.session.flush()
    set_banner(request, messages['USER_SIGN_OUT_SUCCESS'], BANNER_INFO)
    return HttpResponseRedirect(reverse('padsweb:index'))

def session_quicklist(request):
    """Django View to sign in a Quick List User.
    Quick List Users are like normal Users except that they don't have
    a username and are accessed with a generated random password.
    Sign-ins for regular accounts are handled by session_new.
    """
    # End all existing sessions
    session_end(request)
    
    # POST Requests initiate Quick List sign-in
    if request.method == "POST":
        form_data = SignInQuickListForm(request.POST)
        
        if form_data.is_valid():
            password = form_data.cleaned_data['password']
            password_parts = user_helper.split_anon_user_password(
                password)
            quick_list_id = password_parts[0]
            password_raw = password_parts[1]
        
            # Only Handle Sign-in if well-form password is provided
            if quick_list_id.isdigit() > 0 and len(password_raw) > 0:
                quick_list_user = user_helper.get_user_for_view_by_id(
                    quick_list_id)

                # Only proceed if Quick List exists
                if quick_list_user:
                    
                    # QL Sign-in Success
                    if quick_list_user.check_password(password_raw):
                        set_user_id(request, quick_list_user.id())
                        set_banner(
                            request, messages['USER_SIGN_IN_QL_SUCCESS'], 
                            BANNER_SUCCESS)
                        return HttpResponseRedirect(
                            reverse('padsweb:index_personal'))

                    # Failure: Quick List exists but password not correct
                    # Hide the fact that the QL exists.
                    else:
                        set_banner(
                            request, messages['USER_SIGN_IN_QL_WRONG_PASSWORD'], 
                            BANNER_FAILURE_DENIAL)
                        return HttpResponseRedirect(
                            reverse('padsweb:sign_up_intro'))
                            
                # Failure: Quick List does not exist
                else:
                    set_banner(
                        request, messages['USER_SIGN_IN_QL_WRONG_PASSWORD'],
                        BANNER_FAILURE_DENIAL)
                    return HttpResponseRedirect(
                        reverse('padsweb:sign_up_intro'))
                    
            # Handle Malformed Quick List password
            else:
                set_banner(
                    request,
                    messages['USER_SIGN_IN_QL_MALFORMED_PASSWORD'], 
                    BANNER_FAILURE_DENIAL)
                return HttpResponseRedirect(
                    reverse('padsweb:sign_up_intro'))

        # Handle invalid sign in form data
        else:
            set_banner(
                request, 
                messages['USER_SIGN_IN_QL_MALFORMED_PASSWORD'],
                BANNER_FAILURE_DENIAL)
            return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))

    # Non-POST Requests redirect to the Sign Up/Sign In view
    else:
        set_banner(
            request, messages['USER_SIGN_IN_REDIRECT'],
            BANNER_FAILURE_DENIAL)
        return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))

def session_new(request):
    """Django View to sign in a User. Quick List sign-ins are handled
    by session_quicklist.
    """
    # End all existing sessions
    session_end(request)
    
    # POST Requests initiate sign-in process
    if request.method == "POST":
        form_data = SignInForm(request.POST)
        if form_data.is_valid():
            username = form_data.cleaned_data['username']
            password = form_data.cleaned_data['password']
        
            # Handle sign in only if user exists in database
            user_old = user_helper.get_user_by_nickname_short(username) 
            if user_old:
            
                # Success
                #  e.g. Valid Password
                if user_old.check_password(password) == True:
                    set_user_id(request, user_old.id())
                    banner_text = messages['USER_SIGN_IN_SUCCESS'].format(
                        user_old.username())
                    set_banner(request, banner_text, BANNER_INFO)
                    # Return to index view after signing in
                    return HttpResponseRedirect(
                        reverse('padsweb:index_personal'))
                else:
                    # Failure
                    #  e.g. Invalid Password
                    set_banner(
                        request, messages['USER_SIGN_IN_WRONG_PASSWORD'],
                        BANNER_FAILURE_DENIAL)
                    return HttpResponseRedirect(
                        reverse('padsweb:sign_up_intro'))
            else:
                # If the User does not exist.
                # Hide the fact that the user might exist.
                set_banner(
                    request, messages['USER_SIGN_IN_WRONG_PASSWORD'],
                    BANNER_FAILURE_DENIAL)
                return HttpResponseRedirect(
                    reverse('padsweb:sign_up_intro'))
                
        else:
            # Handle invalid data received from sign-in form
            set_banner(
                request, messages['USER_SIGN_IN_INVALID_CREDS'],
                BANNER_FAILURE_DENIAL)
            return HttpResponseRedirect(
                reverse('padsweb:sign_up_intro'))
    else:
        # Non-POST requests return a redirect to the Sign Up/Sign In screen
        set_banner(
            request, messages['USER_SIGN_IN_REDIRECT'],
            BANNER_FAILURE_DENIAL)
        return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))

def timer_new(request):
    """Django View to initiate a request to create a new timer.
    """
            
    # POST Requests initiate the creation of a new Timer
    if request.method == "POST":
        
        # Detect if User is Signed In
        dummy_view = PADSView(request, dict())
        user = dummy_view.get_session_user()

        # User Signed In: Read New Timer Form data, create Timer
        if dummy_view.user_present():
            form_data = NewTimerForm(request.POST)

            # Valid Form Data
            if form_data.is_valid():
                
                # Read basic Timer information
                description = form_data.cleaned_data['description']
                first_history_message = form_data.cleaned_data['first_history_message']
                is_historical = form_data.cleaned_data['historical']

                # If the Use Current Date Time option is enabled, the
                #  date_time value is set to None, causing the Timer
                #  Helper to use the exact time of the method call to
                #  save the timer to the database as the count-from time.
                if form_data.cleaned_data['use_current_date_time']:
                    date_time = None
                else:                    
                    year = int(form_data.cleaned_data['year'])
                    month = int(form_data.cleaned_data['month'])
                    day = int(form_data.cleaned_data['day'])
                    hour = int(form_data.cleaned_data['hour'])
                    minute = int(form_data.cleaned_data['minute'])
                    second = int(form_data.cleaned_data['second'])

                    # Construct Date Time object
                    date_time = datetime.datetime(
                            year, month, day,
                            hour = hour,
                            minute = minute,
                            second = second,
                            tzinfo = pytz.timezone(user.get_timezone())
                        )
                
                #  Prepare the Timer Helper
                editing_timer_helper = PADSEditingTimerHelper(user.id())

                # Put the new timer into the Database
                new_timer_id = editing_timer_helper.new_timer(
                    description, 
                    first_history_message, 
                    date_time, 
                    False, 
                    is_historical)
                
                # Remember the Timer id, and inform the user with a banner
                set_last_new_item_id(request, new_timer_id)
                banner_text = ''.join(
                    [messages['TIMER_NEW_SUCCESS'], description])
                set_banner(request, "Timer created!", BANNER_INFO)
                
                # Redirect to Personal Index when done
                return HttpResponseRedirect(reverse('padsweb:index_personal'))
                
            # Invalid Form Data received from new Timer form
            else:
                set_banner(
                    request, messages['TIMER_NEW_INVALID_INFO']
                    , BANNER_FAILURE_DENIAL)
                return HttpResponseRedirect(reverse('padsweb:timer_new'))
                
        # User is not signed in
        else:
            set_banner(
                request, messages['USER_SIGN_IN_REQUIRED'], 
                BANNER_FAILURE_DENIAL)
        return HttpResponseRedirect(reverse('padsweb:index'))
        
    # Non-POST Requests Redirect to Sign In or New Timer screens
    else:
        new_timer_view = PADSView(request, dict())
        
        # User Signed In: Redirect to the New Timer screen
        if new_timer_view.user_present():
            # Import the Add New Timer form
            new_timer_view.add_context_item("add_new_timer_form", NewTimerForm())
            # Render the New Timer form
            return new_timer_view.render_template("padsweb/timer_new.html")

        # Signed Out: Redirect to the Sign In screen
        else:
            set_banner(
                request, messages['USER_SIGN_IN_REQUIRED'], 
                BANNER_FAILURE_DENIAL)
        return HttpResponseRedirect(reverse('padsweb:index'))

def timer(request, timer_id):
    """Django View to display a Timer's details, and with editing options
    when a signed-in User opens his own Timer
    """
    # Prepare a view object to extract User info from session 
    timer_view = PADSTimerDetailView(request, timer_id)
    
    # GET Requests return a page with the Timer's details
    if request.method == "GET":
        
        timer = timer_view.timer
        # Success
        if timer:
            
            # Prepare the Set Timer Groups by Name Form
            assoc_group_names = timer.get_associated_group_names_as_str()
            set_timer_inclusions_form = TimerGroupNamesForm(
                    initial={'group_names': assoc_group_names})
            timer_view.add_context_item('set_timer_inclusions_form', 
                                        set_timer_inclusions_form)
            
            # Prepare the Add Timer To Group Form
            add_timer_inclusion_form = TimerGroupForm(
                timer_group_choices=timer.get_available_groups_for_choicefield())
            timer_view.add_context_item(
                'add_timer_inclusion_form', add_timer_inclusion_form)
                
            # Prepare the Remove Timer From Group Form
            add_timer_inclusion_form = TimerGroupForm(
                timer_group_choices=timer.get_associated_groups_for_choicefield())
            timer_view.add_context_item(
                'remove_timer_inclusion_form', add_timer_inclusion_form)
            timer_view.add_context_item(
                'rename_timer_form', TimerRenameForm())
            
            return timer_view.render_template()
        
        # Failure
        else:
            set_banner(
                request, messages['TIMER_NOT_FOUND'],
                 BANNER_FAILURE_DENIAL)
            return HttpResponseRedirect(reverse('padsweb:index'))

    # Non-GET Requests redirect to the index
    else:
        set_banner(
            request, messages['TIMER_SETTINGS_INVALID_REQUEST'], 
            BANNER_FAILURE_DENIAL)
        return HttpResponseRedirect(reverse('padsweb:index'))

def timer_by_permalink(request, link_code):
    timer_req = timer_helper.get_timer_for_view_by_permalink_code(link_code)
    return timer(request, timer_req.id())

def timer_set_groups(request, timer_id):
    """Django view to assign a Timer's inclusions in a Timer Groups
    by group names. The names are to be specified in a single space-delimited
    string.
    """ 
    if request.method == "POST":
        form_data = TimerGroupNamesForm(request.POST)
        dummy_view = PADSTimerEditView(request, timer_id)
        dummy_view.prepare_context()
        if dummy_view.user_present():
            timer = dummy_view.get_timer()
            if timer:
                
                # Valid Form Data                
                if form_data.is_valid():
                    # Success
                    group_names = form_data.cleaned_data['group_names']
                    if timer.set_groups_by_name(group_names):
                        set_banner(
                            request, messages['TIMER_SETTINGS_GROUPS_SET'], 
                            BANNER_INFO)
                        
                    # Failure
                    else:
                        set_banner(
                            request, messages['TIMER_SETTINGS_SAVE_ERROR'], 
                            BANNER_FAILURE_ERROR)
                
                # Invalid form data received
                else:
                    set_banner(
                        request, messages['TIMER_SETTINGS_INVALID_REQUEST'],
                         BANNER_FAILURE_DENIAL)
                    dummy_view.redirect_to_timer()
                    
            # Timer not found or available
            else:
                set_banner(
                    request, messages['TIMER_NOT_FOUND'], 
                    BANNER_FAILURE_DENIAL)
                return HttpResponseRedirect(reverse('padsweb:index'))
        
        # Edit mode not enabled (current User id doesn't match)
        # creator User's id, or not signed in.
        else:
            set_banner(
                request, messages['TIMER_SETTINGS_WRONG_USER'], 
                BANNER_FAILURE_DENIAL)

    # Handle non-POST requests
    else:
        set_banner(
            request, messages['TIMER_SETTINGS_INVALID_REQUEST'],
             BANNER_FAILURE_DENIAL)
        return HttpResponseRedirect(reverse('padsweb:index'))

    # Return to the timer detail view by default
    return dummy_view.redirect_to_timer()

def timer_add_to_group(request, timer_id):
    """Django view to request a Timer's inclusion in a Timer Group"""
    
    if request.method == "POST":
        timer_group_id = request.POST.get('timer_group')
        dummy_view = PADSTimerEditView(request, timer_id)
        dummy_view.prepare_context()
        if dummy_view.user_present():
            timer = dummy_view.get_timer()
            if timer:
                
                # Success
                if timer.add_to_group(timer_group_id):
                    set_banner(
                        request, messages['TIMER_SETTINGS_ADDED_TO_GROUP'], 
                        BANNER_INFO)
                    
                # Failure
                else:
                    set_banner(
                        request, messages['TIMER_SETTINGS_SAVE_ERROR'], 
                        BANNER_FAILURE_ERROR)

            # Timer not found or available
            else:
                set_banner(
                    request, messages['TIMER_NOT_FOUND'], 
                    BANNER_FAILURE_DENIAL)
                return HttpResponseRedirect(reverse('padsweb:index'))
        
        # Edit mode not enabled (current User id doesn't match)
        # creator User's id, or not signed in.
        else:
            set_banner(
                request, messages['TIMER_SETTINGS_WRONG_USER'], 
                BANNER_FAILURE_DENIAL)

    # Handle non-POST requests
    else:
        set_banner(
            request, messages['TIMER_SETTINGS_INVALID_REQUEST'],
             BANNER_FAILURE_DENIAL)
        return HttpResponseRedirect(reverse('padsweb:index'))

    # Return to the timer detail view by default
    return dummy_view.redirect_to_timer()

def timer_remove_from_group(request, timer_id):
    """Django view to request a Timer's exclusion from a Timer Group."""
    if request.method == "POST":
        dummy_view = PADSTimerEditView(request, timer_id)
        user_id = dummy_view.get_session_user_id()

        if dummy_view.edit_enabled():
            timer = dummy_view.get_timer()
            form_data = TimerGroupForm(
                request.POST,
                timer_group_choices=timer.get_associated_groups_for_choicefield())

            if form_data.is_valid():
                timer_group_id = form_data.cleaned_data['timer_group']

                if timer:
                    
                    # Success
                    if timer.remove_from_group(timer_group_id):
                        set_banner(
                            request, 
                            messages['TIMER_SETTINGS_REMOVED_FROM_GROUP'],
                            BANNER_INFO)

                    # Failure
                    else:
                        set_banner(
                            request, messages['TIMER_SETTINGS_SAVE_ERROR'], 
                            BANNER_FAILURE_ERROR)
                            
                # Timer not found or available
                else:
                    set_banner(
                        request, messages['TIMER_NOT_FOUND'], 
                        BANNER_FAILURE_DENIAL)
                    return HttpResponseRedirect(reverse('padsweb:index'))

            # Handle invalid form data
            else:
                set_banner(
                    request, messages['TIMER_SETTINGS_INVALID_REQUEST'],
                     BANNER_FAILURE_DENIAL)


        # Edit mode not enabled (current User id doesn't match)
        # creator User's id, or not signed in.
        else:
            set_banner(
                request, messages['TIMER_SETTINGS_WRONG_USER'], 
                BANNER_FAILURE_DENIAL)

    # Handle non-POST requests
    else:
        set_banner(
            request, messages['TIMER_SETTINGS_INVALID_REQUEST'],
             BANNER_FAILURE_DENIAL)
        return HttpResponseRedirect(reverse('padsweb:index'))

    # Return to the timer detail view by default
    return dummy_view.redirect_to_timer()


# TODO: Re-implement Timer delete to respond to the "DELETE" method
# instead. This will likely require the use of AJAX on the client side
# because HTML forms only submit requests using "POST" and "GET".
def timer_del(request, timer_id):
    """Django view to request a Timer's deletion"""
    
    if request.method == "POST":
        dummy_view = PADSTimerEditView(request, timer_id)
        dummy_view.prepare_context()
        
        if dummy_view.edit_enabled():
            timer = dummy_view.get_timer()
            
            if timer:
                # Success
                if timer.delete():
                    banner_text = messages['TIMER_DELETE_SUCCESS'].format(
                        timer.get_description())
                    set_banner(request, banner_text, BANNER_INFO)
                    return HttpResponseRedirect(reverse('padsweb:index_personal'))

                # Failure
                else:
                    set_banner(
                    request, messages['TIMER_DELETE_ERROR'],
                     BANNER_FAILURE_ERROR)

            # Timer not found or available
            else:
                set_banner(
                    request, messages['TIMER_NOT_FOUND'], 
                    BANNER_FAILURE_DENIAL)
                return HttpResponseRedirect(reverse('padsweb:index'))

        # Edit mode not enabled (current User id doesn't match)
        # creator User's id, or not signed in.
        else:
            set_banner(
                request, messages['TIMER_SETTINGS_WRONG_USER'], 
                BANNER_FAILURE_DENIAL)

    # Handle non-POST requests
    else:
        set_banner(
            request, messages['TIMER_SETTINGS_INVALID_REQUEST'],
             BANNER_FAILURE_DENIAL)

    return HttpResponseRedirect(reverse('padsweb:index'))

def timer_export(request, timer_id):
    # Prepare a view object to extract User info from session 
    timer_view = PADSTimerDetailView(request, timer_id)
    
    # GET Requests return the Timer's details in JSON
    if request.method == "GET":
        
        timer = timer_view.timer
        # Success
        if timer:
            timer_view = PADSTimerView(request, timer_id)
            response = HttpResponse(json.dumps(timer.dict()))
            response['content-type'] = 'application/json'
            return response
        
        # Failure
        else:
            set_banner(
                request, messages['TIMER_NOT_FOUND'],
                 BANNER_FAILURE_DENIAL)
            return HttpResponseRedirect(reverse('padsweb:index'))

    # Non-GET Requests redirect to the index
    else:
        set_banner(
            request, messages['TIMER_SETTINGS_INVALID_REQUEST'], 
            BANNER_FAILURE_DENIAL)
        return HttpResponseRedirect(reverse('padsweb:index'))
    
def timer_reset(request, timer_id):
    if request.method == "POST":
        dummy_view = PADSTimerEditView(request, timer_id)
        dummy_view.prepare_context()
        if dummy_view.edit_enabled():
            timer = dummy_view.get_timer()

            if timer:
                form_data = ReasonForm(request.POST)

                if form_data.is_valid():
                    reason = form_data.cleaned_data['reason']

                    # Success
                    if timer.reset(reason):
                        banner_text = messages['TIMER_SETTINGS_TIMER_RESET'].format(
                            timer.get_description_short())
                        set_banner(request, banner_text, BANNER_INFO)
                        return dummy_view.redirect_to_timer()

                    # Failure
                    else:
                        set_banner(
                            request, messages['TIMER_SETTINGS_SAVE_ERROR'],
                             BANNER_FAILURE_ERROR)

                # Handle invalid form data
                else:
                    set_banner(
                        request, messages['TIMER_SETTINGS_INVALID_REQUEST'],
                         BANNER_FAILURE_DENIAL)
                    
            # Timer not found or available
            else:
                set_banner(
                    request, messages['TIMER_NOT_FOUND'], 
                    BANNER_FAILURE_DENIAL)
                return HttpResponseRedirect(reverse('padsweb:index'))

        # Edit mode not enabled (current User id doesn't match)
        # creator User's id, or not signed in.
        else:
            set_banner(
                request, messages['TIMER_SETTINGS_WRONG_USER'], 
                BANNER_FAILURE_DENIAL)
    
    # Handle non-POST requests
    else:
        set_banner(
            request, messages['TIMER_SETTINGS_INVALID_REQUEST'],
             BANNER_FAILURE_DENIAL)
    
    # Redirect to index by default
    return dummy_view.redirect_to_index()

def timer_share(request, timer_id):
    """Django view to make a Timer public"""
    
    if request.method == "POST":
        dummy_view = PADSTimerEditView(request, timer_id)
        dummy_view.prepare_context()
        
        if dummy_view.edit_enabled():
            timer = dummy_view.get_timer()
        
            if timer:
                
                if timer.set_public():
                    banner_text = messages['TIMER_SETTINGS_TIMER_SHARED'].format(
                        timer.get_description_short())
                    set_banner(request, banner_text, BANNER_SUCCESS)
                
                # Failure
                else:
                    set_banner(
                        request, messages['TIMER_SETTINGS_SAVE_ERROR'],
                         BANNER_FAILURE_ERROR)

            # Timer not found or available
            else:
                set_banner(
                    request, messages['TIMER_NOT_FOUND'], 
                    BANNER_FAILURE_DENIAL)
                return HttpResponseRedirect(reverse('padsweb:index'))

        # Edit mode not enabled (current User id doesn't match)
        # creator User's id, or not signed in.
        else:
            set_banner(
                request, messages['TIMER_SETTINGS_WRONG_USER'], 
                BANNER_FAILURE_DENIAL)

    # Handle non-POST requests
    else:
        set_banner(
            request, messages['TIMER_SETTINGS_INVALID_REQUEST'],
             BANNER_FAILURE_DENIAL)

    # Redirect to index by default
    return dummy_view.redirect_to_index()


def timer_stop(request, timer_id):
    """Django view to initiate a Timer stop request"""
    
    if request.method == "POST":
        form_data = ReasonForm(request.POST)
        
        if form_data.is_valid():
            dummy_view = PADSTimerEditView(request, timer_id)
            dummy_view.prepare_context()
            
            if dummy_view.edit_enabled():
                timer = dummy_view.get_timer()
                
                if timer:
                    reason = form_data.cleaned_data['reason']
                    
                    # Success
                    if timer.stop(reason):
                        
                        if timer.is_historical():
                            banner_text = messages['TIMER_SETTINGS_HISTORICAL_TIMER_STOPPED'].format(
                                timer.get_description_short())
                            
                        else:
                            banner_text = messages['TIMER_SETTINGS_TIMER_SUSPENDED'].format(
                                timer.get_description_short())
                        
                        set_banner(request, banner_text, BANNER_SUCCESS)

                    # Failure
                    else:
                        set_banner(
                            request, messages['TIMER_SETTINGS_SAVE_ERROR'],
                             BANNER_FAILURE_ERROR)
                
                # Timer not found or not available
                else:
                    set_banner(
                        request, messages['TIMER_NOT_AVAILABLE'], 
                        BANNER_FAILURE_DENIAL)            
            
            # Edit mode not enabled (current User id doesn't match)
            # creator User'd id, or not signed in.
            else:
                set_banner(
                    request, messages['TIMER_SETTINGS_WRONG_USER'], 
                    BANNER_FAILURE_DENIAL)
        
        # Handle invalid form input
        else:
            set_banner(
                request, messages['TIMER_SETTINGS_INVALID_REQUEST'], 
                BANNER_FAILURE_DENIAL)
    
    # Handle Non-POST requests
    else:
        set_banner(
            request, messages['TIMER_SETTINGS_INVALID_REQUEST'], 
            BANNER_FAILURE_DENIAL)
    
    # Redirect to index by default if nothing happens by now
    return dummy_view.redirect_to_index()

def timer_unshare(request, timer_id):
    """Django view to make a Timer private."""
    
    # POST requests initiate request to make Timer private.
    if request.method == "POST":
        dummy_view = PADSTimerEditView(request, timer_id)
        dummy_view.prepare_context()
        
        if dummy_view.edit_enabled():
            timer = dummy_view.get_timer()
        
            if timer:                
                # Success
                if timer.set_private():
                    banner_text = messages['TIMER_SETTINGS_TIMER_UNSHARED'].format(
                        timer.get_description_short())
                    set_banner(request, banner_text, BANNER_SUCCESS)
                
                # Failure
                else:
                    set_banner(
                        request, messages['TIMER_SETTINGS_SAVE_ERROR'],
                         BANNER_FAILURE_ERROR)
                         
            # Timer not found or not available
            else:
                set_banner(
                    request, messages['TIMER_NOT_AVAILABLE'], 
                    BANNER_FAILURE_DENIAL)            
        
        # Edit mode not enabled (current User id doesn't match)
        # creator User'd id, or not signed in.
        else:
            set_banner(
                request, messages['TIMER_SETTINGS_WRONG_USER'], 
                BANNER_FAILURE_DENIAL)

    # Non-POST requests redirect to the index.
    else:
        set_banner(
            request, messages['TIMER_SETTINGS_INVALID_REQUEST'], 
            BANNER_FAILURE_DENIAL)
    return dummy_view.redirect_to_index()

def timer_rename(request, timer_id):
    """Django view to request a change to a Timer's description.
    Remember that changing a Timer's description also resets it.
    """
    if request.method == "POST":
        dummy_view = PADSTimerEditView(request, timer_id)
        dummy_view.prepare_context()
        
        if dummy_view.edit_enabled():
            timer = dummy_view.get_timer()
            form_data = TimerRenameForm(request.POST)
            
            if form_data.is_valid():
                if timer:
                    new_description = form_data.cleaned_data['description']
                    # Success
                    if timer.set_description(new_description):
                        banner_text = messages['TIMER_SETTINGS_DESC_CHANGED'].format(
                            new_description)
                        set_banner(request, banner_text, BANNER_SUCCESS)
                    
                    # Failure
                    else:
                        set_banner(
                            request, messages['TIMER_SETTINGS_SAVE_ERROR'],
                             BANNER_FAILURE_ERROR)            

                # Timer not found or available        
                else:
                    set_banner(
                        request, messages['TIMER_NOT_AVAILABLE'], 
                        BANNER_FAILURE_DENIAL)            

            # Handle invalid form input
            else:
                set_banner(
                    request, messages['TIMER_SETTINGS_INVALID_REQUEST'], 
                    BANNER_FAILURE_DENIAL)
                        
        # Edit mode not enabled (current User id doesn't match)
        # creator User's id, or not signed in.
        else:
            set_banner(
                request, messages['TIMER_SETTINGS_WRONG_USER'], 
                BANNER_FAILURE_DENIAL)
                
    # Non-POST requests redirect to the index
    else:
        set_banner(
            request, messages['TIMER_SETTINGS_INVALID_REQUEST'], 
            BANNER_FAILURE_DENIAL)
    return dummy_view.redirect_to_index()

def user_new(request):
    """Django View to sign up a User.
    """
    # POST requests initiate a sign-up
    if request.method == "POST":
        form_data = SignUpForm(request.POST)
        
        if form_data.is_valid():
            # Read Form Data
            username = form_data.cleaned_data['username']
            password = form_data.cleaned_data['password']
            password_confirm = form_data.cleaned_data['password_confirm']
            
            # Prevent users from using usernames that may cause PADS
            # to mistake them for Quick List Users
            if username.startswith(ANONYMOUS_USER_SHORT_NICKNAME_PREFIX):
                banner_text = '{0}: {1}'.format(
                    username, messages['USER_NAME_NOT_ALLOWED'])
                set_banner(request, banner_text, BANNER_FAILURE_DENIAL)
                return HttpResponseRedirect(
                    reverse('padsweb:sign_up_intro'))
            
            # Inform users if their username is taken or otherwise
            # not available
            if user_helper.get_user_by_nickname_short(username) != None:
                banner_text = '{0}: {1}'.format(
                    username, messages['USER_SIGN_UP_NAME_NOT_AVAILABLE'])
                set_banner(request, banner_text, BANNER_FAILURE_DENIAL)
                return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))

            # Inform users if password confirmation fails
            if(password != password_confirm):
                set_banner(
                    request, messages['USER_PASSWORD_CONFIRM_FAILED'], 
                    BANNER_FAILURE_DENIAL)
                return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))

            # Continue with an apparently valid registration
            if(password == password_confirm):
                new_user_id = user_helper.put_user_in_db(
                    username, password)
                    
                # Success
                if new_user_id:
                    set_banner(
                        request, messages['USER_SIGN_UP_SUCCESS'], 
                        BANNER_SUCCESS)
                    return HttpResponseRedirect(
                        reverse('padsweb:sign_up_intro'))
                    
                # Failure
                else:
                    set_banner(
                        request, messages['USER_SIGN_UP_DB_ERROR'], 
                        BANNER_FAILURE_ERROR)
                    return HttpResponseRedirect(
                        reverse('padsweb:sign_up_intro'))

        # Handle invalid form data: reload the sign up screen
        else:
            set_banner(
                request, messages['USER_NAME_INVALID_CHARACTERS'], 
                BANNER_FAILURE_DENIAL)
            return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))
    
    # Non-POST requests redirect to the sign-up screen
    else:
        return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))

def user_export_all(request):
    """Django View to export User Settings and all Timers created to JSON
    """
    # Prepare a view object to extract User info from session 
    #  PADSTimerView used because it has a built-in PADSTimerHelper
    settings_view = PADSTimerView(request, dict())

    if settings_view.user_present():
        user = settings_view.get_session_user()
        timer_helper = settings_view.timer_helper
        
        # Get Timers by User
        timers_export = []
        timers = timer_helper.get_timers_for_view_all().get_timers_all()
        for t in timers:
            timers_export.append(t.dict())
        
        # Get Timer Groups by User
        group_names = []
        groups = timer_helper.get_timer_groups_for_view_all()
        for g in groups:
            group_names.append(g.get_title())
        
        # Prepare user info
        user_info = user.dict()
        user_info['timers'] = timers_export
        user_info['groups'] = group_names
        
        # Render the Template
        response = HttpResponse(json.dumps(user_info))
        response['content-type'] = 'application/json'
        return response
    
    # Reject users who have not signed in
    else:
        set_banner(
            request, messages['USER_SIGN_IN_REQUIRED'], 
            BANNER_FAILURE_DENIAL)
        return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))


def settings_info(request):
    """Django View to display User Setup Screen
    """
    # Prepare a view object to extract User info from session 
    #  PADSTimerView used because it has a built-in PADSTimerHelper
    settings_view = PADSTimerView(request, dict())
    
    # Setup the Setup page for Users
    if settings_view.user_present():
        user = settings_view.get_session_user()
        timer_helper = settings_view.timer_helper
        
        # Prepare Delete Timer Group Form
        delete_timer_group_form = TimerGroupForm(
            timer_group_choices=timer_helper.get_timer_groups_for_choicefield_all())
        settings_view.add_context_item(
            'delete_timer_group_form', delete_timer_group_form)

        # Prepare New Timer Group Form
        settings_view.add_context_item(
            'new_timer_group_form', NewTimerGroupForm())
        
        # Prepare Time Zone Form
        initial_tz = {'time_zone':user.get_timezone()}
        settings_view.add_context_item(
            "time_zone_form", TimeZoneForm(initial=initial_tz))
        
        # Prepare Password Change forms
        initial_pwc = {'user_id':user.id()}
        settings_view.add_context_item(
            'password_change_form', PasswordChangeForm(initial=initial_pwc))
                
        # Prepare QL Import form
        #  Get a list of the User's Timer Groups with an option to select
        #  none of them.
        timer_group_choices = timer_helper.get_timer_groups_for_choicefield_all()
        #  Populate QL import form choice field
        form_ql_import = QuickListImportForm(
            timer_group_choices=timer_group_choices)
        settings_view.add_context_item(
            'quick_list_import_form', form_ql_import)
            
        # Prepare all other info
        settings_view.add_context_item(
            "timer_groups", timer_helper.get_timer_groups_for_view_all())
        settings_view.add_context_item("user", user)
        settings_view.add_context_item("user_id",user.id())
        settings_view.add_context_item(
            "user_nickname_short", user.username())
        
        # Render the Template
        return settings_view.render_template("padsweb/user_settings.html")
    
    # Reject users who have not signed in
    else:
        set_banner(
            request, messages['USER_SIGN_IN_REQUIRED'], 
            BANNER_FAILURE_DENIAL)
        return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))

def settings_import_ql(request):
    """Django view to initiate a request to import a Quick List's timers
    and delete the QL afterwards.
    """
    # POST requests initiate Quick List import process
    if request.method == "POST":
        dummy_view = PADSView(request, dict())
        dummy_view.prepare_context()    
    
        if dummy_view.user_present():
            timer_helper = PADSTimerHelper(dummy_view.get_session_user_id())
            timer_group_choices = timer_helper.get_timer_groups_for_choicefield_all()
            form_data = QuickListImportForm(
                request.POST, timer_group_choices=timer_group_choices)

            if form_data.is_valid():
                quick_list_password = form_data.cleaned_data['password']
                default_group_id = form_data.cleaned_data['timer_group']
                current_user = dummy_view.get_session_user()
                
                # Success
                if current_user.import_quick_list(
                    quick_list_password, 
                    default_group_id=default_group_id):
                    
                    set_banner(
                        request, messages['USER_SETTINGS_QL_IMPORT_SUCCESS'], 
                        BANNER_SUCCESS)
                    return HttpResponseRedirect(
                        reverse('padsweb:index_personal'))

                # Failure:
                else:
                    set_banner(
                        request, messages['USER_SETTINGS_QL_IMPORT_FAILURE'],
                        BANNER_FAILURE_DENIAL)
                    return HttpResponseRedirect(
                        reverse('padsweb:settings_info'))

            # Invalid Form data
            else:
                set_banner(
                    request, messages['USER_SETTINGS_INVALID_REQUEST'], 
                    BANNER_FAILURE_DENIAL)
                return HttpResponseRedirect(reverse('padsweb:settings_info'))
        
        # Failure: user not signed in, redirect to sign in screen
        else:
            set_banner(
                request, messages['USER_SIGN_IN_REQUIRED'],
                BANNER_FAILURE_DENIAL)
            return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))            
    
    # Non-POST requests redirect to the index screen
    else:
        return HttpResponseRedirect(reverse('padsweb:index'))

def settings_new_timer_group(request):
    """Django View to create a new Timer Group
    """
    # Prepare a dummy view to extract User info from session 
    dummy_view = PADSView(request, dict())

    # No need to prepare context, as we are not rendering a template.
    # Contexts are only needed for templates!
    
    # Process request for signed in Users
    if dummy_view.user_present():
        user = dummy_view.get_session_user()

        # Block Quick List Users from creating Timer Groups
        # As of Version 0.5x, Timer Groups are only supported for
        # regular accounts.
        if user.is_anonymous():
            set_banner(
                request, messages['USER_SETTINGS_QL_NOT_SUPPORTED'], 
                BANNER_FAILURE_DENIAL)            
            return HttpResponseRedirect(reverse('padsweb:index_personal'))
        
        # POST Requests create Timer Groups
        elif request.method == "POST":
            form_data = NewTimerGroupForm(request.POST)
            if form_data.is_valid():
                timer_group_name = form_data.cleaned_data['name']
                editing_timer_helper = PADSEditingTimerHelper(user.id())
    
                # Attempt to create the new Timer Group
                new_timer_group_id = editing_timer_helper.new_timer_group(
                    timer_group_name)
                    
                if new_timer_group_id:
                    # Success
                    banner_text = messages['USER_SETTINGS_NEW_TIMER_GROUP_SUCCESS'].format(
                        timer_group_name)
                    set_banner(request, banner_text, BANNER_SUCCESS)
                    set_last_new_item_id(request, new_timer_group_id)
                    
                else:
                    # Failure
                    set_banner(
                        request, messages['USER_SETTINGS_NEW_TIMER_GROUP_FAILURE'],
                        BANNER_FAILURE_ERROR)

                # Return to the settings screen, success or failure.
                return HttpResponseRedirect(
                    reverse('padsweb:settings_info'))
            
            # Handle invalid form data
            else:
                set_banner(
                    request, messages['USER_SETTINGS_INVALID_REQUEST'],
                    BANNER_FAILURE_ERROR)
                return HttpResponseRedirect(
                    reverse('padsweb:settings_info'))
                

        # Non-POST Requests send users to the settings screen
        else:
            set_banner(
                request, messages['USER_SIGN_IN_REQUIRED'], 
                BANNER_FAILURE_DENIAL)
            return HttpResponseRedirect(reverse('padsweb:settings_info'))

    # Reject requests by non-signed in Users
    else:
        set_banner(request, "You must sign in before adding or removing groups.", BANNER_FAILURE_DENIAL)
        return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))

def settings_delete_timer_group(request):
    """Django View to delete Timer Groups
    """    
    # Prepare a dummy view to extract User info from session 
    dummy_view = PADSView(request, dict())

    # No need to prepare context, as we are not rendering a template.
    #  Contexts are only for templates!

    # Quick List Users are not blocked from deleting their Timer Groups,
    #  just in case they somehow manage to create them!
    
    if dummy_view.user_present():
        user = dummy_view.get_session_user()
    
        # POST requests initiate requests to delete Timer Groups
        if request.method == "POST":

            # Get User and Timer Group info
            timer_helper = PADSEditingTimerHelper(user.id())
            form_data = TimerGroupForm(
                request.POST,
                timer_group_choices=timer_helper.get_timer_groups_for_choicefield_all())
            
            if form_data.is_valid():
                timer_group_id = form_data.cleaned_data['timer_group']
                timer_group = timer_helper.get_timer_group_for_view_by_id(
                    timer_group_id)

                if timer_helper.delete_timer_group_by_id(
                    timer_group_id):
                    
                    # Success
                    banner_text = messages['USER_SETTINGS_DELETE_TIMER_GROUP_SUCCESS'].format(
                         timer_group.get_title())
                    set_banner(request, banner_text, BANNER_SUCCESS)
                    
                else:
                    # Failure
                    set_banner(
                        request, messages['USER_SETTINGS_SAVE_ERROR'], 
                        BANNER_FAILURE_ERROR)
                return HttpResponseRedirect(reverse('padsweb:settings_info'))

            # Failure: Form data is not valid
            else:
                set_banner(
                    request, messages['USER_SETTINGS_INVALID_REQUEST'], 
                    BANNER_FAILURE_DENIAL)
                return HttpResponseRedirect(reverse('padsweb:settings_info'))
                        
        # Non-POST Requests send users to the settings screen
        else:
            set_banner(
                request, messages['USER_SIGN_IN_REQUIRED'], 
                BANNER_FAILURE_DENIAL)
            return HttpResponseRedirect(reverse('padsweb:settings_info'))            

    # Reject requests by non-signed in Users
    else:
        set_banner(
            request, messages['USER_SIGN_IN_REQUIRED'], 
            BANNER_FAILURE_DENIAL)
    return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))

def settings_set_password(request):
    """Django View to change a User's Password
    """
    # POST requests initiate password change
    if request.method == "POST":
        form_data = PasswordChangeForm(request.POST)
        if form_data.is_valid():
            password_old = form_data.cleaned_data["old_password"]
            password_new = form_data.cleaned_data["new_password"]
            password_new_confirm = form_data.cleaned_data["new_password_confirm"]
            user_id = form_data.cleaned_data["user_id"]
            user = user_helper.get_user_for_view_by_id(user_id)
            
            if user.check_password(password_old):

                if password_new == password_new_confirm:
                    user.set_password(password_old, password_new)
                    
                    # Success
                    if user.check_password(password_new):
                        set_banner(
                            request,
                            messages['USER_SETTINGS_PASSWORD_CHANGED'], 
                            BANNER_SUCCESS)
                    
                    # Failure: Password change not verified
                    else:
                        set_banner(
                            request, messages['USER_SETTINGS_SAVE_ERROR'], 
                            BANNER_FAILURE_ERROR)
                
                # Failure: New password confirmation failed
                else:
                    set_banner(
                        request, messages['USER_PASSWORD_CONFIRM_FAILED'],
                        BANNER_FAILURE_DENIAL)
        
            # Failure: Old password is not correct
            else:
                set_banner(
                    request, messages['USER_SIGN_IN_WRONG_PASSWORD'], 
                    BANNER_FAILURE_DENIAL)
        
        # Failure: Form data is not valid
        else:
            set_banner(
                request, messages['USER_SETTINGS_INVALID_REQUEST'], 
                BANNER_FAILURE_DENIAL)

        # Reload settings screen after password change request, regardless
        # of success or failure
        return HttpResponseRedirect(reverse('padsweb:settings_info'))
                
    # Non-POST requests redirect to the index view
    else:
        return HttpResponseRedirect(reverse('padsweb:index'))

def settings_set_tz(request):
    """Django View to request a Time Zone Change
    """
    dummy_view = PADSView(request)
    if dummy_view.user_present():
        
        # POST requests initiate Time Zone Change
        if request.method == "POST":
            form_data = TimeZoneForm(request.POST)
            if form_data.is_valid():
                timezone_name = form_data.cleaned_data['time_zone']
                user = dummy_view.get_session_user()
                if user.set_timezone(timezone_name):
                    banner_text = messages['USER_SETTINGS_TIME_ZONE_CHANGED'].format(
                        timezone_name)
                    set_banner(request, banner_text, BANNER_SUCCESS)
                    return HttpResponseRedirect(
                        reverse('padsweb:settings_info'))
                else:
                    set_banner(
                        request, message['USER_SETTINGS_SAVE_ERROR'],
                        BANNER_FAILURE_ERROR)
                    return HttpResponseRedirect(
                        reverse('padsweb:settings_info'))
            else:
                set_banner(
                    request, message['USER_SETTINGS_INVALID_REQUEST'], 
                    BANNER_FAILURE_DENIAL)
                return HttpResponseRedirect(reverse('padsweb:settings_info'))
        
        # Non-POST requests redirect to the setup screen
        else:
            set_banner(
                request, messages['USER_SETTINGS_REDIRECT'],
                BANNER_FAILURE_DENIAL)
            return HttpResponseRedirect(reverse('padsweb:settings_info'))
            
    else:
        return HttpResponseRedirect(reverse('padsweb:sign_up_intro'))
    return HttpResponseRedirect(reverse('padsweb:index'))

def sign_up_sign_in_intro(request):
    """Django View to open the Sign Up/Sign In screen
    """
    # Use a view to sense the presence of a signed-in User
    dummy_view = PADSView(request, dict())
    
    # User is signed in: redirect to settings page
    if dummy_view.user_present():
        return HttpResponseRedirect(reverse('padsweb:settings_info'))

    # User not signed in: render sign in page
    else:
        dummy_view.add_context_item('sign_in_form', SignInForm())
        dummy_view.add_context_item(
            'sign_in_quicklist_form', SignInQuickListForm())
        dummy_view.add_context_item('sign_up_form', SignUpForm())
        return dummy_view.render_template("padsweb/sign_up.html")
        
def set_banner(request, text, banner_type=BANNER_INFO):
    """Inserts Banner Text and Type into a session.
    """
    request.session["banner_text"] = text
    request.session["banner_type"] = banner_type

def set_last_new_item_id(request, item_id):
    """Inserts the last_new_item_id session variable. This is intended 
    to keep track of id of the last item created.
    """
    request.session['last_new_item_id'] = item_id

def set_user_id(request, user_id):
    """ Inserts a User's id into the session, effectively signing in the
    User.
    """
    request.session['user_id'] = user_id

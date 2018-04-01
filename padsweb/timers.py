#
#
# Public Archive of Days Since Timers
# Timer-related View Helper Classes and Functions
#
#

#
# Imports
#
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone
from padsweb.models import GroupInclusion
from padsweb.models import PADSTimer
from padsweb.models import PADSTimerGroup
from padsweb.models import PADSTimerReset 
from padsweb.misc import *
from padsweb.settings import *
from padsweb.strings import labels

# Standard Library Imports
import datetime
import secrets # for token_urlsafe()

#
# Constants
#

# Constant Objects
pads_timer_default_models = {
    "timer_model" : PADSTimer,
    "group_model" : PADSTimerGroup,
    "group_inclusion_model" : GroupInclusion,
    "reset_history_model" : PADSTimerReset,
    }

#
# Timer Classes
#

class PADSTimerHelper:
    """The PADSTimerHelper is a Helper class to load Timers and 
    Timer Groups from the database. For creating and editing Timers and 
    their Groups, please use the PADSEditingTimerHelper instead.
    
    Timers and Timer Groups loaded by this Helper are returned in 
    PADSViewTimer and PADSViewTimerGroup objects, which wrap around their 
    corresponding Django Models to provide additional methods intended for 
    easier access by Views.
    
    This Helper can be restricted to load only timers owned by a specific 
    User by specifying a User's id when instantiating it. The use of 
    non-restricted Helpers for purporses other than testing is discouraged.
    """
    
    #
    # QuerySet Preparation Methods
    #
    def get_timers_from_db(self):
        if self.user_id != INVALID_SESSION_ID:
            return self.timer_model.objects.filter(
                creator_user_id=self.user_id).order_by('-count_from_date_time')
        else:
            return self.timer_model.objects.all()
    
    def get_timer_groups_from_db(self):
        if self.user_id != INVALID_SESSION_ID:
            return self.group_model.objects.filter(
                creator_user_id=self.user_id)
        else:
            return self.group_model.objects.all()
    
    def get_timer_group_inclusions_from_db(self):
        return self.group_inclusion_model.objects.all()
    
    def get_timer_resets_from_db(self):
        if self.user_id != INVALID_SESSION_ID:
            return self.reset_history_model.objects.filter(
                creator_user_id=self.user_id)
        else:
            return self.reset_history_model.objects.all()
    
    #
    # Timer Methods
    #
    def get_timers_for_view_all(self):
        """Returns a PADSSpecialViewTimerGroup containing all timers
        accessible by this Helper.
        """
        view_timers = self.get_timers_from_db()
        return PADSSpecialViewTimerGroup(view_timers)

    def get_timer_for_view_by_id(self, timer_id):
        """Returns a PADSViewTimer of a single Timer by its id.
        Only Timers accessible by this Helper may be returned.
        """
        if self.get_timers_from_db().filter(pk=timer_id).exists():
            timer_from_db = self.get_timers_from_db().get(pk=timer_id)
            return self.prepare_view_timer(timer_from_db)
        else:
            return None

    def get_timer_for_view_by_permalink_code(self, link_code):
        """Returns a PADSViewTimer of a single Timer by its id.
        Only Timers accessible by this Helper may be returned.
        """
        if self.get_timers_from_db().filter(permalink_code=link_code).exists():
            timer_from_db = self.get_timers_from_db().get(
                    permalink_code=link_code)
            return self.prepare_view_timer(timer_from_db)
        else:
            return None


    #
    # Timer Group Methods
    #
    def get_timer_group_for_view_by_id(self, timer_group_id):
        if self.get_timer_groups_from_db().filter(pk=timer_group_id).exists():
            group_from_db = self.get_timer_groups_from_db().get(
                pk=timer_group_id)
            return PADSViewTimerGroup(group_from_db, self)
        else:
            return None
    
    def get_timer_group_for_view_by_name(self, group_name):
        if self.get_timer_groups_from_db().filter(name=group_name).exists():
            group_from_db = self.get_timer_groups_from_db().get(
                    name=group_name)
            return PADSViewTimerGroup(group_from_db, self)
        else:
            return None
    
    def get_timer_groups_for_view_all(self):
        timer_groups_from_db = self.get_timer_groups_from_db()
        view_timer_groups = self.prepare_view_timer_group_list(
            timer_groups_from_db)
        return view_timer_groups

    def get_timer_groups_for_choicefield_all(self):
        timer_groups_from_db = self.get_timer_groups_from_db()
        timer_choices = []
        for tg in timer_groups_from_db:
            i = (tg.id, tg.name)
            timer_choices.append(i)
        return timer_choices

    def get_timer_groups_for_view_by_name(self, search_term):
        timer_groups_from_db = self.get_timer_groups_from_db().filter(
            name__icontains=search_term)
        return self.prepare_view_timer_group_list(timer_groups_from_db)

    def get_timer_groups_for_view_by_name_prefix(self, search_term):
        timer_groups_from_db = self.get_timer_groups_from_db().filter(
            name__istartswith=search_term)
        return self.prepare_view_timer_group_list(timer_groups_from_db)
    
    #
    # View Object Preparation Methods
    #
    def prepare_view_timer_group_list(self, timer_groups_from_db):
        view_timer_groups = []
        for tg in timer_groups_from_db:
            view_timer_groups.append(PADSViewTimerGroup(tg, self))
        return view_timer_groups
    
    def prepare_view_timer(self, timer_from_db):
        if timer_from_db.historical==True:
            return PADSViewHistoricalTimer(timer_from_db, self)
        if timer_from_db.running==False:
            return PADSViewSuspendedTimer(timer_from_db, self)
        else:
            return PADSViewRegularTimer(timer_from_db, self)
        return None
        
    #
    # Special Methods
    #
    def __init__(self, user_id=None, **kwargs):
                
        # Set Models
        self.timer_model = kwargs.get(
            'timer_model', pads_timer_default_models.get('timer_model'))
        self.group_model = kwargs.get(
            'group_model', pads_timer_default_models.get('group_model'))
        self.group_inclusion_model = kwargs.get(
            'group_inclusion_model',
            pads_timer_default_models.get('group_inclusion_model'))
        self.reset_history_model = kwargs.get(
            'reset_history_model', 
            pads_timer_default_models.get('reset_history_model'))
        
        if user_id:
            self.user_id = user_id
        else:
            self.user_id = INVALID_SESSION_ID
        
    def __repr__(self):
        return self.__str__()
        
    def __str__(self):
        if self.user_id != INVALID_SESSION_ID:
            return "PADS Timer Helper (restricted to User Id {0})".format(self.user_id)
        else:
            return "PADS Timer Helper (unrestricted)"

class PADSEditingTimerHelper(PADSTimerHelper):
    """Helper class to make changes to Timers and Timer Groups.
    Timer Helpers must be restricted to a specific user. This is done by
     specifying a user id when instantiating it.
    """
    
    #
    # QuerySet Preparation Methods
    #
    def get_timers_from_db(self):
        if self.user_id != INVALID_SESSION_ID:
            return super().get_timers_from_db()
        else:
            return None

    def get_timer_groups_from_db(self):
        if self.user_id != INVALID_SESSION_ID:
            return super().get_timer_groups_from_db()
        else:
            return None

    #
    # Timer Manipulation Methods
    #
    def delete_timer_by_id(self, timer_id):
        timer = self.get_timers_from_db().get(pk=timer_id)
        return (timer.delete()[0] > 0)
        
    def set_timer_description(self, timer_id, description):
        timer_from_db = self.get_timers_from_db().get(
            creator_user_id=self.user_id, pk=timer_id)
        timer_from_db.description = description
        timer_from_db.save()
    
    def set_timer_public_flag(self, timer_id, flag):
        timer_from_db = self.get_timers_from_db().get(
            creator_user_id=self.user_id, pk=timer_id)
        timer_from_db.public = flag
        timer_from_db.save()
    
    def set_timer_running_flag(self, timer_id, flag):
        timer_from_db = self.get_timers_from_db().get(
            creator_user_id=self.user_id, pk=timer_id)
        timer_from_db.running = flag
        timer_from_db.save()
        
    def new_timer_reset_history(self, timer_id, reason, 
        date_time=timezone.now()):
        reset_history_item = PADSTimerReset()
        reset_history_item.reason = reason
        reset_history_item.date_time = date_time
        reset_history_item.timer_id = timer_id
        reset_history_item.save()

    def new_timer(self, description, 
        first_history_message=labels['TIMER_DEFAULT_CREATION_REASON'],
        date_time=None, public=False, historical=False):
            
        with transaction.atomic():
            # Capture the current date time first, to avoid falsely
            #  marking timers as back-dated.
            # TODO: Write up and explanation.
            request_date_time = timezone.now()
            # Prevent creation of timers that start in the future
            if date_time:
                if date_time > request_date_time:
                    date_time = request_date_time
            else:
                date_time = request_date_time
            new_timer = PADSTimer()
            new_timer.description = description
            new_timer.creation_date_time = request_date_time
            new_timer.count_from_date_time = date_time
            new_timer.creator_user_id = self.user_id
            new_timer.public = public
            new_timer.historical = historical
            new_timer.running = True
            new_timer.permalink_code = secrets.token_urlsafe(
                    TIMERS_PERMALINK_CODE_LENGTH)
            new_timer.save()        
            
            # Create a history entry to mark timer creation
            self.new_timer_reset_history(
                new_timer.id, first_history_message, request_date_time) 
            
            # Return Timer id
            return new_timer.id
    
    #
    # Timer Group Methods
    #    
    def delete_timer_group_by_id(self, group_id):
        try:
            timer_group = self.group_model.objects.get(
                creator_user_id=self.user_id, pk=group_id)
            deleted_items = timer_group.delete()[0]
            return (deleted_items > 0)
        except:
            pass
        return False

    def new_timer_group(self, name):
        if name:
            # Timer group names are strictly single-line
            name = name.rstrip(SINGLE_LINE_RSTRIP_CHARS)
            if str_is_empty_or_space(name) == False:
                new_timer_group = PADSTimerGroup()
                new_timer_group.creator_user_id = self.user_id
                # Timer group names are all-lowercase
                new_timer_group.name = name.lower()
            try:
                new_timer_group.save()
                return new_timer_group.id
            except IntegrityError:
                pass
        return None
        
    #
    # Group Inclusion Methods                    
    #
    def new_group_inclusion_by_id(self, timer_id, group_id):
        new_inclusion = GroupInclusion()
        new_inclusion.timer_id = timer_id
        new_inclusion.group_id = group_id
        try:
            new_inclusion.save()
            return True
        except IntegrityError:
            return False

    def delete_group_inclusion_by_id(self, timer_id, group_id):
        inclusion = self.get_timer_group_inclusions_from_db().get(
            timer_id=timer_id, group_id=group_id)
        return (inclusion.delete()[0] > 0)
    
    def __init__(self, user_id, **kwargs):
        super().__init__(user_id, **kwargs)
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        if self.user_id != INVALID_SESSION_ID:
            return "PADS Editing Timer Helper (restricted to User Id {0})".format(self.user_id)
        else:
            return "PADS Editing Timer Helper (unrestricted and invalid!)"

        
class PADSPublicTimerHelper(PADSTimerHelper):
    """Helper class to load Timers and Timer Groups.
    Public Timer Helpers are restricted to loading Timer items that
     have been marked as public.
    This is a safety measure to prevent accidental loading of private
     timers in the event of a typo.
    """

    #
    # QuerySet Preparation Methods
    #
    def get_timers_from_db(self):
        if self.user_id != INVALID_SESSION_ID:
            timers = self.timer_model.objects.filter(
                public=True, creator_user_id=self.user_id).order_by(
                    '-count_from_date_time')
        else:
            timers = self.timer_model.objects.filter(public=True)            
        return timers

    def __str__(self):
        if self.user_id != INVALID_SESSION_ID:
            return "PADS Public Timer Helper (restricted to User Id {0})".format(self.user_id)
        else:
            return "PADS Public Timer Helper (not restricted to any user)"

    
class PADSViewTimer:
    """View-friendly representation of the PADSTimer Class"""
    
    # Class attributes
    DESCRIPTION_LENGTH_SHORT = 32
    UNITS = ("min","h")
    UNIT_LIMITS = (60,24) # 60 minutes, 24 hours
    OVERFLOW_UNIT = "days"
    
    def count_from_date_time(self):
        return self.timer_from_db.count_from_date_time
    
    def creator_user_id(self):
        return self.timer_from_db.creator_user_id
        
    def creator_user_nickname_short(self):
        if self.is_in_quick_list():
            return ANONYMOUS_USER_SHORT_NICKNAME_PREFIX
        else:
            return self.timer_from_db.creator_user.nickname_short
        
    def creation_date_time(self):
        return self.timer_from_db.creation_date_time

    def get_running_time_minutes(self):
        if self.is_running():
            # Running timers: run time is time since the Count From
            #  Date Time, which must be the same as the 
            #  time of last reset.
            running_time = timezone.now() - self.count_from_date_time()
        else:
            # Suspended timers: run time is the time between the last
            #  reset, and the reset immediately before it.
            start_time = self.reset_history()[1].date_time
            end_time = self.reset_history()[0].date_time
            running_time = end_time - start_time
        return (running_time.total_seconds()/60)
    
    def get_running_time_string(self):
        if int(self.get_running_time_minutes()) > 0:
            return self.get_measures().get_string(zeroes=False)
        else:
            return labels['TIMER_LT_ONE_MINUTE']
    
    def get_days_since_string(self):
        # Show only number of days
        measure = self.get_measures()
        unit = self.OVERFLOW_UNIT
        quantity = measure.get_measure(unit)
        # Running Timers
        if self.is_running():
            if int(quantity) > 0:
                return '{0} {1} since'.format(quantity, unit)
            else:
                return 'Just Today'
        # Non-running Timers
        else:
            return '{0} {1} last run'.format(quantity, unit)
                
            
    def get_heading(self):
        if int(self.get_running_time_minutes()) > 0:
            return '{0} since {1}'.format(self.get_running_time_string(), self.get_description())
        else:
            return 'Just Now: {0}'.format(self.get_description())
    
    def get_heading_short(self):
        return self.get_days_since_string()
    
    def get_heading_short_split(self):
        pre_output = self.get_heading_short()
        return pre_output.split(' ')
    
    def get_measures(self):
        return NonMetricMeasureInt(
            self.UNITS, self.OVERFLOW_UNIT, 
            self.UNIT_LIMITS, int( self.get_running_time_minutes() ))

    def get_description(self):
        description = self.timer_from_db.description
        if description:
            # Return a description if the timer's description is a
            #  non-empty string of letters, numbers and punctuation
            if str_is_empty_or_space(description) == False:
                return description
            else:
                pass
        else:
            pass
        return labels['TIMER_DEFAULT_DESCRIPTION']
        
    def get_description_short(self):
        description = self.get_description()
        if len(description) > TIMERS_DESCRIPTION_LENGTH_SHORT:
            return '{0}...'.format(description[:TIMERS_DESCRIPTION_LENGTH_SHORT])
        else:
            return description
    
    def get_item_url(self):
        return reverse('padsweb:timer', kwargs={'timer_id':self.id()})
        
    def get_permalink_url(self):
        link_code=self.timer_from_db.permalink_code
        return reverse('padsweb:timer_by_permalink', 
                 kwargs={'link_code':link_code})
    
    # Return groups associated with this timer
    def get_associated_groups_from_db(self):
        # TODO: explain the db wizardry here
        return list(self.timer_from_db.in_groups.all().order_by("name"))
    
    def get_associated_view_groups(self):
        return self.helper.prepare_view_timer_group_list(
            self.get_associated_groups_from_db())
    
    def get_associated_groups_for_choicefield(self):
        associated_groups = self.get_associated_groups_from_db()
        # TODO: Find a more efficient way of doing this
        view_group_choices = []
        for tg in associated_groups:
            view_group_choices.append((tg.id,tg.name))
        return view_group_choices
            
    def get_available_groups_from_db(self):
        available_groups = list(self.helper.get_timer_groups_from_db())
        associated_groups = self.get_associated_groups_from_db()
        # TODO: Find a more efficient way of doing this
        for g in associated_groups:
            available_groups.remove(g)
        return available_groups
    
    def get_available_groups_for_choicefield(self):
        available_view_groups = self.get_available_groups_from_db()
        # TODO: Find a more efficient way of doing this
        view_group_choices = []
        for tg in available_view_groups:
            view_group_choices.append((tg.id,tg.name))
        return view_group_choices
        
    def get_available_view_groups(self):
        return self.helper.prepare_view_timer_group_list(
            self.get_available_groups_from_db())
        
    def add_to_group(self, group_id):
        self.helper.new_group_inclusion_by_id(self.id(), group_id)
        return True

    def set_groups_by_name(self, names):
        """Attempts to assign a Timer to Timer Groups specified by a delimited
        string 'names', and removes it from Groups not specified in the string.
        If a group does not exist, it will be automatically created.
        """
        # TODO: Find a more efficient way of implementing this method
        
        # Generate a list of names from string
        # TODO: Move separator character into a configuration variable
        names_set = names.split(' ')
                
        with transaction.atomic():
            self.remove_from_all_groups()
            for name in names_set:
                old_group = self.helper.get_timer_group_for_view_by_name(name)
                if old_group is None:
                    new_group_id = self.helper.new_timer_group(name)                    
                    self.add_to_group(new_group_id)
                else:
                    self.add_to_group(old_group.id())
        return True
        
    def delete(self):
        return self.helper.delete_timer_by_id(self.id())

    # Export to dictionary for easy serialisation (e.g. with json.dumps())
    def dict(self):
        timer_d = dict() # Timer details
        
        # Export history
        reset_history = self.reset_history()
        export_hlist = []
        export_hitem = {}
        for i in reset_history:
            export_hitem['timestamp'] = i.date_time.timestamp()
            export_hitem['reason'] = i.reason
            export_hlist.append(export_hitem)

        # Export group names
        groups = self.get_associated_groups_from_db()
        export_groups = []
        for n in groups:
            export_groups.append(n.name)
        
        # Export vital information
        timer_d['description'] = self.timer_from_db.description
        timer_d['creation_timestamp'] = self.timer_from_db.creation_date_time.timestamp()
        timer_d['associated_groups'] = export_groups
        timer_d['historical'] = self.timer_from_db.historical
        timer_d['history_list'] = export_hlist
        timer_d['permalink_code'] = self.timer_from_db.permalink_code
        timer_d['public'] = self.timer_from_db.public
        timer_d['running'] = self.timer_from_db.running
        return timer_d
    
    def remove_from_group(self, group_id):
        self.helper.delete_group_inclusion_by_id(self.id(), group_id)
        return True
    
    def remove_from_all_groups(self):
        with transaction.atomic():
            # Get list of Timer Groups
            assoc_groups = self.get_associated_groups_from_db()
            # Remove Timer from all Groups
            for group in assoc_groups:
                self.remove_from_group(group.id)
        return True
    
    def id(self):
        return self.timer_from_db.id
        
    # TODO: Rename to 'is_back_dated()'
    def is_pre_dated(self):
        return self.count_from_date_time() < self.creation_date_time()

    def is_public(self):
        return self.timer_from_db.public
    
    def is_running(self):
        return self.timer_from_db.running
        
    def is_in_quick_list(self):
        creator_nick = self.timer_from_db.creator_user.nickname_short
        return creator_nick.startswith(
            ANONYMOUS_USER_SHORT_NICKNAME_PREFIX)

    def reset(self, reason):
        date_time_now = timezone.now()
        if str_is_empty_or_space(reason):
            reason = labels['REASON_NONE']
        with transaction.atomic():
            self.timer_from_db.count_from_date_time = date_time_now
            self.timer_from_db.running = True
            self.timer_from_db.save()
            reason_full = labels['TIMER_RESET_NOTICE'].format(reason)
            self.helper.new_timer_reset_history(
                self.id(), reason_full, date_time_now)
        return True

    def reset_count(self):
        return self.timer_from_db.padstimerreset_set.count()

    def reset_history(self):
        return tuple(
            self.timer_from_db.padstimerreset_set.order_by("-date_time"))

    def reset_history_latest(self):
        if self.timer_from_db.padstimerreset_set.count() > 0:
            return self.timer_from_db.padstimerreset_set.order_by(
                "-date_time")[0]
        else:
            return None
                
    def set_public(self):
        self.helper.set_timer_public_flag(self.id(), True)
        return True
    
    def set_private(self):
        self.helper.set_timer_public_flag(self.id(), False)
        return True
                
    def __init__(self, timer_from_db, helper=PADSTimerHelper()):
        self.timer_from_db = timer_from_db
        self.helper = helper

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if len(self.get_description()) > self.DESCRIPTION_LENGTH_SHORT:
            dstr = self.get_description()[:self.DESCRIPTION_LENGTH_SHORT] + "..."
        else:
            dstr = self.get_description()
        return "({0}) {1}".format(self.id(), dstr)
    

class PADSViewHistoricalTimer(PADSViewTimer):

    def is_historical(self):
        return True

    def stop(self, reason):
        """Permanently stops the Timer.
        """
        if str_is_empty_or_space(reason):
            reason = labels['REASON_NONE']
            
        reason_full = labels['TIMER_STOP_NOTICE'].format(reason)
        with transaction.atomic():
            self.helper.set_timer_running_flag(self.id(), False)
            self.helper.new_timer_reset_history(self.id(), reason_full)
        return True

    def get_status_line(self):
        return 'Hist.'

class PADSViewRegularTimer(PADSViewTimer):

    def is_historical(self):
        return False

    def set_description(self, description):
        """Changes the Description on a Timer.
        This also resets the Timer. Description changes are recorded
        in the Timer's History.
        """
        if str_is_empty_or_space(description):
            description = labels['TIMER_DEFAULT_DESCRIPTION']
        with transaction.atomic():
            reset_reason = labels['TIMER_RENAME_NOTICE'].format(
                description)
            # TODO: Investigate this:
            # On MariaDB 10.0.29 the reset has to take place before the 
            # rename or the timer will not be renamed at all.
            self.reset(reset_reason)
            self.helper.set_timer_description(self.id(), description)
        return True

    def stop(self, reason):
        """Temporarily stops the Timer without resetting its count.
        Suspensions are recorded in the Timer's History. Regular
        Timers can be restarted.
        """
        request_datetime = timezone.now()
        if str_is_empty_or_space(reason):
            reason = labels['REASON_NONE']
        message = labels['TIMER_SUSPEND_NOTICE'].format(reason)
        with transaction.atomic():
            self.helper.set_timer_running_flag(self.id(), False)
            self.helper.new_timer_reset_history(
                self.id(), message, request_datetime)
        return True
            
    def get_status_line(self):
        separator = ' '
        status = ''
        if self.is_pre_dated():
            status += 'B.D.' + separator
        return status.rstrip(separator)


class PADSViewSuspendedTimer(PADSViewTimer):

    def is_historical(self):
        return False
    
    def set_running(self):
        """Resumes a Timer after it has been suspended.
        The Timer will also be reset. This will be recorded in the
        Timer's History.
        """
        with transaction.atomic():
            # Resuming a timer resets it.
            self.helper.set_timer_running_flag(self.id(), True)
            self.reset(labels['TIMER_RESUME_NOTICE'])
        return True
        
    def get_status_line(self):
        return 'Susp.'


class PADSViewTimerGroup:
    """Timer Group Presentation Class that provides a view-friendly 
    interface to the Timer Group Model.
    """
    
    def get_current_page(self):
        return self.page(self.current_page_number)

    def get_first_page(self):
        return self.page()

    def get_pagination_url(self):
        if self.id():
            return reverse(
                'padsweb:index_group',kwargs={'timer_group_id':self.id()})
        else:
            return ''
    
    def get_previous_natural_page_number(self):
        if self.at_first_page():
            return 0
        else:
            return self.current_natural_page_number() - 1
    
    def get_previous_page_url(self):
        tg_url = self.get_pagination_url()
        if len(tg_url) > 0:
            return '{0}?p={1}'.format(
                tg_url, self.get_previous_natural_page_number())
        else:
            return ''
    
    def get_previous_page_label(self):
        if self.at_first_page():
            return ''
        else:
            return '<'

    def get_next_natural_page_number(self):
        if self.at_last_page():
            return self.max_page()
        else:
            return self.current_natural_page_number() + 1

    def get_next_page_url(self):
        tg_url = self.get_pagination_url()
        if len(tg_url) > 0:
            return '{0}?p={1}'.format(
                tg_url, self.get_next_natural_page_number())
        else:
            return ''

    def get_next_page_label(self):
        if self.at_last_page():
            return ''
        else:
            return '>'

    def set_description_filter(self, search_term):
        self.filtered_timers_set = self.timers_from_db.filter(
            description__icontains=search_term).order_by('description')
        
    def set_description_prefix_filter(self, search_term):
        self.filtered_timers_set = self.timers_from_db().filter(
            description__istartswith=search_term).order_by('description')

    # Helper Functions
    def add_timer_by_id(self, timer_id):
        return self.helper.new_group_inclusion_by_id(
            timer_id, self.timer_group_from_db.id)
    
    def remove_timer_by_id(self, timer_id):
        return self.helper.delete_group_inclusion_by_id(
            timer_id, self.timer_group_from_db.id)
    
    def get_timers(self, first=0, last=None):
        if self.filtered_timers_set == self.timers_from_db:
            return self.get_timers_all(first, last)
        else:
            return self.get_timers_filtered(first, last)

    def get_timers_all(self, first=0, last=None):
        timers_from_db = self.timers_from_db.all()[first:last]
        return self.prepare_view_timer_list(timers_from_db)

    def get_timers_filtered(self, first=0, last=None):
        timers_from_db = self.filtered_timers_set.all()[first:last]
        return self.prepare_view_timer_list(timers_from_db)
        
    def set_page_size(self, size=0):
        if size > 0:
            self.page_size = size
    
    def at_first_page(self):
        return self.current_page_number == 0
    
    def at_last_page(self):
        return self.current_page_number >= self.max_page()
    
    def is_filtered(self):
        return self.filtered_timers_set == self.timers_from_db
    
    def set_natural_page_number(self, n=1):
        if n >= (self.max_page() + 1):
            self.current_page_number = self.max_page()
        elif n < 0:
            self.current_page_number = 0
        self.current_page_number = n - 1
    
    def current_natural_page_number(self):
        return self.current_page_number + 1
    
    def get_title(self):
        if self.title:
            return self.title
        else:
            return labels['TIMER_GROUP_DEFAULT_TITLE']
    
    def set_title(self, title):
        self.title = title
    
    def page(self, page=0):
        # First page is 0, get the first page by default
        max_page = self.max_page()
        if max_page > 0:
            # Get the last page if the page number is out of range
            if page > max_page:
                page = max_page
            # Handle last page request
            if (page == max_page) & (self.small_last_page()):
                last_i = self.count()
            else:
                last_i = ((page + 1) * self.page_size)
            first_i = page * self.page_size
            return self.get_timers(first_i, last_i)
        else:
            return self.get_timers()

    def natural_page(self, page=1):
        # First page is 1, get the first page by default
        if page <= 0:
            # Automatically get the first page if 0 is entered
            req_page = self.get_first_page() 
        else:
            req_page = self.page(page - 1)
        return req_page
            
    def count(self):
        return self.filtered_timers_set.count()
    
    def max_page(self):
        if self.page_size:
            if self.page_size > 0:
                pages = int((self.count() / self.page_size))
                if self.small_last_page():
                    return pages - 1
                else:
                    return pages
        return 0

    def max_natural_page(self):
        return self.max_page() + 1

    def is_multi_page(self):
        return self.max_page() > 0        
        
    def id(self):
        return self.timer_group_from_db.id
    
    def small_last_page(self):
        """Determines if the last page will contain less than the page
        size's number of items.
        """
        return (self.count() % self.page_size) <= int(self.page_size / 2)
    
    def prepare_view_timer_list(self, timers_from_db):
        view_timers = []
        for t in timers_from_db:
            view_timers.append(self.helper.get_timer_for_view_by_id(t.id))
        return view_timers
        
    def __init__(self, timer_group_from_db=None, helper=PADSTimerHelper()):
        self.page_size = abs(INDEX_PAGE_SIZE)
        self.current_page_number = 0
        self.helper = helper
        self.timer_group_from_db = timer_group_from_db
        if timer_group_from_db:
            self.title = timer_group_from_db.name
            self.timers_from_db = timer_group_from_db.padstimer_set.all()
            self.filtered_timers_set = self.timers_from_db

class PADSSpecialViewTimerGroup(PADSViewTimerGroup):
    """Unbound Timer Group presentation class to provide a view-friendly 
    interface to a QuerySet from the Timer model, but for aggregrations 
    such as search results, instead of a timer group in the database.
    This class is for presentation purposes only and is not bound to the
    database. Adding and removing Timers from this group have no effect
    on the permanent Group Inclusions in the database.
    """
                    
    def count(self):
        return self.filtered_timers_set.count()
    
    def id(self):
        # Special Groups are not bound to a database record, and thus
        # have no id
        return None
    
    def __init__(self, timers_set, title=labels['TIMER_GROUP_DEFAULT_TITLE'], 
        helper=PADSTimerHelper()):
        super().__init__(None, helper)
        self.timers_from_db = timers_set
        self.filtered_timers_set = timers_set
        self.title = title
    
    def __str__(self):
        return self.title

class PADSLongestRunningTimerGroup(PADSSpecialViewTimerGroup):
    
    def get_pagination_url(self):
        return reverse('padsweb:index_longest_running')

    def __init__(self, helper=PADSTimerHelper()):
        timers_set = helper.get_timers_from_db().order_by(
            'count_from_date_time')
        super().__init__(
            timers_set, labels['TIMER_GROUP_DEFAULT_LONGEST_RUNNING_TITLE'],
            helper)

class PADSRecentlyResetTimerGroup(PADSSpecialViewTimerGroup):
    
    def get_pagination_url(self):
        return reverse('padsweb:index_recent_resets')

    def __init__(self, helper=PADSTimerHelper()):
        earliest_time = timezone.now() - datetime.timedelta(days=TIMERS_RECENT_RESET_MAX_AGE)
        timers_set = helper.get_timers_from_db().filter(
            count_from_date_time__gt=earliest_time).order_by('-count_from_date_time')
        super().__init__(
            timers_set, labels['TIMER_GROUP_DEFAULT_SHORTEST_RUNNING_TITLE'],
            helper)

class PADSNewestTimerGroup(PADSSpecialViewTimerGroup):
    
    def get_pagination_url(self):
        return reverse('padsweb:index_newest')

    def __init__(self, helper=PADSTimerHelper()):
        timers_set = helper.get_timers_from_db().order_by(
            '-creation_date_time')
        super().__init__(timers_set, labels['TIMER_GROUP_DEFAULT_NEWEST_TITLE'],
         helper)

class PADSSharedTimerGroup(PADSSpecialViewTimerGroup):
    
    def get_pagination_url(self):
        return reverse(
            'padsweb:index_shared_by_user', kwargs={'user_id':self.user_id})
    
    def __init__(self, user_id):
        helper = PADSPublicTimerHelper(user_id)
        timers_set = helper.get_timers_from_db().filter(public=True)
        super().__init__(timers_set, 
            labels['TIMER_GROUP_DEFAULT_PUBLIC_TITLE'], helper)
        self.user_id = user_id

class PADSPrivateTimerGroup(PADSSpecialViewTimerGroup):
    
    def get_pagination_url(self):
        return reverse('padsweb:index_private_by_user')
    
    def __init__(self, user_id):
        helper = PADSTimerHelper(user_id)
        timers_set = helper.get_timers_from_db().filter(public=False)
        super().__init__(
            timers_set,
            labels['TIMER_GROUP_DEFAULT_PRIVATE_TITLE'], helper)
        self.user_id = user_id



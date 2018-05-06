#
#
# Public Archive of Days Since Timers
# Model Helper Classes and Functions
#
#
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from pytz import all_timezones
from padsweb.settings import defaults
from padsweb.strings import labels
from padsweb.misc import split_posint_rand
from padsweb.models import PADSUser
from padsweb.models import PADSTimer, PADSTimerReset
from padsweb.models import PADSTimerGroup, GroupInclusion
import datetime, secrets

settings = defaults

class PADSHelper:
    """Base class for other PADS helper classes"""
    def get_user_from_db(self):
        if self.user_is_registered():
            if self.user_model.objects.filter(pk=self.user_id).exists():
                return self.user_model.objects.get(pk=self.user_id)
            else:
                return None
        else:
            return None
    
    def set_user_id(self, user_id):
        """Assigns a Helper to a User id. This is intended to assist access 
        control routines. Only valid User ids may be assigned. If the User is 
        not found in the database, the default User id (user_id_signed_out) 
        is set.
        """
        if isinstance(user_id, int):
            if user_id > 0:
                self.user_id = user_id
                if self.user_is_registered() is False:
                    self.user_id = settings['user_id_signed_out']
            else:
                self.user_id = settings['user_id_signed_out']
        else:
            self.user_id = settings['user_id_signed_out']

    def set_user_model(self, user_model=PADSUser):
        if user_model is not None:
            self.user_model = user_model

    def user_is_present(self):
        """Indicates if a User id has been assigned to the helper. Returns
        True or False.
        """
        return self.user_id != settings['user_id_signed_out']

    def user_is_registered(self):
        if self.user_model is None:
            return False
        elif self.user_model.objects.filter(pk=self.user_id).exists():
            return True
        else:
            return False
    
    def __init__(self, user_id=settings['user_id_signed_out'], **kwargs):
        # Local Variables
        # TODO: Explain how models are specified to the Timer Helper
        self.user_id = settings['user_id_signed_out']
        self.class_desc = 'PADS Helper Base Class'
        self.models = kwargs.get('models', dict())
        self.user_model = None
        # Constructor Routine
        self.set_user_model()
        self.set_user_id(user_id)        

    def __repr__(self):
        return self.__str__()
        
    def __str__(self):
        output = '{0} ({1})'
        if self.user_is_present():
            user_id_str = 'user id {0}'.format(self.user_id)
        else:
            user_id_str = 'user unassigned'
        return output.format(self.class_desc, user_id_str)
    

class PADSReadHelper(PADSHelper):
    """Base class for helper classes that load data"""
    def get_all_from_db(self):
        raise NotImplementedError
        
    def get_from_db(self, item_id):
        raise NotImplementedError
        
    def __init__(self, user_id, **kwargs):
        super().__init__(user_id, **kwargs)

    
class PADSWriteHelper(PADSHelper):
    """Base class for helper classes that store data, whether saving new
    items or modifying existing ones
    """
    def new(self, item_id):
        raise NotImplementedError
        
    def delete(self, item_id):
        raise NotImplementedError

    def __init__(self, user_id=settings['user_id_signed_out'], **kwargs):
        super().__init__(user_id, **kwargs)


class PADSReadTimerHelper(PADSReadHelper):
    """The PADSTimerHelper is a Helper class to load Timer data"""
    def get_all_from_db(self):
        if self.user_is_present() is True:
            
            # TODO: Find out why doing the following results in 
            # the get() method failing on timers_available when a getting a 
            # timer that appears in both timers_own and timers_others_shared.
            # 
            #timers_own = self.timer_model.objects.filter(
            #        creator_user_id=self.user_id)
            #timers_others_shared = self.timer_model.objects.exclude(
            #        creator_user_id=self.user_id)
            #timers_available = timers_own.union(timers_others_shared)
            
            timers_available_q = self.timer_model.objects.filter(
                    Q(creator_user_id=self.user_id) | Q(public=True) )
            return timers_available_q
        else:
            return self.timer_model.objects.filter(public=True)

    def get_from_db(self, timer_id):
        if self.get_all_from_db().filter(pk=timer_id).exists() is True:
            return self.get_all_from_db().get(pk=timer_id)
        else:
            return None
    
    def get_from_db_by_description(self, description):
        return self.get_all_from_db().filter(
                description__icontains=description)
    
    def get_from_db_by_permalink_code(self, link_code):
        if isinstance(link_code, str) is False:
            return None
        if self.get_all_from_db().filter(
                permalink_code=link_code).exists() is True:
            return self.get_all_from_db().get(permalink_code=link_code)
        else:
            return None
    
    def get_by_group_id(self, group_id):
        return self.get_all_from_db().filter(in_groups=group_id)

    def get_groups_all(self):
        if self.user_is_present() is True:
            groups_own = self.group_model.objects.filter(
                    creator_user_id=self.user_id)
            return groups_own
        else:
            return None

    def get_groups_from_db_by_name(self, name):
        return self.get_groups_all().filter(name__icontains=name)

    def get_groups_by_timer_id(self, timer_id):
        timer_exists = self.get_all_from_db().filter(
                pk=timer_id, creator_user_id=self.user_id).exists()
        if timer_exists is True:
            timer = self.get_all_from_db().get(pk=timer_id, 
                                        creator_user_id=self.user_id)
            groups = timer.in_groups.all()
            return groups
        return None

    def get_resets_from_db_by_timer_id(self, timer_id):
        return self.timer_log_model.objects.filter(timer_id=timer_id)    
    
    #
    # Introspection and Constructor Methods
    #
    def __init__(self, user_id=None, **kwargs):
        super().__init__(user_id, **kwargs)

        # Set Models
        self.class_desc = "PADS Read Timer Helper"
        # Beginner's PROTIP: Use Django database model classes directly to 
        # access an entire SQL table, create instances of the model classes to 
        # access individual records in the table.
        self.timer_model = self.models.get('timer_model', PADSTimer)
        self.group_model = self.models.get('group_model', PADSTimerGroup)
        self.group_incl_model = self.models.get(
                'group_incl_model', GroupInclusion)
        self.timer_log_model = self.models.get('timer_log_model', 
                                               PADSTimerReset)

class PADSWriteTimerHelper(PADSWriteHelper):
    def new(self, description, **kwargs):
        """Creates a new Timer and saves it to the database.
        Returns the new Timer's id as an int on success. Returns None on 
        failure.
        """
        if self.user_is_registered() is False:
            return None
        else:
            creation_time = timezone.now()
            new_timer = PADSTimer()
            new_timer.creator_user_id = self.user_id
            new_timer.description = description
            new_timer.count_from_date_time = kwargs.get(
                    'count_from_date_time', creation_time)
            new_timer.creation_date_time = creation_time
            new_timer.historical = kwargs.get('historical', False)
            new_timer.permalink_code = secrets.token_urlsafe(
                    settings['timer_permalink_code_length'])
            new_timer.public = kwargs.get('public', False)
            new_timer.running = kwargs.get('running', True)
            new_timer.save()
            return new_timer.id
    
    def new_group(self, name):
        """Creates a new Timer Group and saves it to the database. 
        Returns the new Timer Group's id as an int on success. Returns None
        on failure.
        """
        if self.user_is_registered() is False:
            return None
        else:
            group_exists = self.group_model.objects.filter(name=name).exists()
            if group_exists is True:
                return None
            else:
                new_group = PADSTimerGroup()
                new_group.name = name
                new_group.creator_user_id = self.user_id
                new_group.save()
                return new_group.id
        
    def new_log_entry(self, timer_id, description, **kwargs):
        """Creates a Log Entry for a Timer. Log entries are currently used
        only for edits to Timers that trigger a reset, and are thus may be 
        called Timer resets. Returns None on failure, or the id of the Timer
        Log Entry on success.
        """
        if self.user_is_registered() is False:
            return None
        else:
            timer_exists = self.timer_model.objects.filter(
                    pk=timer_id).exists()
            if timer_exists is True:
                log_time = timezone.now()
                new_log_entry = PADSTimerReset()
                new_log_entry.timer_id = timer_id
                new_log_entry.date_time = log_time
                new_log_entry.save()
                return new_log_entry.id
            else:
                return None
        
    def add_to_group(self, timer_id, group_id):
        if self.user_is_registered() is False:
            return False
        else:
            timer_exists = self.timer_model.objects.filter(
                    pk=timer_id).exists()
            group_exists = self.group_model.objects.filter(
                    pk=group_id).exists()
            if (timer_exists is True) & (group_exists is True):
                group_inclusion = GroupInclusion()
                group_inclusion.group_id = group_id
                group_inclusion.timer_id = timer_id
                group_inclusion.save()
                return True
            else:
                return False
                
    def remove_from_group(self, timer_id, group_id):
        if self.user_is_registered() is False:
            return False
        else:
            timer_exists = self.timer_model.objects.filter(
                    pk=timer_id).exists()
            group_exists = self.group_model.objects.filter(
                    pk=group_id).exists()
            if (timer_exists is True) & (group_exists is True):
                group_inclusion = self.group_incl_model.objects.get(
                        timer_id=timer_id, group_id=group_id)
                group_inclusion.delete()
                return True
            else:
                return False

    def delete(self, timer_id):
        if self.user_is_registered() is False:
            return False
        else:
            timer_exists = self.timer_model.objects.filter(
                    pk=timer_id).exists()
            if timer_exists is True:
                timer = self.timer_model.objects.get(pk=timer_id)
                timer.delete()
                return True
            else:
                return False
    
    def set_description(self, timer_id, description):
        edit_time = timezone.now()
        if self.user_is_registered() is False:
            return False
        else:
            with transaction.atomic():
                timer_exists = self.timer_model.objects.filter(
                        pk=timer_id).exists()
                if timer_exists is True:
                    timer = self.timer_model.objects.get(pk=timer_id)
                    timer.description = description
                    timer.count_from_date_time = edit_time  # Reset timer
                    # Log the change in description
                    notice = labels['TIMER_RENAME_NOTICE'].format(
                            description)
                    self.new_log_entry(timer_id, notice)
                    timer.save()
                    return True
                else:
                    return False
    
    def reset_by_id(self, timer_id, reason):
        reset_time = timezone.now()
        if self.user_is_registered() is False:
            return False        
        else:
            timer_exists = self.timer_model.objects.filter(
                    pk=timer_id).exists()

            if timer_exists is False:
                return False
            else:
                timer = self.timer_model.objects.get(pk=timer_id)
                timer_historical = timer.historical
            
            if timer_historical is False:
                with transaction.atomic():
                        timer.count_from_date_time = reset_time
                        timer.running = True
                        # Log the reset
                        notice = labels['TIMER_RESET_NOTICE'].format(
                                reason)
                        self.new_log_entry(timer_id, notice)
                        timer.save()
                        return True
            else:
                # Historical Timers shall not be reset 
                return False
        
    def stop_by_id(self, timer_id, reason):
        if self.user_is_registered() is False:
            return False        
        else:
            timer_exists = self.timer_model.objects.filter(
                    pk=timer_id).exists()

        if timer_exists is False:
            return False
        else:
            timer = self.timer_model.objects.get(pk=timer_id)
            timer_historical = timer.historical
            timer.running = False
        
            with transaction.atomic():
                # Log the edit
                if timer_historical is False:
                    notice = labels['TIMER_SUSPEND_NOTICE'].format(
                            reason)
                else:
                    notice = labels['TIMER_STOP_NOTICE'].format(
                            reason)
                self.new_log_entry(timer_id, notice)
                timer.save()
            
            return True

    #
    # Introspection and Constructor Methods
    #
    def __init__(self, user_id=None, **kwargs):
        super().__init__(user_id, **kwargs)

        # Set Models
        self.class_desc = "PADS Write Timer Helper"
        self.timer_model = self.models.get('timer_model', PADSTimer)
        self.group_model = self.models.get('group_model', PADSTimerGroup)
        self.group_incl_model = self.models.get(
                'group_incl_model', GroupInclusion)
        self.timer_log_model = self.models.get('timer_log_model', 
                                               PADSTimerReset)

        
class PADSUserHelper(PADSHelper):
    """Helper class for looking up information on User accounts and password
    verifications.
    
    Please be aware that this class does NOT inherit from PADSReadHelper, due
    to the lack of use of the page() and get_by_id() methods. This class is
    meant to only interact with one user account at a time, and the get_by_id()
    method is redundant due to the way this class is used.
    """    
    def get_user_from_db_by_username(self, user_name):
        if isinstance(user_name, str):
            if self.user_model.objects.filter(
                    nickname_short=user_name).exists():
                return self.user_model.objects.get(nickname_short=user_name)
            else:
                return None
        else:
            return None
        
    def set_user_id_by_username(self, user_name):
        user = self.get_user_from_db_by_username(user_name)
        if user is not None:
            self.user_id = user.id
        else:
            self.user_id = settings['user_id_signed_out']

    def check_password(self, password):
        if password is None:
            return False
        elif len(password) <= 0:
            return False
        elif self.user_is_registered() is False:
            return False
        
        user = self.get_user_from_db()
        return self.password_hasher.verify(password, user.password_hash)
    
    def check_ql_password(self, ql_password):
        ql_raw_password = self.split_ql_password(ql_password)[1]
        return self.check_password(ql_raw_password)
    
    def split_ql_password(self, ql_password):
        """Splits a Quick List password into a user id and the raw 
        password. A Quick List password is composed of a user id,
        followed by a separator and the raw password, which is in turn
        a series of alphanumeric characters separated at a psuedo-random
        interval. Trailing whitespace will be stripped from ql_password.
        
        Returns a tuple: (user_id, password_raw)
        """
        password_parts = ql_password.partition(
                settings['ql_password_seg_separator'])
            
        # The quick list ID is the number in the first segment 
        #  of the Quick List password.
        try:
            user_id = int(password_parts[0])  # Remember to parse to an int
        except ValueError:
            return (settings['user_id_signed_out'], None)
            
        password_raw = password_parts[2].rstrip()
        
        # Beginner's PROTIP: I would have written the return statement
        # as return (user_id, password_raw), but that makes it look too
        # much like JavaScript (and all the other C-inspired languages).
        
        output = (user_id, password_raw)
        return output

    def user_is_ql(self):
        """Returns True if a User is a QL User.
        """
        return self.user_from_db.nickname_short.startswith(
                settings['ql_user_name_prefix'])

    def user_has_signed_in(self):
        user = self.get_user_from_db()
        if user is not None:
            return user.last_login_date_time > user.sign_up_date_time
        else:
            return False
        
    def __init__(self, user_id=settings['user_id_signed_out'], **kwargs):
        self.class_desc = 'PADS User Helper (for read operations)'
        self.password_hasher = kwargs.get('password_hasher', 
                                          PBKDF2PasswordHasher())
        super().__init__(user_id, **kwargs)
        self.set_user_id(user_id)
    

class PADSWriteUserHelper(PADSWriteHelper):
    """Helper class for creating and updating User accounts. When updating
    or deleting accounts, please set the helper's user_id to the id of the 
    User account to be updated.
    """
    
    def delete(self):
        """Deletes a User's account. To delete an account, set this helper's
        user_id to the account to be deleted first.
        
        Returns True on success.
        """
        if self.user_is_present():
            user_from_db = self.user_model.objects.get(id=self.user_id)
            user_from_db.delete()
            return True
        else:
            return False
    
    def new(self, username=None, password=None):
        """Creates a User account and saves it into the database.
        If both username and password are specifed, a regular account is
        created. If neither are specified, a Quick List account is created.
        If only either is specified, no action is taken.
        
        Returns a username of the new account as a string for regular username-
        password accounts, or Quick List password for Quick List Users 
        on success. Returns None on failure.
        """
        new_user = None
        new_ql_password = None
        if (username is None) & (password is None):
            # No username nor password: create and save QL User
            new_ql_result = self.prepare_ql_user_in_db()
            new_user = new_ql_result[0]
            new_user.save()
            new_ql_raw_password = new_ql_result[1]
            new_ql_password = '{0}{1}{2}'.format(
                    new_user.id,
                    settings['ql_password_seg_separator'], 
                    new_ql_raw_password)
            return new_ql_password
            
        elif (username is not None) & (password is not None):
            # Both username and password are specified: create regular User
            
            # Cancel account creations with disallowed usernames
            # TODO: Implement a means of rejecting offensive or misleading
            # usernames
            if username.startswith(settings['ql_user_name_prefix']):
                return None
            
            elif (len(username) <= 0) | username.isspace():
                return None
            
            elif len(username) > settings['name_max_length_short']:
                return None
            
            elif self.user_model.objects.filter(
                    nickname_short__iexact=username).exists() is True:
                # Username is taken, regardless of case
                return None
            
            new_user = self.prepare_user_in_db(username, password)
            new_user.save()
            return new_user.nickname_short

        else:
            return None

    def set_nickname_long(self, nickname_long):
        if self.user_is_registered() is False:
            return False

        # Cancel disallowed nicknames
        # TODO: Implement a means of rejecting offensive or misleading
        # nicknames
        if nickname_long is None:
            return False
        elif len(nickname_long) > settings['name_max_length_long']:
            return False
        elif (len(nickname_long) <= 0) | nickname_long.isspace():
            return False

        user = self.get_user_from_db()
        if user is not None:
            user.nickname = nickname_long
            user.save()
            return True
        else:
            return False
    
    def set_password(self, new_password):
        if new_password is None:
            return False
        elif (len(new_password) <= 0) | (new_password.isspace() is True):
            return False
        
        user = self.get_user_from_db()
        if user is not None:
            salt = secrets.token_urlsafe(settings['password_salt_bytes'])
            user.password_hash = self.password_hasher.encode(
                new_password, salt)
            user.save()
            return True
        else:
            return False
        
    def set_time_zone(self, timezone_name):
        user = self.get_user_from_db()
        if user is not None:
            if timezone_name in all_timezones:
                user.time_zone = timezone_name
                user.save()
                return True
            else:
                return False
        else:
            return False

    def merge_users_by_id(self, source_user_id, **kwargs):
        # TODO: Replace this with a more efficient implementation.
        with transaction.atomic():
            source_user = self.get_user_from_db_by_id(source_user_id)

            # Transfer Timer Groups
            timer_groups_in_db = source_user.padstimergroup_set.all()
            for tg in timer_groups_in_db:
                tg.creator_user_id = self.user_id
                tg.save()
            
            # Transfer Timers
            timers_in_db = source_user.padstimer_set.all()
            for t in timers_in_db:
                t.creator_user_id = self.user_id    
                t.save()
                # Optionally transfer ungrouped timers into a default group
                default_group_id = kwargs.get("default_group_id")
                if default_group_id:
                    if t.groupinclusion_set.count() <= 0:
                        inclusion = GroupInclusion()
                        inclusion.group_id = default_group_id
                        inclusion.timer_id = t.id
                        inclusion.save()
            # Delete Source User
            self.delete_user(source_user_id)

    def generate_ql_password(self, length, segments, 
        chars, separator=settings['ql_password_seg_separator']):
        """Generates a random password of a nominated length and number 
        of segments, composed entirely of characters in chars. 
        The separator is placed in between segments.
        """
        new_password = ''
        segment_lengths = split_posint_rand(length, segments)
        
        # For every segment...
        for i in range (0, len(segment_lengths)):
            # Pick some letters for the password
            for j in range(0, segment_lengths[i]):
                new_password = ''.join(
                    [new_password, secrets.choice(chars)])
            # Finish the segments with a separator
            new_password = ''.join([new_password, separator])
            
        # Return the password sans the extra separator
        return new_password.rstrip(separator)
        
    def prepare_user_in_db(self, nickname_short, password, **kwargs):
        """Prepares a new User account record. This method only prepares the
        record model object. The record is saved to the database in the new()
        method. The account username (nickname_short) must not begin with the
        Quick List User username prefix.
        
        Returns a PADSUser object of the User on success, None on failure.
        """
        new_user = PADSUser()

        # Generate a new password salt
        salt = secrets.token_urlsafe(settings['password_salt_bytes'])

        # Initialise mandatory information
        new_user.nickname_short = nickname_short
        new_user.sign_up_date_time = timezone.now()
        new_user.time_zone = timezone.get_current_timezone_name()
        new_user.password_hash = self.password_hasher.encode(password, salt)
        
        # Initialise optional information
        new_user.nickname = kwargs.get('nickname', nickname_short)

        # Set the last login time to a second before sign up date time.
        # A User has not logged on at all if the last login time is earlier 
        # than the sign up time.
        new_user.last_login_date_time = timezone.now() - datetime.timedelta(
                seconds=-1)
        
        return new_user    

    def prepare_ql_user_in_db(self):
        """Prepares a new Quick List User account record. This method only 
        prepares the record model object. The record is saved to the database 
        in the new() method.
        
        Returns a tuple: (new_user, raw_password)
        - new_user is a PADSUser object (DB record object) of the new user
        - raw password is the QL password without the first segment (which is 
        only known after the account has been saved to the database)
        """
        # Prepare the random password
        raw_password = self.generate_ql_password(
            settings['ql_new_password_length'],
            settings['ql_new_password_max_segments'],
            settings['ql_new_password_chars'],
            settings['ql_password_seg_separator'])
            
        # Prepare the User Info
        # The generate_anon_user_password() method is reused to generate the
        # nickname suffix of the Quick List User account. The suffix is 
        # equivalent to a single-segment QL password.
        nickname_suffix = self.generate_ql_password(
            settings['ql_user_name_suffix_length'], 
            1, settings['ql_new_password_chars'])
        nickname_short = "{0}{1}".format(
            settings['ql_user_name_prefix'], nickname_suffix)
        new_user = self.prepare_user_in_db(nickname_short, raw_password)
        
        output = (new_user, raw_password)
        return output
    
    #
    # Constructor
    #
    def __init__(self, user_id=settings['user_id_signed_out'], **kwargs):
        super().__init__(user_id, **kwargs)

        # Instance Variables
        #  Models
        self.user_model = self.models.get('user_model', PADSUser)

        # Other stuff
        self.password_hasher = kwargs.get('password_hasher', 
                                          PBKDF2PasswordHasher())

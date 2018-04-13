#
#
# Public Archive of Days Since Timers
# Model Helper Classes and Functions
#
#
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.db import IntegrityError, transaction
from django.utils import timezone
from padsweb.settings import defaults
from padsweb.misc import split_posint_rand
from padsweb.models import PADSUser
from padsweb.models import PADSTimer, PADSTimerReset
from padsweb.models import PADSTimerGroup, GroupInclusion
import datetime, secrets

settings = defaults


class PADSHelper:
    """Base class for other PADS helper classes"""
    def set_user_id(self, user_id):
        if isinstance(user_id, int) & (user_id > 0):
            self.user_id = user_id
        else:
            self.user_id = settings['user_id_signed_out']

    def user_is_present(self):
        return self.user_id != settings['user_id_signed_out']
    
    def __init__(self, user_id=settings['user_id_signed_out'], **kwargs):
        # TODO: Explain how models are specified to the Timer Helper
        self.class_desc = 'PADS Helper Base Class'
        self.models = kwargs.get('models', dict())
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
        super(user_id, **kwargs)

    
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
    def get_from_db(self):
        raise NotImplementedError
    
    def get_all_from_db(self):
        raise NotImplementedError

    def get_from_db_by_permalink_code(self, link_code):
        """Returns a PADSViewTimer of a single Timer by its id."""
        raise NotImplementedError
    
    def get_by_group_id(self):
        raise NotImplementedError

    def get_groups_all(self):
        raise NotImplementedError

    def get_groups_by_timer_id(self):
        raise NotImplementedError

    def get_resets_from_db(self):
        raise NotImplementedError

    def get_resets_from_db_by_user(self):
        raise NotImplementedError
    
    
    #
    # Introspection and Constructor Methods
    #
    def __init__(self, user_id=None, **kwargs):
        super(user_id, **kwargs)

        # Set Models
        self.class_desc = "PADS Read Timer Helper"
        self.timer_model = self.models.get('timer_model', PADSTimer())
        self.group_model = self.models.get('group_model', PADSTimerGroup())
        self.group_incl_model = self.models.get(
                'group_incl_model', GroupInclusion())
        self.timer_log_model = self.models.get('timer_log_model', 
                                               PADSTimerReset())

class PADSWriteTimerHelper(PADSWriteHelper):
    def new(self, description, **kwargs):
        raise NotImplementedError
    
    def new_group(self, name):
        raise NotImplementedError
        
    def new_log_entry(self, timer_id, description):
        raise NotImplementedError

    def delete(self, timer_id):
        raise NotImplementedError
    
    def set_description(self, description):
        raise NotImplementedError
    
    def reset_by_id(self, timer_id):
        raise NotImplementedError
        
    def stop_by_id(self, timer_id):
        raise NotImplementedError

    #
    # Introspection and Constructor Methods
    #
    def __init__(self, user_id=None, **kwargs):
        super(user_id, **kwargs)

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
    def get_user_from_db(self):
        if self.user_is_registered():
            return self.user_model.objects.get(pk=self.user_id)
        else:
            return None
    
    def get_user_from_db_by_username(self, user_name):
        if isinstance(user_name, str):
            if self.user_model.objects.filter(
                    nickname_short=user_name).exists():
                return self.user_model.objects.get(nickname_short=user_name)
            else:
                return None
        else:
            return None
    
    def set_user_id(self, user_id):
        super().set_user_id(user_id)
        if self.user_is_registered():
            self.user_id = user_id
        else:
            self.user_id = settings['user_id_signed_out']
    
    def set_user_model(self, user_model=PADSUser):
        if self.user_model is None:
            self.user_model = user_model
    
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
        user_id = password_parts[0]
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

    def user_is_registered(self):
        if self.user_model.objects.filter(pk=self.user_id).exists():
            return True
        else:
            return False
    
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
        self.user_model = None
        self.user_id = settings['user_id_signed_out']
        self.set_user_model()  # This must be done before calling super()
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
        
    def get_user_from_db(self):
        if self.user_is_registered:
            if self.user_model.objects.filter(pk=self.user_id).exists():
                return self.user_model.objects.get(pk=self.user_id)
            else:
                return None
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
        
    def set_timezone(self, timezone_name):
        user = self.get_user_from_db()
        if user is not None:
            user.time_zone = timezone_name
            user.save()
            return True
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
        nickname_short = "{0} {1}".format(
            settings['ql_user_name_prefix'], nickname_suffix)
        new_user = self.prepare_user_in_db(nickname_short, raw_password)
        
        output = (new_user, raw_password)
        return output

    def user_is_registered(self):
        if self.user_model.objects.filter(pk=self.user_id).exists():
            return True
        else:
            return False
    
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

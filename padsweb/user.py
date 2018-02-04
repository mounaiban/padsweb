#
#
# Public Archive of Days Since Timers
# User account-related View Helper Classes
#
#
"""Contains Helper classes to open and edit User profiles and accounts
in a more view-friendly way than directly handling the Django Models.
"""

#
# Imports
#
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.utils import timezone
from padsweb.misc import split_posint_rand
from padsweb.models import PADSUser
from padsweb.models import GroupInclusion
from padsweb.settings import *

# Standard Library Imports
import datetime, random, secrets

# Constants
pads_user_default_models = {"user_model" : PADSUser,}
pads_password_hasher = PBKDF2PasswordHasher()

#
# Classes
#
class PADSUserHelper:
	"""User Helper Class for creating, loading and deleting User accounts.
	"""
	
	# Class Constants
	ANONYMOUS_USER_SUFFIX_LENGTH = 12
	SALT_BYTES = 48
	#  The letter 'O' and number '1' are omitted
	PARTIAL_ALPHANUM_UPPER = "ABCDEFGHIJKLMNPQRSTUVWXYZ234567890" 
	RANDOM_PASSWORD_LENGTH = 8
	RANDOM_PASSWORD_MAX_SEGMENTS = 3
	RANDOM_PASSWORD_SEGMENT_SEPARATOR = '-'

	#
	# Back-end Methods
	# (Methods that do not return a PADSViewUser)
	#
	def delete_user(self, user_id):
		user_from_db = self.user_model.objects.get(id=user_id)
		user_from_db.delete()
		return True

	def generate_anon_user_password(self, length, segments, 
		chars, separator='-'):
		"""Generates a random password of a nominated length and number 
		of segments, composed entirely of characters in chars. 
		The separator is placed in between segments.
		"""
		new_password = ""
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

	def split_anon_user_password(self, ql_password):
		"""Splits a Quick List password into a user id and the raw 
		password. A Quick List password is composed of a user id,
		followed by a separator and the raw password, which is in turn
		a series of alphanumeric characters separated at a psuedo-random
		interval. Trailing whitespace will be stripped from ql_password.
		
		Returns a tuple: (user_id, password_raw)
		"""
		password_parts = ql_password.partition(
			RANDOM_PASSWORD_SEGMENT_SEPARATOR)
			
		# The quick list ID is the number in the first segment 
		#  of the Quick List password. 
		user_id = password_parts[0]
		password_raw = password_parts[2].rstrip()
		
		# Beginner's PROTIP: I would have written the return statement
		# as return (user_id, password_raw), but that makes it look too
		# much like JavaScript (and all the other C-inspired languages).
		
		output = (user_id, password_raw)
		return output
		
	def get_user_from_db_by_id(self, user_id):
		if user_id:
			if self.user_model.objects.filter(pk=user_id).exists():
				return self.user_model.objects.get(pk=user_id)
			else:
				return None
		else:
			return None

	# TODO: Replace this with a more efficient implementation.
	def merge_users_by_id(self, source_user_id, target_user_id, **kwargs):
		with transaction.atomic():
			source_user = self.get_user_from_db_by_id(source_user_id)

			# Transfer Timer Groups
			timer_groups_in_db = source_user.padstimergroup_set.all()
			for tg in timer_groups_in_db:
				tg.creator_user_id = target_user_id
				tg.save()
			
			# Transfer Timers
			timers_in_db = source_user.padstimer_set.all()
			for t in timers_in_db:
				t.creator_user_id = target_user_id	
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

	def prepare_user_in_db(self, nickname_short, password, **kwargs):
		new_user = PADSUser()

		# Generate a new password salt
		salt = secrets.token_urlsafe(SALT_BYTES)

		# Initialise mandatory information
		new_user.nickname_short = nickname_short
		new_user.sign_up_date_time = timezone.now()
		new_user.time_zone = timezone.get_current_timezone_name()
		new_user.password_hash = self.password_hasher.encode(password, salt)
		
		# Initialise optional information
		new_user.nickname = kwargs.get('nickname', nickname_short)

		# A user has not logged on at all if the last login time is 
		#  before the creation time
		new_user.last_login_date_time = timezone.now() - datetime.timedelta(seconds=-1)
		
		return new_user	
			
	#
	# Front-end Methods
	# (Methods that return a PADSViewUser)
	#	
	def get_user_for_view_by_id(self, user_id):
		user_from_db = self.get_user_from_db_by_id(user_id)
		if user_from_db:
			return PADSViewUser(user_from_db, self)
		else:
			return None
		
	def get_user_by_nickname_short(self, nick_short):
		if nick_short:
			try:
				user_from_db = self.user_model.objects.get(
					nickname_short=nick_short)
				return PADSViewUser(user_from_db, self)
			except ObjectDoesNotExist:
				return None
		# Reject null input
		else:
			return None
	
		
	# Generates a new Anonymous account, saves it to db
	# Returns dictionary with user object and its password
	def new_anon_user_in_db(self):
		# Prepare the random password
		raw_password = self.generate_anon_user_password(
			self.RANDOM_PASSWORD_LENGTH,
			self.RANDOM_PASSWORD_MAX_SEGMENTS,
			self.PARTIAL_ALPHANUM_UPPER, 
			self.RANDOM_PASSWORD_SEGMENT_SEPARATOR)
			
		# Prepare the User Info
		nickname_suffix = self.generate_anon_user_password(
			self.ANONYMOUS_USER_SUFFIX_LENGTH, 
			1, self.PARTIAL_ALPHANUM_UPPER)
		nickname_short = "{0} {1}".format(
			ANONYMOUS_USER_SHORT_NICKNAME_PREFIX, nickname_suffix)
		new_user = self.prepare_user_in_db(
			nickname_short, raw_password)
		
		# Save new user to database, and return password
		try:
			new_user.save()
			new_ql_password = "{0}{1}{2}".format(
				new_user.id, self.RANDOM_PASSWORD_SEGMENT_SEPARATOR,
				raw_password)
			return new_ql_password
		except:
			return None
			
	def put_user_in_db(self, username, password):
		"""Creates a User account and saves it into the database. 
		
		In spirit of the guidelines from the HTTP standard, This method is
		prefixed 'put' instead of 'new' due to its idempotence; creating
		a user with the same username and password more than once should
		have the same effect on the database as doing it just once.
		
		See: RFC 2616, Section 9.5 and 9.6
		"""
		new_user = self.prepare_user_in_db(username, password)
		try:
			new_user.save()
			return new_user.id
		except IntegrityError:
			return None
	
	#
	# Dependency-injecting constructor
	#
	def __init__(self, **kwargs):

		# Instance Variables
		#  Models		
		self.user_model = kwargs.get(
			'db_models', pads_user_default_models.get('user_model'))

		# Other stuff
		self.password_hasher = kwargs.get(
			'password_hasher', pads_password_hasher)
		
		
# User info model helper class
class PADSViewUser:
	"""User Helper Class for modifying user accounts, and checking
	detailed account information.
	"""
	
	def id(self):
		return self.user_from_db.id

	def check_password(self, password):
		return self.helper.password_hasher.verify(
			password, self.user_from_db.password_hash)
	
	# Export to dictionary for easy serialisation (e.g. with json.dumps())
	def dict(self):
		user_d = {}
		user_d['nickname_short'] = self.user_from_db.nickname
		user_d['nickname'] = self.user_from_db.nickname
		user_d['time_zone'] = self.get_timezone()
		return user_d
		
	def get_timezone(self):
		return self.user_from_db.time_zone
	
	def set_password(self, old_password, new_password):
		if self.check_password(old_password):
			salt = secrets.token_urlsafe(SALT_BYTES)
			self.user_from_db.password_hash = self.helper.password_hasher.encode(
				new_password, salt)
			self.user_from_db.save()
			return True
		else:
			return False
	
	def set_timezone(self, timezone_name):
		self.user_from_db.time_zone = timezone_name
		self.user_from_db.save()
		return True
	
	def import_quick_list(self, quick_list_password, **kwargs):
		password_ql_split = self.helper.split_anon_user_password(
			quick_list_password)
		ql_id = password_ql_split[0]
		ql_password_raw = password_ql_split[1]
		
		# Reject malformed quick list password
		if ql_id.isdecimal():
			user_ql = self.helper.get_user_for_view_by_id(ql_id)
		else:
			return False
		
		if user_ql:
			if user_ql.check_password(ql_password_raw):
				default_group_id = kwargs.get("default_group_id")
				if default_group_id.isnumeric():
					self.helper.merge_users_by_id(
						user_ql.id(), self.id(), 
						default_group_id=default_group_id)
				else:
					self.helper.merge_users_by_id(
						user_ql.id(), self.id())
				return True
			else:
				return False
		else:
			return False
	
	def username(self):
		if self.is_anonymous():
			return ANONYMOUS_USER_SHORT_NICKNAME_PREFIX
		else:
			return self.user_from_db.nickname_short
	
	def is_anonymous(self):
		"""Method to indicate if an account is a Quick List or a regular
		 account.
		"""
		return self.user_from_db.nickname_short.startswith(
			ANONYMOUS_USER_SHORT_NICKNAME_PREFIX)
	
	def __init__(self, user_from_db, helper=PADSUserHelper()):
		self.user_from_db = user_from_db
		self.helper = helper


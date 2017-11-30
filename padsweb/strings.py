#
#
# Public Archive of Days Since Timers
# String Classes and Resources
#
#
""" A primitive implementation of the concept of String Resources 
found in other platforms such as Java and Android. This module (ver 0.5x)
contains the PADSStringDictionary class, as well as instances of it
containing the default labels and messages used in various parts of the
PADS UIs to get things started.
"""

# TODO: Move strings out of source code into a non-code asset and implement
#  some means of reading the asset into a PADSStringDictionary

#
#
# Class
#
#

class PADSStringDictionary:
	"""PADS String Dictionary Class"""
	
	def get_patch_level(self):
		return (len(self.patches) ) - 1
		
	def get_string(self, name):
		"""Gets a string of a specified name from the string dictionary.
		For unpatched dictionaries, a straightforward string lookup
		is performed from the internal dictionary.

		For patched dictonaries, a recursive search is peformed, starting
		with the string dictionary at the highest patch level, moving on
		to the lower levels if the string cannot be found.
		
		PADSStringDictionary is aware of recursion loops, but this
		awareness is dependent upon the host Python interpreter to detect
		the recursion loop.
		"""
		
		level = self.get_patch_level()
		while(level >= 1):
			try:
				return self.patches[level][name]
			except KeyError:
				level -= 1
			except RecursionError:
				self.infinite_loop = True
				break
		return self.strings[name]
		
	def patch(self, string_dict):
		"""Attaches a patch PADSStringDictionary. Patch dictionaries
		will expand the dictionary for strings that are only found in the
		patching dictionary, and replace existing ones where the
		strings have the same name in both the local dictionary and the
		patching dictionary.
		
		Multiple patches can be applied to a single dictionary. Please
		be aware that patched dictionaries can also be used as patches,
		so take care to avoid recursion loops (e.g. dict_a patched by
		dict_b, which is patched by dict_a).
		"""
		if(string_dict != self):
			self.patches.append(string_dict)
			self.description = None
	
	def __getitem__(self, key):
		return self.get_string(key)
	
	def __init__(self, init_dict, description):
		self.description = description
		self.patches = [self]  # First entry in patch list is self
		self.strings = init_dict
		self.infinite_loop = False
	
	def __repr__(self):
		return self.__str__()
		
	def __str__(self):
		pre_output = 'String Dictionary: {0}'.format(self.description)
		has_inf_loop = None
		if self.infinite_loop:
			has_inf_loop = '(has Infinite Loop)'
		return ''.join([pre_output, inf_loop])

#
#
# Strings
#
#

#
# Default Labels
#

labels_en_au_desc = 'Default Labels (en-au)'
labels_en_au_dict = {
	'DAY' : 'Day',
	'DESCRIPTION' : 'Description',
	'GREGORIAN_MONTH_1' : 'January',
	'GREGORIAN_MONTH_2' : 'February',
	'GREGORIAN_MONTH_3' : 'March',
	'GREGORIAN_MONTH_4' : 'April',
	'GREGORIAN_MONTH_5' : 'May',
	'GREGORIAN_MONTH_6' : 'June',
	'GREGORIAN_MONTH_7' : 'July',
	'GREGORIAN_MONTH_8' : 'August',
	'GREGORIAN_MONTH_9' : 'September',
	'GREGORIAN_MONTH_10' : 'October',
	'GREGORIAN_MONTH_11' : 'November',
	'GREGORIAN_MONTH_12' : 'December',
	'HOUR' : 'Hour',
	'MINUTE' : 'Minute',
	'MONTH' : 'Month',
	'NAME' : 'Name',
	'NONE' : '---',
	'PASSWORD' : 'Password',
	'PASSWORD_QL' : 'Quick List Password',
	'PASSWORD_CURRENT' : 'Current Password',
	'PASSWORD_NEW' : 'New Password',
	'PASSWORD_NEW_CONFIRM' : 'Confirm New Password',
	'QL_IMPORT_TO_GROUP' : 'Import into Group',
	'REASON' : 'Reason',
	'REASON_NONE' : 'No Reason Given',
	'SECOND' : 'Second',
	'TIME_ZONE' : 'Time Zone',
	'TIMER_CREATE_HISTORICAL' : 'Create a Historical Timer',
	'TIMER_FIRST_HISTORY' : 'First History Entry',
	'TIMER_USE_CURRENT_DATE_TIME' : 'Use the current Date and Time',
	'TIMER_DEFAULT_CREATION_REASON' : 'Timer Created.',
	'TIMER_DEFAULT_DESCRIPTION' : 'A Timer Without a Purpose',
	'TIMER_GROUP' : 'Timer Group',
	'TIMER_GROUP_DEFAULT_TITLE' : 'Timer Query',
	'TIMER_GROUP_DEFAULT_PRIVATE_TITLE' : 'Private Timers',
	'TIMER_GROUP_DEFAULT_PUBLIC_TITLE' : 'Shared Timers',
	'TIMER_GROUP_DEFAULT_LONGEST_RUNNING_TITLE' : "Longest Running Timers",
	'TIMER_GROUP_DEFAULT_SHORTEST_RUNNING_TITLE' : "Recently Reset Timers",
	'TIMER_GROUP_DEFAULT_NEWEST_TITLE' : "Newest Timers",
	'TIMER_GROUP_PERSONAL_INDEX_TITLE' : 'All Your Timers',
	'TIMER_LT_ONE_MINUTE' : 'Just Now',
	'TIMER_RENAME_NOTICE' : 'Timer description changed to: {0}',
	'TIMER_RESET_NOTICE' : 'Timer reset ({0}).',
	'TIMER_RESUME_NOTICE' : 'Timer restarted',
	'TIMER_STOP_NOTICE' : 'Timer Stopped ({0})',
	'TIMER_SUSPEND_NOTICE' : "Timer suspended ({0})",
	'USERNAME' : 'Username:',
	'YEAR' : 'Year',
	}
labels = PADSStringDictionary(labels_en_au_dict, labels_en_au_desc)

#
#  Default Messages
#

#  NOTE: There should be a space at the end of every line of a 
#  multi-line string

messages_en_au_desc = 'Default Messages (en-au)'
messages_en_au_dict = {
		'TEST_MANUAL_MODE_WELCOME' 
			: '''If you are in an interactive Python console, run 
			setup_test_environment() or test_manual.setup_test_environment() 
			to manually run View Tests.''',

		'TIMER_DELETE_SUCCESS' : '''The Timer was deleted: {0}''',
		
		'TIMER_DELETE_ERROR' 
			: '''Your timer was not deleted due to a problem, please 
			try again later.''',

		'TIMER_NEW_SUCCESS': '''Timer Created: ''',

		'TIMER_NEW_INVALID_INFO'
			: '''The Timer settings you specified are not valid. This is 
			most likely due to entering a date past the last day for a 
			particular month, such as a February 29th on a non-leap year.''',
		
		'TIMER_NOT_FOUND' : '''Timer not found or available. ''',
		
		'TIMER_SETTINGS_ADDED_TO_GROUP'
			: '''Your Timer has been added to the group.''',
		
		'TIMER_SETTINGS_DESC_CHANGED'
			: '''Your Timer's description has been changed to: {0}''',

		'TIMER_SETTINGS_HISTORICAL_TIMER_STOPPED'
			:'''The Historical Timer {0} has been stopped. We
			hope that the future will be brighter for you.''',
		
		'TIMER_SETTINGS_INVALID_REQUEST' : '''Invalid Request.''',

		'TIMER_SETTINGS_REMOVED_FROM_GROUP'
			: '''Your Timer has been removed from the group.''',

		'TIMER_SETTINGS_TIMER_RESET'
			: '''Your Timer has been reset: {0}''' ,
			
		'TIMER_SETTINGS_TIMER_RESUMED'
			: '''Your Timer has been reset and is counting again! ({0})''',

		'TIMER_SETTINGS_TIMER_SHARED'
			: '''Your Timer has been made public for the world to see!
				({0})''',
		
		'TIMER_SETTINGS_TIMER_SUSPENDED'
			: '''Your Timer has been suspended. ({0})''',
		
		'TIMER_SETTINGS_TIMER_UNSHARED'
			: '''Your Timer has been made private again. ({0})''',
		
		'TIMER_SETTINGS_SAVE_ERROR'
			: '''Due to a problem, your Timer's settings were not saved.''',
		
		'TIMER_SETTINGS_WRONG_USER'
			: '''You can only edit Timers that you have created, and 
				only after signing in. ''',
		
		'USER_NAME_INVALID_CHARACTERS'
			: '''It appears that you are attempting 
			to use a username that is made entriely of, or contains, 
			disallowed characters. Please try again with a regular username 
			of letters and numbers.''',
			
		'USER_NAME_NOT_ALLOWED'
			: '''This username you were attempting to 
			use is not allowed. Try a different sounding name?''',
		
		'USER_NOT_FOUND' : '''User not found.''',
		
		'USER_PASSWORD_CONFIRM_FAILED'
			: '''The password confirmation did not match the password you 
			entered. You have to enter your password correctly twice 
			before using it.''',
		
		'USER_SETTINGS_INVALID_REQUEST' : '''Invalid request.''',

		'USER_SETTINGS_REDIRECT'
			: '''Please change your settings at the setup page.''',

		'USER_SETTINGS_PASSWORD_CHANGED'
			: '''Your password has been changed. Please recall it
				regularly to remember it.''',
		
		'USER_SETTINGS_QL_NOT_SUPPORTED'
		   : '''This feature is not supported with a Quick List.''',
		
		'USER_SETTINGS_QL_IMPORT_SUCCESS'
			:'''Quick List imported successfuly! The Quick List is no
				longer available.''',

		'USER_SETTINGS_QL_IMPORT_FAILURE'
			:'''The Quick List import failed. This may be due to an
				incorrect Quick List password, an attempt to import
				a deleted Quick List or a technical difficulty.''',

		'USER_SETTINGS_DELETE_TIMER_GROUP_SUCCESS'
			:'''Timer Group Deleted: {0}''',

		'USER_SETTINGS_NEW_TIMER_GROUP_FAILURE'
			:'''We were unable to create your timer group, either
				because there is another existing group with the same
				name, or because there was a techinical difficulty. ''',

		'USER_SETTINGS_NEW_TIMER_GROUP_SUCCESS'
			:'''Timer Group Created: {0}''',

		'USER_SETTINGS_TIME_ZONE_CHANGED'
			: '''Your time zone has been changed to {0}''',

		'USER_SETTINGS_SAVE_ERROR'
			: '''Your settings were not saved due to a technical 
				difficulty. Please try again later.''',				

		'USER_SIGN_IN_INVALID_CREDS'
			: '''Sign in credentials rejected. 
			This may be because your have attempted to sign in with 
			a blank username or password.''',
				
		'USER_SIGN_IN_REDIRECT'
			: '''Please sign in with your username and password,
			or with a Quick List password from the sign-in screen.''',
		
		'USER_SIGN_IN_REQUIRED'
			: '''You must sign in first to do that. ''',
		
		'USER_SIGN_IN_SUCCESS' : '''Welcome Back, {0}''',

		'USER_SIGN_IN_QL_SUCCESS' : '''Welcome Back!''',
		
		'USER_SIGN_IN_QL_MALFORMED_PASSWORD'
			: '''Please check your Quick List password. It should start 
			with a number and have at least two segments.''',
				
		'USER_SIGN_IN_WRONG_PASSWORD'
			: '''Your sign-in password or username is incorrect. 
			Please try again.''',
		
		'USER_SIGN_IN_QL_WRONG_PASSWORD' 
			: '''A Quick List of the password you entered was not found. 
			Check your password and try again. If a Quick List has been 
			imported into a regular User Account, it is no longer 
			available.''',

		'USER_SIGN_OUT_SUCCESS'
			:  '''You have been signed out. Please close the browser or 
			tab to help protect your account. See you again!''',

		'USER_SIGN_UP_DB_ERROR'
			: '''We were unable to register your account right now 
			due to a technical problem, please try again later.''',

		'USER_SIGN_UP_QL_DB_ERROR'
			: '''We were unable to create a Quick List at this time  
			due to a technical problem, please try again later.''',
			
		'USER_SIGN_UP_SUCCESS'
			: '''Welcome to the Public Archive of 
			Days Since Timers! Sign in with your username and password 
			to begin.''',
			
		'USER_SIGN_UP_QL_SUCCESS'
			: '''You have created a Quick List.
			Please record or remember this password and use it
			to sign in: ''',
			
		'USER_SIGN_UP_NAME_NOT_AVAILABLE'
			: '''This username you were attempting to use 
			is not available. Try a different name?''',
	}
messages = PADSStringDictionary(messages_en_au_dict, messages_en_au_desc)

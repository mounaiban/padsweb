#
#
# Public Archive of Days Since Timers
# Miscellaneous Helper Classes and Functions
#
#

#
# Imports
#
from django.utils import timezone
from pytz import all_timezones

# Standard Library Imports
import random

#
# Classes
#

class NonMetricMeasureInt:
	"""The NonMetricMeasureInt class is intended to provide an easy way
	to manage non-metric currencies and measurements such as 
	pre-decimalisation pound sterling (Lsd), many non-S.I. units of 
	measure, and in PADS, the days-hours-minutes-seconds measure of time.
	
	At the moment, this class only supports integer measures.
	"""
	
	#
	# Class attributes
	#
	
	# The separator is a string and multiple character separators 
	# are totally fine.
	DEFAULT_SEPARATOR_STR = ", "
	
	def set_value(self, decimal_int_value):
		self.decimal_int_value = decimal_int_value

	def set_separator_str(self, separator_str):
		self.separator_str = separator_str

	def get_measure(self, measure):
		"""Returns a single measure."""
		self.measures = self.get_measures()
		return self.measures.get(measure)

	def get_measures(self):
		"""Returns all measures in a dictionary."""
		output = dict()
		working_value = self.decimal_int_value
	
		# The number of labels and radixes should match. In case of a
		# mismatch, excess labels or radixes will be ignored.
		pairs = zip(self.unit_labels, self.limits)
		
		# The measures are derived by cumulative division, and recording
		# the result of every division. 
		for p in list(pairs):
			label = p[0]
			radix = p[1]
			output[label] = int(working_value % radix)
			working_value /= radix
			
		# If there is some value left after positions have been filled
		output[self.overflow_unit_label] = int(working_value)
		return output
	
	def get_string(self, **kwargs):
		"""Returns all measures in a string.
		When the zeroes option is set to True, zero measures will be
		included in the string.
		"""
		output = ""
		measures = self.get_measures()
		zeroes = kwargs.get('zeroes', True)
		
		# Build string from measures in dictionary, one-by-one
		for u in self.get_units():
			u_value = measures[u]
			if ( (u_value == 0) & (zeroes != True) ):
				pass
			else:
				current_measure = "{0} {1}{2}".format(
					u_value, u, self.separator_str)
				output = ''.join([current_measure, output])
				
		# Add a negative sign if negative
		if self.negative == True:
			output = ''.join(['-', output])
			
		# Clean up and return string
		# TODO: Find a more elegant way to build strings without 
		# needing to rstrip.
		return output.rstrip(self.separator_str)
		
	def get_units(self):
		"""Returns all units including the overflow unit in a tuple."""
		output = list(self.unit_labels)
		output.append(self.overflow_unit_label)
		return tuple(output)
		
	#
	# Special Methods
	#
	def __init__(self, unit_labels, overflow_unit_label, limits, decimal_int_value):
		"""How to use NonMetricMeasureInt
		
		Specify unit_labels and limits in tuples.		
		Units are specified in order of the *smallest to the largest*,
		akin to little endian encoding. Limits are to correspond with
		unit labels; the first unit in the measure will use the first
		label from unit_labels and have a limit defined by the first
		value in limits.
		
		Next, specify overflow_unit_label as a string. This is the final
		measure that will be used if there is still some value left after
		cumulatively dividing by all limits.
		
		Finally, specify the value of the measure in the smallest unit,
		as decimal_int_value. Zero, negative and positive values are
		supported.

		For example:
		  - A pound was worth 20 shillings,
		  - A shilling was worth 12 pence and,
		  - A pence was worth 4 farthings.
		  You are to measure 240 pence.
		  
		  The unit_labels will be ('farthings', 'pence', 'shillings').
		  The overflow_unit_label will be 'pounds'.
		  The limits will be (4, 12, 20).
		  The decimal_int_value will actually be 960, because you have
		   to specify it in the smallest unit, which is the farthing.
		  
		  You should get a measure of exactly 1 pound.
		"""
		
		self.decimal_int_value = 0
		self.limits = limits
		self.negative = False
		self.overflow_unit_label = overflow_unit_label
		self.separator_str = self.DEFAULT_SEPARATOR_STR
		self.unit_labels = unit_labels

		# Set the initial decimal_int_value
		if decimal_int_value < 0:
			self.negative = True
			self.decimal_int_value = abs(decimal_int_value)
		else:
			self.decimal_int_value = decimal_int_value
	
	def __str__(self):
		return self.get_string(zeroes=True)

	def __repr__(self):
		return self.__str__()

		
#
# Functions
#
def get_timezones_all():
	"""Dump the list of timezones from ptyz into a format suitable 
	for use with the Django Forms API's ChoiceField
	"""
	# TODO: Find a more user-friendly way of managing 500+ timezones

	output = []
	for tz in all_timezones:
		output.append( (tz, tz) )
	return output

def split_posint_rand(i, n):
	""" Split a positive integer i into four random numbers that add up
	to itself. Returns a list of positive integers. Specify the number
	of numbers as n.
	"""
	# Reject non-positive integers and zero.
	if i <= 0 or n <= 0:
		return None
	# Short-cut codepath when n is just 1 (just return the same value)
	if n == 1:
		return [i]
	# Handle all other cases
	else:
		result = []
		# Perform cumulative division and subtraction, remembering the
		# result of the every division as we go along.
		#
		# Beginner's PROTIP: The number of divisions we perform is one 
		# less than n, because we are making divisions on the scalar
		# value instead of populating existing divisions. To put it
		# in perspective, to split a basket into three compartments
		# requires two divisions to be made, hence two iterations.
		for j in range(n-1, 0, -1):
			# Generate a number not too different from half of the current i
			s = int(random.gauss(i/2, 0.3) )
			# Ensure s is at least 1
			if s < 1:
				s = 1
			# Save into the results list
			result.append(s)
			# Subtract s from i
			i -= s
		# Finally, add the last number
		result.append(i)
	return result

def str_is_empty_or_space(s):
	"""Checks if a string from a form submitted via a web page *looks 
	like or is* an empty string.
	
	At one stage this was called a 'perceptual null'.
	"""
	if s:
		# A string isn't empty if it is at least one character long
		# A string doesn't look empty if it is not entirely composed of
		#  whitespace.
		if (len(s) > 0) & (s.isspace() == False):
			return False
	else:
		return True


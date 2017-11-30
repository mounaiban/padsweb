#
#
# Public Archive of Days Since Timers (PADS)
# Informal Manual Testing Environment Setup
#
#
"""To use the Manual Testing Environment in your Python console and
mess around with PADS, import this module. The default name is 
padsweb.tests_informal (ver 0.5x).
"""

#
#
# Imports
#
#

# Django Features
from django.test import Client
from django.test.utils import setup_test_environment
from django.urls import reverse

# Standard Library Imports
import datetime, random, secrets 

# Modules to be tested
from padsweb.forms import *
from padsweb.models import *
from padsweb.misc import *
from padsweb.timers import *
from padsweb.user import *
from padsweb.urls import *

# Manual Access to Automated Test Modules
from padsweb.tests.tests_views import *

# Other Stuff
from padsweb.strings import *


#
#
# Test Items
#
#

# Client
#  See: https://docs.djangoproject.com/en/1.11/topics/testing/tools/ 
client = Client()

# Helpers
user_helper = PADSUserHelper()
timer_helper = PADSTimerHelper()
timer_helper_public = PADSPublicTimerHelper()
longest = PADSLongestRunningTimerGroup()
longest_public = PADSLongestRunningTimerGroup(timer_helper_public)

#
#
# Miscellaneous Functions
#
#
def get_measure_by_timer_id(timer_id):
	return new_measure_from_view_timer(
		timer_helper.get_timer_for_view_by_id(timer_id))
	
def new_measure_from_view_timer(view_timer):
	return NonMetricMeasureInt(
		view_timer.UNITS, 
		view_timer.OVERFLOW_UNIT, 
		view_timer.UNIT_LIMITS, 
		int(view_timer.get_running_time_minutes()),)

#
#
# Welcome message
#
#
print(messages['TEST_MANUAL_MODE_WELCOME'].replace('\t',''))

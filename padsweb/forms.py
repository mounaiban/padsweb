#
#
# Public Archive of Days Since Timers
# Form Classes
#
#

from django import forms
from django.utils import timezone

from padsweb.settings import *
from padsweb.strings import labels
from padsweb.misc import get_timezones_all

# Python Beginner's PROTIP:
#
# Due to the way Django (1.11.2) initialises forms, For some of the 
# Fields in the Forms herein, the initial state had to be set from the 
# __init__ constructor, using a dictionary named 'initial'.
# A good example is ChoiceField.
#
# See: https://stackoverflow.com/a/11400559
# See Also: http://avilpage.com/2015/03/django-form-gotchas-dynamic-initial.html        

class TimerGroupForm(forms.Form):
    timer_group = forms.ChoiceField(
        label = labels['TIMER_GROUP'],)

    def __init__(self, *args, **kwargs):
        try:
            timer_group_choices = kwargs.pop('timer_group_choices')
        except:
            pass
        super().__init__(*args, **kwargs)
        # TODO: Find out why choices must be extended in both choices
        # and widget.choices, and why widget.choices wasn't automatically
        # extended along with choices.
        self.fields['timer_group'].widget.choices.extend(
            timer_group_choices)
        self.fields['timer_group'].choices.extend(
            timer_group_choices)

class QuickListImportForm(TimerGroupForm):
    password = forms.CharField(
        label=labels['PASSWORD_QL'],
        max_length=MAX_MESSAGE_LENGTH_SHORT,
        strip=True,)
    timer_group = forms.ChoiceField(
        label=labels['QL_IMPORT_TO_GROUP'],
        choices=[('', labels['NONE'])],
        required=False,)
        
class TimerRenameForm(forms.Form):
    description=forms.CharField(
        label=labels['DESCRIPTION'],
        max_length=MAX_MESSAGE_LENGTH_SHORT,
        strip=True,)    

class NewTimerForm(forms.Form):
    description = forms.CharField(
        label=labels['DESCRIPTION'],
        max_length=MAX_MESSAGE_LENGTH_SHORT,)
    first_history_message = forms.CharField(
        label=labels['TIMER_FIRST_HISTORY'],
        max_length=MAX_MESSAGE_LENGTH_SHORT,
        initial=labels['TIMER_DEFAULT_CREATION_REASON'],)
    year = forms.DecimalField(
        label = 'Year',
        max_value = 9999,
        min_value = 1,
        max_digits = 4,
        decimal_places = 0,)
    month = forms.ChoiceField(
            label = labels['MONTH'],
            choices = (
                (1, labels['GREGORIAN_MONTH_1']),
                (2, labels['GREGORIAN_MONTH_2']),
                (3, labels['GREGORIAN_MONTH_3']),
                (4, labels['GREGORIAN_MONTH_4']),
                (5, labels['GREGORIAN_MONTH_5']),
                (6, labels['GREGORIAN_MONTH_6']),
                (7, labels['GREGORIAN_MONTH_7']),
                (8, labels['GREGORIAN_MONTH_8']),
                (9, labels['GREGORIAN_MONTH_9']),
                (10, labels['GREGORIAN_MONTH_10']),
                (11, labels['GREGORIAN_MONTH_11']),
                (12, labels['GREGORIAN_MONTH_12']),
                ), )
    day = forms.DecimalField(
        label = labels['DAY'],
        max_digits = 2,
        max_value = 31,
        min_value = 1,
        decimal_places = 0,)
    hour = forms.DecimalField(
        label = labels['HOUR'],
        max_digits = 2,
        max_value = 23,
        min_value = 0,
        decimal_places = 0,)
    minute = forms.DecimalField(
        label = labels['MINUTE'],
        max_digits = 2,
        max_value = 59,
        min_value = 0,
        decimal_places = 0,)
    second = forms.DecimalField(
        label = labels['SECOND'],
        max_digits = 2,
        max_value = 59,
        min_value = 0,
        decimal_places = 0,)
    use_current_date_time = forms.BooleanField(
        label=labels['TIMER_USE_CURRENT_DATE_TIME'],
        required=False,
        initial=False,)
    historical = forms.BooleanField(
        label=labels['TIMER_CREATE_HISTORICAL'],
        required=False,
        initial=False,)
        
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)  # Important!
        self.start_datetime = timezone.now()
        self.initial = {
            'year' : self.start_datetime.year,
            'month': self.start_datetime.month,
            'day': self.start_datetime.day,
            'hour': self.start_datetime.hour,
            'minute': self.start_datetime.minute,
            'second': self.start_datetime.second,
            }

class NewTimerGroupForm(forms.Form):
    name = forms.CharField(
        label=labels['NAME'],
        strip=True,
        max_length = MAX_NAME_LENGTH_SHORT,)

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label=labels['PASSWORD_CURRENT'], 
        widget=forms.PasswordInput,
        strip=False,
        max_length=MAX_MESSAGE_LENGTH_SHORT,
        min_length=MIN_USER_PASSWORD_LENGTH,)
    new_password = forms.CharField(
        label=labels['PASSWORD_NEW'], 
        widget=forms.PasswordInput,
        strip=False,
        max_length=MAX_MESSAGE_LENGTH_SHORT,
        min_length=MIN_USER_PASSWORD_LENGTH,)
    new_password_confirm = forms.CharField(
        label=labels['PASSWORD_NEW_CONFIRM'], 
        widget=forms.PasswordInput, 
        strip=False,
        max_length=MAX_MESSAGE_LENGTH_SHORT,
        min_length=MIN_USER_PASSWORD_LENGTH,)
    user_id = forms.CharField(
        widget=forms.HiddenInput,)

class SignInForm(forms.Form):
    username = forms.SlugField(
        label=labels['USERNAME'], 
        max_length=MAX_NAME_LENGTH_SHORT,
        )    
    password = forms.CharField(
        label=labels['PASSWORD'],
        widget=forms.PasswordInput,
        strip=False,
        max_length=MAX_MESSAGE_LENGTH_SHORT,
        min_length=1,)

class SignInQuickListForm(forms.Form):
    password = forms.CharField(
        label=labels['PASSWORD_QL'],
        max_length=MAX_MESSAGE_LENGTH_SHORT,
        strip=True,)

class SignUpForm(forms.Form):
    username = forms.SlugField(
        label=labels['USERNAME'], 
        max_length=MAX_NAME_LENGTH_SHORT,
        min_length=MIN_USERNAME_LENGTH,)
    password = forms.CharField(
        label=labels['PASSWORD'], 
        widget=forms.PasswordInput,
        strip=False,
        max_length=MAX_MESSAGE_LENGTH_SHORT,
        min_length=MIN_USER_PASSWORD_LENGTH,)
    password_confirm = forms.CharField(
        label=labels['PASSWORD_NEW_CONFIRM'], 
        widget=forms.PasswordInput, 
        strip=False,
        max_length=MAX_MESSAGE_LENGTH_SHORT,
        min_length=MIN_USER_PASSWORD_LENGTH,)

class ReasonForm(forms.Form):
    reason = forms.CharField(
        label=labels['REASON'],
        initial=labels['REASON_NONE'],
        max_length=MAX_MESSAGE_LENGTH_SHORT,
        min_length=1,)

class TimeZoneForm(forms.Form):
    time_zone = forms.ChoiceField(
        label=labels['TIME_ZONE'],
        choices=get_timezones_all(),)

class TimerGroupNamesForm(forms.Form):
    text_line = forms.CharField(
            label=labels['TIMER_GROUP_FIELD'],
            max_length=MAX_MESSAGE_LENGTH_SHORT,
            min_length=1,)

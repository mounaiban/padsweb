#
#
# Public Archive of Days Since Timers
# Hard-coded Configuration
#
#

from padsweb.strings import PADSStringDictionary

#
# Hard-coded configuration in dictionary
#
app_metadata = {
        'copyright_message_html' : '&copy; 2018 Mounaiban',
        'current_version' : '0.590',
        }

defaults_content = {
        'view_items_per_page' : 6,
        'user_id_signed_out' : -1, # User id when no User has signed in
        }
defaults = PADSStringDictionary(defaults_content,
                                "PADS Hard-coded Default Settings")

#
# Hard-coded configuration in separate constants
# TODO: Migrate codebase to use dictionary only, then remove these constants
#

# App Metadata
PADS_CURRENT_VERSION = '0.587'

# App Miscellaneous Settings
MAX_NAME_LENGTH_SHORT = 24
MAX_NAME_LENGTH_LONG = 255
MAX_MESSAGE_LENGTH_SHORT = 280 # Two Tweets

# User Account Settings (Applies also to Quick List)
SALT_BYTES = 48
MIN_USERNAME_LENGTH = 6
MIN_USER_PASSWORD_LENGTH = 8

# Description and Title Settings
SINGLE_LINE_RSTRIP_CHARS = ' \n\r\t' # Spaces, Newlines, CR's, Tabs

# Quick List Settings
ANONYMOUS_USER_SHORT_NICKNAME_PREFIX = "Quick List User"
ANONYMOUS_USER_SUFFIX_LENGTH = 12
#  The letter 'O' and number '1' are omitted:
PARTIAL_ALPHANUM_UPPER = "ABCDEFGHIJKLMNPQRSTUVWXYZ234567890"
RANDOM_PASSWORD_LENGTH = 8
RANDOM_PASSWORD_MAX_SEGMENTS = 3
RANDOM_PASSWORD_SEGMENT_SEPARATOR = '-'

# Timer Settings
TIMERS_RECENT_RESET_MAX_AGE = 7
TIMERS_DESCRIPTION_LENGTH_SHORT = 140 # One Tweet
TIMERS_PERMALINK_CODE_LENGTH = 10

# View Settings
INVALID_SESSION_ID = None
SEARCH_TERMS_MIN_LEN = 4
INDEX_PAGE_SIZE = 6
INDEX_DEFAULT_NATURAL_PAGE = 1

# Deprecated View Settings
MIN_SEARCH_TERMS_LEN = 4
MAX_TOP_ITEMS = 3

#  Banner CSS Classes
BANNER_FAILURE_DENIAL = 'banner-failure-denial' # Operation was intentionally not performed
BANNER_FAILURE_ERROR = 'banner-failure-error' # Operation failed due to an error
BANNER_INFO = 'banner-info' # Miscellaneous information
BANNER_SUCCESS = 'banner-success'  # Operation was successful

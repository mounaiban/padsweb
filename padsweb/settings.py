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
        # Please do not alter app metadata during normal operation
        'copyright_message_html' : '&copy; 2018 Mounaiban',
        'current_version' : '0.588-pre590',
        }

defaults_content = {
        # The letter 'O' and number '1' are omitted
        'ql_password_letters' : 'ABCDEFGHIJKLMNPQRSTUVWXYZ234567890',
        'ql_password_length' : 8,
        'ql_password_max_segments' : 3,
        'ql_password_seg_separator' : '-',
        'ql_user_name_suffix_length' : 12,
        'password_salt_bytes' : 48,
        'user_id_signed_out' : -1, # User id when no User has signed in
        'view_items_per_page' : 6,
        }
defaults = PADSStringDictionary(defaults_content,
                                "PADS Hard-coded Default Settings")

#
# Hard-coded configuration in separate constants
# TODO: Migrate codebase to use dictionary only, then remove these constants
#

# App Metadata
PADS_CURRENT_VERSION = '0.588'

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

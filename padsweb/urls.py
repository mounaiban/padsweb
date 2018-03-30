#
#
# Public Archive of Days Since Timers
# Routes
#
#

from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'padsweb'
urlpatterns = [
    #
    # Timer Read URLs
    # 
    # Public Index
    url(r'^$', views.index, name='index'),
    url(r'^timers/$', views.index, name='index_alt'),
    # Personal Index
    url(r'^timers/personal/$', views.index_personal, name='index_personal'),
    # Private Timers by User (private)
    url(r'^timers/personal/private/$', views.index_private_by_user, 
        name='index_private_by_user'),
    # Personal Timer Groups Index for signed-in User (private)
    url(r'^timers/personal/groups/$', views.index_personal_groups, 
        name='index_personal_groups'),
    # Timers by Group
    url(r'^timers/group/(?P<timer_group_id>[0-9]+)/$', 
        views.index_group, name='index_group'),
    # Shared Timers by User 
    url(r'^timers/shared/user/(?P<user_id>[0-9]+)/$', 
        views.index_shared_by_user, name='index_shared_by_user'),
    # Longest Running Timers
    url(r'^timers/shared/longest_running/$', 
        views.index_longest_running, name='index_longest_running'),    
    # Recently Reset Timers
    url(r'^timers/shared/recent_resets/$', views.index_recent_resets,
        name='index_recent_resets'),    
    # Newest Timers
    url(r'^timers/shared/newest/$', views.index_newest, name='index_newest'),    
    
    #
    # Timer URLs
    #
    # Timer Detail View:
    url(r'^timer/(?P<timer_id>[0-9]+)/$', views.timer, name='timer'),
    # Timer Detail Vies, via Permalink
    path('timer/link/<slug:link_code>/',
         views.timer_by_permalink, name='timer_by_permalink'),
    # Timer Export to JSON
    url(r'^timer/export/(?P<timer_id>[0-9]+)/$', views.timer_export, 
        name='timer_export'),

    #
    # Timer Configuration URLs
    #
    # Timer Creation
    url(r'^timer/new/$', views.timer_new, name='timer_new'),
    # Timer Delete
    url(r'^timer/(?P<timer_id>[0-9]+)/delete/$', views.timer_del, 
        name='timer_del'),
    # Timer Reset
    url(r'^timer/(?P<timer_id>[0-9]+)/reset/$', views.timer_reset, 
        name='timer_reset'),
    # Timer Share
    url(r'^timer/(?P<timer_id>[0-9]+)/share/$', views.timer_share, 
        name='timer_share'),
    # Timer Unshare    
    url(r'^timer/(?P<timer_id>[0-9]+)/unshare/$', views.timer_unshare, 
        name='timer_unshare'),
    # Timer Rename    
    url(r'^timer/(?P<timer_id>[0-9]+)/rename/$', views.timer_rename, 
        name='timer_rename'),    
    # Timer Suspend / Stop
    url(r'^timer/(?P<timer_id>[0-9]+)/stop/$', views.timer_stop, 
        name='timer_stop'),
    # Add Timer to Group
    url(r'^timer/(?P<timer_id>[0-9]+)/add_to_group/$', 
        views.timer_add_to_group, name='timer_add_to_group'),    
    # Remove Timer from Group    
    url(r'^timer/(?P<timer_id>[0-9]+)/remove_from_group/$', 
        views.timer_remove_from_group, name='timer_remove_from_group'),    
    
    #
    # User Account URLs
    #
    # User Sign In
    url(r'^sign_in/$', views.session_new, name='session'),
    # Quick List User Sign In
    url(r'^sign_in/quicklist/$', views.session_quicklist, 
        name='session_quicklist'),        
    # User Sign Out
    url(r'^sign_out/$', views.session_end, name='session_end'),
    # User Sign Up Intro
    url(r'^sign_up/$', views.sign_up_sign_in_intro, name='sign_up_intro'),
    # User Sign Up
    url(r'^sign_up/user/$', views.user_new, name='sign_up_user'),
    # Quick List User Sign Up
    url(r'^sign_up/quicklist/$', views.quicklist_new, 
        name='sign_up_quicklist'),

    #
    # User Account Configuration URLs
    #
    # User Settings
    url(r'^setup/$', views.settings_info, name='settings_info'),
    # User Settings: new Timer Group
    url(r'^timers/group/new/$', views.settings_new_timer_group, 
        name='settings_new_timer_group'),
    # User Settings: delete Timer Group
    url(r'^timers/group/delete$', views.settings_delete_timer_group, 
        name='settings_delete_timer_group'),
    # User Settings Password Change
    url(r'^setup/password$', views.settings_set_password, 
        name='settings_set_password'),    
    # User Settings Time Zone Change
    url(r'^setup/time_zone', views.settings_set_tz, name='settings_set_tz'),
    # User Settings Import Quick List
    url(r'^setup/import_ql/$', views.settings_import_ql, 
        name='settings_import_ql'),
     # User Info Export to JSON
    url(r'^setup/export_all', views.user_export_all, name='user_export_all')
        
    ]

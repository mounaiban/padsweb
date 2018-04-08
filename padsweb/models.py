#
#
# Public Archive of Days Since Timers
# Django Models
#
#

from django.db import models
from padsweb.settings import defaults

settings = defaults

class PADSUser(models.Model):
    password_hash = models.CharField(
            max_length=settings['message_max_length_short'])
    sign_up_date_time = models.DateTimeField()
    last_login_date_time = models.DateTimeField()
    # The Short Nickname is to enforce the use of ASCII-friendly
    # nicknames for signing in, while allowing Users to have a more 
    # freeform one with non-Roman characters.
    nickname_short = models.SlugField(
            max_length=settings['message_max_length_short'], unique=True)
    nickname = models.CharField(
            max_length=settings['message_max_length_short'])
    # TODO: Find out the maximum length of a tz database entry name
    time_zone = models.CharField(
            max_length=settings['name_max_length_long'])
    def __str__(self):
        return "{0} ({1})".format(self.nickname_short)
    

class PADSTimerGroup(models.Model):
    """Timer Groups are used for organising Timers"""
    name = models.CharField(max_length=settings['message_max_length_short'])
    creator_user = models.ForeignKey(PADSUser, on_delete=models.CASCADE)
    
    def __str__(self):
        return "({0}) {1} by ({2}) {3}".format(
            self.id, self.name, self.creator_user_id, self.creator_user)

    class Meta:
        # A user may only have one group of the same name
        unique_together = (("creator_user","name"))

class PADSTimer(models.Model):
    """A long-term count-up timer"""
    creation_date_time = models.DateTimeField()
    count_from_date_time = models.DateTimeField()
    description = models.CharField(
            max_length=settings['message_max_length_short'])
    creator_user = models.ForeignKey(PADSUser, on_delete=models.CASCADE)
    public = models.BooleanField()
    historical = models.BooleanField()
    running = models.BooleanField()
    permalink_code = models.CharField(
            max_length=settings['timer_permalink_code_length'])
    in_groups = models.ManyToManyField(
        PADSTimerGroup,
        through = 'GroupInclusion',
        through_fields = ('timer','group')
    )

    def __str__(self):
        if len(self.description) > settings['name_max_length_short']:
            return "{0}: {1}...".format(
            self.pk, self.description[:settings['name_max_length_short']])
        else:
            return "{0}: {1}".format(self.pk, self.description)


class GroupInclusion(models.Model):
    """Through Model which determines which Groups a Timer belongs to"""
    timer = models.ForeignKey(PADSTimer, on_delete=models.CASCADE)
    group = models.ForeignKey(PADSTimerGroup, on_delete=models.CASCADE)

    def __str__(self):
        return "{0} is in {1}".format(self.timer.id, self.group.id)

    class Meta:
        # A timer may only be in a group once
        unique_together = (("timer", "group"))


class PADSTimerReset(models.Model):
    """An entry in a Timer's Reset History"""
    timer = models.ForeignKey(PADSTimer, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    reason = models.CharField(max_length=settings['message_max_length_short'])

    def __str__(self):
        return "({0}) {1}".format(self.date_time,self.reason)

    class Meta:
        # A timer may only be reset once at the same exact moment
        unique_together = (("timer", "date_time"))

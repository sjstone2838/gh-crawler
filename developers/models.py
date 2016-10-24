from __future__ import unicode_literals

from django.db import models

class Developer(models.Model):
    login = models.CharField(max_length=200, blank=False, unique=True)
    gh_id = models.IntegerField(blank=False, unique=True)
    url = models.URLField(max_length=500, blank=False, unique=True)
    gh_type = models.CharField(max_length=200)
    site_admin = models.CharField(max_length=200)
    name = models.CharField(max_length=500, blank=True, null=True)
    company = models.CharField(max_length=500, blank=True, null=True)
    blog = models.CharField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=500, blank=True, null=True)
    email = models.CharField(max_length=500, blank=True, null=True)
    hireable = models.CharField(max_length=500, blank=True, null=True)
    bio = models.CharField(max_length=501, blank=True, null=True)
    public_repos = models.IntegerField(blank=True, null=True)
    public_gists = models.IntegerField(blank=True, null=True)
    followers = models.IntegerField(blank=True, null=True)
    following = models.IntegerField(blank=True, null=True)
    gh_created_at = models.DateTimeField(blank=True, null=True)
    gh_updated_at = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.login

class Event(models.Model):
    actor = models.ForeignKey('Developer', blank=False, null=False)
    gh_type = models.CharField(max_length=500, blank=False, null=False)
    public = models.BooleanField(blank=False, null=False)
    payload = models.TextField(blank=True, null=True)
    repo_id = models.IntegerField(blank=True, null=True)
    repo_name = models.CharField(max_length=500, blank=True, null=True)
    repo_url = models.CharField(max_length=500, blank=True, null=True)
    gh_actor_id = models.IntegerField(blank=True, null=True)
    actor_login = models.CharField(max_length=200, blank=False, null=False)
    org_id = models.IntegerField(blank=True, null=True)
    org_login = models.CharField(max_length=200, blank=True, null=True)
    gh_created_at = models.DateTimeField(blank=False, null=False)
    gh_id = models.CharField(max_length=200,
                             blank=True, null=True, unique=True)
    other = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return '{} by {} on {}'.format(
            self.gh_type, self.actor, self.gh_created_at)

TEMPORAL_PREDICTOR_REFERENCES = (
    ('CommitCommentEvent', 'CommitCommentEvent'),
    ('CreateEvent', 'CreateEvent'),
    ('DeleteEvent', 'DeleteEvent'),
    ('ForkEvent', 'ForkEvent'),
    ('GistEvent', 'GistEvent'),
    ('GollumEvent', 'GollumEvent'),
    ('IssueCommentEvent', 'IssueCommentEvent'),
    ('IssuesEvent', 'IssuesEvent'),
    ('MemberEvent', 'MemberEvent'),
    ('PublicEvent', 'PublicEvent'),
    ('PullRequestEvent', 'PullRequestEvent'),
    ('PullRequestReviewCommentEvent', 'PullRequestReviewCommentEvent'),
    ('PushEvent', 'PushEvent'),
    ('ReleaseEvent', 'ReleaseEvent'),
    ('WatchEvent', 'WatchEvent')
)

TEMPORAL_PREDICTOR_FORMULAS = (
    ('Count', 'Count'),
    ('Sum', 'Sum'),
)

# Example: ForkEvent_count_2014_01
class TemporalPredictor(models.Model):
    reference = models.CharField(max_length=200, blank=False, null=False,
                                 choices=TEMPORAL_PREDICTOR_REFERENCES)
    formula = models.CharField(max_length=200, blank=False, null=False,
                               choices=TEMPORAL_PREDICTOR_FORMULAS)
    developer = models.ForeignKey('Developer', blank=False, null=False)
    statistic = models.FloatField(blank=False, null=False)
    period = models.DateTimeField(blank=False, null=False)

    def __unicode__(self):
        return '{}_{}_{}'.format(self.reference, self.formula, self.period)

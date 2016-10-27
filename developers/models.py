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
    ('WatchEvent', 'WatchEvent'),
    ('QualityPROpened', 'QualityPROpened'),
    ('QualityPRClosed', 'QualityPRClosed')
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
    year = models.IntegerField(blank=False, null=False)
    month = models.IntegerField(blank=False, null=False)

    def __unicode__(self):
        return '{}_{}_{}-()'.format(self.reference, self.formula,
                                    self.year, self.month)

class Repo(models.Model):
    gh_id = models.IntegerField(blank=False, null=False)
    name = models.CharField(max_length=500, blank=False, null=False)
    full_name = models.CharField(max_length=500,
                                 blank=False, null=False, unique=True)
    owner = models.ForeignKey('Developer', blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    fork = models.BooleanField(blank=False, null=False)
    created_at = models.DateTimeField(blank=False, null=False)
    updated_at = models.DateTimeField(blank=False, null=False)
    pushed_at = models.DateTimeField(blank=False, null=False)
    homepage = models.CharField(max_length=500, blank=True, null=True)
    size = models.IntegerField(blank=False, null=False)
    stargazers_count = models.IntegerField(blank=False, null=False)
    watchers_count = models.IntegerField(blank=False, null=False)
    # Language can be null, if repository is empty
    # For example:  https://api.github.com/repos/rforge/adrminer
    language = models.CharField(max_length=500, blank=True, null=True)
    has_issues = models.BooleanField(blank=False, null=False)
    has_downloads = models.BooleanField(blank=False, null=False)
    has_wiki = models.BooleanField(blank=False, null=False)
    has_pages = models.BooleanField(blank=False, null=False)
    forks_count = models.IntegerField(blank=False, null=False)
    mirror_url = models.CharField(max_length=500, blank=True, null=True)
    open_issues_count = models.IntegerField(blank=False, null=False)
    forks = models.IntegerField(blank=False, null=False)
    open_issues = models.IntegerField(blank=False, null=False)
    watchers = models.IntegerField(blank=False, null=False)
    default_branch = models.CharField(max_length=500, blank=False, null=False)

    def __unicode__(self):
        return self.full_name

class PullRequest(models.Model):
    event = models.OneToOneField('Event', blank=False, null=False, unique=True)
    action_initiator = models.ForeignKey('Developer', blank=False, null=False)
    url = models.CharField(max_length=500, blank=False, null=False)
    action = models.CharField(max_length=200, blank=False, null=False)
    opener = models.CharField(max_length=500, blank=False, null=False)
    repo_still_exists = models.NullBooleanField(blank=True, null=True)
    merged = models.NullBooleanField(blank=True, null=True)
    closer = models.CharField(max_length=500, blank=True, null=True)
    self_referential = models.NullBooleanField(blank=True, null=True)

    def __unicode__(self):
        return self.url

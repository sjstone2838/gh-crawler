from django.conf import settings
from django.core.management.base import BaseCommand

from developers.models import Event
from developers.models import Developer
from developers.models import PullRequest

import json
import requests

class Command(BaseCommand):
    help = """
    python manage.py parse_pr_since_id [pk_min] [pk_max]

    Classify and save TemporalPredictor objects based on
    PullRequestEvents from developers with pks between
    [pk_min] and [pk_max]
    """

    def __init__(self):
        self.auth = 'client_id={}&client_secret={}'.format(
            settings.GITHUB_CLIENT_ID,
            settings.GITHUB_CLIENT_SECRET
        )

    def add_arguments(self, parser):
        parser.add_argument('pk_min', nargs='+')
        parser.add_argument('pk_max', nargs='+')

    def parse_pull_request(self, pr, initiator):
        payload = json.loads(pr.payload)

        # Developer tagged in the event from GithubArchive has closed
        # the pull request; this does not necessarily mean s/he opened it
        # or that it was merged
        if payload['action'] == 'closed':
            self.handle_pr_closure(payload, initiator, pr)

        # Developer tagged in the event from GithubArchive has opened
        # a pull request; this PR may or may not be for one of his/her
        # own repos ('self-referential') and we need to query the GH API
        # to find out if the PR was closed, and if so, by whom
        elif payload['action'] in ['opened', 'reopened']:
            self.handle_pr_opening(payload, initiator, pr)

        else:
            print '\n\n\nUnknown pull request action: {}\n\n\n'.format(
                payload['action']
            )

    def handle_pr_closure(self, payload, initiator, event):
        self_ref = (payload['pull_request']['user']['login'] ==
                    initiator.login)
        merged = payload['pull_request']['merged']
        self.create_pr_object(self_ref, merged, payload, initiator, event)

    def handle_pr_opening(self, payload, initiator, event):
        url = payload['pull_request']['_links']['self']['href']
        response = requests.get('{}?{}'.format(url, self.auth))

        if response.status_code == 200:
            body = response.json()
            self_ref = (body['merged_by']['login'] == initiator.login)
            merged = body['merged']
            self.create_pr_object(self_ref, merged, payload, initiator, event)

        else:
            print 'Failed to get {}'.format(url)

    def create_pr_object(self, self_ref, merged, payload, initiator, event):
        new_pr = PullRequest.objects.update_or_create(
            defaults={'event': event},
            action_initiator=initiator,
            url=payload['pull_request']['_links']['self']['href'],
            action=payload['action'],
            pr_submitter=payload['pull_request']['user']['login'],
            self_referential=self_ref,
            merged=merged
        )[0]

        print 'Created {}, action={}, self_ref={} and merged={}'.format(
            new_pr,
            new_pr.action,
            new_pr.self_referential,
            new_pr.merged
        )

    def handle(self, *arg, **options):
        dev = Developer.objects.get(login='jamesrossiter')
        prs = Event.objects.filter(
            actor=dev,
            gh_type='PullRequestEvent'
        )

        for pr in prs[:20]:
            self.parse_pull_request(pr, dev)

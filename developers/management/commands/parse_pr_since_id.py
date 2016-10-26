from django.conf import settings
from django.core.management.base import BaseCommand

from developers.models import Event
from developers.models import Developer
from developers.models import PullRequest

import json
import requests

from rate_limiting import pause_if_rate_limit_reached

class Command(BaseCommand):
    help = """
    python manage.py parse_pr_since_id [pk_min] [pk_max]

    Classify and save TemporalPredictor objects based on
    PullRequestEvents from developers with pks between
    [pk_min] and [pk_max].

    This classifies PRs based on whether they were merged or not,
    and whether the merge was done by the same person who submitted
    the PR. It does NOT evaluate whether the PR was for a repo owned by the
    submitter; nor does it consider PRs that are not mergeable (e.g. "dirty")
    """

    def __init__(self):
        self.auth = 'client_id={}&client_secret={}'.format(
            settings.GITHUB_CLIENT_ID,
            settings.GITHUB_CLIENT_SECRET
        )
        self.api_error_counter = 0

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

        # 'Self-referential' refers to whether the submitter of the PR
        # was the person who merged (accepted) the PR
        elif payload['action'] in ['opened', 'reopened']:
            self.handle_pr_opening(payload, initiator, pr)

        else:
            print '\n\n\nUnknown pull request action: {}\n\n\n'.format(
                payload['action']
            )

    def handle_pr_closure(self, payload, initiator, event):
        merged = payload['pull_request']['merged']
        if merged:
            self_ref = (payload['pull_request']['user']['login'] ==
                        initiator.login)
        else:
            self_ref = None

        self.create_pr_object(
            event,
            initiator,
            payload,
            None,
            merged,
            initiator.login,
            self_ref,
        )

    def handle_pr_opening(self, payload, initiator, event):
        url = payload['pull_request']['_links']['self']['href']
        response = requests.get('{}?{}'.format(url, self.auth))

        if response.status_code == 200:
            body = response.json()
            merged = body['merged']
            if merged:
                closer = body['merged_by']['login']
                self_ref = (closer == initiator.login)
            else:
                closer = None
                self_ref = None

            self.create_pr_object(
                event,
                initiator,
                payload,
                True,
                merged,
                closer,
                self_ref
            )

        # Repository has been deleted, so we can't see how the pull request
        # was resolved
        elif response.status_code == 404:
            self.create_pr_object(
                event,
                initiator,
                payload,
                False,
                None,
                None,
                None
            )

        else:
            print 'API error for {}, initiated by {}'.format(url, initiator)
            self.api_error_counter += 1

        pause_if_rate_limit_reached(
            response.headers['X-RateLimit-Remaining'],
            response.headers['X-RateLimit-Reset']
        )

    def create_pr_object(
        self,
        event,
        initiator,
        payload,
        repo_still_exists,
        merged,
        closer,
        self_ref
    ):
        new_pr = PullRequest.objects.update_or_create(
            defaults={'event': event},
            action_initiator=initiator,
            url=payload['pull_request']['_links']['self']['href'],
            action=payload['action'],
            opener=payload['pull_request']['user']['login'],
            repo_still_exists=repo_still_exists,
            merged=merged,
            closer=closer,
            self_referential=self_ref
        )[0]

        print '{}: initiator={}, action={}, self_ref={}, merged={}'.format(
            new_pr,
            new_pr.action_initiator,
            new_pr.action,
            new_pr.self_referential,
            new_pr.merged
        )

    def handle(self, *arg, **options):
        devs = Developer.objects.filter(
            pk__gte=options['pk_min'][0],
            pk__lt=options['pk_max'][0],
        )

        dev_count = len(devs)

        for i, dev in enumerate(devs):
            print 'Working on {}, {} of {}, {}% complete'.format(
                dev,
                i,
                dev_count,
                float(i) / float(dev_count) * 100
            )

            prs = Event.objects.filter(
                actor=dev,
                gh_type='PullRequestEvent'
            )

            for pr in prs:
                self.parse_pull_request(pr, dev)

        print 'API ERROR COUNT: {}'.format(self.api_error_counter)

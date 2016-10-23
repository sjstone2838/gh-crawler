# from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from developers.models import Developer
from developers.models import Event

import datetime
from math import pow
# import pprint as pp

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials

class Command(BaseCommand):
    help = """
    python manage.py get_events_by_actor [dataset_path]

    Query BigQuery dataset at [dateset_path] for all events
    where actor.login is included in Developer.login and save each
    event to database, with primary_key mapped to developer.

    Example dataset_path: gh-crawler:githubarchive_2011.201401_copy
    """

    # def __init__(self):
    #     self.domain = 'https://api.github.com/users'

    def add_arguments(self, parser):
        parser.add_argument('dataset_path', nargs='+')

    def str_to_bool(self, s):
        # Convert strings 'true' and 'false' to python bools
        if s.upper() == 'TRUE':
            return True
        elif s.upper() == 'FALSE':
            return False
        else:
            raise ValueError("Cannot covert {} to a bool".format(s))

    def handle(self, *args, **options):
        logins = list(Developer.objects.values_list('login', flat=True))
        credentials = GoogleCredentials.get_application_default()
        bigquery_service = build('bigquery', 'v2', credentials=credentials)

        query_request = bigquery_service.jobs()
        query_data = {
            'query': (
                'SELECT * '
                'FROM [{}] '
                'WHERE actor.login '
                'IN ("{}")'.format(
                    options['dataset_path'][0], '", "'.join(logins)
                )
            )
        }

        query_response = query_request.query(
            projectId='gh-crawler',
            body=query_data).execute()

        event_count = len(query_response['rows'])
        print 'Found {} events'.format(event_count)

        for count, event in enumerate(query_response['rows'], start=1):
            actor_login = event['f'][7]['v']
            unix_epoch_integer = float(
                event['f'][16]['v'].split('E')[0]) * pow(10, 9)
            event_time = datetime.datetime.fromtimestamp(unix_epoch_integer)

            try:
                dev = Developer.objects.get(login=actor_login)

                e = Event.objects.create(
                    actor=dev,
                    gh_type=event['f'][0]['v'],
                    public=self.str_to_bool(event['f'][1]['v']),
                    payload=event['f'][2]['v'],
                    repo_id=event['f'][3]['v'],
                    repo_name=event['f'][4]['v'],
                    repo_url=event['f'][5]['v'],
                    gh_actor_id=event['f'][6]['v'],
                    actor_login=actor_login,
                    org_id=event['f'][11]['v'],
                    org_login=event['f'][12]['v'],
                    gh_created_at=event_time,
                    gh_id=event['f'][17]['v'],
                    other=event['f'][18]['v']
                )

                print 'Created {}, event {} of {} '.format(
                    e, count, event_count)

            except ObjectDoesNotExist:
                print "Could not find or update developer: {}".format(
                    dev['login'])

"""
Ordering of fields in GithubArchive
0'type',
1'public',
2'payload',
3'repo_id',
4'repo_name',
5'repo_url',
6'actor_id',
7'actor_login',
8'actor_gravatar_id',
9'actor_avatar_url',
10'actor_url',
11'org_id',
12'org_login',
13'org_gravatar_id',
14'org_avatar_url',
15'org_url',
16'created_at',
17'id',
18'other',
"""

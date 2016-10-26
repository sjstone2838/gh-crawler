# from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from developers.models import Developer
from developers.models import Event

import datetime
from math import pow
from math import ceil
import pytz
# import pprint as pp

from googleapiclient.discovery import build
# from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

class Command(BaseCommand):
    help = """
    python manage.py get_events_by_actor [dataset_name] [pk_min] [pk_max]

    Query BigQuery dataset at [dateset_name] for all events
    where actor.login is included in Developer.login and save each
    event to database, with primary_key mapped to developer.

    Example dataset_name: githubarchive_2011.2014_copy
    """

    def __init__(self):
        self.project_id = 'gh-crawler'
        self.timezone = pytz.timezone('US/Eastern')

    def add_arguments(self, parser):
        parser.add_argument('dataset_name', nargs='+')
        parser.add_argument('pk_min', nargs='+')
        parser.add_argument('pk_max', nargs='+')

    def str_to_bool(self, s):
        # Convert strings 'true' and 'false' to python bools
        if s.upper() == 'TRUE':
            return True
        elif s.upper() == 'FALSE':
            return False
        else:
            raise ValueError("Cannot covert {} to a bool".format(s))

    def write_events_to_db(self, events, page_number):
        print 'Found {} events in page {} of query results.'.format(
            len(events), page_number)

        for count, event in enumerate(events, start=1):
            actor_login = event['f'][7]['v']
            unix_epoch_integer = float(
                event['f'][16]['v'].split('E')[0]) * pow(10, 9)
            naive_time = datetime.datetime.fromtimestamp(unix_epoch_integer)
            event_time = self.timezone.localize(naive_time)

            try:
                dev = Developer.objects.get(login=actor_login)

                """
                Ordering of fields in GithubArchive:
                -------------------
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

                # print 'Created {}, event {} of {} on results page {}'.format(
                # e, count, len(events), page_number)

            except ObjectDoesNotExist:
                print "Could not find or update developer: {}".format(
                    dev['login'])

    def get_events_by_actor_batch(self, dev_pk_min,
                                  dev_pk_max, dataset_name, bigquery_service):
        actor_batch = Developer.objects.filter(
            pk__gt=dev_pk_min,
            pk__lte=dev_pk_max
        )

        logins = list(actor_batch.values_list('login', flat=True))

        query_data = {
            'query': (
                'SELECT * '
                'FROM [{}:{}] '
                'WHERE actor.login '
                'IN ("{}")'.format(
                    self.project_id,
                    dataset_name,
                    '", "'.join(logins)
                )
            ),
            'allowLargeResults': True
        }

        print "Running query on Google BigQuery..."

        query_response = bigquery_service.jobs().query(
            projectId='gh-crawler',
            body=query_data
        ).execute()

        print "Query returned {} total events.".format(
            query_response['totalRows']
        )

        page_number = 1
        # TODO: subsequent lines are repetitive
        self.write_events_to_db(query_response['rows'], page_number)
        page_token = query_response.get('pageToken', None)

        job_id = query_response['jobReference']['jobId']

        # http://stackoverflow.com/questions/22191085/bigquery-pagination
        # TODO: results per page can change; need to confirm that eTag is the
        # same that indicates that results have not changed.
        # Currently there is risk that we double-count if events move between
        # pages (risk is low as this script is run a matter of minutes.)
        while page_token is not None:
            query_request = bigquery_service.jobs().getQueryResults(
                projectId=self.project_id,
                jobId=job_id,
                pageToken=page_token,
                maxResults=100000
            )
            query_response = query_request.execute()

            page_number += 1
            # TODO: subsequent lines are repetitive
            self.write_events_to_db(query_response['rows'], page_number)
            page_token = query_response.get('pageToken', None)

    def handle(self, *args, **options):
        credentials = GoogleCredentials.get_application_default()
        bigquery_service = build('bigquery', 'v2', credentials=credentials)
        # query_request = bigquery_service.jobs()

        dev_pk_min = int(options['pk_min'][0])
        dev_pk_max = int(options['pk_max'][0])

        # Assumes actors have continuous pk's - no gaps
        total_dev_count = dev_pk_max - dev_pk_min
        batches = 1
        batch_size = min(10000, ceil(float(total_dev_count) / batches))

        for i in range(0, batches):
            batch_pk_min = i * batch_size + dev_pk_min
            batch_pk_max = (i + 1) * batch_size + dev_pk_min

            print "Running batch {}: pks {}-{}".format(
                i,
                batch_pk_min,
                batch_pk_max
            )

            self.get_events_by_actor_batch(
                batch_pk_min,
                batch_pk_max,
                options['dataset_name'][0],
                bigquery_service
            )

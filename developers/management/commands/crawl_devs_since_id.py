# import datetime
# from pydash import py_
# import pprint as pp
# import time
from django.conf import settings
from django.core.management.base import BaseCommand
from developers.models import Developer
import requests

class Command(BaseCommand):
    help = """
    python manage.py crawl_devs_since_id [starting_id] [limit]

    Writes developer data to database by calling github API.
    Approximate first new user on Jan 1 2014 has id 6296000.
    """

    def __init__(self):
        # self.calls_per_minute = 30
        self.per_page = 100

    def add_arguments(self, parser):
        parser.add_argument('starting_id', nargs='+')
        parser.add_argument('limit', nargs='+')

    def get_devs_by_page(self, url, limit, n):
        # n is number of pages written

        # TODO: rate-limiting avoidance can be improved
        # check r.headers['X-RateLimit-Remaining']; if 0, then sleep delta
        # between current time r.headers['X-RateLimit-Reset']
        # However, with 5000 calls/hour as auth'd user, not a big issue
        # This script can retrieve 10K users with 100 API calls

        # if n != 1 and n % self.calls_per_minute == 1:
        #     print "sleeping for 60 sec to avoid rate-limiting..."
        #     time.sleep(60)

        r = requests.get(url)
        # TODO: add error-handling

        for dev in r.json():
            if not Developer.objects.filter(login=dev['login']).exists():
                Developer.objects.create(
                    login=dev['login'],
                    gh_id=dev['id'],
                    url=dev['url'],
                    gh_type=dev['type'],
                    site_admin=dev['site_admin'],
                )
        print 'Wrote devs {} - {}; moving to page {}'.format(
            (n - 1) * self.per_page + 1, n * self.per_page, n + 1)

        if int(n * self.per_page) < int(limit) and 'next' in r.links:
            self.get_devs_by_page(r.links['next']['url'], limit, n + 1)

    def handle(self, *args, **options):
        domain = 'https://api.github.com/users'
        query = 'since={}&per_page={}&client_id={}&client_secret={}'.format(
            options['starting_id'][0], self.per_page,
            settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET
        )
        url = '{}?{}'.format(domain, query)
        self.get_devs_by_page(url, options['limit'][0], 1)

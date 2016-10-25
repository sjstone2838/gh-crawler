# import datetime
# from pydash import py_
# import pprint as pp
# import time
from django.conf import settings
from django.core.management.base import BaseCommand
from developers.models import Developer
import requests

from rate_limiting import pause_if_rate_limit_reached

class Command(BaseCommand):
    help = """
    python manage.py crawl_devs_since_id [starting_id] [limit]

    Writes developer data to database by calling github API.
    Approximate first new user on Jan 1 2014 has id 6296000.
    """

    def __init__(self):
        self.per_page = 100

    def add_arguments(self, parser):
        parser.add_argument('starting_id', nargs='+')
        parser.add_argument('limit', nargs='+')

    def get_devs_by_page(self, url, limit, n):
        # n is number of pages written

        response = requests.get(url)
        # TODO: add error-handling

        for dev in response.json():
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

        # Go to next page if n < limit and there is another page
        if int(n * self.per_page) < int(limit) and 'next' in response.links:
            self.get_devs_by_page(response.links['next']['url'], limit, n + 1)

        # If at rate limit, pause execution to allow limit to reset before next
        # recursive call. Should guarantee next recursive call has proper
        # response.json().
        # TODO: add proper error-checking.
        pause_if_rate_limit_reached(
            response.headers['X-RateLimit-Remaining'],
            response.headers['X-RateLimit-Reset']
        )

    def handle(self, *args, **options):
        domain = 'https://api.github.com/users'
        query = 'since={}&per_page={}&client_id={}&client_secret={}'.format(
            options['starting_id'][0], self.per_page,
            settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET
        )
        url = '{}?{}'.format(domain, query)
        self.get_devs_by_page(url, options['limit'][0], 1)

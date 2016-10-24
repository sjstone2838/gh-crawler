# from pydash import py_
# import pprint as pp
from django.conf import settings
from django.core.management.base import BaseCommand
from developers.models import Developer
from django.core.exceptions import ObjectDoesNotExist

from rate_limiting import pause_if_rate_limit_reached

import requests

class Command(BaseCommand):
    help = """
    python manage.py append_profiles_by_id_range [gh_id_min] [gh_id_max]

    For each developer in the DB where [gh_id_min] < github_id =< [gh_id_max],
    makes a call to Github API for developer's profile data and updates
    data in existing profile (which may or may not be blank).

    This command can be run simultaneously on different id_ranges.
    """

    def __init__(self):
        # self.calls_per_minute = 30
        self.domain = 'https://api.github.com/users'
        self.query = 'client_id={}&client_secret={}'.format(
            settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET
        )

    def add_arguments(self, parser):
        parser.add_argument('gh_id_min', nargs='+')
        parser.add_argument('gh_id_max', nargs='+')

    def get_dev_profile(self, login):

        url = '{}/{}?{}'.format(self.domain, login, self.query)
        response = requests.get(url)

        pause_if_rate_limit_reached(
            response.headers['X-RateLimit-Remaining'],
            response.headers['X-RateLimit-Reset']
        )

        r = response.json()
        try:
            dev = Developer.objects.get(login=r['login'])
            dev.name = r['name']
            dev.company = r['company']
            dev.blog = r['blog']
            dev.location = r['location']
            dev.email = r['email']
            dev.hireable = r['hireable']
            dev.bio = r['bio']
            dev.public_repos = r['public_repos']
            dev.public_gists = r['public_gists']
            dev.followers = r['followers']
            dev.following = r['following']
            dev.gh_created_at = r['created_at']
            dev.gh_updated_at = r['updated_at']
            dev.save()

        except ObjectDoesNotExist:
            print "Could not find or update developer with login {}".format(
                dev['login'])

    def handle(self, *args, **options):
        devs = Developer.objects.filter(
            gh_id__gt=options['gh_id_min'][0],
            gh_id__lte=options['gh_id_max'][0],
        )
        dev_ct = len(devs)

        for i, dev in enumerate(devs):
            self.get_dev_profile(dev.login)
            print ('Wrote developer with login '
                   '{}, {} of {}, {:.2f}% complete.'.format(
                       dev.login, i, dev_ct, float(i) / float(dev_ct) * 100))

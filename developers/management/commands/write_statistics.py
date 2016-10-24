# import datetime
# from pydash import py_
# import pprint as pp
# import time
from django.conf import settings
from django.core.management.base import BaseCommand
from developers.models import Developer
from django.core.exceptions import ObjectDoesNotExist

import requests

class Command(BaseCommand):
    help = """
    python manage.py append_dev_profiles [gh_id_minimum]

    For each developer in the database where github_id > [gh_id_minimum],
    makes a call to Github API for developer's profile data and appends
    or replaces existing profile.
    """

    def __init__(self):
        # self.calls_per_minute = 30
        self.domain = 'https://api.github.com/users'
        self.query = 'client_id={}&client_secret={}'.format(
            settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET
        )

    def add_arguments(self, parser):
        parser.add_argument('gh_id_min', nargs='+')

    def get_dev_profile(self, login):
        # TODO: add pause before rate-limiting

        url = '{}/{}?{}'.format(self.domain, login, self.query)
        r = requests.get(url).json()

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
            dev.github_created_at = r['created_at']
            dev.github_updated_at = r['created_at']
            dev.save()

        except ObjectDoesNotExist:
            print "Could not find or update developer with login {}".format(
                dev['login'])

    def handle(self, *args, **options):
        devs = Developer.objects.filter(gh_id__gt=options['gh_id_min'][0])
        dev_ct = len(devs)

        for i, dev in enumerate(devs):
            self.get_dev_profile(dev.login)
            print ('Wrote developer with login '
                   '{}, {} of {}, {:.2f}% complete.'.format(
                       dev.login, i, dev_ct, float(i) / float(dev_ct) * 100))

# from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from developers.models import Developer
from developers.models import Repo

import pprint as pp

class Command(BaseCommand):
    help = """
    python manage.py get_repos_by_developer [pk_min] [pk_max]

    Query Github API for repo details
    """

    def __init__(self):
        # self.project_id = 'gh-crawler'
        self.timezone = pytz.timezone('US/Eastern')

    def add_arguments(self, parser):
        parser.add_argument('pk_min', nargs='+')
        parser.add_argument('pk_max', nargs='+')


    def handle(self, *args, **options):
        xxx

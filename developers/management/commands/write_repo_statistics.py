from django.core.management.base import BaseCommand
from django.db.models import Sum

from developers.models import Repo
from developers.models import Developer

class Command(BaseCommand):
    help = """
    python manage.py write_repo_statistics [pk_min] [pk_max]

    Update or create repo statistics on Developer objects by looping
    through developers within pk range.

    Note that repos may have been deleted, so Developer.public_repos
    may exceed the count of Repos with detailed data from API calls.
    """

    def add_arguments(self, parser):
        parser.add_argument('pk_min', nargs='+')
        parser.add_argument('pk_max', nargs='+')

    def handle(self, *args, **options):
        devs = Developer.objects.filter(
            pk__gte=options['pk_min'][0],
            pk__lt=options['pk_max'][0]
        )
        for dev in devs:
            repos = Repo.objects.filter(owner=dev)

            dev.original_repo_ct = repos.filter(fork=False).count()

            dev.total_fork_ct = repos.aggregate(Sum('forks'))
            dev.forks_per_repo = float(dev.total_fork_ct) / len(repos)

            dev.total_star_ct = repos.aggregate(Sum('stars'))
            dev.stars_per_repo = float(dev.total_star_ct) / len(repos)

            dev.save()

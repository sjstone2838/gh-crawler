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
            print 'Working on pk={} ({})'.format(dev.pk, dev)
            repos = Repo.objects.filter(owner=dev)

            original_repos = repos.filter(fork=False).count()

            total_forks = repos.aggregate(
                Sum('forks_count')).values()[0]
            if total_forks is None:
                forks_per_repo = None
            else:
                forks_per_repo = float(total_forks) / len(repos)

            total_stars = repos.aggregate(
                Sum('stargazers_count')).values()[0]
            if total_stars is None:
                stars_per_repo = None
            else:
                stars_per_repo = float(total_stars) / len(repos)

            dev.original_repos = original_repos
            dev.total_forks = total_forks
            dev.forks_per_repo = forks_per_repo
            dev.total_stars = total_stars
            dev.stars_per_repo = stars_per_repo

            dev.save()

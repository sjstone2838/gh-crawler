from django.conf import settings
from django.core.management.base import BaseCommand
# from django.core.exceptions import ObjectDoesNotExist
from developers.models import Developer
from developers.models import Repo

import requests
from rate_limiting import pause_if_rate_limit_reached
# from pprint import pprint

class Command(BaseCommand):
    help = """
    python manage.py get_repos_by_developer [pk_min] [pk_max]

    Query Github API for repo details, starting with developer
    that has [pk_min] and going to developer with [pk_max]
    """

    def __init__(self):
        self.per_page = 100
        self.domain = 'https://api.github.com/users'
        self.query = '&per_page={}&client_id={}&client_secret={}'.format(
            self.per_page,
            settings.GITHUB_CLIENT_ID,
            settings.GITHUB_CLIENT_SECRET
        )

    def add_arguments(self, parser):
        parser.add_argument('pk_min', nargs='+')
        parser.add_argument('pk_max', nargs='+')

    def get_repos_by_developer(self, developer):
        url = '{}/{}/repos?{}'.format(
            self.domain,
            developer.login,
            self.query
        )

        self.get_repos_by_url(url, developer)

    # Recursively traverse all pages
    def get_repos_by_url(self, url, developer):
        response = requests.get(url)
        print 'Getting new page...'

        if response.status_code == 200:
            repos = response.json()

            for repo in repos:
                if Repo.objects.filter(
                    full_name=repo['full_name']
                ).count() == 0:
                    print 'Creating {}'.format(repo['name'])

                    Repo.objects.create(
                        owner=developer,
                        gh_id=repo['id'],
                        name=repo['name'],
                        full_name=repo['full_name'],
                        description=repo['description'],
                        fork=repo['fork'],
                        created_at=repo['created_at'],
                        updated_at=repo['updated_at'],
                        pushed_at=repo['pushed_at'],
                        homepage=repo['homepage'],
                        size=repo['size'],
                        stargazers_count=repo['stargazers_count'],
                        watchers_count=repo['watchers_count'],
                        language=repo['language'],
                        has_issues=repo['has_issues'],
                        has_downloads=repo['has_downloads'],
                        has_wiki=repo['has_wiki'],
                        has_pages=repo['has_pages'],
                        forks_count=repo['forks_count'],
                        mirror_url=repo['mirror_url'],
                        open_issues_count=repo['open_issues_count'],
                        forks=repo['forks'],
                        open_issues=repo['open_issues'],
                        watchers=repo['watchers'],
                        default_branch=repo['default_branch']
                    )
                else:
                    print "{} already exists, moving to next repo".format(
                        repo['full_name']
                    )

            pause_if_rate_limit_reached(
                response.headers['X-RateLimit-Remaining'],
                response.headers['X-RateLimit-Reset']
            )

            # Go to next page if there is another page
            if 'next' in response.links:
                self.get_repos_by_url(response.links['next']['url'], developer)
        else:
            print '\n\n Error getting repos for {}\n\n'.format(developer.login)

    def handle(self, *args, **options):
        devs = Developer.objects.filter(
            pk__gt=options['pk_min'][0],
            pk__lte=options['pk_max'][0]
        )
        for i, dev in enumerate(devs):
            if dev.public_repos > 0:
                print 'Creating repos for {}, {} of {}, {}%'.format(
                    dev.login,
                    i,
                    len(devs),
                    float(i) / float(len(devs)) * 100
                )
                self.get_repos_by_developer(dev)
            else:
                print '{} has 0 public repos.'.format(dev)

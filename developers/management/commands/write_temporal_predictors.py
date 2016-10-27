from django.core.management.base import BaseCommand
from django.db.models import Max, Min

from developers.models import Event
from developers.models import PullRequest
from developers.models import Developer
from developers.models import TemporalPredictor
from developers.models import TEMPORAL_PREDICTOR_REFERENCES
# 'Count' is the only formula used here
# from developers.models import TEMPORAL_PREDICTOR_FORMULAS

class Command(BaseCommand):
    help = """
    python manage.py write_temporal_predictors [pk_min] [pk_max]

    Update or create TemporalPredictors for devs in range(pk_min, pk_max)
    by looping through events and applying the appropriate aggregation formulas
    (e.g. count by event by month).

    In addition to the standard events logged in the GitHub public timeline,
    this will classify Pull Requests into Quality Opened PRs (where the PR
    was merged by someone else) and Quality Closed PRs (where the actor
    closed a PR opened by someone else) - these indicate collaborative work.
    """

    def add_arguments(self, parser):
        parser.add_argument('pk_min', nargs='+')
        parser.add_argument('pk_max', nargs='+')

    def month_year_iter(self, start_month, start_year, end_month, end_year):
        # http://stackoverflow.com/questions/5734438/how-to-create-a-month-iterator
        periods = []
        ym_start = 12 * start_year + start_month - 1
        ym_end = 12 * end_year + end_month
        for ym in range(ym_start, ym_end):
            y, m = divmod(ym, 12)
            periods.append((y, m + 1))
        return periods

    def create_or_update_temporal_predictor(self, gh_type, formula,
                                            developer, year, month, statistic):
        TemporalPredictor.objects.update_or_create(
            defaults={
                'reference': gh_type,
                'formula': formula,
                'developer': developer,
                'year': year,
                'month': month
            },
            statistic=statistic
        )

    def count_events_by_month(self, actor, gh_type, period):
        if gh_type == 'QualityPROpened':
            statistic = PullRequest.objects.filter(
                action_initiator=actor,
                action__in=['opened', 'reopened'],
                merged=True,
                self_referential=False,
                gh_created_at__year=period[0],
                gh_created_at__month=period[1]
            ).count()

            self.create_or_update_temporal_predictor(
                gh_type, 'Count', actor, period[0], period[1], statistic)

        elif gh_type == 'QualityPRClosed':
            statistic = PullRequest.objects.filter(
                action_initiator=actor,
                action__in=['closed'],
                merged=True,
                self_referential=False,
                gh_created_at__year=period[0],
                gh_created_at__month=period[1]
            ).count()

            self.create_or_update_temporal_predictor(
                gh_type, 'Count', actor, period[0], period[1], statistic)

        else:
            statistic = Event.objects.filter(
                actor=actor,
                gh_type=gh_type,
                gh_created_at__year=period[0],
                gh_created_at__month=period[1]
            ).count()

            self.create_or_update_temporal_predictor(
                gh_type, 'Count', actor, period[0], period[1], statistic)

        return statistic

    def handle(self, *args, **options):
        # TODO: rather than triple for loop,
        # this could done by a SINGLE sql query
        # but that's beyond my level of sql skill

        event_max = Event.objects.all().aggregate(Max(
            'gh_created_at')).values()[0]
        event_min = Event.objects.all().aggregate(Min(
            'gh_created_at')).values()[0]

        periods = self.month_year_iter(
            event_min.month,
            event_min.year,
            event_max.month,
            event_max.year
        )

        devs = Developer.objects.filter(
            pk__gte=options['pk_min'][0],
            pk__lt=options['pk_max'][0]
        )

        for dev in devs:
            for gh_type in TEMPORAL_PREDICTOR_REFERENCES:
                for period in periods:
                    c = self.count_events_by_month(dev, gh_type[0], period)
                    if c != 0:
                        print '{} {} for {} in {}-{}'.format(
                            c, gh_type[0], dev, period[0], period[1])

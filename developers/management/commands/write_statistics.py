from django.core.management.base import BaseCommand
from django.db.models import Max, Min

from developers.models import Event
from developers.models import Developer
from developers.models import TemporalPredictor
from developers.models import TEMPORAL_PREDICTOR_REFERENCES
# from developers.models import TEMPORAL_PREDICTOR_FORMULAS

class Command(BaseCommand):
    help = """
    python manage.py write_statistics

    Update or create TemporalPredictors by looping through events
    and applying the appropriate aggregation formulas (e.g. count by
    event by month).
    """

    def month_year_iter(self, start_month, start_year, end_month, end_year):
        # http://stackoverflow.com/questions/5734438/how-to-create-a-month-iterator
        periods = []
        ym_start = 12 * start_year + start_month - 1
        ym_end = 12 * end_year + end_month
        for ym in range(ym_start, ym_end):
            y, m = divmod(ym, 12)
            periods.append((y, m + 1))
        return periods

    def count_events_by_month(self, actor, gh_type, period):
        count = Event.objects.filter(
            actor=actor,
            gh_type=gh_type,
            gh_created_at__year=period[0],
            gh_created_at__month=period[1]
        ).count()

        TemporalPredictor.objects.update_or_create(
            reference=gh_type,
            formula='Count',
            developer=actor,
            year=period[0],
            month=period[1],
            defaults={'statistic': count}
        )

        return count

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

        devs = Developer.objects.all()

        for dev in devs[:500]:
            for gh_type in TEMPORAL_PREDICTOR_REFERENCES:
                for period in periods:
                    c = self.count_events_by_month(dev, gh_type[0], period)
                    if c != 0:
                        print '{} {} for {} in {}-{}'.format(
                            c, gh_type[0], dev, period[0], period[1])

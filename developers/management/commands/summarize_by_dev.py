from django.core.management.base import BaseCommand

from developers.models import TemporalPredictor
from developers.models import Developer

from developers.models import TEMPORAL_PREDICTOR_REFERENCES

import pandas as pd

class Command(BaseCommand):
    help = """
    python manage.py summarize_by_dev [dev_login]

    Write information on dev in range to a flat file, with features arrayed as
    a matrix (months on x-axis, event-type on y-axis).
    Response variables are included in cell with Dev's login.
    """

    def add_arguments(self, parser):
        parser.add_argument('dev_login', nargs='+')

    def month_year_iter(self, start_month, start_year, end_month, end_year):
        # TODO: this is redundant (in write_temporal_predictors.py)
        # Move both functions to a utils.py service
        periods = []
        ym_start = 12 * start_year + start_month - 1
        ym_end = 12 * end_year + end_month
        for ym in range(ym_start, ym_end):
            y, m = divmod(ym, 12)
            periods.append((y, m + 1))
        return periods

    def handle(self, *args, **options):
        dev = Developer.objects.get(login=options['dev_login'][0])
        periods = self.month_year_iter(1, 2014, 12, 2014)

        refs = [r[0] for r in list(TEMPORAL_PREDICTOR_REFERENCES)]

        title = ('{} \n Joined {} | {} public repos | {} non-forked repos |'
                 ' {} forks ({} per repo) | {} stars ({} per repo |'
                 ' {} followers | {} following').format(
                     dev,
                     dev.gh_created_at,
                     dev.public_repos,
                     dev.original_repos,
                     dev.total_forks,
                     dev.forks_per_repo,
                     dev.total_stars,
                     dev.stars_per_repo,
                     dev.followers,
                     dev.following)
        header = [title] + range(1, 13)
        data = []
        for ref in refs:
            r = [ref]
            for period in periods:
                try:
                    stat = TemporalPredictor.objects.get(
                        developer=dev,
                        year=period[0],
                        month=period[1],
                        reference=ref,
                        formula='Count'
                    ).statistic
                except:
                    stat = 0
                r.append(stat)
            data.append(r)

        df = pd.DataFrame(data, columns=header)
        df.to_csv('summary.csv', mode='a', header=True)

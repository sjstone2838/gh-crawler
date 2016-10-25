# Module for pausing script execution to allow
# Github rate limit to reset before next API call is made.

from datetime import datetime
import time

def pause_if_rate_limit_reached(remaining_calls, rate_limit_reset):
    # print remaining_calls
    # print int(remaining_calls) == 0
    # print rate_limit_reset

    if int(remaining_calls) == 1:
        now = datetime.now()
        reset = datetime.fromtimestamp(int(rate_limit_reset))
        # print reset
        delta = reset - now
        print "Sleeping for {} sec to avoid rate-limiting...".format(
            delta.seconds)
        # Round up by 1 second to adjust for microseconds
        time.sleep(delta.seconds + 1)
    # else:
    #     print '{} calls remain before rate limit reached.'.format(
    #         remaining_calls)

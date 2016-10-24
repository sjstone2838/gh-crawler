from datetime import datetime
import time

def pause_if_rate_limit_reached(remaining_calls, rate_limit_reset):
    if remaining_calls == 0:
        now = datetime.now()
        reset = datetime.fromtimestamp(int(rate_limit_reset))
        delta = reset - now
        print "Sleeping for {} sec to avoid rate-limiting...".format(
            delta.seconds)
        time.sleep(delta)
    # else:
    #     print '{} calls remain before rate limit reached.'.format(
    #         remaining_calls)

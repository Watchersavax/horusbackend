from __future__ import absolute_import, unicode_literals

# Import Celery app when Django is fully loaded
def setup():
    from .tasks import fetch_twitter_engagement, check_followers

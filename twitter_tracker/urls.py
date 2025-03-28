from django.urls import path
from .views import (
    twitter_login,
    twitter_user,
    leaderboard,
    submit_wallet,
    get_engagement_tweets,
    engagement_action,
    fetch_tweet_oembed,
    submit_tweet, 
    get_submitted_tweets,
    submit_application,
    check_application,
    generate_referral_link,   # ✅ NEW: Generate referral link
    handle_referral_signup,   # ✅ NEW: Process referral signups
    
)
from .backup_views import backup_database

urlpatterns = [
    path('api/twitter-login/', twitter_login, name='twitter-login'),
    path('api/twitter-user/', twitter_user, name='twitter_user'),
    path('api/leaderboard/', leaderboard, name='leaderboard'),
    path('api/submit-wallet/', submit_wallet, name='submit_wallet'),
    path('api/engagement-tweets/', get_engagement_tweets, name='get_engagement_tweets'),
    path('api/engagement/', engagement_action, name='engagement_action'),  # ✅ Match frontend POST to /api/engagement/
    path("api/fetch-tweet-oembed/", fetch_tweet_oembed, name="fetch_tweet_oembed"),
    path('api/submit-tweet/', submit_tweet, name="submit_tweet"),
    path('api/submitted-tweets/', get_submitted_tweets, name="submitted_tweets"),
    path("api/submit-application/", submit_application, name="submit_application"),
    path("api/check-application/", check_application, name="check_application"),
    path("api/db-backup/", backup_database, name="db_backup"),
        # ✅ Referral System
    path("api/referral-link/", generate_referral_link, name="generate_referral_link"),
    path("api/referral-signup/", handle_referral_signup, name="handle_referral_signup"),
]

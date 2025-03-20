from django.urls import path
from .views import (
    twitter_login,
    twitter_user,
    leaderboard,
    submit_wallet,
    get_engagement_tweets,
    engagement_action,
)

urlpatterns = [
    path('api/twitter-login/', twitter_login, name='twitter-login'),
    path('api/twitter-user/', twitter_user, name='twitter_user'),
    path('api/leaderboard/', leaderboard, name='leaderboard'),
    path('api/submit-wallet/', submit_wallet, name='submit_wallet'),
    path('api/engagement-tweets/', get_engagement_tweets, name='get_engagement_tweets'),
    path('api/engagement/', engagement_action, name='engagement_action'),  # ✅ Match frontend POST to /api/engagement/
]

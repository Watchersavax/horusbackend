from django.contrib import admin
from .models import TwitterUser, EngagementTweet, EngagementHistory

@admin.register(TwitterUser)
class TwitterUserAdmin(admin.ModelAdmin):
    list_display = ("user", "twitter_handle", "wallet_address", "points")

@admin.register(EngagementTweet)
class EngagementTweetAdmin(admin.ModelAdmin):
    list_display = ("tweet_url", "description", "created_at")

@admin.register(EngagementHistory)
class EngagementHistoryAdmin(admin.ModelAdmin):
    list_display = ("twitter_user", "tweet", "task_type", "points_awarded", "timestamp")


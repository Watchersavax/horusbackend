from django.contrib import admin
from .models import TwitterUser, EngagementTweet, EngagementHistory

from .models import SubmittedTweet, UserApplication

@admin.register(SubmittedTweet)
class SubmittedTweetAdmin(admin.ModelAdmin):
    list_display = ('twitter_user', 'tweet_url', 'submitted_at', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('twitter_user__twitter_handle', 'tweet_url')
    actions = ['approve_tweets']

    def approve_tweets(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected tweets have been approved.")

    approve_tweets.short_description = "Approve selected tweets"

@admin.register(TwitterUser)
class TwitterUserAdmin(admin.ModelAdmin):
    list_display = ("user", "twitter_handle", "wallet_address", "points")

@admin.register(EngagementTweet)
class EngagementTweetAdmin(admin.ModelAdmin):
    list_display = ("tweet_url", "description", "created_at")

@admin.register(EngagementHistory)
class EngagementHistoryAdmin(admin.ModelAdmin):
    list_display = ("twitter_user", "tweet", "task_type", "points_awarded", "timestamp")


@admin.register(UserApplication)
class UserApplicationAdmin(admin.ModelAdmin):
    list_display = ("twitter_user", "discord_handle", "submitted_at")  # Display key fields in the admin list view
    list_filter = ("submitted_at",)  # Filter by submission date
    search_fields = ("twitter_user__twitter_handle", "discord_handle", "motivation", "experience", "skills")  # Allow searching
    readonly_fields = ("twitter_user", "motivation", "experience", "skills", "discord_handle", "submitted_at")  # Prevent editing

    fieldsets = (
        ("User Info", {
            "fields": ("twitter_user", "discord_handle", "submitted_at"),
        }),
        ("Application Responses", {
            "fields": ("motivation", "experience", "skills"),
        }),
    )

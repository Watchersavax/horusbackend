from django.db import models
from django.contrib.auth.models import User
import random
from django.utils import timezone
from datetime import timedelta
import uuid



class TwitterUser(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    twitter_handle = models.CharField(max_length=255, unique=True)
    profile_image = models.URLField(null=True, blank=True)
    wallet_address = models.CharField(max_length=255, null=True, blank=True)
    points = models.IntegerField(default=0)
    has_completed_application = models.BooleanField(default=False)  # ✅ Track if user submitted the form

  
    referred_by = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="referrals")

    @property
    def referral_code(self):
        """Referral code is simply the Twitter handle."""
        return self.twitter_handle
    
    def save(self, *args, **kwargs):

        default_images = [
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQg6jwYSUYcKvlShgwuO90cCWWAIz7PblUFIA&s",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSohm5827LWyoZHVQTUkAjO0hC6Zwh77Z0qSg&s",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQqXk93FpgQBnYBTelsAsssjppvy2Xlu_Oibw&s",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTbdsv-Id9AslFbTvnG0NpabCFlvTV7JAxnUw&s",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQucXGGGahvUv6CM2spXnavctcEKubt9mGwsQ&s",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSRNkPHpBjAO-gMoPm54CCfIAqpNsN8FBrqQg&s",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQKIPdEjElUKyR4cbBIomRVe8B3EWA8UQyq4g&s",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQpOhF3Pevp7FM80QuFLJnN1Mf4i0SIgjUDNQ&s",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQpgQWPZr0avHbuqtoVE91uVWJ6IIt8dKl9kQ&s",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTr54_AjndjQSbEfPeU_ZH7TnDCtB_2Y04YEQ&s",
        ]   

        # If profile_image is missing, randomly assign one from the list
        if not self.profile_image:
            self.profile_image = random.choice(default_images)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.twitter_handle      


def generate_unique_referral_code():
    while True:
        new_code = str(uuid.uuid4().hex[:8])  # Generate a random 8-char code
        if not TwitterUser.objects.filter(referral_code=new_code).exists():
            return new_code


class EngagementTweet(models.Model):
    tweet_url = models.URLField(help_text="Full Tweet URL")
    description = models.CharField(max_length=255, help_text="Optional description", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tweet_url


class EngagementHistory(models.Model):
    twitter_user = models.ForeignKey(TwitterUser, on_delete=models.CASCADE)
    tweet = models.ForeignKey(EngagementTweet, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=10, choices=[('like', 'Like'), ('retweet', 'Retweet'), ('comment', 'Comment')])
    points_awarded = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('twitter_user', 'tweet', 'task_type')  # Prevent double claiming

    def __str__(self):
        return f"{self.twitter_user.twitter_handle} - {self.task_type} - {self.tweet}"



class SubmittedTweet(models.Model):
    twitter_user = models.ForeignKey(TwitterUser, on_delete=models.CASCADE)
    tweet_url = models.URLField(unique=True, help_text="User-submitted Tweet URL")
    description = models.CharField(max_length=255, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)  # ✅ New field for approval


    def __str__(self):
        return f"{self.twitter_user.twitter_handle} - {self.tweet_url}"

    @staticmethod
    def tweets_in_last_24_hours(user):
        time_threshold = timezone.now() - timedelta(hours=24)
        
        return SubmittedTweet.objects.filter(twitter_user=user, submitted_at__gte=time_threshold).count()

class UserApplication(models.Model):
    twitter_user = models.OneToOneField(TwitterUser, on_delete=models.CASCADE)
    motivation = models.TextField()
    experience = models.TextField()
    skills = models.TextField()
    discord_handle = models.CharField(max_length=255)
    submitted_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Application - {self.twitter_user.twitter_handle}"        
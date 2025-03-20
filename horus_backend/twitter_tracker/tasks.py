# import tweepy
# from celery import shared_task
# from .models import TwitterUser
# from django.conf import settings


# # Set up Tweepy API
# auth = tweepy.OAuthHandler(settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET)
# auth.set_access_token(settings.TWITTER_BEARER_TOKEN, settings.TWITTER_API_SECRET)
# api = tweepy.API(auth, wait_on_rate_limit=True)

# # Define point values
# POINTS = {
#     "tweet": 50,
#     "like": 10,
#     "retweet": 30,
#     "comment": 20,
#     "follow": 200,
#     "view": 1
# }

# HORUS_USERNAME = "horussyndicate"  # Official Twitter handle


# @shared_task
# # def fetch_twitter_engagement():
# #     print("🔴 Fetching Twitter engagement...")  # Debug print
# #     return "✅ Function executed!"
# def fetch_twitter_engagement():
#     print("🔴 Fetching Twitter engagement...")  # Debug print
#     return "✅ Function executed!"
#     from .models import TwitterUser, Tweet
#     """Fetch tweets mentioning $HORUS, #HORUS, or @horussyndicate and update user points."""
#     query = "$HORUS OR #HORUS OR @horussyndicate"
    
#     try:
#         tweets = api.search_tweets(q=query, count=100, result_type="recent")
        
#         for tweet in tweets:
#             twitter_handle = tweet.user.screen_name
#             profile_image = tweet.user.profile_image_url_https  # Ensure secure URL

#             user, created = TwitterUser.objects.get_or_create(
#                 twitter_handle=twitter_handle,
#                 defaults={"profile_image": profile_image}
#             )
            
#             # Update profile image if changed
#             if user.profile_image != profile_image:
#                 user.profile_image = profile_image
#                 user.save()

#             # Check if tweet already processed
#             if not Tweet.objects.filter(tweet_id=tweet.id_str).exists():
#                 tweet_points = POINTS["tweet"]

#                 # Engagement Metrics
#                 likes = tweet.favorite_count * POINTS["like"]
#                 retweets = tweet.retweet_count * POINTS["retweet"]
#                 comments = 0  # Tweepy doesn't provide reply count
#                 views = 0  # Twitter API v2 needed for `impression_count`

#                 total_points = tweet_points + likes + retweets + comments + views

#                 # Store tweet & update user points
#                 Tweet.objects.create(
#                     twitter_user=user,
#                     tweet_id=tweet.id_str,
#                     content=tweet.text,
#                     points_awarded=total_points
#                 )

#                 # ✅ Accumulate Points
#                 user.points += total_points
#                 user.save()

#     except tweepy.TweepError as e:
#         print(f"Twitter API Error: {e}")
#     except Exception as e:
#         print(f"Unexpected Error: {e}")


# @shared_task
# def check_followers():
#     from .models import TwitterUser, Tweet
#     """Check if users are following @horussyndicate and award 200 points."""
#     try:
#         followers = api.get_follower_ids(screen_name=HORUS_USERNAME)
        
#         for user in TwitterUser.objects.all():
#             if user.twitter_handle in followers and user.points < POINTS["follow"]:
#                 user.points += POINTS["follow"]
#                 user.save()
    
#     except tweepy.TweepError as e:
#         print(f"Error checking followers: {e}")
#     except Exception as e:
#         print(f"Unexpected Error: {e}")




# def fetch_twitter_engagement():
#     print("🔴 Fetching Twitter engagement...")  # Debug start

#     users = TwitterUser.objects.all()
#     for user in users:
#         print(f"Processing user: {user.twitter_handle}, Current Points: {user.points}")  # Debug print

#         # Simulate points update
#         user.points += 10  # Example increment (replace with actual logic)
#         user.save()

#         print(f"✅ Updated {user.twitter_handle} -> New Points: {user.points}")  # Debug print

#     print("✅ Task completed!")  # Debug end



import requests
from django.conf import settings
from twitter_tracker.models import TwitterUser  # Assuming this is your model

def fetch_twitter_engagement():
    print("🔴 Fetching Twitter engagement...")  

    token = settings.TWITTER_BEARER_TOKEN
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch Twitter user details
    url = "https://api.twitter.com/2/users/by/username/horussyndicate"
    response = requests.get(url, headers=headers)
    twitter_data = response.json()

    print("🟢 Raw Twitter Data:", twitter_data)  

    if "data" not in twitter_data:
        print("❌ No user data received. Possible API error.")
        return

    user_id = twitter_data["data"]["id"]  # Twitter user ID
    username = twitter_data["data"]["username"]  # Twitter handle

    # ✅ Use user_id in get_or_create
    user, created = TwitterUser.objects.get_or_create(
        user_id=user_id,  # Ensure user_id is included
        defaults={"twitter_handle": username}
    )

    print(f"✅ User found/created: {user.twitter_handle} (ID: {user.user_id})")

    # Simulating engagement fetching (replace with actual Twitter API calls)
    engagement_data = {
        "likes": 10,
        "retweets": 5,
        "comments": 3,
        "follows": 1
    }

    print("📊 Engagement Data:", engagement_data)

    # Update points
    user.points += (engagement_data["likes"] * 10) + (engagement_data["retweets"] * 30) + (engagement_data["comments"] * 20) + (engagement_data["follows"] * 200)
    user.save()

    print(f"✅ Updated {user.twitter_handle} -> New Points: {user.points}")
    print("✅ Task completed!")


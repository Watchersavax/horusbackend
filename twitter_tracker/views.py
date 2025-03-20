import json
import time
import logging
import tweepy
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.paginator import Paginator
from .models import TwitterUser, EngagementTweet, EngagementHistory
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

TWITTER_API_KEY = settings.TWITTER_API_KEY
TWITTER_API_SECRET = settings.TWITTER_API_SECRET


### 🔹 Twitter OAuth Login URL
def twitter_login(request):
    try:
        auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        redirect_url = auth.get_authorization_url()
        return JsonResponse({"url": redirect_url})
    except Exception as e:
        logger.error(f"Twitter login error: {e}")
        return JsonResponse({"error": "Twitter login failed"}, status=500)


### 🔹 Twitter OAuth Callback / User Handling

@csrf_exempt
def twitter_user(request):
    if request.method == "POST":
        body = json.loads(request.body)
        oauth_token = body.get("oauth_token")
        oauth_verifier = body.get("oauth_verifier")

        if not oauth_token or not oauth_verifier:
            return JsonResponse({"error": "Missing OAuth token or verifier"}, status=400)

        try:
            access_token_data = get_twitter_access_token(oauth_token, oauth_verifier)
        except Exception as e:
            logger.error(f"Access token fetch error: {e}")
            return JsonResponse({"error": "Failed to get access token"}, status=400)

        twitter_handle = access_token_data.get('screen_name')
        profile_image = access_token_data.get('profile_image_url_https', '')

        if not twitter_handle:
            return JsonResponse({"error": "Failed to fetch Twitter handle"}, status=400)

        # Handle user assignment safely
        twitter_user_data = {
            "profile_image": profile_image
        }

        if request.user.is_authenticated:
            twitter_user_data["user"] = request.user

        try:
            user, created = TwitterUser.objects.get_or_create(
                twitter_handle=twitter_handle,
                defaults=twitter_user_data
            )
        except Exception as e:
            logger.error(f"Error creating/fetching TwitterUser: {e}")
            return JsonResponse({"error": "Failed to create or fetch Twitter user"}, status=500)

        # Update profile image if needed
        if not created and profile_image and user.profile_image != profile_image:
            user.profile_image = profile_image
            user.save()

        return JsonResponse({
            "username": user.twitter_handle,
            "profile_image": user.profile_image,
            "wallet_address": user.wallet_address,
            "points": user.points,
        })

    elif request.method == "GET":
        username = request.GET.get("username")
        if not username:
            return JsonResponse({"error": "Username required"}, status=400)

        try:
            user = TwitterUser.objects.get(twitter_handle=username)
            return JsonResponse({
                "username": user.twitter_handle,
                "profile_image": user.profile_image,
                "wallet_address": user.wallet_address,
                "points": user.points,
            })
        except TwitterUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({"error": "Method not allowed"}, status=405)

# import requests

# @csrf_exempt
# def twitter_user(request):
#     if request.method == "POST":
#         body = json.loads(request.body)
#         oauth_token = body.get("oauth_token")
#         oauth_verifier = body.get("oauth_verifier")

#         if not oauth_token or not oauth_verifier:
#             return JsonResponse({"error": "Missing OAuth token or verifier"}, status=400)

#         try:
#             access_token_data = get_twitter_access_token(oauth_token, oauth_verifier)
#             logger.info(f"Full Twitter API Response: {json.dumps(access_token_data, indent=2)}")
#         except Exception as e:
#             logger.error(f"Access token fetch error: {e}")
#             return JsonResponse({"error": "Failed to get access token"}, status=400)

#         twitter_handle = access_token_data.get("screen_name")
#         user_id = access_token_data.get("user_id")

#         if not twitter_handle:
#             return JsonResponse({"error": "Failed to fetch Twitter handle"}, status=400)

#         # ✅ Step 1: Make an additional request to get full user details
#         profile_image = ""
#         try:
#             twitter_api_url = f"https://api.twitter.com/1.1/users/show.json?screen_name={twitter_handle}"
#             headers = {
#                 "Authorization": f"Bearer YOUR_TWITTER_BEARER_TOKEN"  # 🔥 Replace with your actual Twitter Bearer Token
#             }
#             response = requests.get(twitter_api_url, headers=headers)
#             user_data = response.json()
#             logger.info(f"Twitter User Data Response: {json.dumps(user_data, indent=2)}")

#             # ✅ Extract profile image from the full user data
#             profile_image = user_data.get("profile_image_url_https", "")
#         except Exception as e:
#             logger.error(f"Failed to fetch user profile from Twitter API: {e}")

#         if not profile_image:
#             return JsonResponse({
#                 "error": "Twitter did not return a profile image",
#                 "api_response": access_token_data  # Debugging
#             }, status=400)

#         # ✅ Step 2: Save or update the user in the database
#         user, created = TwitterUser.objects.get_or_create(
#             twitter_handle=twitter_handle
#         )

#         if not user.profile_image or user.profile_image != profile_image:
#             user.profile_image = profile_image
#             user.save()

#         return JsonResponse({
#             "username": user.twitter_handle,
#             "profile_image": user.profile_image,
#             "wallet_address": user.wallet_address,
#             "points": user.points,
#         })




### 🔹 Wallet Submission / Update
@api_view(['POST'])
def submit_wallet(request):
    username = request.data.get('username')
    wallet_address = request.data.get('wallet_address')

    if not username or not wallet_address:
        return Response({'message': 'Username and wallet address are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = TwitterUser.objects.get(twitter_handle=username)
    except TwitterUser.DoesNotExist:
        return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    if not user.wallet_address:
        # First-time submission, reward points
        user.wallet_address = wallet_address
        user.points += 100
        user.save()
        return Response({'message': 'Wallet submitted! You earned 100 points!'}, status=status.HTTP_200_OK)
    else:
        # Wallet update, no points
        user.wallet_address = wallet_address
        user.save()
        return Response({'message': 'Wallet updated successfully.'}, status=status.HTTP_200_OK)


### 🔹 Leaderboard with Pagination
@csrf_exempt
def leaderboard(request):
    try:
        page = int(request.GET.get("page", 1))
        per_page = 50
        users = TwitterUser.objects.all().order_by("-points")
        paginator = Paginator(users, per_page)
        users_page = paginator.get_page(page)

        leaderboard_data = [{
            "twitter_handle": user.twitter_handle,
            "points": user.points,
            "profile_image": user.profile_image,
        } for user in users_page]

        return JsonResponse({
            "leaderboard": leaderboard_data,
            "total_pages": paginator.num_pages,
            "current_page": page,
        }, status=200)
    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
        return JsonResponse({"error": "Failed to fetch leaderboard"}, status=500)


### 🔹 Fetch Engagement Tweets
def get_engagement_tweets(request):
    tweets = EngagementTweet.objects.all().order_by('-created_at')
    data = [{"id": tweet.id, "url": tweet.tweet_url, "description": tweet.description} for tweet in tweets]
    return JsonResponse({"tweets": data}, status=200)


### 🔹 Engagement Action (LIKE, RETWEET, COMMENT)
@csrf_exempt
def engagement_action(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("twitter_handle")
            action = data.get("task_type")
            tweet_id = data.get("tweet_id")

            if not username or not action or not tweet_id:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            twitter_user = TwitterUser.objects.get(twitter_handle=username)
            tweet = EngagementTweet.objects.get(id=tweet_id)

            # Prevent double claiming the same action
            if EngagementHistory.objects.filter(twitter_user=twitter_user, tweet=tweet, task_type=action).exists():
                return JsonResponse({"error": "Task already completed"}, status=400)

            logger.info(f"Engagement: {username} - {action} - TweetID: {tweet_id}")
            time.sleep(3)  # Optional delay (simulate processing)

            EngagementHistory.objects.create(
                twitter_user=twitter_user,
                tweet=tweet,
                task_type=action,
                points_awarded=10
            )
            twitter_user.points += 10
            twitter_user.save()

            return JsonResponse({"message": f"{action} completed", "total_points": twitter_user.points}, status=200)

        except TwitterUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except EngagementTweet.DoesNotExist:
            return JsonResponse({"error": "Tweet not found"}, status=404)
        except Exception as e:
            logger.error(f"Engagement error: {str(e)}")
            return JsonResponse({"error": "Something went wrong"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


### 🔹 Get Twitter Access Token Helper
def get_twitter_access_token(oauth_token, oauth_verifier):
    url = "https://api.twitter.com/oauth/access_token"
    params = {
        'oauth_token': oauth_token,
        'oauth_verifier': oauth_verifier
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        data = dict(x.split('=') for x in response.text.split('&'))
        return data
    else:
        raise Exception('Failed to get Twitter access token')





@csrf_exempt
def fetch_tweet_oembed(request):
    tweet_url = request.GET.get("url")
    if not tweet_url:
        return JsonResponse({"error": "Missing tweet URL"}, status=400)

    oembed_url = f"https://publish.twitter.com/oembed?url={tweet_url}"

    try:
        response = requests.get(oembed_url)
        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({"error": "Failed to fetch tweet embed", "status": response.status_code}, status=400)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Error fetching tweet", "details": str(e)}, status=500)

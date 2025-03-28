import json
import time
import logging
import tweepy
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.paginator import Paginator
from .models import TwitterUser, EngagementTweet, EngagementHistory, SubmittedTweet, UserApplication
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


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
        try:
            body = json.loads(request.body)
            logger.info(f"POST Request Body: {body}")  # ✅ Debugging log

            oauth_token = body.get("oauth_token")
            oauth_verifier = body.get("oauth_verifier")
            referral_code = body.get("referral_code")  # ✅ Referrer’s Twitter handle

            if not oauth_token or not oauth_verifier:
                return JsonResponse({"error": "Missing OAuth token or verifier"}, status=400)

            # ✅ Get Twitter access token
            try:
                access_token_data = get_twitter_access_token(oauth_token, oauth_verifier)
            except Exception as e:
                logger.error(f"Access token fetch error: {e}")
                return JsonResponse({"error": "Failed to get access token"}, status=400)

            twitter_handle = access_token_data.get("screen_name")
            profile_image = access_token_data.get("profile_image_url_https", "")

            if not twitter_handle:
                return JsonResponse({"error": "Failed to fetch Twitter handle"}, status=400)

            # ✅ Get or create user
            try:
                user, created = TwitterUser.objects.get_or_create(
                    twitter_handle=twitter_handle,
                    defaults={"profile_image": profile_image}
                )
            except Exception as e:
                logger.error(f"Error creating/fetching TwitterUser: {e}")
                return JsonResponse({"error": "Failed to create or fetch Twitter user"}, status=500)

            # ✅ Update profile image if changed
            if not created and profile_image and user.profile_image != profile_image:
                user.profile_image = profile_image
                user.save()

            # ✅ Handle referral system
            if created and referral_code:
                try:
                    referrer = TwitterUser.objects.get(twitter_handle=referral_code)
                    referrer.points += 10
                    referrer.save()
                    user.referred_by = referrer  # ✅ Track referrer
                    user.save()
                    logger.info(f"Referral success! {referrer.twitter_handle} earned 10 points")
                except TwitterUser.DoesNotExist:
                    logger.warning(f"Invalid referral code used: {referral_code}")

            return JsonResponse({
                "username": user.twitter_handle,
                "profile_image": user.profile_image,
                "wallet_address": user.wallet_address,
                "points": user.points,
                "referral_code": user.referral_code,  # ✅ Twitter handle as referral code
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

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
                "referral_code": user.referral_code,  # ✅ Include referral code
            })
        except TwitterUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({"error": "Method not allowed"}, status=405)

### 🔹 Get Referral Link
@api_view(['GET'])
def generate_referral_link(request):
    username = request.GET.get("username")

    if not username:
        return JsonResponse({"error": "Username required"}, status=400)

    try:
        user = TwitterUser.objects.get(twitter_handle=username)
        referral_link = f"http://localhost:5173/ref={user.referral_code}"
        return JsonResponse({"referral_link": referral_link})
    except TwitterUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

@csrf_exempt
def handle_referral_signup(request):
    if request.method == "POST":
        body = json.loads(request.body)
        twitter_handle = body.get("twitter_handle")
        profile_image = body.get("profile_image", "")
        referral_code = body.get("referral_code")  # ✅ This is now the referrer's Twitter handle

        if not twitter_handle:
            return JsonResponse({"error": "Twitter handle is required"}, status=400)

        try:
            user, created = TwitterUser.objects.get_or_create(
                twitter_handle=twitter_handle,
                defaults={"profile_image": profile_image}
            )
        except Exception as e:
            logger.error(f"Error creating/fetching TwitterUser: {e}")
            return JsonResponse({"error": "Failed to create or fetch Twitter user"}, status=500)

        # ✅ Update profile image if changed
        if not created and profile_image and user.profile_image != profile_image:
            user.profile_image = profile_image
            user.save()

        # ✅ Handle referral points if a valid Twitter handle is provided
        if created and referral_code:
            try:
                referrer = TwitterUser.objects.get(twitter_handle=referral_code)
                referrer.points += 10
                referrer.save()
                user.referred_by = referrer  # ✅ Track who referred them
                user.save()
                logger.info(f"Referral success! {referrer.twitter_handle} earned 10 points")
            except TwitterUser.DoesNotExist:
                logger.warning(f"Invalid referral code used: {referral_code}")

        return JsonResponse({
            "username": user.twitter_handle,
            "profile_image": user.profile_image,
            "wallet_address": user.wallet_address,
            "points": user.points,
            "referral_code": user.referral_code,  # ✅ Return Twitter handle as referral code
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)




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



from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TwitterUser, SubmittedTweet

@csrf_exempt
@api_view(['POST'])
def submit_tweet(request):
    """
    Allows users to submit tweets without requiring authentication.
    """
    tweet_url = request.data.get('tweet_url')
    description = request.data.get('description', "")

    if not tweet_url:
        return Response({"error": "Tweet URL is required."}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Get username from frontend request
    username = request.data.get('username')  # Sent from frontend
    if not username:
        return Response({"error": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # ✅ Get TwitterUser based on the provided username
        user = TwitterUser.objects.get(twitter_handle=username)
    except TwitterUser.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # ✅ Limit to 3 tweets per 24 hours
    if SubmittedTweet.tweets_in_last_24_hours(user) >= 3:
        return Response({"error": "You can only submit up to 3 tweets per 24 hours."}, status=status.HTTP_403_FORBIDDEN)

    # ✅ Prevent duplicate tweet submission
    if SubmittedTweet.objects.filter(tweet_url=tweet_url).exists():
        return Response({"error": "This tweet has already been submitted."}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Save submitted tweet
    SubmittedTweet.objects.create(twitter_user=user, tweet_url=tweet_url, description=description)

    return Response({"message": "Tweet submitted successfully! Awaiting review."}, status=status.HTTP_201_CREATED)



@csrf_exempt
@api_view(['GET'])
def get_submitted_tweets(request):
    """
    Fetch tweets submitted by the currently logged-in user only.
    """
    username = request.GET.get("username")

    if not username:
        return JsonResponse({"error": "Username required."}, status=400)

    try:
        # ✅ Get the user based on username
        user = TwitterUser.objects.get(twitter_handle=username)
    except TwitterUser.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    # ✅ Fetch only tweets submitted by this user
    tweets = SubmittedTweet.objects.filter(twitter_user=user).order_by('-submitted_at')
    
    data = [{
        "id": tweet.id,
        "tweet_url": tweet.tweet_url,
        "description": tweet.description,
        "submitted_at": tweet.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
        "is_approved": tweet.is_approved  # ✅ Return approval status
    } for tweet in tweets]

    return JsonResponse({"submitted_tweets": data}, status=200)


@csrf_exempt
@api_view(['POST'])
def submit_application(request):
    """
    Allows users to submit an application only once.
    """
    username = request.data.get("username")
    motivation = request.data.get("motivation")
    experience = request.data.get("experience")
    skills = request.data.get("skills")
    discord_handle = request.data.get("discord_handle")

    if not username or not motivation or not experience or not skills or not discord_handle:
        return JsonResponse({"error": "All fields are required."}, status=400)

    try:
        user = TwitterUser.objects.get(twitter_handle=username)

        # 🔥 **Enforce Fresh Query to Prevent Stale Data Issues**
        application_exists = UserApplication.objects.filter(twitter_user=user).count() > 0

        if application_exists:
            return JsonResponse({"error": "Application already submitted."}, status=400)

        # ✅ Now save the new application
        UserApplication.objects.create(
            twitter_user=user,
            motivation=motivation,
            experience=experience,
            skills=skills,
            discord_handle=discord_handle
        )

        return JsonResponse({"message": "Application submitted successfully!"}, status=201)

    except TwitterUser.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

@csrf_exempt
def check_application(request):
    """
    Check if the user has submitted an application.
    """
    username = request.GET.get("username")
    
    if not username:
        return JsonResponse({"error": "Username is required."}, status=400)

    try:
        user = TwitterUser.objects.get(twitter_handle=username)

        # ✅ Fetch application explicitly and count
        application_count = UserApplication.objects.filter(twitter_user=user).count()
        
        return JsonResponse({"application_exists": application_count > 0})

    except TwitterUser.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)





@api_view(['GET'])
def get_referral_link(request):
    username = request.GET.get("username")

    if not username:
        return JsonResponse({"error": "Username required"}, status=400)

    try:
        user = TwitterUser.objects.get(twitter_handle=username)
        referral_link = f"https://horus.app/signup?ref={user.referral_code}"
        return JsonResponse({"referral_link": referral_link})
    except TwitterUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)


@api_view(['GET'])
def get_total_referrals(request):
    username = request.GET.get("username")

    if not username:
        return JsonResponse({"error": "Username required"}, status=400)

    try:
        user = TwitterUser.objects.get(twitter_handle=username)

        # ✅ Count how many users were referred by this user
        referral_count = TwitterUser.objects.filter(referred_by=user).count()

        return JsonResponse({"username": user.twitter_handle, "total_referrals": referral_count})

    except TwitterUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

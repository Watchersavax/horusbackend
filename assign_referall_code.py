import os
import django

# ✅ Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horus_backend.settings')
django.setup()

from twitter_tracker.models import TwitterUser
import uuid

# ✅ Assign referral codes to existing users
def assign_referral_codes():
    users_without_referral = TwitterUser.objects.filter(referral_code__isnull=True) | TwitterUser.objects.filter(referral_code="")

    for user in users_without_referral:
        user.referral_code = uuid.uuid4().hex[:8]
        user.save()
        print(f"Assigned referral code {user.referral_code} to {user.twitter_handle}")

if __name__ == "__main__":
    assign_referral_codes()
    print("Referral code assignment complete.")



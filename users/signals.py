from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New user created: {instance.username} ({instance.email})")


@receiver(post_delete, sender=UserProfile)
def log_profile_deletion(sender, instance, **kwargs):
    logger.warning(f"UserProfile deleted for user: {instance.user.username}")

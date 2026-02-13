from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderItem, Cart
import logging

logger = logging.getLogger(__name__)
import uuid


@receiver(post_save, sender=Order)
def set_order_number(sender, instance, created, **kwargs):
    if created and not instance.order_number:
        order_number = f"ORD-{instance.id}-{uuid.uuid4().hex[:6].upper()}"
        instance.order_number = order_number
        instance.save(update_fields=['order_number'])
        logger.info(f"Order created: {order_number} by {instance.user.username}")


@receiver(post_save, sender=Order)
def log_order_status_change(sender, instance, updated_fields=None, **kwargs):
    if updated_fields and 'status' in updated_fields:
        logger.info(
            f"Order {instance.order_number} status changed to: {instance.status}"
        )


@receiver(post_save, sender=OrderItem)
def log_order_item_creation(sender, instance, created, **kwargs):
    if created:
        logger.info(
            f"OrderItem added to order {instance.order.order_number}: "
            f"{instance.product.name} x {instance.quantity}"
        )


@receiver(pre_delete, sender=Order)
def log_order_deletion(sender, instance, **kwargs):
    logger.warning(f"Order deleted: {instance.order_number}")

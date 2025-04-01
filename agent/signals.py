from django.dispatch import receiver
from django.db.models.signals import post_save
from . import models


@receiver(post_save, weak=False, sender=models.Login)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.enqueue()


@receiver(post_save, weak=False, sender=models.GetInvoice)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.enqueue()


@receiver(post_save, weak=False, sender=models.DownloadInvoice)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.enqueue()


@receiver(post_save, weak=False, sender=models.GetInvoiceFile)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.enqueue()


@receiver(post_save, weak=False, sender=models.GetDeduction)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.enqueue()


@receiver(post_save, weak=False, sender=models.GetCurrentDeduction)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.enqueue()


@receiver(post_save, weak=False, sender=models.FileVat)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.enqueue()


@receiver(post_save, weak=False, sender=models.RevokeTax)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.enqueue()


@receiver(post_save, weak=False, sender=models.Invoicing)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.enqueue()


@receiver(post_save, weak=False, sender=models.InvoiceQuota)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.enqueue()


@receiver(post_save, weak=False, sender=models.FileBsis)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.enqueue()


@receiver(post_save, weak=False, sender=models.FileCit)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.enqueue()


@receiver(post_save, weak=False, sender=models.StampDuty)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.enqueue()

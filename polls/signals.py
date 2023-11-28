from django.db.models.signals import post_save, post_delete
import polls.models
from django.dispatch import receiver
from django.core import serializers
import logging

oplogger = logging.getLogger('oplogger')

 
@receiver(post_save) 
def model_saved(sender, instance, **kwargs):
    print(instance.__class__.__name__)
    if instance.__class__.__name__ == 'ProcessedFile' or instance.__class__.__name__ == 'Migration':
        return
    data = serializers.serialize('json', [instance, ])
    log = f'SAVE {data}'
    print(log)
    oplogger.info(msg=log)

@receiver(post_delete) 
def model_deleted(sender, instance, **kwargs):
    print(instance.__class__.__name__)
    if instance.__class__.__name__ == 'ProcessedFile' or instance.__class__.__name__ == 'Migration':
        return
    data = serializers.serialize('json', [instance, ])
    log = f'DELETE {data}'
    print(log)
    oplogger.info(msg=log)
# coding:utf-8

from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        for app in apps.get_app_configs():
            for model in app.get_models(include_auto_created=True):
                if model._meta.managed and not (model._meta.proxy or model._meta.swapped):
                    for base in model.__bases__:
                        if hasattr(base, '_meta'):
                            base._meta.local_many_to_many = []
                    model._meta.local_many_to_many = []
                    with connection.schema_editor() as editor:
                        editor._remake_table(model)

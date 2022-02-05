from django.apps import AppConfig
from iommi.path import register_path_decoding

class BaseConfig(AppConfig):
    name = 'dh.base'

    def ready(self):
        from dh.base.models import (
            Actor,
            MetaData,
            MetaDataObject,
            Role,
            Show,
        )

        register_path_decoding(
            Actor,
            Show,
            Role,
            MetaData,
            MetaDataObject,
        )

# fields.py
from django.db import models

class MediumTextField(models.TextField):
    def db_type(self, connection):
        if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
            return 'mediumtext'
        return super().db_type(connection)


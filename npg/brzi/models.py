import sys
import inspect

import peewee
import peewee_async

from playhouse.postgres_ext import JSONField


DBCONF = dict(
    database='letssharebooks',
    host='0.0.0.0',
    user='letssharebooks',
    password='letssharebooks'
)


DB = peewee_async.PostgresqlDatabase(**DBCONF)
DB.set_allow_sync(False)
OBJ = peewee_async.Manager(DB)


#
# Database models
#

class Library(peewee.Model):
    id = peewee.CharField(primary_key=True)
    librarian = peewee.CharField()
    # last_modified = peewee.CharField()
    library_url = peewee.CharField()
    presence = peewee.CharField(
        default='off',
        choices=[('off', 'off'), ('on', 'on'), ('check', 'check')])

    class Meta:
        database = DB


class Book(peewee.Model):
    id = peewee.CharField(primary_key=True)
    title = peewee.CharField()
    title_sort = peewee.CharField()
    authors = JSONField(default=list)
    timestamp = peewee.CharField()
    comments = peewee.TextField()
    last_modified = peewee.CharField()
    cover_url = peewee.CharField()
    publisher = peewee.CharField()
    formats = JSONField(default=dict)
    tags = JSONField(default=list)
    pubdate = peewee.CharField()
    series_index = peewee.FloatField()
    languages = JSONField(default=list)
    identifiers = JSONField(default=list)

    library = peewee.ForeignKeyField(Library, related_name='books')

    class Meta:
        database = DB


#
# Helper functions
#


def _create_tables():
    # get all class members in current module
    cls_members = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for cls_name, cls in cls_members:
        # filter for peewee Models
        if issubclass(cls, peewee.Model):
            print('Creating table: {}'.format(cls_name))
            cls.drop_table(True, cascade=True)
            cls.create_table(True)


if __name__ == '__main__':
    with OBJ.allow_sync():
        _create_tables()

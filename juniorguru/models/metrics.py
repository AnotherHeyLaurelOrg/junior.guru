from peewee import CharField, IntegerField

from juniorguru.models.base import BaseModel


class GlobalMetric(BaseModel):
    name = CharField(choices=[
        ('avg_monthly_users', None),
        ('avg_monthly_pageviews', None),
        ('subscribers', None),
    ])
    value = IntegerField()

    @classmethod
    def as_dict(cls):
        return {metric.name: metric.value for metric in cls.select()}
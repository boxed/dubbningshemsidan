from django.db import models
from django.template import (
    Template,
    Context,
)


class Actor(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Actor: {self}>'

    def get_absolute_url(self):
        return f'/actors/{self.pk}/'


class Show(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    url = models.CharField(max_length=255, unique=True, db_index=True, null=True, default=None)
    successful_parse = models.BooleanField(default=False)
    raw_data = models.TextField(null=True, default=None)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Show: {self.name}>'

    def get_absolute_url(self):
        return f'/shows/{self.pk}/'


class Role(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    actor = models.ForeignKey(Actor, on_delete=models.PROTECT, related_name='roles')
    show = models.ForeignKey(Show, on_delete=models.PROTECT, related_name='roles')
    index = models.IntegerField(default=0)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Role: show: {self.show} - name: {self.name} - actor: {self.actor}>'

    def get_absolute_url(self):
        return f'/roles/{self.pk}/'

    def recreate(self):
        return [str(self), str(self.actor)]

    def html(self):
        return Template('<td>{{ x.name }}</td><td><a href="{{ x.actor.get_absolute_url }}">{{ x.actor }}</a></td>').render(context=Context(dict(x=self)))

    @property
    def col0(self):
        return self.name

    @property
    def col1(self):
        return self.actor

    def col0_get_absolute_url(self):
        return None

    def col1_get_absolute_url(self):
        return self.actor.get_absolute_url()


class MetaDataObject(models.Model):
    name = models.CharField(max_length=255, db_index=True, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/metadata/{self.pk}/'


class MetaData(models.Model):
    # Key can be none if it's text we didn't know what to do about
    key = models.CharField(max_length=255, db_index=True, blank=True)
    value = models.CharField(max_length=255, db_index=True)
    metadata_object = models.ForeignKey(MetaDataObject, null=True, blank=True, on_delete=models.PROTECT, related_name='foo')
    show = models.ForeignKey(Show, on_delete=models.PROTECT, related_name='metadata')
    index = models.IntegerField(default=0)

    class Meta:
        ordering = ('index',)

    def __repr__(self):
        return f'<MetaData: show: {self.show} - {self.key}: {self.value}>'

    def recreate(self):
        return [self.key, self.value] if self.key else [self.value]

    def html(self):
        t = '<td>{{ x.value }}</td>' if self.metadata_object is None else '<td><a href="{{ x.metadata_object.get_absolute_url }}">{{ x.value }}</a></td>'
        return Template(t).render(context=Context(dict(x=self)))

    def get_absolute_url(self):
        return None

    @property
    def col0(self):
        return self.metadata_object or self.value

    @property
    def col1(self):
        return self.key if self.metadata_object is None else None

    def col0_get_absolute_url(self):
        return self.metadata_object.get_absolute_url() if self.metadata_object else None

    def col1_get_absolute_url(self):
        return None

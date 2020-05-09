from django.db import models


class Actor(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Actor: {self.name}>'

    def get_absolute_url(self):
        return f'/actors/{self.pk}/'


class Show(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Show: {self.name}>'

    def get_absolute_url(self):
        return f'/shows/{self.pk}/'


class Role(models.Model):
    name = models.CharField(max_length=255)
    actor = models.ForeignKey(Actor, on_delete=models.PROTECT, related_name='roles')
    show = models.ForeignKey(Show, on_delete=models.PROTECT, related_name='roles')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Role: {self.show.name} - {self.actor.name}>'

    def get_absolute_url(self):
        return f'/roles/{self.pk}/'

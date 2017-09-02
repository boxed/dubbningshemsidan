from django.db import models


class Actor(models.Model):
    name = models.CharField(max_length=255)

    def __repr__(self):
        return f'<Actor: {self.name}>'


class Show(models.Model):
    name = models.CharField(max_length=255)

    def __repr__(self):
        return f'<Show: {self.name}>'


class Role(models.Model):
    name = models.CharField(max_length=255)
    actor = models.ForeignKey(Actor)
    show = models.ForeignKey(Show)

    def __repr__(self):
        return f'<Role: {self.show.name} - {self.actor.name}>'

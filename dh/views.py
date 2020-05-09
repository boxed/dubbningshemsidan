from iommi import (
    Table,
    Page,
)

from dh.base.models import (
    Actor,
    Show,
    Role,
)


def actor(request, pk):
    actor = Actor.objects.get(pk=pk)
    return Table(
        title=actor.name,
        auto__rows=actor.roles.all(),
    )


def show(request, pk):
    show = Show.objects.get(pk=pk)
    return Table(
        title=show.name,
        auto__rows=show.roles.all(),
    )


def index(request):
    def basic(model):
        return Table(
            auto__model=model,
            page_size=5,
            columns__name__filter__include=True,
            columns__name__filter__freetext=True,
        )

    class IndexPage(Page):
        actors = basic(Actor)
        shows = basic(Show)
        roles = basic(Role)

    return IndexPage()

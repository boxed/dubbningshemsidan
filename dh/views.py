from iommi import (
    Header,
    html,
    Page,
    Table,
)

from dh.base.models import (
    Actor,
    Role,
    Show,
)


def actor(request, pk):
    actor = Actor.objects.get(pk=pk)
    return Table(
        title=actor.name,
        auto__rows=actor.roles.all(),
    )


def show(request, pk):
    show = Show.objects.get(pk=pk)
    return Page(
        parts__roles=Table(
            title=show.name,
            auto__rows=show.roles.all(),
        ),
        parts__raw_data = html.pre(show.raw_data),
    )


def index(request):
    def basic(model, **kwargs):
        return Table(
            auto__model=model,
            page_size=5,
            columns__name__filter__include=True,
            columns__name__filter__freetext=True,
            columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
            **kwargs
        )

    class IndexPage(Page):
        title = Header(children__text='Dubbningshemsidans databas')

        actors = basic(Actor)
        shows = basic(Show, columns__raw_data__include=False, columns__successful_parse__filter__include=True)
        roles = basic(Role)

    return IndexPage()

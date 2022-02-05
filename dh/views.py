from django.utils.safestring import mark_safe
from iommi import (
    Header,
    html,
    Page,
    Table,
    Form,
)
from iommi.path import decode_path

from dh.base.models import (
    Actor,
    MetaData,
    MetaDataObject,
    Role,
    Show,
)


class NameLinkTable(Table):
    class Meta:
        page_size = 5
        columns__name__cell__url = lambda row, **_: row.get_absolute_url()


def role(request, pk):
    role = Role.objects.get(pk=pk)

    class MyPage(Page):
        title = Header(role.name)
        actor = html.a(role.actor, attrs__href=role.actor.get_absolute_url())
        p = html.p()
        show = html.a(role.show, attrs__href=role.show.get_absolute_url())

    return MyPage()


@decode_path
def metadata_object(request, meta_data_object):
    return Table(
        title=str(meta_data_object),
        auto__rows=MetaData.objects.filter(metadata_object=meta_data_object),
        columns__value__include=False,
        columns__index__include=False,
        columns__metadata_object__include=False,
    )


@decode_path
def show(request, show):
    if 'reparse' in request.GET:
        from dubbning import parse
        parse(show)

    data = sorted(
        list(show.roles.all()) + list(show.metadata.all()),
        key=lambda x: x.index
    )

    class ShowPage(Page):
        title = Header(show)
        foo = Table(
            rows=data,
            attrs__class__table=False,
            header__template=None,
            page_size=None,
            columns=dict(
                col0__auto_rowspan=True,
                col0__cell__attrs__colspan=lambda row, **_: 2 if row.col1 is None else 1,
                col0__cell__url=lambda row, **_: row.col0_get_absolute_url(),
                col1__cell__url=lambda row, **_: row.col1_get_absolute_url(),
            )
        )
        raw_data = html.pre(show.raw_data, include='raw_data' in request.GET)

    return ShowPage()


search_form = Form(
    fields__q__include=True,
    fields__q__label__attrs__style__display='none',
    attrs__action='/search/',
    attrs__method='GET',
    actions__submit__display_name='Search',
)

focus_on_search_form = mark_safe('<script>document.getElementById("id_search__search").focus();</script>')


def search(request):
    q = request.GET['q'].strip()

    class MyPage(Page):
        title = Header('Search results')

        search = search_form
        focus_on_search_form = focus_on_search_form

        actors = NameLinkTable(auto__rows=Actor.objects.filter(name__icontains=q))
        roles = NameLinkTable(auto__rows=Role.objects.filter(name__icontains=q), columns__index__include=False)
        show = NameLinkTable(
            auto__rows=Show.objects.filter(name__icontains=q),
            columns__successful_parse__include=False,
            columns__raw_data__include=False,
        )
        other = NameLinkTable(
            title='Other',
            auto__rows=MetaDataObject.objects.filter(name__icontains=q),
            columns__key=dict(
                include=True,
                attr=None,
                cell__value=lambda row, **_: ', '.join(x.key for x in row.foo.all()),
            ),
        )

    return MyPage()


def index(request):
    class IndexPage(Page):
        title = Header(children__text='Dubbningshemsidans databas')

        search = search_form
        focus_on_search_form = focus_on_search_form

        shows = NameLinkTable(
            auto__model=Show,
            columns__raw_data__include=False,
            columns__successful_parse__include=False,
            columns__url__cell__url=lambda value, **_: value,
        )
        actors = NameLinkTable(auto__model=Actor)

    return IndexPage()

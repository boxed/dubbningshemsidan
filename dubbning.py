import re

import ftfy
import requests
from bs4 import BeautifulSoup
from tri_struct import Struct

from dh.base.models import Show, Actor, Role


def normalize(name):
    return name.strip().title()


def get_actors_by_role_from_url(url):
    x = requests.get(url)
    soup = BeautifulSoup(ftfy.fix_text(x.text), "html.parser")

    sections = re.split('\n\n([^\n]+):\n', soup.find('pre').text.replace('\r\n', '\n'))
    sections = [x.partition(' (')[0].lower() for x in sections]

    # TODO: 'Huvudroller', 'Röster'

    if 'svenska röster' not in sections:
        print(url)
        print('    ', sections)
        return None
    voices_index = sections.index('svenska röster')

    voices = sections[voices_index + 1]

    lines = [x.split('\t') for x in voices.split('\n')[1:] if not x.startswith(' ')]
    lines = [[y for y in line if y] for line in lines]
    lines = [(normalize(line[0]), normalize(line[-1])) for line in lines if len(line) > 1]
    return dict(lines)


def get_data_for_shows():
    index_url = 'http://www.dubbningshemsidan.se/credits/'
    x = requests.get(index_url)
    soup = BeautifulSoup(ftfy.fix_text(x.text), "html.parser")
    link_tags = soup.select('.mainbg table a')
    return [
        Struct(
            url=index_url + x['href'],
            name=x.text,
        )
        for x in link_tags
    ]


def scrape_dubbningshemsidan():
    for show_data in get_data_for_shows():
        # if show_data.name != 'Frost':
        #     continue
        url = show_data.url

        urls_without_data = {
            'http://www.dubbningshemsidan.se/credits/kalleankasjul/',
            'http://www.dubbningshemsidan.se/credits/lillabla/',
            'http://www.dubbningshemsidan.se/credits/paddington/',
            'http://www.dubbningshemsidan.se/credits/starla/',
        }

        if url in urls_without_data:
            continue

        actor_by_role = get_actors_by_role_from_url(url)

        if not actor_by_role:
            continue

        show, _ = Show.objects.get_or_create(name=show_data.name)

        for role_name, actor_name in actor_by_role.items():
            actor, _ = Actor.objects.get_or_create(name=actor_name)
            role, _ = Role.objects.get_or_create(name=role_name, actor=actor, show=show)

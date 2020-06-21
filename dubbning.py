import re

import ftfy
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from tri_struct import Struct

from dh.base.models import (
    Show,
    Actor,
    Role,
    MetaData,
    MetaDataObject,
)


def normalize(name):
    return name.strip().title()


def parse_spaces_to_tabs(lines):
    return [re.sub('  +', '\t', l.rstrip()) for l in lines]


def parse0(lines):
    return [re.sub('\t+', '\t', l.rstrip()) for l in lines]


def parse1(lines):
    return [l.split('\t') for l in lines]


def parse2(rows):
    r = []
    col0 = None
    for row in rows:
        # This is a heading, store for next lines
        if row[0] and row[0].endswith(':'):
            col0 = row[0]
        # There was a previous heading and the leftmost column is blank
        elif col0 and len(row) > 1 and not row[0]:
            # Use the previous heading
            row[0] = col0
        # This is a new paragraph, forget the last heading
        if len(row) == 0 or (len(row) == 1 and not row[0]):
            col0 = None
        r.append(row)
    return r


skiplist = {
    'fotnot',
}


def parse3(show, rows):
    r = []
    heading = None
    for i, row in enumerate(rows):
        # New paragraph, forget heading
        if not row or not row[0]:
            heading = None

        r0_lower = row[0].lower().rstrip(':') if row else None

        invalid_first_char = ('(', '"', '-')

        # This is a heading, store for next lines
        if len(row) == 1 and row[0].endswith(':'):
            heading = row[0].rstrip(':')
            r.append(MetaData.objects.create(index=i, show=show, key='', value=row[0]))
        elif len(row) == 2 and row[0].endswith(':') and r0_lower not in skiplist and not row[0][0] in invalid_first_char:
            role = row[0].rstrip(':')
            r.append(Role.objects.create(index=i, show=show, name=role, actor=Actor.objects.get_or_create(name=row[1])[0]))
        elif heading and len(row) == 2 and not row[0][0] in invalid_first_char:
            r.append(Role.objects.create(index=i, show=show, name=row[0], actor=Actor.objects.get_or_create(name=row[1])[0]))
        elif heading:
            value = '\t'.join(row)
            metadata_object, _ = MetaDataObject.objects.get_or_create(name=value)
            r.append(MetaData.objects.create(index=i, show=show, key=heading, value=value, metadata_object=metadata_object))
        elif len(row) == 2 and row[0] and row[1] and r0_lower not in skiplist and not row[0][0] in invalid_first_char:
            r.append(Role.objects.create(index=i, show=show, name=row[0], actor=Actor.objects.get_or_create(name=row[1])[0]))
        elif len(row) == 2:
            r.append(MetaData.objects.create(index=i, show=show, key=row[0], value=row[1]))
        else:
            r.append(MetaData.objects.create(index=i, show=show, key='', value='\t'.join(row).strip()))

    return r


def parse(show):
    show.roles.all().delete()
    show.metadata.all().delete()
    lines = show.raw_data.split('\n')
    p_tabs = parse_spaces_to_tabs(lines)
    p0 = parse0(p_tabs)
    p1 = parse1(p0)
    p2 = parse2(p1)
    parse3(show, p2)


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
    print('Fetching raw data...')
    for show_data in tqdm(get_data_for_shows()):
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

        show, _ = Show.objects.get_or_create(name=show_data.name)
        if show.raw_data is None:
            x = requests.get(url)
            soup = BeautifulSoup(ftfy.fix_text(x.text), "html.parser")
            raw_data = soup.find('pre').text
            show.raw_data = raw_data
        show.url = url
        show.save()

    parse_raw_data()


def parse_raw_data():
    print('Parsing...')
    for show in tqdm(Show.objects.all()):
        parse(show)
        show.successful_parse = True
        show.save()

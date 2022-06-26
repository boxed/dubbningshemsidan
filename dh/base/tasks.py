import Levenshtein

from dh.base.models import Actor
from dubbning import (
    parse_raw_data,
    scrape_dubbningshemsidan,
)


def task(f):
    f._is_task = True
    return f


@task
def scrape():
    scrape_dubbningshemsidan()


@task
def parse():
    parse_raw_data()


@task
def find_spelling_errors():
    names = [x.name for x in Actor.objects.all()]
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            if Levenshtein.distance(x, y) <= 1:
                print(f"    '{x}': '{y}',")

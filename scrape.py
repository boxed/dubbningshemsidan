import os

import django


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dh.settings")
    django.setup()

    from dubbning import scrape_dubbningshemsidan

    scrape_dubbningshemsidan()
    # from dubbning import get_actors_by_role_from_url
    # print(get_actors_by_role_from_url('https://www.dubbningshemsidan.se/credits/trassel/'))

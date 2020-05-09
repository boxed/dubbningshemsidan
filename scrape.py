import os

import django


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dh.settings")
    django.setup()

    from dubbning import scrape_dubbningshemsidan

    scrape_dubbningshemsidan()

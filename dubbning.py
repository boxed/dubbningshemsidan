import requests
from bs4 import BeautifulSoup

with open('dubbning.txt', encoding='utf8') as f:
    t = f.read()

def parse_actor_by_role(t):
    voices = None
    for section in t.split('\n\n'):
        if section.startswith('Svenska röster'):
            voices = section
            break
    if voices is None:
        # TODO: handle credits that have no voice coupled to them
        return {}
    lines = [x.split('\t') for x in voices.split('\n')[1:] if not x.startswith(' ')]
    lines = [[y for y in l if y] for l in lines]
    lines = [(l[0], l[-1]) for l in lines if len(l) > 1]
    return dict(lines)

#print(parse_actor_by_role(t))
#exit()

def actors_by_role_from_url(url):
    x = requests.get(url)
    soup = BeautifulSoup(x.content)
    return parse_actor_by_role(soup.find('pre').text)
    
def all_series_and_movie_data():
    index_url = 'http://www.dubbningshemsidan.se/credits/'
    x = requests.get(index_url)
    soup = BeautifulSoup(x.text)
    link_tags = soup.select('.mainbg table a')
    return [dict(url=index_url + x['href'], title=x.text) for x in link_tags]
    
#print(all_series_and_movie_data())
#exit()

for data in all_series_and_movie_data():
    url = data['url']
    a_by_r = actors_by_role_from_url(url)
    print(data['title'], url, len(a_by_r))
    break

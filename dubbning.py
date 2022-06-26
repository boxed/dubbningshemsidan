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


name_corrections = {
    'Adam Alsing': 'Adam Allsing',
    'Adam Fietz/': 'Adam Fietz',
    'Adan Fietz': 'Adam Fietz',
    'Asam Fietz': 'Adam Fietz',
    'Adam Vassée': 'Adam Vassé',
    'Aksel Morrisse': 'Aksel Morisse',
    'Alba Wadman': 'Alba Vadman',
    'Amadeo Quintanilla Lindström': 'Amadeo Quintanilla Lidström',
    'Amadeus Häggqvist Sögaard': 'Amadeus Häggkvist Sögaard',
    'Amanda Kruger': 'Amanda Krüger',
    'Ana-Gil de Melo Nascimento': 'Ana Gil de Melo Nascimento',
    'Anastasious Soulis': 'Anastasios Soulis',
    'Anders Forsslund': 'Anders Forslund',
    'Anders öjebo': 'Anders Öjebo',
    'Andreas Nisson': 'Andreas Nilsson',
    'Andreas Rothlin Svenssin': 'Andreas Rothlin Svensson',
    'Andreas Rothlin Svensson,': 'Andreas Rothlin Svensson',
    'Angela Kovacs': 'Angela Kovács',
    'Ann-Sofie Andersson': 'Ann Sofie Andersson',
    'Anna Johnsson': 'Anna Johnson',
    'Anna Rygren': 'Anna Rydgren',
    'Anna-Lisa Kronström': 'Anna-Lisa Cronström',
    'Annelie Ahlgren': 'Anneli Ahlgren',
    'Annelie Berg': 'Anneli Berg',
    'ANNELIE BLOMSTRÖM': 'Anneli Blomström',
    'Annelie Heed': 'Anneli Heed',
    'Annelie Martini': 'Anneli Martini',
    'Annelie Norberg': 'Anneli Norberg',
    'Annelie Berg-Bhagavan': 'Annelie Berg Bhagavan',
    'Annika Edstam': 'Annica Edstam',
    'Anton Lundqvist': 'Anton Lundquist',
    'Anton Olafsson': 'Anton Olofsson',
    'Anton Olofosson': 'Anton Olofsson',
    'Anton Olofson': 'Anton Olofsson',
    'Anton Olofsson Raeder': 'Anton Olofson Raeder',
    'Arianna Lleshaj': 'Ariana Lleshaj',
    'Astrid Assega': 'Astrid Assefa',
    'Axel Karlsson': 'Axel Carlsson',
    'Beata Harrysson': 'Beata Harryson',
    'Beatrice Järås/': 'Beatrice Järås',
    'Bengt Jörnblad': 'Bengt Järnblad',
    'Benjamin Wahlgren/': 'Benjamin Wahlgren',
    'Bert-Åke Varg': 'Bert Åke Varg',
    'Björn Gustafsson': 'Björn Gustafson',
    'Karl Dyall': 'Carl Dyall',
    'Carl-Henric Qvarfordt': 'Carl Henric Qvarfordt',
    'Carl-Magnus Liljedahl': 'Carl Magnus Liljedahl',
    'Carl-Magnus Lilljedahl': 'Carl-Magnus Liljedahl',
    'Carla Abrahamsen': 'Carla Abrahamse',
    'Carla Abrahamssen': 'Carla Abrahamsen',
    'Casper Bjørner': 'Casper Björner',
    'Cathrine Hansson': 'Catherine Hansson',
    'Cecilia Frohde': 'Cecilia Frode',
    'Cecilia Lundh': 'Cecilia Lund',
    'Cecilia Olin': 'Cecilia Ohlin',
    'Cecilia Wrangel Schough': 'Cecilia Wrangel Schoug',
    'Charlotte Strandberg': 'Charlott Strandberg',
    'Charlotte Ardai Jennefors/': 'Charlotte Ardai Jennefors',
    'Charlotte Ardai-Jennefors': 'Charlotte Ardai Jennefors',
    'Charlotte Ardai-Jennerfors': 'Charlotte Ardai Jennefors',
    'Christel Körner/': 'Christel Körner',
    'Cristian Troncoso': 'Christian Troncoso',
    'Christoffer Levak': 'Christoffer Levah',
    'Christoffer Schough': 'Christoffer Schoug',
    'Christopher Carlqvist': 'Christopher Carlkvist',
    'Claes Grufman-Björnlund': 'Claes Grufman Björnlund',
    'Claes Ljunmark': 'Claes Ljungmark',
    'Daniel Engmann': 'Daniel Engman',
    'Dick Ericksson': 'Dick Eriksson',
    'Dick Erikssn': 'Dick Eriksson',
    'Doréen Denning': 'Doreen Denning',
    'Edward Lindblom': 'Edvard Lindblom',
    'Elina Raeder Olofsson': 'Elina Raeder Olofson',
    'Elina Raeder-Olofson': 'Elina Raeder Olofson',
    'Elina Raeder-Olofsson': 'Elina Raeder Olofson',
    'Elina Raeder-Olofsson': 'Elina Raeder Olofson',
    'Elizabet Edgren': 'Elisabet Edgren',
    'Ellen Thuresson': 'Ellen Thureson',
    'Elsa Gröndal Trotzig': 'Elsa Gröndahl Trotzig',
    'Emilie Clausen': 'Emelie Clausen',
    'Emilie Kempe': 'Emelie Kempe',
    'Emil Almén': 'Emil Almen',
    'Emma Swenninger': 'Emma Svenninger',
    'Erik Bergelin': 'Eric Bergelin',
    'Erik Donell': 'Eric Donell',
    'Erik Ahrnbom': 'Erik Ahnbom',
    'Erik Arhnbom': 'Erik Ahnbom',
    'Eskil Eckert-Lundin': 'Eskil Eckert Lundin',
    'Ewa Maria Björkström Roos': 'Eva Maria Björkström Roos',
    'Ewa Röse': 'Eva Röse',
    'Ewa Widgren': 'Eva Widgren',
    'Ewa Fröling': 'Ewa Fröhling',
    'Ewa Maria Björkström-Roos': 'Ewa Maria Björkström Roos',
    'Ewa-Maria Björkström Roos': 'Ewa Maria Björkström Roos',
    'EwaMaria Björkström-Roos': 'Ewa Maria Björkström Roos',
    'EwaMaria Roos': 'Ewa Maria Roos',
    'Fabienne Glader': 'Fabianne Glader',
    'Felix Wallón': 'Felix Wallon',
    'Filip Hallqvist/': 'Filip Hallqvist',
    'Filippa Alm-Nylén': 'Filippa Alm Nylén',
    'Fred Johansson': 'Fred Johanson',
    'Fredrik Hiller': 'Frederik Hiller',
    'Fredrik Beckmann': 'Fredrik Beckman',
    'Fredrik Bäckman': 'Fredrik Beckman',
    'Fredrik Dolk/': 'Fredrik Dolk',
    'Frida Linnell': 'Frida Linell',
    'Frida Örn': 'Frida Öhrn',
    'Gizela Rash': 'Gizela Rasch',
    'Gladys del Pilar Bergh': 'Gladys del Pilar Berg',
    'Gry Forsell': 'Gry Forssell',
    'Gunnar Ernblad/': 'Gunnar Ernblad',
    'Gunnar Ernblad/': 'Gunnar Ernblad',
    'Gustav Hammarsten': 'Gustaf Hammarsten',
    'Gustav Larsson': 'Gustav Larson',
    'Gösta Pruzelius': 'Gösta Prüzelius',
    'Gösta Prützelius': 'Gösta Prüzelius',
    'Hanna Bhagavan': 'Hana Bhagavan',
    'Sanna Ekman': 'Hanna Ekman',
    'Hannah Storm-Nielsen': 'Hanna Storm-Nielsen',
    'Hans Gustavsson': 'Hans Gustafsson',
    'Heidi Gardenkans': 'Heidi Gardenkrans',
    'Helena Thornqvist': 'Helena Thörnqvist',
    'Heléne Lundström': 'Helene Lundström',
    'Henrik Blomqvist': 'Henrik Blomkvist',
    # 'Henrik Norlén': 'Henrik Nordén',
    'Hilda Henzen': 'Hilda Henze',
    'Hilde Henze': 'Hilda Henze',
    'Hilga Holgersson': 'Hilda Holgersson',
    'Hugo Gummesson': 'Hugo Gummeson',
    'Hugo Paulsson': 'Hugo Paulson',
    'Håkan Julander': 'Håkan Juhlander',
    'Håkan Jullander': 'Håkan Juhlander',
    'Håkan Jullander': 'Håkan Julander',
    'Ikue Otani': 'Ikue Ohtani',
    'Ingmar Carlehed': 'Ingemar Carlehed',
    'Ingvar Kjellsson': 'Ingvar Kjellson',
    'Irene Lindh': 'Irene Lind',
    'Iréne Lindh': 'Irene Lindh',
    'Isak Gummesson': 'Isak Gummeson',
    'Isidor Beslik-Löfdahl': 'Isidor Beslick-Löfdahl',
    'Jacob Bergmalm': 'Jacob Bergemalm',
    'Jakob Bergström': 'Jacob Bergström',
    'Jacob Nordensson': 'Jacob Nordenson',
    'Jakob Stadell': 'Jacob Stadell',
    'James Lundh': 'James Lund',
    'Jan Jönsson': 'Jan Jönson',
    'Jan Modin/': 'Jan Modin',
    'Jan Simonsson': 'Jan Simonssen',
    'Jan Waldekranz': 'Jan Waldekrantz',
    'Jennie JKahns': 'Jennie Jahns',
    'Jenny Wåhlander': 'Jenny Wåhander',
    'Jesper Adefelt': 'Jesper Adefeldt',
    'Jesper Adefelt/': 'Jesper Adefelt',
    'Jester Adefelt': 'Jesper Adefelt',
    'Jimmy Björndahl/': 'Jimmy Björndahl',
    'Joakim Jennefors': 'Joakim Jenneford',
    'Joakim Jennefors/': 'Joakim Jennefors',
    'Joakim Jennerfors': 'Joakim Jennefors',
    'Johan Randqvist': 'Johan Randquist',
    'Johan Rundqvist': 'Johan Randqvist',
    'Johan Schninkler': 'Johan Schinkler',
    'Johan Ulvesson': 'Johan Ulveson',
    'John-Alexander Eriksson': 'John Alexander Eriksson',
    'John Harrysson': 'John Harryson',
    'Jonas Hellman Driessen': 'Jonas Hellman Driesen',
    'Jonathan Jaarnek-Norén': 'Jonathan Jaarnek Norén',
    'Josefin Ahlqvist': 'Josefin Ahlquist',
    'Josefine Götestam': 'Josefin Götestam',
    'Josefina Hylén': 'Josefina Hylen',
    'Josefine Götestam': 'Josefine Göstestam',
    'Josefine Götestam': 'Josefine Götenstam',
    'Josephine Bornebush': 'Josephine Bornebusch',
    'Juan Rodríguez': 'Juan Rodriguez',
    'Juan Rodríguez': 'Juan Rodrígues',
    'Julia Moreau/': 'Julia Moreau',
    'Julia Simonsson': 'Julia Simonson',
    'Julius Lindfors': 'Julius Lindford',
    'Karolina Khativ-Nia': 'Karolina Khatib-Nia',
    'Katarina Josephsson': 'Katarina Josephson',
    'Kjerstin Dellert': 'Kerstin Dellert',
    'Kristian Stålgren': 'Kristian Ståhlgren',
    'Kristina Adolphsson': 'Kristina Adolphson',
    'Laila Adéle': 'Laila Adèle',
    'Lars-Göran Persson': 'Lars Göran Persson',
    'Lawrence Macrory': 'Lawrence Mackrory',
    'Lee Tokar': 'Lee Tockar',
    'Leif Andrée': 'Leif André',
    'Lena Carlsson': 'Lena Carlson',
    'Lena-Pia Bernhardsson': 'Lena-Pia Bernhardson',
    'Leopoldo Méndez': 'Leopoldo Mendez',
    'Lilly Thuresson': 'Lilly Thureson',
    'Lily Thuresson': 'Lilly Thuresson',
    'Lily Wahlsteen': 'Lilly Wahlsteen',
    'Linnéa Berglund': 'Linnea Berglund',
    'Linnéa Järpestam': 'Linnea Järpestam',
    'Linnéa Öjebo Caiman': 'Linnea Öjebo Caiman',
    'Linnéa Fändå': 'Linnéa Frändå',
    'Linus Lindman': 'Linus Lidman',
    'Loke Ornered': 'Loke Onered',
    'Lovixa Blixt': 'Lovisa Blixt',
    'Lucas Kråuger': 'Lucas Kruger',
    'Lucas Krüger': 'Lucas Kruger',
    'Lukas Kruger': 'Lucas Kruger',
    'Lucas Krüger/': 'Lucas Krüger',
    'Lukas Krüger': 'Lucas Krüger',
    'Ludwig Dietmann': 'Ludvig Dietmann',
    'Ludvig Johansson Wiborg': 'Ludvig Johansson Wiberg',
    'Ludvig Törner': 'Ludvig Turner',
    'Ludwig Dietmann': 'Ludwig Dietman',
    'Lukas Krüger': 'Lukas Kruger',
    # 'm.fl.': 'm.fl',
    'Magnus Rongedal': 'Magnus Rongedahl',
    'Magnus Roosmann': 'Magnus Roosman',
    'Mia Hansson': 'Maia Hansson',
    'Malena Lazlo': 'Malena Laszlo',
    'Malin Güettler': 'Malin Guettler',
    'Malin-My Wall': 'Malin My Wall',
    'Malva Goldmann': 'Malva Goldman',
    # 'Mann': 'Man',
    # 'Max': 'Man',
    'Markus Hartwig': 'Marcus Hartwig',
    'Marie Rydberg': 'Maria Rydberg',
    'Maria Weisby/': 'Maria Weisby',
    'Marianne Wäyrynen': 'Marianne Väyrynen',
    'Marie Richardsson': 'Marie Richardson',
    'Marie Robertsson': 'Marie Robertson',
    'Marie Sernholt': 'Marie Serneholt',
    'Martin Carlberg': 'Martin Calberg',
    'Mathias Bladh': 'Mathias Blad',
    'Mathias Henriksson': 'Mathias Henrikson',
    'Matilda Knutsson': 'Mathilda Knutsson',
    'Mathilda Lilliestiärna': 'Mathilda Lilliestierna',
    'Matilda Smedius': 'Mathilda Smedius',
    'Matilda Knutsson': 'Matilda Knutson',
    'Maude Cantoreggi': 'Maud Cantoreggi',
    'Max Lorenz': 'Max Lorentz',
    'Maximillian Fjellner': 'Maximilian Fjellner',
    'Maximillian Fjellner': 'Maximilliam Fjellner',
    'Maxmilliam Fjellner': 'Maximilliam Fjellner',
    'Mia Kihl/': 'Mia Kihl',
    'Micaela Remondi': 'Micaela Ramondi',
    'Michaela Remondi': 'Micaela Remondi',
    'Michael B. Tretow': 'Michael B Tretow',
    'Michael Blomqvist': 'Michael Blomquist',
    'Michael Blomqvisth': 'Michael Blomqvist',
    'Mikael Regenholz': 'Mikael Regenholtz',
    'Mikaela Regenholz': 'Mikael Regenholz',
    'Nikael Roupé': 'Mikael Roupé',
    'Mikaela Ardai-Jennefors': 'Mikaela Ardai Jennefors',
    'Mikaela Tidermark': 'Mikaela Tidemark',
    'Mikaela Tidermark/': 'Mikaela Tidermark',
    'Mimmi Sandén': 'Mimmi Sanden',
    'Monica Nordqvist': 'Monica Nordquist',
    'Morghan Elfving': 'Morgan Elfving',
    'Märta Josefsson': 'Märta Josefson',
    'Måns Nathanaelson': 'Måns Natanaelson',
    'Måns Nathanaelsson': 'Måns Nathanaelson',
    'Nanne Grönwall': 'Nanne Grönvall',
    'Niclas Berglund': 'Nicklas Berglund',
    'Niklas Romson': 'Nicklas Romson',
    'Niklas Ekholm': 'Niclas Ekholm',
    'Niels Pettersson/': 'Niels Pettersson',
    'Nikita Winter': 'Nikita Vinter',
    'Niklas Lindh': 'Niklas Lind',
    'Nina Nelsson': 'Nina Nelson',
    'Norea Sjöqvist': 'Norea Sjöquist',
    'Nour El-Refai': 'Nour El Refai',
    'Olav F Andersen/': 'Olav F Andersen',
    'Ole Örnered': 'Ole Ornered',
    'Olli Markenros': 'Olli Markenroos',
    'Orlando Wahlsteen': 'Orlanda Wahlsteen',
    'Oscar Harrysson': 'Oscar Harryson',
    'Oskar Harryson': 'Oscar Harryson',
    'Oskar Harrysson': 'Oscar Harrysson',
    'Oskar Nilsson': 'Oscar Nilsson',
    'Oskar Svensson': 'Oscar Svensson',
    'Oskar Harrysson': 'Oskar Harryson',
    'Patrik Almkvisth': 'Patrik Almkvist',
    'Patrik Almqvisth': 'Patrik Almkvisth',
    'Patrik Martinsson': 'Patrik Martinson',
    'Pauline Åberg': 'Paulina Åberg',
    'Per-Arne Wahlgren': 'Per Arne Wahlgren',
    'Per-Erik Hallin': 'Per Erik Hallin',
    'Per Steffenson': 'Per Steffensen',
    'Peter Harryson/': 'Peter Harryson',
    'Peter Harrysson': 'Peter Harryson',
    'PETER KJÄLLSTRÖM': 'PETER KJELLSTRÖM',
    'Peter Kjällström': 'Peter Kjellström',
    'PETER SJÖQVIST': 'PETER SJÖQUIST',
    'Peter Sjöquist': 'Peter Sjöquisr',
    'Peter Sjöqvist': 'Peter Sjöquist',
    'Phillip Zandén': 'Philip Zandén',
    # 'Polis 2': 'Polis 1',
    'Pontus Gustafsson': 'Pontus Gustafson',
    'Pontus Gustavsson': 'Pontus Gustafsson',
    'Rachel Molin': 'Rachel Mohlin',
    'Rafael Pettersson': 'Rafael Petterson',
    'Ragna Nyblom/': 'Ragna Nyblom',
    'Ragnar Falk': 'Ragnar Falck',
    'Rakel Wärmländer': 'Rakel Wermländer',
    'Rickard Carlsohn': 'Richard Carlsohn',
    'Rikard Wolff': 'Rickard Wolff',
    'Rico Rönnbäck': 'Ricko Rönnbäck',
    'Rikard Bergqvist': 'Rikard Bergquist',
    'Robert Cronholt/': 'Robert Cronholt',
    'Robert Gustavsson': 'Robert Gustafsson',
    'Rufus Bladh': 'Rufus Blad',
    'Ruth Almgren': 'Rut Almgren',
    'Sebastian Gahrton': 'Sabastian Gahrton',
    'Sandra Caménisch': 'Sandra Camènisch',
    'Sanna Sundqvist': 'Sanna Lundqvist',
    'Sanna Sundqvist': 'Sanna Sundkvist',
    'Sarah Dawn Finer': 'Sara Dawn Finer',
    'Shebly Niavarani': 'Shebli Niavarani',
    'Simon Nøiers': 'Simon Nöiers',
    'Simon Sjöqvist': 'Simon Sjökvist',
    'Simon Sjöqvist': 'Simon Sjöquist',
    'Sissel Kyrkjebø': 'Sissel Kyrkjebö',
    'Siw Malmqvist': 'Siw Malmkvist',
    'Sofia Calman': 'Sofia Caiman',
    # 'Soldat 2': 'Soldat 1',
    'Staffan Hellerstam': 'Staffan Hallerstam',
    'Stefan Lungqvist': 'Stefan Ljungqvist',
    'Sten-Johan Hedman': 'Sten Johan Hedman',
    'STEPHAN KARLSÉN': 'STEPHAN CARLSÉN',
    'Stephan Karlsén': 'Stephan Carlsén',
    'Stephen Karlsén': 'Stephan Karlsén',
    'Suzanne Reuter': 'Susanne Reuter',
    'SuzannaDilber': 'Suzanna Dilber',
    'Svante Thuresson': 'Svante Thureson',
    'Sven-Erik Vikström': 'Sven Erik Vikström',
    'Sven Wolter': 'Sven Wollter',
    'Teodore Runsiö': 'Teodor Runsiö',
    'Theodor Siljeholm': 'Teodor Siljeholm',
    'Thea Gothensjö': 'Thea Gotensjö',
    'Thea Järnbro': 'Thea Jernbro',
    'Thérese Andersson Lewis': 'Therese Andersson Lewis',
    'Therese Reuterswärd/': 'Therese Reuterswärd',
    'Thomas Engelbrektsson': 'Thomas Engelbrektson',
    'Tomas Hanzon': 'Thomas Hanzon',
    'Tomas Hellberg': 'Thomas Hellberg',
    'Tomas Laustiola': 'Thomas Laustiola',
    'Thomas Pettersson': 'Thomas Petersson',
    'Thérèse Andersson': 'Thérese Andersson',
    'Thérèse Andersson Lewis': 'Thérese Andersson Lewis',
    'Thérése Andersson Lewis': 'Thérese Andersson Lewis',
    'Thérése Andersson Lewis': 'Thérèse Andersson Lewis',
    'Tin Carlsson': 'Tim Carlsson',
    'Tim Johnsson': 'Tim Johnson',
    'Tim Lindner-Morin': 'Tim Lindner Morin',
    # 'Tjuv 2': 'Tjuv 1',
    'Tobias Swärd/': 'Tobias Swärd',
    'Tomas Bolme/': 'Tomas Bolme',
    'Tor Isedal/': 'Tor Isedal',
    'Towa Carson': 'Tova Carson',
    'Towa Carsson': 'Towa Carson',
    'Truls Gille': 'Trulls Gille',
    'Tyra Olin': 'Tya Olin',
    'Ulf Bergstrand/': 'Ulf Bergstrand',
    'Ulf Eklund/': 'Ulf Eklund',
    'Ulf P. Johansson': 'Ulf G. Johansson',
    'Ulf-Håkan Jansson': 'Ulf Håkan Jansson',
    'Ulf Peder Johansson/': 'Ulf Peder Johansson',
    'Ulf-Peder Johansson': 'Ulf Peder Johansson',
    'Ulricha Johnsson': 'Ulricha Johnson',
    'Urban Wrethagen': 'Uran Wrethagen',
    'Viki Benkert': 'Vicki Benkert',
    'Viktor Kilsberger': 'Victor Kilsberger',
    'Viktor Lindblad': 'Victor Lindblad',
    'Ville Ziljeholm': 'Ville Siljeholm',
    'Vivian Cardinal': 'Vivan Cardinal',
    'Vivian Vardinal': 'Vivian Cardinal',
    'Zacharias Bladh': 'Zacharias Blad',
    'Zeth Nätterqvist': 'Zeth Nätterquist',
    'Åsa Jonsson': 'Åsa Johnsson',
    'Åsa Jonsson': 'Åsa Jonson',
    'Åskådare 2': 'Åskådare 1',
    'Özz Nûyen': 'Özz Nûjen',

    'Carl Magnus Liljedahl': 'Carl-Magnus Liljedahl',
    'Eva Maria Björkström Roos': 'Ewa Maria Björkström Roos',
    'Gunnar Ernblad': 'Gunnar Ernblad ',
    'Henrik Nordén': 'Henrik Norlén',
    'Håkan Juhlander': 'Håkan Julander',
    'Irene Lind': 'Irene Lindh',
    'Irene Lindh': 'Irené Lindh',
    'Joakim Jenneford': 'Joakim Jennefors',
    'Johan Randquist': 'Johan Randqvist',
    'Kim Stålnacke': 'Kim Stålnacke ',
    'Lilly Thureson': 'Lilly Thuresson',
    'Lucas Kruger': 'Lukas Kruger',
    'Micaela Ramondi': 'Micaela Remondi',
    'Michael Blomquist': 'Michael Blomqvist',
    'Mikael Regenholtz': 'Mikael Regenholz',
    'Måns Natanaelson': 'Måns Nathanaelson',
    'Oscar Harryson': 'Oskar Harryson',
    'Patrik Almkvist': 'Patrik Almkvisth',
    'Pontus Gustafson': 'Pontus Gustafsson',
    'Stephan Carlsén': 'Stephan Karlsén',
    'Therese Andersson Lewis': 'Thérese Andersson Lewis',
    'Thérese Andersson Lewis': 'Thérèse Andersson Lewis',
    'Tova Carson': 'Towa Carson',
    'Vivan Cardinal': 'Vivian Cardinal',
}


def get_artist(name):
    name = name.strip()
    m = re.match('(.*) \\(.*\\)', name)
    if m:
        name = m.group(1)

    if name.endswith(('/', ',')):
        name = name[:-1]

    name = name_corrections.get(name, name)

    return Actor.objects.get_or_create(name=name)


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
        elif len(row) == 2 and row[0].endswith(':') and r0_lower not in skiplist and not row[0][0] in invalid_first_char and not row[1][0] in invalid_first_char:
            role = row[0].rstrip(':')
            r.append(Role.objects.create(index=i, show=show, name=role, actor=get_artist(row[1])[0]))
        elif heading and len(row) == 2 and not row[0][0] in invalid_first_char and not row[1][0] in invalid_first_char:
            r.append(Role.objects.create(index=i, show=show, name=row[0], actor=get_artist(row[1])[0]))
        elif heading:
            value = '\t'.join(row)
            metadata_object, _ = MetaDataObject.objects.get_or_create(name=value)
            r.append(MetaData.objects.create(index=i, show=show, key=heading, value=value, metadata_object=metadata_object))
        elif len(row) == 2 and row[0] and row[1] and r0_lower not in skiplist and not row[0][0] in invalid_first_char and not row[1][0] in invalid_first_char:
            r.append(Role.objects.create(index=i, show=show, name=row[0], actor=get_artist(row[1])[0]))
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
    Role.objects.all().delete()
    Actor.objects.all().delete()
    for show in tqdm(Show.objects.all()):
        parse(show)
        show.successful_parse = True
        show.save()

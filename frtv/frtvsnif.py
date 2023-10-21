#! /usr/bin/python3
# par github.com/BG47510/

import requests
from random import randint
from time import sleep
import sys
import random

# User-Agent laisse des informations dans les logs du site visité.
# Elles permettent de savoir si leur site est crawlé.
# Changer son user agent ua :
ua = [
    'Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0',
    'Mozilla/5.0 (Android 12; Mobile; rv:100.0) Gecko/100.0 Firefox/100.0',
    'Mozilla/5.0 (X11; U; Linux i686; fr; rv:1.7.2) Gecko/20040804',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Dalvik/2.1.0 (Linux; U; Android 13; POCO F1 Build/TQ3A.230805.001)',
    'Mozilla/5.0 (X11; Linux x86_64; rv:5.1) Goanna/20220721 PaleMoon/31.1.1',
]

# l’User-Agent et le Referer dans l’en-tête de la requête.
headers = {
    "User-Agent": random.choice(ua),
    "Referer": "https://www.france.tv/",
}


erreur = 'https://raw.githubusercontent.com/BG47510/Zap/main/assets/error.m3u8'

def snif(line):
    domaine = "https://hdfauth.ftven.fr/esi/TA?url=https://"
    source = line.split('https://')[-1]
    lien = s.get(domaine + source, headers=headers, timeout=25).text
    if '.m3u8' not in lien:
        print(erreur)
    else:
        print(lien)
    sleep(randint(15,25))

# L’objet Session conserve les paramètres entre plusieurs requêtes.
# Il conserve également les cookies entre toutes les requêtes de la même instance Session.
# Il peut aussi être utilisés pour fournir des valeurs par défaut aux requêtes (auth, headers)

s = requests.Session()

print('#EXTM3U')
with open('frtv/frtvsource.txt', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('##'):
            continue
        if not line.startswith('https:'):
            line = line.split('|')
            chnom = line[0].strip()
            grp = line[1].strip().title()
            tvgname = line[2].strip()
            idepg = line[3].strip()
            print(f'#EXTINF:-1 tvg-id="{idepg}" tvg-name="{tvgname}" group-title="{grp}", {chnom}')
        else:
            snif(line)

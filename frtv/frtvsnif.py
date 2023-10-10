#! /usr/bin/python3
# par github.com/BG47510/

import requests
import re
import sys

# l’User-Agent et le Referer dans l’en-tête de la requête.
# Pour imiter une session de navigation d’un utilisateur humain.
headers = {
    "User-Agent": "QwantMobile/2.0 (Android 5.1; Tablet; rv:61.0) Gecko/61.0 Firefox/59.0 QwantBrowser/61.0",
    "Referer": "https://www.qwant.com/",
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


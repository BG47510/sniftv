#!/usr/bin/python3
# par github.com/BG47510

import requests
import sys

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "authority": "mediainfo.tf1.fr",
}
params = {
    "context": "ONEINFO_SC2",
    "format": "hls",
}

erreur = "https://github.com/BG47510/Zap/raw/main/assets/error.m3u8"
s = requests.session()
def snif(url):
    try:
        source = s.get(url, params=params, headers=headers)
        base = (source).json()
        lien = base["delivery"]["url"] # valable 4 heures
        flux = requests.get(lien).text
        mu = lien.replace(".m3u8", "")
        m3u8 = flux.replace("index", (mu))
    except Exception as e:
        m3u8 = requests.get(erreur).text
    finally:
        print(m3u8)
clic = snif(sys.argv[1])

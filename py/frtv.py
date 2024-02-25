#! /usr/bin/python3
# par github.com/BG47510
import requests
import sys

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Referer": "http://www.callofliberty.fr/",
    "visitorCountry":"FR"
}

erreur = requests.get("https://raw.githubusercontent.com/BG47510/Zap/main/assets/error.m3u8").text

s = requests.session()

def snif(url):
    try:
        source = s.get(url, headers=headers)
        flux = (source).text
        m3u8 = flux.replace("http://s2.callofliberty.fr/HLS-AES/", "")
    except Exception as e:
        m3u8 = erreur
    finally:
        print(m3u8)

clic = snif(sys.argv[1])




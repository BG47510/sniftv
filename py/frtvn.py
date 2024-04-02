#!/usr/bin/python3
# par github.com/BG47510
import sys
import requests
import re

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "authority": "https://www.france.tv/",
}

erreur = requests.get("https://raw.githubusercontent.com/BG47510/Zap/main/assets/error.m3u8").text

s = requests.session()
def snif(url):
    try:
        token = "https://hdfauth.ftven.fr/esi/TA?url="
        source = s.get(token + url, headers=headers).text
        base = s.get(source, headers=headers).text
        pat = re.compile("index[^\n\r]*")
        res = re.sub(pat,"",source)
        m3u8 = base.replace("France", (res + "France"))
    except Exception as e:
        m3u8 = erreur
    finally:
        print(m3u8)
clic = snif(sys.argv[1])




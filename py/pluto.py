#!/usr/bin/python3
# par github.com/BG47510
import requests
import sys

headers = {
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Referer":"http://api.pluto.tv",
    "visitorCountry":"FR",
    "Accept-Language":"fr-FR,fr;q=0.8"
}

erreur = "https://github.com/BG47510/Zap/raw/main/assets/error.m3u8"

def snif(pluto):
    print("#EXTM3U")
    try:
        api = requests.get(pluto, headers=headers).json()
    #print("#EXTM3U")
        for p in api:
              try:
                  print('')
                  idflux = (f'{p["_id"]}') # aussi tvg-id
                  m3u8 = (f'https://stitcher.pluto.tv/v1/stitch/embed/hls/channel/{idflux}/master.m3u8?\
terminate=false&sid=WEB-45961ff4-d9cc-44b0-9a73-6e39ffde45ad\
&deviceDNT=0&deviceModel=web&deviceVersion=web&deviceId=web\
&appVersion=web&deviceType=web&deviceMake=web')
                  nom = (f',{p["name"]}')
                  groupe = (f'#EXTINF:-1 group-title="{p["category"]}"')
                  print(groupe + nom)
              except Exception as e:
                  m3u8 = requests.get(erreur).text
              finally:
              	print(m3u8)
    except:
        bug = requests.get(erreur).text
    finally:
    	print(bug)
clic = snif(sys.argv[1])

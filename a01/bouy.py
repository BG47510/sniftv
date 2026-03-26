import re
import requests
from pathlib import Path
from urllib.parse import urlparse

# URL qui retourne le JSON
info_url = "https://mediainfo.tf1.fr/mediainfocombo/L_LCI?format=hls&context=ONEINFO"

# fichier m3u8 local à mettre à jour (écrasé)
m3u8_path = Path("a01/bouylci.m3u8")

# obtenir le JSON
resp = requests.get(info_url, timeout=10)
resp.raise_for_status()
j = resp.json()

# extraire l'URL dans delivery.url
delivery_url = j.get("delivery", {}).get("url")
if not delivery_url:
    raise SystemExit("delivery.url introuvable dans le JSON")

# extraire le token JWT (la partie entre le domaine/ et le reste, i.e. header.payload.signature)
# on suppose que l'URL contient .../<token>/out/...
parsed = urlparse(delivery_url)
# trouver le token dans le chemin : premier segment contenant deux points '.' (JWT)
path_parts = parsed.path.split('/')
token_candidate = None
for part in path_parts:
    if part.count('.') >= 2 and all(c.isalnum() or c in "-_." for c in part):
        token_candidate = part
        break
if not token_candidate:
    # fallback : chercher un JWT dans toute l'URL avec regex
    m = re.search(r"([A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+)", delivery_url)
    if m:
        token_candidate = m.group(1)
if not token_candidate:
    raise SystemExit("Token JWT introuvable dans delivery.url")

new_token = token_candidate

# regex pour remplacer tout token JWT déjà présent dans les URLs du fichier m3u8
jwt_re = re.compile(r"(https?://[^\s/]+/)([A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+)(/[^ \r\n\"]*)")

text = m3u8_path.read_text(encoding="utf-8")

def repl(m):
    return m.group(1) + new_token + m.group(3)

new_text = jwt_re.sub(repl, text)

# écrire en écrasant le fichier source
m3u8_path.write_text(new_text, encoding="utf-8")

print("Fichier mis à jour :", m3u8_path)


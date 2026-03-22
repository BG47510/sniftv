import requests
import re
from pathlib import Path

# Config — modifier si besoin
auth_url = "https://hdfauth.ftven.fr/esi/TA?format=json&url=https://simulcast-p.ftven.fr/simulcast/France_Info/hls_monde_frinfo/index.m3u8"
m3u8_path = Path("a02/frinfo.m3u8")   # fichier m3u8 local à modifier
backup_path = m3u8_path.with_suffix(".m3u8.bak")

# 1) Requête et extraction du "url" dans le JSON
resp = requests.get(auth_url, timeout=10)
resp.raise_for_status()
data = resp.json()
full_url = data.get("url")
if not full_url:
    raise SystemExit("Champ 'url' absent dans la réponse JSON.")

# 2) Extraire le token entre le domaine et "/simulcast"
m = re.search(r"https?://[^/]+/([^/]+?)/simulcast/", full_url)
if not m:
    # cas où le token est suivi directement de "/simulcast" sans slash intermédiaire
    m = re.search(r"https?://[^/]+/([^/]+)/simulcast/", full_url)
if not m:
    raise SystemExit("Impossible d'extraire le token dans l'URL retournée.")
new_token = m.group(1)

# 3) Lire le fichier m3u8 et remplacer toutes les occurrences de l'ancien token
text = m3u8_path.read_text(encoding="utf-8")

# Extraire un token existant depuis le fichier m3u8 (première occurrence)
m_old = re.search(r"https?://[^/]+/([^/]+?)/simulcast/", text)
if not m_old:
    raise SystemExit("Aucun token existant trouvé dans le fichier m3u8.")
old_token = m_old.group(1)

if old_token == new_token:
    print("Le token est déjà à jour.")
else:
    # sauvegarde
    backup_path.write_text(text, encoding="utf-8")

    # remplacement global (remplace toutes les occurrences du token dans les URLs)
    updated = text.replace(old_token, new_token)
    m3u8_path.write_text(updated, encoding="utf-8")
    print(f"Remplacé '{old_token}' par '{new_token}' dans {m3u8_path} (backup: {backup_path}).")

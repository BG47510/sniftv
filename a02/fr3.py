import requests
import re
from pathlib import Path
from urllib.parse import urlparse

# Config
auth_url = "https://hdfauth.ftven.fr/esi/TA?format=json&url=https://simulcast-p.ftven.fr/simulcast/France_3/hls_fr3/index.m3u8"
m3u8_path = Path("a02/fr3.m3u8")

def get_token_from_url(url):
    """Extrait le token (le premier dossier après le domaine)."""
    path_parts = urlparse(url).path.split('/')
    # Sur l'URL cible, le token semble être l'élément juste avant 'simulcast'
    try:
        idx = path_parts.index("simulcast")
        return path_parts[idx-1]
    except (ValueError, IndexError):
        return None

try:
    # 1) Récupération
    resp = requests.get(auth_url, timeout=10)
    resp.raise_for_status()
    full_url = resp.json().get("url", "")
    new_token = get_token_from_url(full_url)
    
    if not new_token:
        raise ValueError("Impossible d'extraire le nouveau token.")

    # 2) Lecture et comparaison
    if not m3u8_path.exists():
        raise FileNotFoundError(f"Le fichier {m3u8_path} est introuvable.")

    text = m3u8_path.read_text(encoding="utf-8")
    old_token = get_token_from_url(text) # On cherche le token dans le texte existant

    if old_token == new_token:
        print("✅ Le token est déjà à jour.")
    else:
        # 3) Mise à jour
        m3u8_path.with_suffix(".m3u8.bak").write_text(text, encoding="utf-8")
        # On remplace spécifiquement le motif lié au token pour éviter les faux positifs
        updated = text.replace(f"/{old_token}/simulcast/", f"/{new_token}/simulcast/")
        m3u8_path.write_text(updated, encoding="utf-8")
        print(f"🚀 Token mis à jour : {old_token} -> {new_token}")

except Exception as e:
    print(f"❌ Erreur : {e}")
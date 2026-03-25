import requests
import re
from pathlib import Path

# Config
auth_url = "https://hdfauth.ftven.fr/esi/TA?url=https://live-sport-p.ftven.fr/simulcast/Sports/FRANCE/_TV/_INDEX.m3u8"
m3u8_path = Path("a02/frsport.m3u8")

def extract_token(text):
    """Extrait le token dynamique situé avant /simulcast/ via Regex."""
    # Cherche une suite de caractères alphanumériques juste avant /simulcast/
    match = re.search(r'/([^/]+)/simulcast/', text)
    return match.group(1) if match else None

try:
    # 1) Récupération du nouveau token via l'API
    resp = requests.get(auth_url, timeout=10)
    resp.raise_for_status()
    full_url = resp.json().get("url", "")
    new_token = extract_token(full_url)
    
    if not new_token:
        raise ValueError("Impossible d'extraire le nouveau token depuis l'API.")

    # 2) Lecture du fichier local
    if not m3u8_path.exists():
        raise FileNotFoundError(f"Le fichier {m3u8_path} est introuvable.")

    text = m3u8_path.read_text(encoding="utf-8")
    old_token = extract_token(text)

    if not old_token:
        # Si on ne trouve pas d'ancien token, on ne peut pas faire de .replace()
        # On pourrait ici décider de forcer l'écriture si besoin
        print("⚠️ Aucun ancien token détecté dans le fichier m3u8.")
    
    if old_token == new_token:
        print(f"✅ Le token est déjà à jour ({new_token}).")
    else:
        # 3) Mise à jour
        # On crée une sauvegarde
        m3u8_path.with_suffix(".m3u8.bak").write_text(text, encoding="utf-8")
        
        # Remplacement global dans le fichier
        # Si old_token est None, on peut utiliser une regex pour remplacer n'importe quel token
        if old_token:
            updated = text.replace(f"/{old_token}/dai/", f"/{new_token}/dai/")
        else:
            # Cas de secours : remplace n'importe quel motif /.../simulcast/
            updated = re.sub(r'/[^/]+/dai/', f'/{new_token}/dai/', text)
            
        m3u8_path.write_text(updated, encoding="utf-8")
        print(f"🚀 Mise à jour réussie : {old_token} -> {new_token}")

except Exception as e:
    print(f"❌ Erreur : {e}")

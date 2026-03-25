import requests
import re
from pathlib import Path

# Config
auth_url = "https://hdfauth.ftven.fr/esi/TA?url=https://simulcast-fr3regions-p.ftven.fr/simulcast/Regions_noa/hls_noa/master.m3u8"
m3u8_path = Path("a02/frnoa.m3u8")

def extract_token(text):
    """Extrait le token dynamique situé avant /simulcast/ via Regex."""
    match = re.search(r'/([^/]+)/simulcast/', text)
    return match.group(1) if match else None

try:
    # 1) Récupération du nouveau token via l'API (support JSON ou texte brut)
    resp = requests.get(auth_url, timeout=10)
    resp.raise_for_status()

    ct = resp.headers.get("Content-Type", "")
    if "application/json" in ct:
        try:
            data = resp.json()
            full_url = data.get("url", "") or resp.text.strip()
        except ValueError:
            full_url = resp.text.strip()
    else:
        full_url = resp.text.strip()

    new_token = extract_token(full_url)
    if not new_token:
        raise ValueError(f"Impossible d'extraire le nouveau token depuis: {full_url[:200]!r}")

    # 2) Lecture du fichier local
    if not m3u8_path.exists():
        raise FileNotFoundError(f"Le fichier {m3u8_path} est introuvable.")

    text = m3u8_path.read_text(encoding="utf-8")
    old_token = extract_token(text)

    if not old_token:
        print("⚠️ Aucun ancien token détecté dans le fichier m3u8.")

    if old_token == new_token:
        print(f"✅ Le token est déjà à jour ({new_token}).")
    else:
        # 3) Mise à jour
        m3u8_path.with_suffix(".m3u8.bak").write_text(text, encoding="utf-8")

        if old_token:
            updated = text.replace(f"/{old_token}/simulcast/", f"/{new_token}/simulcast/")
        else:
            updated = re.sub(r'/[^/]+/simulcast/', f'/{new_token}/simulcast/', text)

        m3u8_path.write_text(updated, encoding="utf-8")
        print(f"🚀 Mise à jour réussie : {old_token} -> {new_token}")

except Exception as e:
    print(f"❌ Erreur : {e}")

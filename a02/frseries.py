import requests
import re
from pathlib import Path

# Config
auth_url = "https://hdfauth.ftven.fr/esi/TA?url=https://live-series.ftven.fr/hls-francedomtom/index.m3u8"
m3u8_path = Path("a02/frsport.m3u8")
bak_path = Path("a02/bak/frseries.bak")

def extract_token(text):
    """Extrait le token (suite sans slash) situé avant /dai/, /simulcast/ ou /hls-francedomtom/."""
    match = re.search(r'/([^/]+)/(?:dai|simulcast|hls-francedomtom)/', text)
    return match.group(1) if match else None

try:
    # 1) Récupération du nouveau token via l'API
    resp = requests.get(auth_url, timeout=10)
    resp.raise_for_status()

    # Tenter JSON d'abord, sinon texte brut
    full_url = ""
    ct = resp.headers.get("Content-Type", "")
    if "application/json" in ct:
        try:
            full_url = resp.json().get("url", "") or ""
        except ValueError:
            full_url = resp.text.strip()
    else:
        try:
            full_url = resp.json().get("url", "") or ""
        except Exception:
            full_url = resp.text.strip()

    if not full_url or not any(k in full_url for k in ("dai", "simulcast", "hls-francedomtom")):
        raise ValueError("Réponse API inattendue : URL manquante ou incorrecte.")

    new_token = extract_token(full_url)
    if not new_token:
        raise ValueError("Impossible d'extraire le nouveau token depuis l'API.")

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
        # 3) Mise à jour : sauvegarde puis remplacement ciblé
        bak_path.parent.mkdir(parents=True, exist_ok=True)
        bak_path.write_text(text, encoding="utf-8")

        # Remplacer uniquement le segment /<token>/(dai|simulcast|hls-francedomtom)/
        if old_token:
            updated = re.sub(
                rf'/{re.escape(old_token)}/(dai|simulcast|hls-francedomtom)/',
                f'/{new_token}/\\1/',
                text
            )
        else:
            updated = re.sub(
                r'/[^/]+/(dai|simulcast|hls-francedomtom)/',
                f'/{new_token}/\\1/',
                text
            )

        m3u8_path.write_text(updated, encoding="utf-8")
        print(f"🚀 Mise à jour réussie : {old_token} -> {new_token}")

except Exception as e:
    print(f"❌ Erreur : {e}")

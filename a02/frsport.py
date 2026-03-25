import requests
import re
from pathlib import Path

# Config
auth_url = "https://hdfauth.ftven.fr/esi/TA?url=https://live-sport-p.ftven.fr/simulcast/Sports/FRANCE/_TV/_INDEX.m3u8"
m3u8_path = Path("a02/frsport.m3u8")

def extract_token(text):
    """Extrait le token (suite sans slash) situé avant /dai/ ou /simulcast/."""
    # On tente d'abord de matcher avant /dai/, sinon avant /simulcast/
    match = re.search(r'/([^/]+)/dai/', text)
    if match:
        return match.group(1)
    match = re.search(r'/([^/]+)/simulcast/', text)
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
        # Cas courant : l'API renvoie peut-être une URL en texte brut ou du HTML
        try:
            full_url = resp.json().get("url", "") or ""
        except Exception:
            full_url = resp.text.strip()

    if not full_url or ("dai" not in full_url and "simulcast" not in full_url):
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
        m3u8_path.with_suffix(".m3u8.bak").write_text(text, encoding="utf-8")

        # Si on a identifié l'ancien token, on fait un remplacement prudent
        if old_token:
            # Remplacer uniquement le segment /<old_token>/dai/ ou /<old_token>/simulcast/
            updated = re.sub(
                rf'/{re.escape(old_token)}/(dai|simulcast)/',
                f'/{new_token}/\\1/',
                text
            )
        else:
            # Cas de secours : remplacer tout segment /.../dai/ ou /.../simulcast/
            updated = re.sub(r'/[^/]+/(dai|simulcast)/', f'/{new_token}/\\1/', text)

        m3u8_path.write_text(updated, encoding="utf-8")
        print(f"🚀 Mise à jour réussie : {old_token} -> {new_token}")

except Exception as e:
    print(f"❌ Erreur : {e}")

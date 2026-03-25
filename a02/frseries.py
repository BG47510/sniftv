import requests
import re
from pathlib import Path

# Config
auth_url = "https://hdfauth.ftven.fr/esi/TA?url=https://live-series.ftven.fr/hls-francedomtom/index.m3u8"
m3u8_path = Path("a02/frseries.m3u8")
bak_path = Path("a02/bak/frseries.bak")
TIMEOUT = 10

TOKEN_REGEX = re.compile(r'/([^/]+)/(?:dai|simulcast|hls-francedomtom)/')

def extract_token_from_text(text: str):
    m = TOKEN_REGEX.search(text)
    return m.group(1) if m else None

def replace_token_in_text(text: str, old_token: str | None, new_token: str):
    if old_token:
        pattern = re.compile(rf'/{re.escape(old_token)}/(dai|simulcast|hls-francedomtom)/')
    else:
        # If no old token discovered, replace any matching segment so we still insert the new token
        pattern = re.compile(r'/([^/]+)/(dai|simulcast|hls-francedomtom)/')
    new = pattern.sub(fr'/{new_token}/\1/', text)
    return new

def get_url_from_response(resp: requests.Response) -> str:
    # Try JSON first, but fall back to raw text safely
    ct = resp.headers.get("Content-Type", "")
    body = resp.text.strip()
    if "application/json" in ct:
        try:
            j = resp.json()
            # Common keys that might hold the URL
            for key in ("url", "uri", "data", "location"):
                if isinstance(j, dict) and key in j and isinstance(j[key], str) and j[key].strip():
                    return j[key].strip()
        except ValueError:
            pass
    # Fallback: try to find an URL-like substring in the text body
    # simple heuristic: look for https?://... containing one of the markers
    m = re.search(r'https?://\S+(?:dai|simulcast|hls-francedomtom)\S*', body)
    return m.group(0) if m else body

def main():
    try:
        resp = requests.get(auth_url, timeout=TIMEOUT)
        resp.raise_for_status()
        full_url = get_url_from_response(resp)
        if not full_url or not any(k in full_url for k in ("dai", "simulcast", "hls-francedomtom")):
            raise ValueError("Réponse API inattendue : URL manquante ou ne contenant pas les segments attendus.")
        new_token = extract_token_from_text(full_url)
        if not new_token:
            raise ValueError("Impossible d'extraire le nouveau token depuis l'URL renvoyée par l'API.")

        if not m3u8_path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {m3u8_path}")

        text = m3u8_path.read_text(encoding="utf-8")
        old_token = extract_token_from_text(text)

        if old_token == new_token:
            print(f"✅ Le token est déjà à jour ({new_token}).")
            return

        # Backup
        bak_path.parent.mkdir(parents=True, exist_ok=True)
        bak_path.write_text(text, encoding="utf-8")

        updated = replace_token_in_text(text, old_token, new_token)

        if updated == text:
            # Nothing changed — give a diagnostic
            raise RuntimeError("Aucune modification appliquée au fichier : motif non trouvé pour remplacement.")

        m3u8_path.write_text(updated, encoding="utf-8")
        print(f"🚀 Mise à jour réussie : {old_token or '<inconnu>'} -> {new_token}")

    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    main()

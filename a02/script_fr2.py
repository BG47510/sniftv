import requests
import os

# Configuration
URL_SOURCE = 'https://hdfauth.ftven.fr/esi/TA?format=json&url=https://simulcast-p.ftven.fr/simulcast/France_2/hls_fr2/index.m3u8'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}
NOM_FICHIER = 'fr2.m3u8'

def extraire_url_flux(url_api):
    try:
        response = requests.get(url_api, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json().get('url')
    except Exception as e:
        print(f"Erreur API : {e}")
        return None

def modifier_contenu_m3u8(contenu, base_url):
    lignes = contenu.splitlines()
    for i in range(len(lignes)):
        # Ajout de la base URL pour les segments
        if "France_2-avc1" in lignes[i]:
            lignes[i] = base_url + lignes[i]
        # Ajout de la base URL pour les fichiers de clés/sous-playlists
        elif "URI=" in lignes[i]:
            start = lignes[i].find("URI=") + 5
            end = lignes[i].find("\"", start)
            uri = lignes[i][start:end]
            lignes[i] = lignes[i].replace(uri, base_url + uri)
    return "\n".join(lignes)

def main():
    print("Démarrage de l'actualisation...")
    m3u_url = extraire_url_flux(URL_SOURCE)
    
    if not m3u_url:
        print("Impossible de récupérer l'URL source.")
        return

    try:
        res = requests.get(m3u_url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        
        base_url = m3u_url.split('hls_fr2/')[0] + 'hls_fr2/'
        m3u_modifie = modifier_contenu_m3u8(res.text, base_url)

        # Écriture du fichier sur le disque du runner GitHub
        with open(NOM_FICHIER, 'w', encoding='utf-8') as f:
            f.write(m3u_modifie)
        
        print(f"Fichier {NOM_FICHIER} mis à jour avec succès.")
        
    except Exception as e:
        print(f"Erreur lors du traitement du M3U8 : {e}")

if __name__ == "__main__":
    main()

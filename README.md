# starlink-edl

Listes de prefixes **Starlink (SpaceX)** pour une *External Dynamic List* (EDL) de pare-feu,
generees tous les jours a partir du geofeed officiel de Starlink
(<https://geoip.starlinkisp.net/feed.csv>, RFC 8805).

| Fichier | Contenu |
|---|---|
| `starlink-ipv4.txt` | prefixes IPv4 agreges, un par ligne |
| `starlink-ipv6.txt` | prefixes IPv6 agreges, un par ligne |

- Mise a jour : GitHub Actions (`.github/workflows/update.yml`), tous les jours a 03:17 UTC.
  Un commit n'est cree que si le contenu change.
- Garde-fous : si le flux est inaccessible, trop petit ou depasse 50 000 entrees, rien n'est publie
  et les fichiers precedents restent en place.
- Lancer a la main : onglet **Actions** > *update-starlink-edl* > *Run workflow*,
  ou `python3 update.py` en local (Python 3, aucune dependance).

## Utilisation (Palo Alto Networks)

Objects > External Dynamic Lists > Add, type **IP List** :

- Source : `https://raw.githubusercontent.com/<compte>/<depot>/main/starlink-ipv4.txt` (puis `-ipv6.txt`)
- Certificate profile : un profil contenant l'autorite racine du certificat de `raw.githubusercontent.com`
- Repeat : *Daily* (ou *Hourly*)

Les donnees sont publiques ; ce depot ne contient aucune information propre a un utilisateur.

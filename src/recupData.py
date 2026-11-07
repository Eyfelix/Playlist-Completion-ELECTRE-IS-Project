from findBestMusic import *
import spotipy
from spotipy.oauth2 import SpotifyOAuth,SpotifyClientCredentials
import csv
import http.client
import json
from pprint import pprint
import time 

# --- Configuration des identifiants ---
CLIENT_ID = "A VALID CLIENT ID"
CLIENT_SECRET = "A VALID CLIENT SECRET"
SPOTIFY_REDIRECT_URI = "https://example.com/callback"
conn = http.client.HTTPSConnection("api.reccobeats.com")
headers = {
        'Accept': 'application/json'
        }

auth_manager = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,redirect_uri=SPOTIFY_REDIRECT_URI)
sp = spotipy.Spotify(auth_manager=auth_manager)

def loadMusicNames(file_path):
    music_list = []
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            #* DictReader utilise les en-têtes du CSV comme clés du dictionnaire
            reader = csv.DictReader(csvfile)
            for row in reader:
                music_list.append(dict(row))
                
        return music_list

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{file_path}' n'a pas été trouvé.")
        return []

def findSpotifyIDsAndISRC(music_list):

    for track in music_list:
        #* Construction de la requête de recherche (Artiste + Titre)
        query = f"track:{track['name']} artist:{track['artist']}"
        try:
            #* Recherche du titre (limit=1 pour avoir le résultat le plus pertinent)
            results = sp.search(q=query, limit=1, type='track')
            items = results['tracks']['items']
            
            if items:
                #* Récupération de l'ID et de l'ISRC du premier résultat
                track['spotify_id'] = items[0]['id']
                track['isrc'] = items[0].get('external_ids', {}).get('isrc', None)
                #* print(f'{items[0]["name"]} - {items[0]["artists"][0]["name"]} for {track["name"]} - {track["artist"]} ')
                if not track['isrc']:
                    print(f"WARNING : ISRC non disponible pour : {track['name']} de {track['artist']}")
            else:
                track['spotify_id'] = None
                track['isrc'] = None
                print(f"WARNING : Aucun résultat trouvé pour : {track['name']} de {track['artist']}")
                
        except Exception as e:
            print(f"Erreur lors de la recherche pour {track['name']} : {e}")
            track['spotify_id'] = None
            track['isrc'] = None

    return music_list

def fetchMusicFromPlaylist(playlistID:str,playlistName:str="Playlist"):
    tracksData = {}
    tracksWithoutISRC = []
    
    try:
        #* Fetch playlist tracks (Spotify API returns max 50 items per request)
        offset = 0
        limit = 50
        totalTracks = 0
        
        while True:
            #* Get batch of tracks
            results = sp.playlist_tracks(playlistID, offset=offset, limit=limit)
            items = results['items']
            
            if not items:
                break
            
            totalTracks += len(items)
            
            #* Process each track
            for item in items:
                track = item.get('track')
                
                #* Skip if track is None (can happen with removed tracks)
                if not track:
                    continue
                
                #* Extract ISRC
                isrc = track.get('external_ids', {}).get('isrc')
                
                #* Skip tracks without ISRC
                if not isrc:
                    tracksWithoutISRC.append({
                        'name': track.get('name', 'Unknown'),
                        'artist': track.get('artists', [{}])[0].get('name', 'Unknown')
                    })
                    continue
                
                #* Extract release year from album release_date
                releaseDate = track.get('album', {}).get('release_date', '')
                try:
                    #* Release date can be in formats: YYYY, YYYY-MM, or YYYY-MM-DD
                    year = int(releaseDate.split('-')[0]) if releaseDate else 0
                except (ValueError, IndexError):
                    year = 0
                
                if year < MIN_YEAR or year > MAX_YEAR:
                    print(f"{track.get('name', 'Unknown')} de {track.get('artists', [{}])[0].get('name', 'Unknown')} n'est pas dans les années retenues")
                    continue
                
                #* Extract popularity (0-100)
                popularity = track.get('popularity', 0)
                
                #* Extract main artist ID (first artist in the list)
                artists = track.get('artists', [])
                artistID = artists[0].get('id', '') if artists else ''
                artistName = artists[0].get('name','') if artists else ''
                #* Store track data
                tracksData[isrc] = {
                    'year': year,
                    'popularity': popularity,
                    'artistID': artistID,
                    'artist':artistName,
                    'title':track.get('name','undefined')
                }
            
            #* Check if there are more tracks to fetch
            if not results['next']:
                break
            time.sleep(0.5)
            offset += limit
        
        #* Log summary
        print(f"Playlist '{playlistName}': {len(tracksData)} tracks processed")
        print(f"Total tracks found: {totalTracks}")
        print(f"Tracks with ISRC: {len(tracksData)}")
        print(f"Tracks without ISRC (ignored): {len(tracksWithoutISRC)}")
        
        #* Log tracks without ISRC
        if tracksWithoutISRC:
            print(f"\n  WARNING: The following tracks were ignored (no ISRC):")
            for track in tracksWithoutISRC[:5]:  # Show max 5 examples
                print(f"    - {track['name']} by {track['artist']}")
            if len(tracksWithoutISRC) > 5:
                print(f"    ... and {len(tracksWithoutISRC) - 5} more")
        
        return tracksData
    
    except spotipy.exceptions.SpotifyException as e:
        print(f"Spotify API error for playlist '{playlistName}': {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error while fetching playlist '{playlistName}': {e}")
        return {}
    
def fetchMusicAudioFeature(musicsByISRC: dict[str,dict[str,str]]) -> dict[str, dict]:
    if not musicsByISRC:
        return {}
    isrcs = list(musicsByISRC.keys())
    tracks_data = []
    for i in range(0, len(isrcs), 40):
        #* Construire le paramètre isrcs pour l'URL
        isrcs_str = ','.join(isrcs[i:i+40])

        #* Effectuer la requête avec les ISRC
        conn.request("GET", f"/v1/audio-features?ids={isrcs_str}", '', headers)
        res = conn.getresponse()
        data = res.read()

        response_data = json.loads(data.decode("utf-8"))
        #* print("Response data:",response_data)

        #* Vérifier la structure de la réponse
        if isinstance(response_data, dict) and 'content' in response_data:
            tracks_data.extend(response_data['content'])
        elif isinstance(response_data, list):
            tracks_data.extend(response_data)
        else:
            print(f"Erreur: structure de réponse inattendue: {response_data}")
            return []
        time.sleep(0.5)
    print(f"Total tracks fetched: {len(tracks_data)}/{len(isrcs)}")

    seenISRC = set()
    #* Créer un objet Music pour chaque morceau
    for track_data in tracks_data:
        if (track_data.get("tempo")==None or 
            track_data.get("valence")==None or 
            track_data.get("energy")==None or 
            track_data.get("instrumentalness")==None or 
            track_data.get("key")==-1 or 
            track_data.get("tempo") > MAX_TEMPO or 
            track_data.get("tempo") < MIN_TEMPO): #* No key defined or out of tempo range
            print(f'Was not conform  : {track_data}')
            continue
        isrc = track_data.get('isrc', '')
        
        #* Si on a déjà traité cet ISRC, on ignore les duplicatas
        if isrc in seenISRC:
            continue
        seenISRC.add(isrc)

        musicsByISRC[isrc] = musicsByISRC[isrc] | track_data

    missing_isrcs = set(isrcs) - seenISRC
    if missing_isrcs:
        print(f"WARNING : {len(missing_isrcs)} ISRC non trouvés dans l'API: {missing_isrcs}")
    for missing_isrc in missing_isrcs:
        del musicsByISRC[missing_isrc]

    print(f"Récupéré {len(musicsByISRC)}/{len(isrcs)} audio features.")
    return musicsByISRC

def getArtistGenre(musicsByISRC:dict[str,dict[str,str]]):
    artistIdToISRCs = {}
    for isrc, music in musicsByISRC.items():
        artistID = music.get("artistID")
        if artistID:
            if artistID not in artistIdToISRCs:
                artistIdToISRCs[artistID] = []
            artistIdToISRCs[artistID].append(isrc)
    
    #* Get unique artist IDs
    uniqueArtistIDs = list(artistIdToISRCs.keys())
    
    if not uniqueArtistIDs:
        print("WARNING: No artist IDs found in the music data")
        return musicsByISRC
    
    print(f"Fetching genres for {len(uniqueArtistIDs)} unique artists...")
    
    #* Fetch artist data in batches (Spotify API allows max 50 artists per request)
    artistsWithoutGenres = []
    processedArtists = 0
    
    for i in range(0, len(uniqueArtistIDs), 50):
        batch = uniqueArtistIDs[i:i+50]
        
        try:
            #* Fetch artist information
            artistsData = sp.artists(batch)['artists']
            
            #* Process each artist
            for artistData in artistsData:
                if not artistData:
                    continue
                
                artistID = artistData.get('id')
                genres = artistData.get('genres', [])
                
                #* Add genres to all tracks by this artist
                if artistID in artistIdToISRCs:
                    for isrc in artistIdToISRCs[artistID]:
                        musicsByISRC[isrc]['genres'] = []
                        for genre in POSSIBLES_GENRES:
                            if any([genre in musicGenre for musicGenre in genres]):
                                musicsByISRC[isrc]['genres'].append(genre)
                    
                    processedArtists += 1
                    
                    #* Track artists without genres
                    if not genres:
                        artistsWithoutGenres.append({
                            'name': artistData.get('name', 'Unknown'),
                            'id': artistID
                        })
            time.sleep(0.5)
        except spotipy.exceptions.SpotifyException as e:
            print(f"Spotify API error while fetching artists batch: {e}")
            continue
        except Exception as e:
            print(f"Unexpected error while fetching artists: {e}")
            continue
        
    #* Log summary
    print(f"Processed {processedArtists} artists")
    print(f"Artists with genres: {processedArtists - len(artistsWithoutGenres)}")
    print(f"Artists without genres: {len(artistsWithoutGenres)}")
    
    #* Log artists without genres
    if artistsWithoutGenres:
        print(f"\n  WARNING: The following artists have no genres:")
        for artist in artistsWithoutGenres[:5]:  # Show max 5 examples
            print(f"    - {artist['name']} (ID: {artist['id']})")
        if len(artistsWithoutGenres) > 5:
            print(f"    ... and {len(artistsWithoutGenres) - 5} more")
    
    return musicsByISRC

def getDetailedMusicData(musicsByISRC:dict[str,dict[str,str]]) -> list[Music]:


    # # 1. Extraire uniquement les IDs valides
    # trackIds = [m['spotify_id'] for m in muscisIdsAndIsrcs if m.get('spotify_id')]
    # # 2. Extraire uniquement les ISRC valides
    # isrcs = [m['isrc'] for m in muscisIdsAndIsrcs if m.get('isrc')]

    # 3. Récupérer les audio features par ISRC
    musicsByISRC = fetchMusicAudioFeature(musicsByISRC)

    #* Get the genre by the artist
    musicsByISRC = getArtistGenre(musicsByISRC)

    # 4. Création des instances de la classe Music
    music_objects = []
    
    # pprint(musicsByISRC)
    # 5. Assemblage final
    for isrc, track_info in musicsByISRC.items():
        if not track_info:
            continue

        music_obj = Music(
            title=track_info['title'],
            artist=track_info['artist'],
            isrc=isrc,
            genres=track_info["genres"],
            tempo=int(track_info['tempo']),
            valence=int(track_info['valence'] * 100),
            energy=int(track_info['energy'] * 100),
            instrumentality=int(track_info['instrumentalness'] * 100),
            year=track_info["year"],
            popularity=track_info['popularity']
        )
        music_objects.append(music_obj)

    return music_objects

def saveMusicToCSV(musicsList: list[Music], filename: str) -> None:
    if not musicsList:
        print("Empty list, no file create")
        return
    
    # Définir les en-têtes du CSV
    fieldnames = ['title', 'artist', 'isrc', 'genres', 'tempo', 'valence', 
                  'energy', 'instrumentality', 'year', 'popularity']
    
    try:
        # Vérifier si le fichier existe déjà
        file_exists = os.path.isfile(filename)

        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Écrire l'en-tête seulement si le fichier est nouveau
            if not file_exists:
                writer.writeheader()
            
            # Écrire chaque musique
            for music in musicsList:
                # Convertir la liste de genres en JSON pour la stocker dans une cellule
                genres_json = json.dumps(music.genres)
                
                writer.writerow({
                    'title': music.title,
                    'artist': music.artist,
                    'isrc': music.isrc,
                    'genres': genres_json,
                    'tempo': music.tempo,
                    'valence': music.valence,
                    'energy': music.energy,
                    'instrumentality': music.instrumentality,
                    'year': music.year,
                    'popularity': music.popularity
                })
        
        print(f"Done {len(musicsList)} musiques saved dans '{filename}'")
    
    except IOError as e:
        print(f"ERROR when writing in file {e}")
    except Exception as e:
        print(f"ERROR: {e}")





# --- Exemple d'utilisation ---
if __name__ == "__main__":
    # inputData = loadMusicNames('musicName.csv')
    # print(f"Loaded {len(inputData)} musics from CSV.")
    # spotifyDataWithIDs = findSpotifyIDsAndISRC(inputData)
    # print(f"Retrieved Spotify IDs {len(spotifyDataWithIDs)} musics.")
    # final_list = getDetailedMusicData(spotifyDataWithIDs)
    # print(f"Retrieved detailed data for {len(final_list)} musics.")
    musicByISRC = fetchMusicFromPlaylist("78yM6MjbDEc2TYHtc4zmjc")
    musicsList = getDetailedMusicData(musicByISRC)
    saveMusicToCSV(musicsList, './data/thePlaylistData.csv')

#* Playlists saved for the base 
#* https://open.spotify.com/playlist/65mcGIHLOkknEIXGrygyO7?si=909a7c22ffc14a2c Rap
#* https://open.spotify.com/playlist/6ylvGA8NeX2CuaeGtwHWDJ?si=91b36e28120f4869 Jazz
#* https://open.spotify.com/playlist/1h0CEZCm6IbFTbxThn6Xcs?si=e79f10e8515b4496 Classic
#* https://open.spotify.com/playlist/3tRhisNDv5YZXPQltBbJNc?si=75ea54b6dcc349c0 Electro
#* https://open.spotify.com/playlist/5KUEeL5pxPT2E0ddQExb4o?si=720b012ac1794a19 Latin
#* https://open.spotify.com/playlist/1puQ0hv40TUre24cFillJS?si=c47083816be24a94 Rock
#* https://open.spotify.com/playlist/2DAsBss2UksVZs1ZSFmUNI?si=5abcff73879943f6 Metal
#* https://open.spotify.com/playlist/0ZUw7asLc5ZGOaI6IAUtaE?si=8644a0f4f63b4845 French Var
#* https://open.spotify.com/playlist/414ImOZ0R7hRgmA7DX17bb?si=c98dfc7388c94f13 Pop

#* The playlist : 
#* https://open.spotify.com/playlist/78yM6MjbDEc2TYHtc4zmjc?si=59fae480e7f84bce
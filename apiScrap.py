## imports
import csv
import spotipy
import os
import time
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv


## accessed .env information
load_dotenv()
client_id = os.getenv('Client_ID')
client_secret = os.getenv('Client_Secret')

## spotipy authorizes your own cool stuff.
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))

## cool ahh function to do paginates
def paginate(data, page_size=100):
    """Divide the data into chunks of page_size."""
    for i in range(0, len(data), page_size):
        yield data[i:i + page_size]


## most likely to be used
def readCSVdata(filename):
    data = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append({
                'author': row['author'],
                'name': row['name'],
                'rank': row['rank'],
                'date': row['date']
            })
    return data


## only needed if file had failed exported and need to access checkpoint.
def readCSVfull(filename):
    data = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append({
                'author': row['author'],
                'name': row['name'],
                'rank': row['rank'],
                'date': row['date'],
                'duration': row['duration'],
                'id': row['id'],
                'popularity': row['popularity'],
                'album_Name': row['album_Name'],
                'albumType': row['albumType'],
                'releaseDate': row['releaseDate'],
                'explicit': row['explicit']
            })
    return data

## makes it look nice.
def update_song_message(num, total, author, name):
    print("\033[34m{}/{}\033[0m: Querying {}: {}".format(num, total, author, name))


## makes it look nice.
def update_page_message(num, total):
    print("\033[34m{}/{}\033[0m: Querying Pages".format(num, total))


## helper
def createSearchString(song):
    mainArtist = song['author'].split("Featuring")[0].strip()
    return "track: {} artist: {}".format(song['name'], mainArtist)


## needed because I had to grab all the spotify song ids before getting their features
def grabAPIdata(song):
    q = createSearchString(song)
    result = sp.search(q, limit=1, type='track', market=None)
    if result["tracks"]["items"]:
        
        track = result["tracks"]["items"][0]

        ## update song dict
        song['duration'] = track['duration_ms']
        song['id'] = track['id']
        song['popularity'] = track['popularity']
        song['album_Name'] = track['album']['name']
        song['albumType'] = track['album']['album_type']
        song['releaseDate'] = track['album']['release_date']
        song['explicit'] = track['explicit']
    else:
        print("uh oh found an error")


## update given object with newly aquired features
def updateSongAcoustic(song, features):
    if(features['id'] != song['id']):
        print("error this is a mismatched id? what went wrong here?")
    else:
        song['danceability'] = features['danceability']
        song['energy'] = features['energy']
        song['key'] = features['key']
        song['loudness'] = features['loudness']
        song['mode'] = features['mode']
        song['speechiness'] = features['speechiness']
        song['acousticness'] = features['acousticness']
        song['instrumentalness'] = features['instrumentalness']
        song['liveness'] = features['liveness']
        song['valence'] = features['valence']
        song['tempo'] = features['tempo']
        song['timeSig'] = features['time_signature']


# grabs audio features and calls to update song object with new information
def grabAudioFeatures(page):
    song_ids = [song['id'] for song in page]
    audio_features = sp.audio_features(song_ids)

    for song, features in zip(page, audio_features):
        if features:
            updateSongAcoustic(song, features)


# always use first, unless it was failed file export.
def basicRead(fileName):
    songData = readCSVdata(fileName)
    for num, song in enumerate(songData, 1):
            update_song_message(num, len(songData), song['author'], song['name'])
            grabAPIdata(song)
            time.sleep(0.1)
    return songData

# in case the export fails, you can finish where it left off by using idx
def checkpointRead(fileName, idx):
    songData = readCSVfull(fileName)
    for i in range(idx - 1, len(songData)):
        song = songData[i]
        update_song_message(i, 1698, song['author'], song['name'])
        grabAPIdata(song)
        time.sleep(0.1)

# wrapper
def export(outputFilename, songData, header):
    with open(outputFilename, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        for song in songData:
            writer.writerow(song)


## def isn't needed, but left it in here anyways
def exportBasic(outputFilename, songData):
    header = ['author', 'name', 'rank', 'date', 'duration', 'id', 'popularity', 'album_Name', 'albumType', 'releaseDate', 'explicit']
    export(outputFilename, songData, header)

## should probably use this at all times, make sure to call grabaudiofeatures first or it bugs out.
def exportFull(outputFilename, songData):
    header = ['author', 'name', 'rank', 'date', 'duration', 'id', 'popularity', 'album_Name', 'albumType', 'releaseDate', 'explicit', 
              'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
              'valence', 'tempo', 'timeSig']
    export(outputFilename, songData, header)

## needed.
def grabAcousticFeatures(idData):
    paginated_lists = list(paginate(idData, 100))
    for idx, chunk in enumerate(paginated_lists, 1):
        update_page_message(idx, len(paginated_lists))
        grabAudioFeatures(chunk)
        time.sleep(0.5)


def main():
    
    ## Start - Finish  comment everything else except this block
    songs = basicRead('exported_dataV2.csv')
    grabAcousticFeatures(songs)
    exportFull("spotifyFinal.csv", songs)
    ## 

    ## Failed export, need checkpoint 
    ##  songs = checkpointRead(filename, idx) <-- idx represents the song # that it failed at.
    ##  grabAcousticFeatures(songs)
    ##  exportFull("spotifyFinal.csv", songs)
    ##

    pass

if __name__ == "__main__":
    main()
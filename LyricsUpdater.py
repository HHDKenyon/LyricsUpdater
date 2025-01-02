import os
import lyricsgenius
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.id3._frames import USLT
from mutagen.flac import FLAC
from mutagen.asf import ASF

# Initialize Genius API
genius = lyricsgenius.Genius("M05OffvrQaFmzlTd4Bnbs1gghydd7cv7ziO-fzu4adev4tyQ-7NbXfNSTvFme55a")

def get_lyrics(song_title, artist):
    try:
        song = genius.search_song(song_title, artist)
        if song:
            return song.lyrics
    except Exception as e:
        print(f"Error fetching lyrics: {e}")
    return None

def embed_lyrics(file_path, lyrics, file_type):
    if file_type == 'mp3':
        audio = EasyID3(file_path)
        audio.save()
        audio = ID3(file_path)
        audio["USLT"] = USLT(encoding=3, lang="eng", desc="desc", text=lyrics)
        audio.save()
    elif file_type == 'flac':
        audio = FLAC(file_path)
        audio["lyrics"] = lyrics
        audio.save()
    elif file_type == 'wma':
        audio = ASF(file_path)
        audio["WM/Lyrics"] = lyrics
        audio.save()

def process_folder(folder_path, overwrite):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".mp3", ".flac", ".wma")):
                file_path = os.path.join(root, file)
                if file.endswith(".mp3"):
                    file_type = 'mp3'
                    audio = EasyID3(file_path)
                elif file.endswith(".flac"):
                    file_type = 'flac'
                    audio = FLAC(file_path)
                elif file.endswith(".wma"):
                    file_type = 'wma'
                    audio = ASF(file_path)
                
                song_title = audio.get("Title", [None]) if file_type == 'wma' else audio.get("title", [None])
                song_title = song_title[0] if song_title else None
                artist = audio.get("WM/ARTISTS", [None]) if file_type == 'wma' else audio.get("artist", [None])
                artist = artist[0] if artist else None
                existing_lyrics = audio.get("lyrics", None) if file_type == 'flac' else audio.get("USLT", None) if file_type == 'mp3' else audio.get("WM/Lyrics", None)

                if song_title and artist:
                    if existing_lyrics and not overwrite:
                        print(f"Skipping {song_title} by {artist} (lyrics already embedded)")
                        continue
                    lyrics = get_lyrics(song_title, artist)
                    if lyrics:
                        embed_lyrics(file_path, lyrics, file_type)
                        print(f"Embedded lyrics for {song_title} by {artist}")
                    else:
                        print(f"Lyrics not found for {song_title} by {artist}")
                else:
                    print(f"Metadata missing for {file}")

if __name__ == "__main__":
    folder_path = input("Please paste the folder path: ")
    overwrite = input("Do you want to overwrite existing lyrics? (yes/no): ").strip().lower() == 'yes'
    process_folder(folder_path, overwrite)
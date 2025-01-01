import os
import requests
from bs4 import BeautifulSoup
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.id3._frames import USLT


def get_lyrics(song_title, artist):
    search_url = f"https://www.google.com/search?q={song_title}+{artist}+lyrics"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # This part depends on the structure of the website you're scraping from
    # Here, we assume the lyrics are within a <div> with a specific class
    lyrics_div = soup.find("div", class_="BNeawe tAd8D AP7Wnd")
    if lyrics_div:
        return lyrics_div.get_text()
    return None


def embed_lyrics(file_path, lyrics):
    audio = EasyID3(file_path)
    audio.save()
    audio = ID3(file_path)
    audio["USLT"] = USLT(encoding=3, lang="eng", desc="desc", text=lyrics)
    audio.save()


def process_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                audio = EasyID3(file_path)
                song_title = audio.get("title", [None])
                song_title = song_title[0] if song_title else None
                artist = audio.get("artist", [None])
                artist = artist[0] if artist else None

                if song_title and artist:
                    lyrics = get_lyrics(song_title, artist)
                    if lyrics:
                        embed_lyrics(file_path, lyrics)
                        print(f"Embedded lyrics for {song_title} by {artist}")
                    else:
                        print(f"Lyrics not found for {song_title} by {artist}")
                else:
                    print(f"Metadata missing for {file}")


# Replace 'your_music_folder' with the path to your folder of music files
process_folder("your_music_folder")

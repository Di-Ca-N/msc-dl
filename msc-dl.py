import sys
import os
import requests
import youtube_dl

from credentials import API_KEYS


DOWNLOAD_DIR_NAME = 'Songs'


YOUTUBE_API_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search?part=id&q={}&type=video"

if API_KEYS["youtube"]:
    YOUTUBE_API_SEARCH_URL += "&key=" + API_KEYS["youtube"]

else:
    print("""
===========================================================================================
WARNING: Running without YouTube API Key. May cause trouble when downloading multiple files
===========================================================================================
""")


def main():
    args = sys.argv
    file_path = args[1]

    with open(file_path, 'r') as file:
        songs = get_songs_list(file)
        ids = get_ids_list(songs)
        download_songs(ids, songs)


def get_songs_list(file):
    songs = []
    for line in file:
        if sanitize_line(line):
            songs.append(sanitize_line(line))

    return songs


def get_ids_list(songs):
    ids = []
    for term in songs:
        print("Getting ID for {}: ".format(sanitize_line(term)))
        video_id = get_video_id(term)
        ids.append(video_id)
    return ids


def sanitize_line(line):
    return line.rstrip("\n")


def get_video_id(term):
    try:
        return get_id_from_youtube_api(term)

    except KeyError:
        raise Exception("Cant get video ID from YouTube API. Check your API-Key or add one, if not exists")

    except ConnectionError:
        raise ConnectionError("Check your internet connection")


def get_id_from_youtube_api(term):
    response = requests.get(YOUTUBE_API_SEARCH_URL.format(term))
    json_response = response.json()
    video_id = json_response['items'][0]['id']['videoId']
    return video_id


def download_songs(id_list, filenames):
    print("Downloading and converting files...")

    for video_id, filename in zip(id_list, filenames):
        options = get_ytd_options(filename=filename)

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([video_id])

        print("{}: Conversion Done!".format(filename))


def get_ytd_options(filename=None):
    class YTDCustomLogger:
        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)

        def debug(self, msg):
            pass

    def custom_hook(data):
        if data['status'] == 'finished':
            print("{}: Download Done!".format(filename))

    return {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(os.getcwd(), DOWNLOAD_DIR_NAME, filename + ".%(ext)s"),
        'logger': YTDCustomLogger(),
        'progress_hooks': [custom_hook],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }


if __name__ == '__main__':
    main()

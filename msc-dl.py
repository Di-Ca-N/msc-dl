import sys
import os
import requests
import bs4
import youtube_dl


DOWNLOAD_DIR_NAME = 'Songs'

SEARCH_SOURCES = {
    "YOUTUBE_BASE": "https://www.youtube.com/results?search_query={}",
    "YOUTUBE_API": "https://www.googleapis.com/youtube/v3/search?part=id&q={}&type=video&key=",
}


def main():
    args = sys.argv
    file_path = args[1]

    with open(file_path, 'r') as file:
        songs_list = get_songs_list(file)
        id_list = get_ids_list(songs_list)
        download_songs(id_list, songs_list)


def get_songs_list(file):
    songs = []
    for line in file:
        if sanitize_line(line):
            songs.append(sanitize_line(line))

    return songs


def get_ids_list(songs):
    ids = []

    for term in songs:
        print("Getting ID for \"{}\"".format(sanitize_line(term)))
        video_id = get_video_id(term)
        ids.append(video_id)
    return ids


def sanitize_line(line):
    return line.strip()


def get_video_id(term):
    try:
        video_id = get_id_from_youtube_api(term)

    except (AssertionError, ImportError, KeyError, ConnectionError):
        video_id = get_id_from_youtube_scrapping(term)

    return video_id


def get_id_from_youtube_api(term):
    from credentials import API_KEYS
    assert API_KEYS["youtube"] == ""
    search_url = SEARCH_SOURCES["YOUTUBE_API"] + API_KEYS["youtube"]

    response = requests.get(search_url.format(term))
    json_response = response.json()

    # First video id from youtube api response
    video_id = json_response['items'][0]['id']['videoId']
    return video_id


def get_id_from_youtube_scrapping(term):
    search_url = SEARCH_SOURCES["YOUTUBE_BASE"]
    response = requests.get(search_url.format(term))
    scrapper = bs4.BeautifulSoup(response.content, 'html.parser')

    # Finding id of the first result video in page (no Ads)
    video_id = scrapper.find("div", {"data-context-item-id": True,
                                     "data-ad-impressions": False}).get("data-context-item-id")
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
        @staticmethod
        def error(msg):
            print(msg)

        def warning(self, msg):
            pass

        def debug(self, msg):
            pass

    def custom_hook(data):
        if data['status'] == 'finished':
            print("{}: Download Done!".format(filename))

    options = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(os.getcwd(), DOWNLOAD_DIR_NAME, filename + ".%(ext)s"),
        'logger': YTDCustomLogger(),
        'progress_hooks': [custom_hook],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            },
            {
                'key': 'FFmpegMetadata',
            }]
    }

    return options


if __name__ == '__main__':
    main()

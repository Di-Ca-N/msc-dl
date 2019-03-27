import sys
import os
import requests
import bs4
import youtube_dl

DOWNLOAD_DIR_NAME = 'Songs'

YOUTUBE_BASE_URL = "https://www.youtube.com"
YOUTUBE_SEARCH_BASE_URL = YOUTUBE_BASE_URL + "/results?search_query="


def main():
    args = sys.argv
    file_path = args[1]
    with open(file_path, 'r') as file:
        songs = get_songs_list(file)
        urls = get_url_list(songs)
        download_songs(urls, songs)


def get_songs_list(file):
    songs = []
    for line in file:
        if sanitize_line(line):
            songs.append(sanitize_line(line))

    return songs


def get_url_list(songs):
    urls = []
    for term in songs:
        print("Getting URL for {}: ".format(sanitize_line(term)), end='')
        video_url = YOUTUBE_BASE_URL + get_video_watch_url(term)
        print(video_url)
        urls.append(video_url)
    return urls


def get_video_watch_url(search_term):
    url = YOUTUBE_SEARCH_BASE_URL + sanitize_line(search_term)
    results = requests.get(url)
    parsed = bs4.BeautifulSoup(results.content, "html.parser")
    watch_url = parsed.find("div", {"class": "yt-lockup-thumbnail contains-addto"}).find("a").get("href")
    return watch_url


def sanitize_line(line):
    return line.rstrip("\n")


def download_songs(url_list, filenames):
    print("Downloading and converting files...")

    for index in range(len(url_list)):
        url = url_list[index]
        filename = filenames[index]

        options = get_ytd_options(filename)

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([url])

        print("{}: Conversion Done!".format(filename))


def get_ytd_options(filename):
    class Logger:
        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)

        def debug(self, msg):
            pass

    def hook(data):
        if data['status'] == 'finished':
            print("{}: Download Done!".format(filename))

    return {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(os.getcwd(), DOWNLOAD_DIR_NAME, filename + ".%(ext)s"),
        'logger': Logger(),
        'progress_hooks': [hook],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }


if __name__ == '__main__':
    main()

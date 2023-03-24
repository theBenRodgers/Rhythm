from pytube import YouTube
from pytube import Search


def youtube_search_results(search: str) -> list:
    s = Search(search)

    results = []
    for i in s.results[:3]:
        title_url = []
        title_url.append(i.title)
        title_url.append(i.watch_url)
        results.append(title_url)

    return results


def title_from_url(url: str) -> str:
    yt = YouTube(url)
    return yt.title


def download_audio(url: str, server, name) -> str:
    yt = YouTube(url)
    path = yt.streams.get_audio_only().download(output_path=
                                                f"C:/Users/Ben/OneDrive/Documents/Programming/Pycharm/Rhythm/audio/{server}", filename=f"{name}.mp3")
    return path


def get_thumbnail_url(url: str) -> str:
    yt = YouTube(url)
    return yt.thumbnail_url

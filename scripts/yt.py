from __future__ import unicode_literals
import yt_dlp 
import time
from pathlib import Path


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    'format': 'bestaudio/best',
    'logger': MyLogger(),
    'outtmpl': 'streamfiles/%(title)s.%(ext)s',
    'progress_hooks': [my_hook],
}

start = time.time()


def downloader(url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return Path(str(ydl_opts['outtmpl']))


end = time.time()
print(end - start)

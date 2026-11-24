"""Download YouTube videos or audio that you have permission to download."""
from pathlib import Path
from shutil import which
from urllib.parse import urlparse


def build_options(download_path, file_format):
    options = {
        'outtmpl': str(download_path / '%(title).150s [%(id)s].%(ext)s'),
        'noplaylist': True,
        'windowsfilenames': True,
        'overwrites': False,
    }
    if file_format == 'mp3':
        options.update({
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '320'}],
        })
    elif file_format == 'mp4':
        # Prefer H.264 and AAC, with a fallback to other codecs if needed.
        options.update({
            'format': ('bestvideo[height<=1080][vcodec^=avc1]+bestaudio[acodec^=mp4a]'
                       '/best[height<=1080][vcodec^=avc1][acodec^=mp4a]'
                       '/bestvideo[height<=1080]+bestaudio/best[height<=1080]'),
            'merge_output_format': 'mp4',
            'postprocessors': [{'key': 'FFmpegVideoConvertor',
                                'preferedformat': 'mp4'}],
        })
    else:
        raise ValueError('Choose MP3 or MP4.')
    return options


def valid_url(link):
    try:
        url = urlparse(link)
        host = url.hostname or ''
        return (url.scheme in ('http', 'https') and
                (host == 'youtu.be' or host == 'youtube.com' or
                 host.endswith('.youtube.com')) and bool(url.path.strip('/')))
    except ValueError:
        return False


def download_video(link, file_format, yt_dlp):
    download_path = Path.home() / 'Downloads'
    try:
        download_path.mkdir(parents=True, exist_ok=True)
        with yt_dlp.YoutubeDL(build_options(download_path, file_format)) as ydl:
            print(f'\nDownloading {file_format.upper()} to: {download_path}')
            if ydl.download([link]) != 0:
                print('Download failed.')
                return False
        print('\nDownload complete!\nSaved to your Downloads folder.')
        return True
    except (yt_dlp.utils.DownloadError, OSError) as error:
        print(f'\nDownload failed: {error}')
        return False


def main():
    print('================================\n   YOUTUBE VIDEO DOWNLOADER\n================================')
    try:
        import yt_dlp
    except ImportError:
        print('Install yt-dlp: python -m pip install -U "yt-dlp[default]"')
        return
    if not which('ffmpeg') or not which('ffprobe'):
        print('FFmpeg and FFprobe must be installed and available on PATH.')
        return
    while True:
        link = input('\nPaste the YouTube URL here (or Q to quit): ').strip()
        if link.lower() == 'q':
            break
        if not valid_url(link):
            print('Please enter a valid YouTube URL.')
            continue
        print('\nSelect a download format:\n[1] MP4 - Video (up to 1080p)\n[2] MP3 - Audio (320 kbps)')
        while True:
            choice = input('Enter your choice (1 or 2): ').strip().lower()
            if choice in ('1', 'mp4', '2', 'mp3'):
                break
            print('Invalid choice. Enter 1 or 2.')
        download_video(link, 'mp4' if choice in ('1', 'mp4') else 'mp3', yt_dlp)
        if input('\nDownload another video? (Y/N): ').strip().lower() != 'y':
            break
    print('Goodbye!')


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nGoodbye!')

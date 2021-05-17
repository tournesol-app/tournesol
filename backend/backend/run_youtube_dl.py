import subprocess
from functools import partial
from backend.cache_timeout_maxmem import cache_timeout_maxmem


def run_command_get_output(command, args, do_print=True, out_fn=None):
    """Run a command and get output."""
    lines = []
    p = subprocess.Popen([command] + args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         bufsize=1, shell=False)
    for line in iter(p.stdout.readline, b''):
        line = line[:-1]
        lines.append(line)
        if do_print:
            print(line.decode('utf-8'))
    p.stdout.close()
    p.wait()
    output = b'\n'.join(lines).decode('utf-8')

    # writing data to out_fn
    if out_fn is not None:
        with open(out_fn, 'w') as f:
            f.write(output)

    return output


# run youtube-dl
run_ytdl = partial(run_command_get_output, command='youtube-dl')


def download_video_info(video_id, **kwargs):
    """Get a video information into the current folder via youtube-dl."""
    args = ['--id', '--write-description', '--write-info-json', '--write-pages',
            '--sleep-interval', '5',
            '--skip-download', '--download-archive', 'archive.txt', '--', video_id]
    return run_ytdl(args=args, **kwargs)


@cache_timeout_maxmem(timeout_s=3600, max_entries=1000)
def search_on_youtube_playlist(search_phrase="video", n_videos=10, **kwargs):
    """Get search results from youtube."""
    args = ['--flat-playlist', '--skip-download', '--print-json', 'ytsearch%d:%s' % search_phrase]
    return run_ytdl(args=args, **kwargs)

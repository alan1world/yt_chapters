# YouTube downloader with chapters

## Requirements:

* Youtube downloader
* ffmpeg
* MP4Box

## Usage

### Basic usage:

`yt_chapters.py "youtube_link"`

### Multiple links can be downloaded:

`yt_chapters.py "link1" "link2"`

### Split chapters

Output chapters as individual files:

`yt_chapters.py --split "https://www.youtube.com/watch?v=m5lp8S-YgrQ"`

### Testing

If there are issues with the chapters file, the script will pause if the `--fix` is passed:

`yt_chapters.py --test` download lowest bitrate version of video to speed up testing

`yt_chapters.py --fix` pause before processing the chapter file

For example:

`yt_chapters.py --fix "https://www.youtube.com/watch?v=EbJos02Xa9Q"` 

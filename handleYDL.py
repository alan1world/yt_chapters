# TODO: create an object with the functions as methods, so the preferences, like use_cli, can be defined only once

from youtube_dl import YoutubeDL
import subprocess

DEFAULT_CLI_PATH = "youtube-dl"

def download( url, ydl_opts=None, use_cli=False, cli_path=DEFAULT_CLI_PATH ):
    
    if not use_cli:
        with YoutubeDL( ydl_opts ) as ydl:
            ydl.prepare_filename( ydl.extract_info( url ) )
            try:
                ydl.download( [ url ] )
            except:
                return False
    else:
        try:
            outtmpl = ydl_opts['outtmpl']
        except:
            outtmpl = ''
        result = subprocess.run( [ cli_path, url, '-o', outtmpl ], capture_output=True, encoding='UTF-8' )
    
    return True

def get_infos( url, ydl_opts=None, use_cli=False, cli_path=DEFAULT_CLI_PATH ):
    
    infos = {}

    if not use_cli:
        with YoutubeDL() as ydl:
            extracted_infos = ydl.extract_info( url, download=False )
            infos = { 
                'title': extracted_infos['title'],
                'description': extracted_infos['description'],
                'duration': extracted_infos['duration']
                }
    else:
        infos['title'] = subprocess.run( [cli_path, url, '--get-title'], capture_output=True, encoding='UTF-8' )
        infos['description'] = subprocess.run( [cli_path, url, '--get-description'], capture_output=True, encoding='UTF-8' )
        infos['duration'] = subprocess.run( [cli_path, url, '--get-duration'], capture_output=True, encoding='UTF-8' )
    
    return infos

def prepare_filename( url, ydl_opts=None, use_cli=False, cli_path=DEFAULT_CLI_PATH ):
    
    infos = get_infos( url, use_cli, cli_path )

    if not use_cli:
        with YoutubeDL( ydl_opts ) as ydl:
            ydl.prepare_filename( infos )
    else:
        subprocess.run( [cli_path, url, '--get-filename', '-o', ydl_opts['outtmpl'] ],
            capture_output=True, encoding='UTF-8' )

if __name__ == '__main__':
    
    url = 'https://www.youtube.com/watch?v=WifI7lOUI-o'

    print( get_filename(url, {'outtmpl':'%(title)s'} ) )

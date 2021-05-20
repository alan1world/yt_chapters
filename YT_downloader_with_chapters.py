#! /usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: change working location to be a temp dir
# TODO: Add option for mkv

import subprocess, os, argparse, datetime, re, sys

def get_source_name(download_source:str)->str:

    # Get the expected filename in order to process everything down the line
    result = subprocess.run(["youtube-dl", "--get-filename",
                            "-o", "%(title)s", download_source],
                            capture_output=True, encoding='UTF8')
    return result.stdout.rstrip('\n')

def get_best_mp4_single_file(download_source:str, description_file:str,
                             fix_required:bool=False)->list:

    # Download the file as mp4 (in order to use MP4)
    subprocess.run(["youtube-dl", "--write-description", "-f",
                    "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                    "-o", "%(title)s.%(ext)s", link_to_download])
    if fix_required:
        input("Fix the description file to have the chapters "
              "on their own lines in the format timecode name "
              "and then press Enter to continue...")
    return read_description_file(description_file=description_file)

def get_worst_mp4_single_file(download_source:str, description_file:str,
                              fix_required:bool=False)->list:

    # Download the file as mp4 (in order to use MP4)
    subprocess.run(["youtube-dl", "--write-description", "-f",
                    "worstvideo[ext=mp4]+worstaudio[ext=m4a]/mp4",
                    "-o", "%(title)s.%(ext)s", link_to_download])
    if fix_required:
        input("Fix the description file to have the chapters "
              "on their own lines in the format timecode name "
              "and then press Enter to continue...")
    return read_description_file(description_file=description_file)

def add_chapters_to_mp4(chapter_file_name:str, name_for_download:str)->None:

    # Use MP4Box to mux the chapter file with the mp4
    subprocess.run(["MP4Box", "-chap", chapter_file_name, name_for_download])

def read_description_file(description_file:str)->list:

    # Read the description file
    # Split into time and chapter name

    list_of_chapters = []

    with open(description_file, 'r') as f:
        # only increment chapter number on a chapter line
        # chapter lines start with timecode
        line_counter = 1
        for line in f:
            result = re.search(r"\(?(\d?[:]?\d+[:]\d+)\)?", line)
            try:
                # result = re.search("\(?(\d+[:]\d+[:]\d+)\)?", line)
                time_count = datetime.datetime.strptime(result.group(1), '%H:%M:%S')
            except:
                try:
                    # result = re.search("\(?(\d+[:]\d+)\)?", line)
                    time_count = datetime.datetime.strptime(result.group(1), '%M:%S')
                except:
                    continue
            chap_name = line.replace(result.group(0),"").rstrip(' :\n')
            chap_pos = datetime.datetime.strftime(time_count, '%H:%M:%S')
            list_of_chapters.append((str(line_counter).zfill(2), chap_pos, chap_name))
            line_counter += 1

    return list_of_chapters

def write_chapters_file(chapter_file:str, chapter_list:tuple)->None:

            #open(chapter_file, 'w').close()

            # Write out the chapter file based on simple MP4 format (OGM)
            with open(chapter_file, 'w') as fo:
                for current_chapter in chapter_list:
                    fo.write(f'CHAPTER{current_chapter[0]}='
                            f'{current_chapter[1]}\n'
                            f'CHAPTER{current_chapter[0]}NAME='
                            f'{current_chapter[2]}\n')


def split_mp4(chapters:list, download_filename:str, download_name:str)->None:

    # current_duration = subprocess.run(['ffprobe', '-i', download_filename,
                                       # '-show_entries', 'format=duration',
                                       # '-v', 'quiet', '-of', 'csv="p=0"'],
                                        # capture_output=True, encoding='UTF8')
    current_duration_pretext = subprocess.run(['ffprobe', '-i', download_filename,
                                       '-show_entries', 'format=duration',
                                       '-v', 'quiet'],
                                        capture_output=True, encoding='UTF8')
    current_duration = float(current_duration_pretext.stdout[18:-13])
    m, s = divmod(current_duration, 60)
    h, m = divmod(m, 60)
    current_dur = ':'.join([str(int(h)),str(int(m)),str(s)])
    for current_index, current_chapter in enumerate(chapters):
        # current_chapter will be a tuple: position, timecode, name
        next_index = current_index + 1
        start_time = current_chapter[1]
        try:
            end_time = chapters[next_index][1]
        except:
            end_time = current_dur
        output_name = f'{download_name} - ({current_chapter[2]}).mp4'
        subprocess.run(["ffmpeg", "-ss", start_time, "-to", end_time,
                        "-i", download_filename, "-acodec", "copy",
                        "-vcodec", "copy", output_name])

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Download Youtube videos with chapters')

    parser.add_argument('links', metavar='N', type=str, nargs='+',
                        help='List of links to download')

    parser.add_argument("--split", help="Split chapters into individual files",
                        action="store_true")
    parser.add_argument("--test", help="Download worst version to speed up testing",
                        action="store_true")
    parser.add_argument("--fix", help="Pause to allow manual correction of the description file",
                        action="store_true")
    args = parser.parse_args()
    # print(args.links)

    for link_to_download in args.links:

        download_name = get_source_name(download_source=link_to_download)
        download_filename = f'{download_name}.mp4'
        description_file = f'{download_name}.description'
        chapter_file = f'{download_name}_chapter.txt'

        if not args.test:
            chapters = get_best_mp4_single_file(download_source=link_to_download,
                                                description_file=description_file,
                                                fix_required=args.fix)
        else:
            chapters = get_worst_mp4_single_file(download_source=link_to_download,
                                                description_file=description_file,
                                                fix_required=args.fix)

        
        if not chapter_file:
            print("No chapters found")
            sys.exit(1)
        
        write_chapters_file(chapter_file=chapter_file, chapter_list=chapters)

        if args.split:
            split_mp4(chapters=chapters, download_filename=download_filename,
                      download_name=download_name)
        
        add_chapters_to_mp4(chapter_file_name=chapter_file,
                              name_for_download=download_filename)

        # Clean up the text files
        os.remove(description_file)
        os.remove(chapter_file)

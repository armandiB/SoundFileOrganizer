import os
from mutagen import File
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
import music_tag
import librosa
import soundfile
import shutil

EXCLUDED_FOLDERS = ['Wreck His Days'] #TODO: what to do when there is a slash in forder name?
EXCLUDED_EXTENSIONS = ['.part']
COPY_FILE_TYPES = ['mp3', 'aac', 'm4a', 'mp4']

def convert_files(input_folder, output_folder, rewrite=False):
    file_paths = {}
    for dirpath, dirnames, filenames in os.walk(input_folder):
        next_folder = False
        for folder in EXCLUDED_FOLDERS:
            if folder in dirpath:
                next_folder = True
        if next_folder: continue

        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file = File(file_path)
            if file is None:
                continue
            else:
                print("Analysing: " + str(file_path))
                rel_path = os.path.relpath(file_path, start=input_folder)
                output_path = os.path.join(output_folder, rel_path)

                file_type, tg_file_type, final_output_path = get_final_output_path(file_path, output_path)

                if os.path.isfile(final_output_path) and not rewrite:
                    continue

                if file_type in COPY_FILE_TYPES and tg_file_type == file_type:
                    make_dir(final_output_path)
                    print("Copying: " + str(final_output_path))
                    shutil.copy2(file_path, final_output_path)
                    continue

                sound, sample_rate, tg_sample_rate, tg_bit_depth = get_target_info(
                    file, file_path, tg_file_type)

                if sound is not None:
                    file_paths[file_path] = final_output_path
                    #TODO: try block with deletion of file if catch
                    convert_file(sound, sample_rate, tg_sample_rate, tg_bit_depth, tg_file_type, final_output_path)
                    copy_tags(file_path, final_output_path, file_type, tg_file_type, file)

    return file_paths

def get_final_output_path(file_path, output_path):
    file_type = file_path.split('.')[-1]
    tg_file_type = get_target_file_type(file_type)
    #TODO: crop file name maximum size rekordbox
    final_output_path = make_final_output_path(output_path, tg_file_type)
    return file_type, tg_file_type, final_output_path

def get_target_info(file, file_path, tg_file_type):
    sample_rate = file.info.sample_rate
    bit_depth = file.info.bits_per_sample

    if tg_file_type == "wav":
        tg_sample_rate, tg_bit_depth = get_target_params_wav(sample_rate, bit_depth)
    elif tg_file_type == "aiff":
        tg_sample_rate, tg_bit_depth = get_target_params_aiff(sample_rate, bit_depth)
    else:
        return None, None, None, None,

    sound, _ = librosa.load(file_path, sr=sample_rate)

    return sound, sample_rate, tg_sample_rate, tg_bit_depth


def get_target_file_type(file_type):
    if file_type == 'wav':
        return 'wav'
    if file_type == 'flac':
        return 'aiff'
    if file_type in COPY_FILE_TYPES:
        return file_type
    else:
        return 'aiff'


def get_target_params_wav(sample_rate, bit_depth):
    if sample_rate >= 48000:
        return 48000, bit_depth
    else:
        return 44100, 16


def get_target_params_aiff(sample_rate, bit_depth): #TODO: test if true
    if sample_rate >= 48000:
        return 48000, bit_depth
    else:
        return 44100, 16


def make_final_output_path(path, file_type):
    folder_path, file_name = os.path.split(path)
    file_list = file_name.split('.')[:-1] + [str(file_type)]
    return os.path.join(folder_path, '.'.join(file_list))


def convert_file(sound, sample_rate, tg_sample_rate, tg_bit_depth, tg_file_type, output_path):
    if tg_sample_rate != sample_rate:
        final_sound = librosa.resample(sound, sample_rate, tg_sample_rate)
    else:
        final_sound = sound

    if tg_file_type in ['wav', 'aiff']:
        make_dir(output_path)
        print("Writing: " + str(output_path))
        soundfile.write(output_path, final_sound, tg_sample_rate, subtype='PCM_' + str(tg_bit_depth))

    return


def make_dir(file_path):
    folder_path = os.path.dirname(file_path)
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    return

def copy_tags(input_path, output_path, file_type, tg_file_type, file):
    if file_type in ['wav', 'aiff'] and tg_file_type == file_type:
        new_file = File(output_path)
        new_file.tags = file.tags
        new_file.save()
    elif tg_file_type in ['aiff']:
        new_file = music_tag.load_file(output_path)
        new_file["title"] = file["title"]
        new_file["artist"] = file["artist"]
        new_file["TRACKNUMBER"] = file["TRACKNUMBER"]
        try:
            new_file["album"] = file["album"]
        except:
            pass
        new_file.save()
    else:
        #TODO: read Rekordbox Library (xml) and go find tags there
        os.system('mid3cp \'' + input_path + '\' \'' + output_path + '\'') #'(' character in path fails
    return

if __name__ == "__main__":
    #convert_files(r'/Volumes/Elements Armand/root_20210122/External Tracks/Clean Downloads',
    #              r'/Volumes/Elements Armand/ConvertedLibrary/Clean Downloads', rewrite=False)
    #convert_files(r'/Volumes/Elements Armand/root_20210122/External Tracks/USB',
    #              r'/Volumes/Elements Armand/ConvertedLibrary/USB', rewrite=False)
    convert_files(r'/Volumes/Elements Armand/root_20210122/Floris Tracks/_MusicTransfer_20201121',
                  r'/Volumes/Elements Armand/ConvertedLibrary/_MusicTransfer_20201121', rewrite=False)
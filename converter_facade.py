import os
import mutagen
import librosa
import soundfile


def convert_files(input_folder, output_folder, rewrite=False):
    file_paths = {}
    for dirpath, dirnames, filenames in os.walk(input_folder):
        for filename in filenames:
            if 'Wreck His Days' in dirpath: #TODO: what to do when there is a slash in forder name?
                continue
            file_path = os.path.join(dirpath, filename)
            file = mutagen.File(file_path)
            if file is None:
                continue
            else:
                rel_path = os.path.relpath(file_path, start=input_folder)
                output_path = os.path.join(output_folder, rel_path)

                tg_file_type, final_output_path = get_final_output_path(file_path, output_path)

                if os.path.isfile(final_output_path) and not rewrite:
                    continue

                sound, sample_rate, tg_sample_rate, tg_bit_depth = get_target_info(
                    file, file_path, tg_file_type)

                if sound is not None:
                    file_paths[file_path] = final_output_path
                    convert_file(sound, sample_rate, tg_sample_rate, tg_bit_depth, tg_file_type, final_output_path)
                    copy_tags(file_path, final_output_path)

    return file_paths

def get_final_output_path(file_path, output_path):
    file_type = file_path.split('.')[-1]
    tg_file_type = get_target_file_type(file_type)

    final_output_path = make_final_output_path(output_path, tg_file_type)
    return tg_file_type, final_output_path

def get_target_info(file, file_path, tg_file_type):
    sample_rate = file.info.sample_rate
    bit_depth = file.info.bits_per_sample

    if tg_file_type == "wav":
        tg_sample_rate, tg_bit_depth = get_target_params_wav(sample_rate, bit_depth)
    else:
        return None, None, None, None,

    sound, _ = librosa.load(file_path, sr=sample_rate)

    return sound, sample_rate, tg_sample_rate, tg_bit_depth


def get_target_file_type(file_type):
    if file_type == 'wav':
        return 'wav'
    else:
        return file_type


def get_target_params_wav(sample_rate, bit_depth):
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

    if tg_file_type == "wav":
        make_dir(output_path)
        soundfile.write(output_path, final_sound, tg_sample_rate, subtype='PCM_' + str(tg_bit_depth))

    return


def make_dir(file_path):
    folder_path = os.path.dirname(file_path)
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    return

def copy_tags(input_path, output_path):
    #TODO: read Rekordbox Library (xml) and go find tags there
    os.system('mid3cp \'' + input_path + '\' \'' + output_path + '\'') #'(' character in path fails
    return

if __name__ == "__main__":
    convert_files(r'/Volumes/Backup Armand/root/External Tracks/Clean Downloads', r'/Volumes/CORSAIRE_ARMAND/Clean Downloads converted', rewrite=False)
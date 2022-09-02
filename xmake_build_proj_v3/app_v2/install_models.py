import sys
import subprocess
import requests
from tqdm.auto import tqdm
import os
import json
from pathlib import Path
import werkzeug
import tarfile
import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("command", type=str, 
                        help="use 'start' to run the app")
arg_parser.add_argument("-m", "--models_dir", type=str, default='models', 
                        help="specify the directory where models are stored")

# print (sys.argv)
download_dir = Path.home().joinpath('.requst_classifier')
download_dir.mkdir(exist_ok=True)

HOME_DIR = Path.home()
FILE_DIR = Path(__file__).parent.absolute()

with open(Path.joinpath(FILE_DIR, 'models_config.json'), 'r') as f:
    config_dict = json.load(f)
    # print (config_dict)


def extract_targz_package(package_file, target_folder):
    package_file = Path(package_file)
    target_folder = Path(target_folder)
    print (f'extracting {package_file} to {target_folder}')
    if package_file.exists():
        if str(package_file).endswith("tar.gz"):
            with tarfile.open(package_file) as tar:
                if target_folder.name == tar.next().name:
                        target_folder = target_folder.parent
            with tqdm.wrapattr(open(package_file, "rb"), "read", miniters=1,
                            total=os.stat(package_file).st_size,
                            desc=str(package_file)) as f_tar:
                # tar = tarfile.open(str(package_file), "r:gz")
                tar = tarfile.open(fileobj=f_tar, mode='r:gz')
                # if target_folder.name == tar.getmembers()[0].name:
                #     target_folder = target_folder.parent
                tar.extractall(target_folder)
                tar.close()
        else:
            raise Exception('File is not a tar.gz')
    else:
        raise FileNotFoundError ('Model file not found at {}'.format(package_file))


def install_models(models_dir):
    models_dir = Path(models_dir)
    print ("Installing model data files...")
    deeppavlov_models_install_dir = config_dict['deeppavlov_models']['path'].format(HOME_DIR=HOME_DIR)
    extract_targz_package(models_dir.joinpath(config_dict['deeppavlov_models']['tar_name']), deeppavlov_models_install_dir)

    nltk_data_install_dir = config_dict['nltk_data']['path'].format(HOME_DIR=HOME_DIR)
    extract_targz_package(models_dir.joinpath(config_dict['nltk_data']['tar_name']), nltk_data_install_dir)

    if models_dir.joinpath(config_dict['spacy_model']['tar_name']).exists():
        print ("Installing {}".format(config_dict['spacy_model']['tar_name']))
        process = subprocess.Popen([sys.executable, '-m', 'pip', 'install', str(models_dir.joinpath(config_dict['spacy_model']['tar_name']))])
        process = process.communicate()
    else:
        raise FileNotFoundError ('Model file not found at {}'.format(config_dict['spacy_model']['tar_name'])) 
    print ("MODELS INSTALLED.")


def install_models_from_partitions(models_dir):
    models_dir = Path(models_dir)
    print ("Creating model package...")
    models_tar_name = 'models.tar.gz'
    models_tar_path = models_dir.joinpath(models_tar_name)
    merge_partfiles(models_dir, models_tar_path)
    extract_targz_package(models_tar_path, models_dir)
    if not models_dir.joinpath(config_dict['deeppavlov_models']['tar_name']).exists():
        for sub in next(os.walk(models_dir))[1]:
            if models_dir.joinpath(sub).joinpath(config_dict['deeppavlov_models']['tar_name']).exists():
                models_dir = models_dir.joinpath(sub)  
    
    print ("Installing model data files...")
    deeppavlov_models_install_dir = config_dict['deeppavlov_models']['path'].format(HOME_DIR=HOME_DIR)
    extract_targz_package(models_dir.joinpath(config_dict['deeppavlov_models']['tar_name']), deeppavlov_models_install_dir)

    nltk_data_install_dir = config_dict['nltk_data']['path'].format(HOME_DIR=HOME_DIR)
    extract_targz_package(models_dir.joinpath(config_dict['nltk_data']['tar_name']), nltk_data_install_dir)

    if models_dir.joinpath(config_dict['spacy_model']['tar_name']).exists():
        print ("Installing {}".format(config_dict['spacy_model']['tar_name']))
        process = subprocess.Popen([sys.executable, '-m', 'pip', 'install', str(models_dir.joinpath(config_dict['spacy_model']['tar_name']))])
        process = process.communicate()
    else:
        raise FileNotFoundError ('Model file not found at {}'.format(config_dict['spacy_model']['tar_name'])) 
    print ("MODELS INSTALLED.")


def compress_to_targz(tarname, dirpath, dirname=None):
    tar = tarfile.open(tarname, 'w:gz')
    tar.add(dirpath, arcname=dirname, recursive=True)
    tar.close()


def split_file_into_chunks(filepath, outdir, part_size=2254857830):
    outdir = Path(outdir)
    outdir.mkdir(exist_ok=True)
    with open(filepath, 'rb') as f:
        i = 0
        while (True):
            chunk = f.read(part_size)
            if not chunk:
                break
            print ('writing chunk ' + str(i))
            part_filename = "part-" + str(i) + ".bin"
            with open(outdir.joinpath(part_filename), 'wb') as outf:
                outf.write(chunk)
            i += 1


def merge_partfiles(part_file_dir, tarname):
    part_file_dir = Path(part_file_dir)
    with open(tarname, 'wb') as outf:
        for i, part_file in enumerate(sorted(part_file_dir.glob('part-[0-9]*.bin'))):
            with open(part_file, 'rb') as fin:
                print ('writing chunk ' + str(i))
                outf.write(fin.read())


def main():
    args = arg_parser.parse_args()
    install_models_from_partitions(args.models_dir)


if __name__ == '__main__':
    compress_to_targz('deeppavlov_models.tar.gz', '.deeppavlov/')
    compress_to_targz('nltk_data.tar.gz', 'nltk_data/')


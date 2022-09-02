import os
import shutil
import sys
from os.path import expanduser, join, relpath, split
from pathlib import Path

def modify_files_rem_vuln():
    '''Copy modified tensorflow files to site-packages to remove vulnerabilities'''
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tf_mods', 'tensorflow_core'))
    # print ('modifications stored in', root_path)
    ls_dirs = []
    # _ = [ls_dirs.extend(os.listdir(p)) for p in sys.path if os.path.isdir(p)]
    ls_dirs = [d for p in sys.path if os.path.isdir(p) for d in Path(p).iterdir() if d.is_dir()]
    # print ('checking in')
    # print (sys.path)
    # print (ls_dirs)
    target_path = None
    for p in ls_dirs:
        if 'tensorflow_core' == p.name:
            target_path = str(p.parent)
            print (target_path)
            for dirpath, dirs, files in os.walk(root_path):
                print (dirpath)
                if not files:
                    continue
                else:
                    for fil in files:
                        print ('file {} is being copied'.format(fil))
                        source_path = join(dirpath,fil)
                        temp = relpath(source_path, os.path.join(os.path.dirname(__file__), 'tf_mods'))
                        head, tail = split(temp)
                        target_dir = join(target_path,head)
                        shutil.copy(source_path, target_dir)
            break

if __name__ == '__main__':
    modify_files_rem_vuln()
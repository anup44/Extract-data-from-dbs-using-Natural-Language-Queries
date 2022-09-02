import shlex
import subprocess
import os
import sys
import shutil
import itertools
import site
from pathlib import Path
from setuptools import setup, find_packages, Command
from codecs import open
from os import path
from setuptools.command.install import install
from subprocess import call

WHEELHOUSE = "wheelhouse"


def get_install_requires():
    with open('requirements.txt') as reqs_file:
        reqs = [line.rstrip() for line in reqs_file.readlines()]
    return reqs

def generate_package_pattern(dirc):
    dirc = Path(dirc)
    paths = dirc.glob('**')
    # depths = [len(f.relative_to(dirc).parts) for f in paths]
    max_depth = max([len(f.relative_to(dirc).parts) for f in paths])
    pattern_list = []
    for i in range(max_depth + 2):
        pattern_list.append(dirc.name + '/' + '/'.join(['*' for x in range(i)]))
    return pattern_list

# def post_install():
#     # from subprocess import call
#     # call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
#     #      cwd=os.path.abspath(os.path.dirname(__file__)))

#     print ("Hello, developer, how are you? :)")
#     # subprocess.Popen(['mkdir', 'lololololololol'])
#     # install.run(self)
#     # from change_script import modify_tf_files
#     # modify_tf_files()
#     import sysconfig
#     ls_dirs = []
#     # _ = [ls_dirs.extend(os.listdir(p)) for p in sys.path if os.path.isdir(p)]
#     ls_dirs = [d for p in sys.path if os.path.isdir(p) for d in Path(p).iterdir() if d.is_dir()]
#     print (sys.path)
#     print (ls_dirs)
#     # ls_dirs = list(itertools.chain(os.listdir(p) for p in sysconfig.get_paths()['purelib']))
#     # ls_dirs = os.listdir(sysconfig.get_paths()['purelib'])
#     for p in ls_dirs:
#         if 'tensorflow_core' == p.name:
#             target_path = str(p.parent)
#             # modify_tf_files(target_path)
#             break

class CustomModCommand(Command):
    """Customized setuptools install command - prints a friendly greeting."""
    description = "Perform modification to remove vulnerabilities."
    user_options = []

    def __init__(self, dist):
        Command.__init__(self, dist)

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
    pass
    def run(self):
        print ("Hello, developer, how are you? :)")
        # subprocess.Popen(['mkdir', 'lololololololol'])
        # install.run(self)
        # from change_script import modify_tf_files
        # modify_tf_files()
        # call([sys.executable] + '-m pip install -r requirements.txt'.split())
        # call([sys.executable] + '-m pip install .'.split())
        
        import sysconfig
        ls_dirs = []
        # _ = [ls_dirs.extend(os.listdir(p)) for p in sys.path if os.path.isdir(p)]
        ls_dirs = [d for p in sys.path if os.path.isdir(p) for d in Path(p).iterdir() if d.is_dir()]
        # print (sys.path)``
        # print (ls_dirs)
        # ls_dirs = list(itertools.chain(os.listdir(p) for p in sysconfig.get_paths()['purelib']))
        # ls_dirs = os.listdir(sysconfig.get_paths()['purelib'])
        for p in ls_dirs:
            if 'tensorflow_core' == p.name:
                target_path = str(p.parent)
                # modify_tf_files()
                break
        #install.run(self)

# class CustomInstallCommand(install):
#     """Customized setuptools install command - prints a friendly greeting."""
#     description = "chale to manu"
#     def run(self):
#         print ("Hello, developer, how are you? :)")
#         self.execute(post_install, (), msg="Running post install task")
#         # subprocess.Popen(['mkdir', 'lololololololol'])
#         install.run(self)
#         # from change_script import modify_tf_files
#         # modify_tf_files()
#         atexit.register(post_install)
#         # self.run_command('remove_vuln')
#         #install.run(self)

class Package(Command):
    """Package Code and Dependencies into wheelhouse"""
    description = "Run wheels for dependencies and submodules dependencies"
    user_options = []

    def __init__(self, dist):
        Command.__init__(self, dist)

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
    pass

    # def localize_requirements(self):
    #     """
    #     After the package is unpacked at the target destination, the requirements can be installed
    #     locally from the wheelhouse folder using the option --no-index on pip install which
    #     ignores package index (only looking at --find-links URLs instead).
    #     --find-links <url | path> looks for archive from url or path.
    #     Since the original requirements.txt might have links to a non pip repo such as github
    #     (https) it will parse the links for the archive from a url and not from the wheelhouse.
    #     This functions creates a new requirements.txt with the only name and version for each of
    #     the packages, thus eliminating the need to fetch / parse links from http sources and install
    #     all archives from the wheelhouse.
    #     """
    #     dependencies = open("requirements.txt").read().split("\n")
    #     local_dependencies = []

    #     for dependency in dependencies:
    #         if dependency:
    #             if "egg=" in dependency:
    #                 pkg_name = dependency.split("egg=")[-1]
    #                 local_dependencies.append(pkg_name)
    #             elif "git+" in dependency:
    #                 pkg_name = dependency.split("/")[-1].split(".")[0]
    #                 local_dependencies.append(pkg_name)
    #             else:
    #                 local_dependencies.append(dependency)

    #     print "local packages in wheel: %s", local_dependencies
    #     self.execute("mv requirements.txt requirements.orig")

    #     with open("requirements.txt", "w") as requirements_file:
    #         # filter is used to remove empty list members (None).
    #         requirements_file.write("\n".join(filter(None, local_dependencies)))

    def execute(self, command, capture_output=False):
        """
        The execute command will loop and keep on reading the stdout and check for the return code
        and displays the output in real time.
        """

        print ("Running shell command: %s", command)

        if capture_output:
            return subprocess.check_output(shlex.split(command))

        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)

        while True:
            output = process.stdout.readline()

            if process.poll() is not None:
                break
            if output:
                print (output.strip())

        return_code = process.poll()

        if return_code != 0:
            print ("Error running command %s - exit code: %s", command, return_code)
            raise IOError("Shell Commmand Failed")
    
        return return_code

    def run_commands(self, commands):
        for command in commands:
            self.execute(command)

    # def restore_requirements_txt(self):
    #     if os.path.exists("requirements.orig"):
    #         print "Restoring original requirements.txt file"
    #         commands = [
    #             "rm requirements.txt",
    #             "mv requirements.orig requirements.txt"
    #         ]
    #         self.run_commands(commands)
    
    def run(self):
        commands = []
        if os.path.exists(WHEELHOUSE):
            shutil.rmtree(WHEELHOUSE)
        os.makedirs(WHEELHOUSE, exist_ok=True)
        commands.extend([
            # "rmdir -r {dir}".format(dir=WHEELHOUSE),
            # "mkdir -p {dir}".format(dir=WHEELHOUSE),
            "pip wheel --wheel-dir={dir} -r requirements.txt".format(dir=WHEELHOUSE)
        ])
    
        print ("Packing requirements.txt into wheelhouse")
        self.run_commands(commands)
        print ("Generating local requirements.txt")
        # self.localize_requirements()
    
        print ("Packing code and wheelhouse into dist")
        self.run_command("sdist")
        # self.restore_requirements_txt()

setup(
    name="DHS_Query_Processor",
    version="0.1.5",
    #packages=find_packages(),
    package_dir={"query_processor": 'app_v2', "bert_dp": 'app_v2/bert_dp'},
    packages=["query_processor", "bert_dp"],
    install_requires=get_install_requires(),
    # install_requires=['flask', 
    #     'flask_restful', 
    #     'flask-cors', 
    #     'numpy', 
    #     'deeppavlov', 
    #     'urllib3==1.25.3', 
    #     'requests==2.22.0', 
    #     'tensorflow==1.15.2'],
    package_data={
        "query_processor": ['*.*', 'config_tables/*.*', *generate_package_pattern(Path(__file__).parent.joinpath('app_v2/tf_mods'))]
    },
    entry_points={
        'console_scripts': ['query_processing=query_processor.main:main'],
    },
    cmdclass={
        'remove_vuln': CustomModCommand,
        # 'install': CustomInstallCommand,
        'package': Package
    },
    description="DHS_ML_POC",
    author="ANup bhutada",
    author_email="anup.bhutada@sap.com, vinutha.yediyur.varadarajaiyengar@sap.com",
)
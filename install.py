import yaml
import shutil
import os
import sys
import subprocess
import re
import urllib.request
import tempfile
import pathlib

tmpDir = tempfile.mkdtemp()

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

def check_cmake():
    if not shutil.which("cmake2"):
        print("cmake not in path. Installing from source...")
        url = f'https://github.com/Kitware/CMake/releases/download/v4.0.2/cmake-4.0.2.tar.gz'

def install_flexiblesusy():
    fsVersion = config["versions"]["FlexibleSUSY"]
    fsDir = f'FlexibleSUSY-{fsVersion}'
    if os.path.isdir(fsDir):
        print(f'{fsDir} directory exists. Do you want to delete it?')
    else:
        url = f'https://github.com/FlexibleSUSY/FlexibleSUSY/archive/refs/tags/v{fsVersion}.tar.gz'

def install_gm2calc():
    global tmpDir
    print('Installing GM2Calc...')
    gm2cVersion = config["versions"]["GM2Calc"]
    url = f'https://github.com/GM2Calc/GM2Calc/archive/refs/tags/v{gm2cVersion}.tar.gz'
    urllib.request.urlretrieve(url, os.path.join(tmpDir, f'GM2Calc-{gm2cVersion}.tar.gz'))
    subprocess.call(f'tar -xf GM2Calc-{gm2cVersion}.tar.gz', cwd=tmpDir, shell=True)
    os.makedirs(os.path.join(tmpDir, f'GM2Calc-{gm2cVersion}', 'build'))
    installPath = os.path.join(pathlib.Path(__file__).parent.resolve(), "FlexibleSUSY-deps", f'GM2Calc-{gm2cVersion}')
    subprocess.call(f'cmake .. -DCMAKE_INSTALL_PREFIX={installPath} -DCMAKE_POSITION_INDEPENDENT_CODE=On && make && make install', cwd=os.path.join(tmpDir, f'GM2Calc-{gm2cVersion}', 'build'), shell=True)

def check_cxx():
    print('Checking C++ compiler: ', end='')
    if shutil.which('g++'):
        print('found g++')
        return 'gcc'
    elif shutil.which('clang++'):
        print('found clang++')
        return 'clang'
    else:
        print('not found')
        return None

if __name__ == '__main__':
    if not os.path.exists('FlexibleSUSY-deps'):
        os.makedirs('FlexibleSUSY-deps')
    if check_cxx() == None:
        print('\nThis script requires at least a C++ compiler')
        distro = subprocess.run(['cat /etc/*-release'], shell=True, capture_output=True).stdout.decode()
        if re.search('ubuntu', distro, re.IGNORECASE):
            print('You seem to be on Ubuntu. You can try running sudo apt install g++')
        elif re.search('opensuse', distro, re.IGNORECASE):
            print('You seem to be on openSUSE. You can try running sudo zypper in gcc-c++')
        print('\nPlease install the compiler using your linux distribution package manager and re-run this script')
        sys.exit()

    check_cmake()

    while True:
        installGM2Calc = input('Install GM2Calc? [yes/no]: ')
        if installGM2Calc != "yes" and installGM2Calc != "no":
            print(f'please type yes or no (you typed {installGM2Calc}')
            continue
        if installGM2Calc:
            install_gm2calc()
        break

    install_flexiblesusy()

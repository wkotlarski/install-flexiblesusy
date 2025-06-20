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
depsPath = os.path.join(pathlib.Path(__file__).parent.resolve(), "FlexibleSUSY-deps")

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

eigenVersion = config["versions"]["Eigen"]
eigenPathInc = os.path.join(depsPath, f'eigen-{eigenVersion}', 'include', 'eigen3')
cmakeVersion = config["versions"]["cmake"]
boostVersion = config["versions"]["Boost"]

QUESTION = 'We recommend you install it using your linux disctibution package manager or I can try installing it from source'

def install_cmake():
    global cmakeVersion, tmpDir
    print('Installing CMake...')
    url = f'https://github.com/Kitware/CMake/releases/download/v{cmakeVersion}/cmake-{cmakeVersion}.tar.gz'
    urllib.request.urlretrieve(url, os.path.join(tmpDir, f'cmake-{cmakeVersion}.tar.gz'))
    subprocess.call(f'tar -xf cmake-{cmakeVersion}.tar.gz', cwd=tmpDir, shell=True)
    installPath = os.path.join(pathlib.Path(__file__).parent.resolve(), "FlexibleSUSY-deps", f'cmake-{cmakeVersion}')
    err = subprocess.run(f'./bootstrap --prefix={installPath} -- -DCMAKE_USE_OPENSSL=OFF && make && make install', cwd=os.path.join(tmpDir, f'cmake-{cmakeVersion}'), shell=True, capture_output=True)
    if err.returncode != 0:
        print(err.stderr)
        print('CMake installation failed')
        sys.exit()

def install_flexiblesusy(localBoost, localGSL, enableGM2Calc):
    global eigenPathInc, tmpDir
    fsVersion = config["versions"]["FlexibleSUSY"]
    fsDir = f'FlexibleSUSY-{fsVersion}'
    if not os.path.exists(fsDir):
        url = f'https://github.com/FlexibleSUSY/FlexibleSUSY/archive/refs/tags/v{fsVersion}.tar.gz'
        urllib.request.urlretrieve(url, os.path.join(tmpDir, f'FlexibleSUSY-{fsVersion}.tar.gz'))
        subprocess.call(f'tar -xf FlexibleSUSY-{fsVersion}.tar.gz -C {pathlib.Path(__file__).parent.resolve()}', cwd=tmpDir, shell=True)
    gm2cVersion = config["versions"]["GM2Calc"]
    boostVersion = config["versions"]["Boost"]
    depsPath = os.path.join(pathlib.Path(__file__).parent.resolve(), "FlexibleSUSY-deps")
    gm2Path = os.path.join(depsPath, f'GM2Calc-{gm2cVersion}')
    if os.path.isdir(os.path.join(gm2Path, 'lib')):
        gm2Pathlib = os.path.join(gm2Path, 'lib')
    elif os.path.isdir(os.path.join(gm2Path, 'lib64')):
        gm2Pathlib = os.path.join(gm2Path, 'lib64')
    gm2PathInc = os.path.join(gm2Path, 'include')

    boostConfig = ''
    if localBoost:
        boostPath = os.path.join(depsPath, f'boost-{boostVersion}')
        if os.path.isdir(os.path.join(boostPath, 'lib')):
            boostPathlib = os.path.join(boostPath, 'lib')
        elif os.path.isdir(os.path.join(boostPath, 'lib64')):
            boostPathlib = os.path.join(boostPath, 'lib64')
        boostPathlib = '--with-boost-libdir=' + boostPathlib
        boostPathInc = '--with-boost-incdir=' + os.path.join(boostPath, 'include')
        boostConfig = boostPathInc + ' ' + boostPathlib

    gslConfig = ''
    if localGSL:
        gslVersion = config["versions"]["GSL"]
        gslConfig = '--with-gm2calc-incdir=' + os.path.join(depsPath, f'gsl-{gslVersion}', 'bin', 'gsl-config')

    fsInstallPath = os.path.join(pathlib.Path(__file__).parent.resolve(), f'FlexibleSUSY-{fsVersion}')
    for m in sys.argv[1].split(','):
        subprocess.call(f'./createmodel -f --name={m}', cwd=fsInstallPath, shell=True)

    subprocess.call(f'./configure --with-models={sys.argv[1]} --with-gm2calc-libdir={gm2Pathlib} --with-gm2calc-incdir={gm2PathInc} --with-eigen-incdir={eigenPathInc} {boostConfig} {gslConfig}', cwd=fsInstallPath, shell=True)
    subprocess.call('make -j2', cwd=fsInstallPath, shell=True)

def install_gm2calc(localCMake, localBoost):
    global tmpDir, eigenPathInc, cmakeVersion, boostVersion
    gm2cVersion = config["versions"]["GM2Calc"]
    installPath = os.path.join(pathlib.Path(__file__).parent.resolve(), "FlexibleSUSY-deps", f'GM2Calc-{gm2cVersion}')
    if os.path.exists(installPath):
        print(f'GM2Calc seems to be already installed locally in {installPath}. ')
        while True:
            installGM2Calc = input('Do you want to reinstall it? [yes/no]: ')
            if installGM2Calc != "yes" and installGM2Calc != "no":
                print(f'please type yes or no (you typed {installGM2Calc})')
                continue
            if installGM2Calc == "yes":
                shutil.rmtree(installPath)
                break
            elif installGM2Calc == "no":
                return None
    print('Installing GM2Calc...')
    url = f'https://github.com/GM2Calc/GM2Calc/archive/refs/tags/v{gm2cVersion}.tar.gz'
    urllib.request.urlretrieve(url, os.path.join(tmpDir, f'GM2Calc-{gm2cVersion}.tar.gz'))
    subprocess.call(f'tar -xf GM2Calc-{gm2cVersion}.tar.gz', cwd=tmpDir, shell=True)
    os.makedirs(os.path.join(tmpDir, f'GM2Calc-{gm2cVersion}', 'build'))

    cmakeCMD = 'cmake'
    if localCMake:
        cmakeCMD = os.path.join(pathlib.Path(__file__).parent.resolve(), "FlexibleSUSY-deps", f'cmake-{cmakeVersion}', 'bin', 'cmake')

    boostFlag = ''
    if localBoost:
        boostFlag = '-DBOOST_ROOT=' + os.path.join(pathlib.Path(__file__).parent.resolve(), "FlexibleSUSY-deps", f'boost-{boostVersion}')

    err = subprocess.run(f'{cmakeCMD} .. -DCMAKE_INSTALL_PREFIX={installPath} -DCMAKE_POSITION_INDEPENDENT_CODE=On -DEigen3_DIR={eigenPathInc} {boostFlag} && make && make install', cwd=os.path.join(tmpDir, f'GM2Calc-{gm2cVersion}', 'build'), shell=True, capture_output=True)
    if err.returncode != 0:
        print(err.stderr)
        print('GM2Calc installation failed')
        sys.exit()


def install_eigen():
    global tmpDir
    print('Installing Eigen...')
    eigenVersion = config["versions"]["Eigen"]
    url = f'https://gitlab.com/libeigen/eigen/-/archive/{eigenVersion}/eigen-{eigenVersion}.tar.gz'
    urllib.request.urlretrieve(url, os.path.join(tmpDir, f'eigen-{eigenVersion}.tar.gz'))
    subprocess.call(f'tar -xf eigen-{eigenVersion}.tar.gz', cwd=tmpDir, shell=True)
    os.makedirs(os.path.join(tmpDir, f'eigen-{eigenVersion}', 'build'))
    installPath = os.path.join(pathlib.Path(__file__).parent.resolve(), "FlexibleSUSY-deps", f'eigen-{eigenVersion}')
    err = subprocess.run(f'cmake .. -DCMAKE_INSTALL_PREFIX={installPath} && make && make install', cwd=os.path.join(tmpDir, f'eigen-{eigenVersion}', 'build'), shell=True, capture_output=True)
    if err.returncode != 0:
        print(err.stderr)
        print('Eigen installation failed')
        sys.exit()

def install_boost():
    global tmpDir, boostVersion
    installPath = os.path.join(pathlib.Path(__file__).parent.resolve(), "FlexibleSUSY-deps", f'boost-{boostVersion}')
    if os.path.exists(installPath):
        print(f'Boost seems to be already installed locally in {installPath}. ')
        while True:
            installBoost = input('Do you want to reinstall it? [yes/no]: ')
            if installBoost != "yes" and installBoost != "no":
                print(f'please type yes or no (you typed {installBoost})')
                continue
            if installBoost == "yes":
                shutil.rmtree(installPath)
                break
            elif installBoost == "no":
                sys.exit()
    print('Installing Boost...')
    boostVersionDash = "_".join(boostVersion.split("."))
    url = f'https://archives.boost.io/release/{boostVersion}/source/boost_{boostVersionDash}.tar.gz'
    urllib.request.urlretrieve(url, os.path.join(tmpDir, f'boost_{boostVersionDash}.tar.gz'))
    subprocess.call(f'tar -xf boost_{boostVersionDash}.tar.gz', cwd=tmpDir, shell=True)
    err = subprocess.run(f'./bootstrap.sh && ./b2 install --prefix={installPath}', shell=True, cwd=os.path.join(tmpDir, f'boost_{boostVersionDash}'), capture_output=True)
    if err.returncode != 0:
        print(err.stderr)
        print('Boost installation failed')
        sys.exit()

def install_gsl():
    global tmpDir
    print('Installing GSL...')
    gslVersion = config["versions"]["GSL"]
    url = f'https://mirror.ibcp.fr/pub/gnu/gsl/gsl-{gslVersion}.tar.gz'
    urllib.request.urlretrieve(url, os.path.join(tmpDir, f'gsl-{gslVersion}.tar.gz'))
    subprocess.call(f'tar -xf gsl-{gslVersion}.tar.gz', cwd=tmpDir, shell=True)
    installPath = os.path.join(pathlib.Path(__file__).parent.resolve(), "FlexibleSUSY-deps", f'gsl-{gslVersion}')
    err = subprocess.run(f'./configure --prefix={installPath} && make && make install', shell=True, cwd=os.path.join(tmpDir, f'gsl-{gslVersion}'), capture_output=True)
    if err.returncode != 0:
        print(err.stderr)
        print('GSL installation failed')
        sys.exit()

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

    distroString = subprocess.run(['cat /etc/*-release'], shell=True, capture_output=True).stdout.decode()
    if re.search('ubuntu', distroString, re.IGNORECASE):
        distro = 'ubuntu'
    elif re.search('opensuse', distroString, re.IGNORECASE):
        distro = 'opensuse'
    else:
        disto = 'unknown'

    if check_cxx() == None:
        print('\nThis script requires at least a C++ compiler')
        if distro == 'ubuntu':
            print('You seem to be on Ubuntu. You can try running sudo apt install g++')
        elif disto == 'opensuse':
            print('You seem to be on openSUSE. You can try running sudo zypper in gcc-c++')
        print('\nPlease install the compiler using your linux distribution package manager and re-run this script')
        sys.exit()

    localGSL = False
    if shutil.which('gsl-config') == None:
        print("FlexibleSUSY requires a GNU scientific library which doesn't seem to be installed on this system")
        print("We recommend you install it using your linux disctibution package manager or I can try installing it from source")
        while True:
            installGSL = input('Install GSL from source? [yes/no]: ')
            if installGSL != "yes" and installGSL != "no":
                print(f'please type yes or no (you typed {installGSL})')
                continue
            if installGSL:
                localGSL = True
                install_gsl()
            break

    install_eigen()

    localBoost = False
    runBoostTest = subprocess.run(['g++', f'-o{os.path.join(tmpDir, "boost_test")}', os.path.join('test', 'boost.cpp')], capture_output=True)
    if runBoostTest.returncode != 0:
        print("FlexibleSUSY and some of the dependencies require boost which doesn't seem to be installed on this system")
        print("We recommend you install it using your linux disctibution package manager or I can try installing it from source")
        while True:
            installBoost = input('Install Boost from source? [yes/no]: ')
            if installBoost != "yes" and installBoost != "no":
                print(f'please type yes or no (you typed {installBoost})')
                continue
            if installBoost:
                localBoost = True
                install_boost()
            break

    localCMake = False
    if shutil.which("cmake") == None:
        print('cmake not found in path')
        print(QUESTION)
        while True:
            installCMake = input('Install CMake from source? [yes/no]: ')
            if installCMake != "yes" and installCMake != "no":
                print(f'please type yes or no (you typed {installCMake})')
                continue
            if installCMake:
                localCMake = True
                install_cmake()
            break

    enableGM2Calc = False
    while True:
        installGM2Calc = input('Install GM2Calc? [yes/no]: ')
        if installGM2Calc != "yes" and installGM2Calc != "no":
            print(f'please type yes or no (you typed {installGM2Calc}')
            continue
        if installGM2Calc:
            install_gm2calc(localCMake, localBoost)
            enableGM2Calc = True
        break

    install_flexiblesusy(localBoost, localGSL, enableGM2Calc)

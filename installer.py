#!/usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess, os, random, string, sys, shutil, socket, zipfile, urllib.request, urllib.error, urllib.parse, json, base64, time
from itertools import cycle
from zipfile import ZipFile
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Configurări pentru nginx 1.26
NGINX_VERSION = "1.26.2"
PHP_VERSION = "8.3"

rDownloadURL = {"main": "https://github.com/sabiralipsl/Xtream-UI-R22F-ubuntu20.04lts-2025/releases/download/xtream1/main_xui_xoceunder.zip", "sub": "https://github.com/sabiralipsl/Xtream-UI-R22F-ubuntu20.04lts-2025/releases/download/xtream1/sub_xui_xoceunder.zip"}

# Adăugăm pachete pentru compilarea nginx
rPackages = ["libcurl4", "libxslt1-dev", "libgeoip-dev", "libonig-dev", "e2fsprogs", "wget", "mcrypt", "nscd", "htop", "zip", "unzip", "mc", "mariadb-server", "libpng16-16", "libzip5", "python3-paramiko", "python-is-python3", "build-essential", "gcc", "make", "git", "curl", "software-properties-common", "libpcre3-dev", "libssl-dev", "zlib1g-dev", "libxml2-dev", "pkg-config", "libgd-dev", "ca-certificates", "gnupg", "lsb-release"]

rInstall = {"MAIN": "main", "LB": "sub"}
rUpdate = {"UPDATE": "update"}
rMySQLCnf = base64.b64decode("IyBYdHJlYW0gQ29kZXMKCltjbGllbnRdCnBvcnQgICAgICAgICAgICA9IDMzMDYKCltteXNxbGRfc2FmZV0KbmljZSAgICAgICAgICAgID0gMAoKW215c3FsZF0KdXNlciAgICAgICAgICAgID0gbXlzcWwKcG9ydCAgICAgICAgICAgID0gNzk5OQpiYXNlZGlyICAgICAgICAgPSAvdXNyCmRhdGFkaXIgICAgICAgICA9IC92YXIvbGliL215c3FsCnRtcGRpciAgICAgICAgICA9IC90bXAKbGMtbWVzc2FnZXMtZGlyID0gL3Vzci9zaGFyZS9teXNxbApza2lwLWV4dGVybmFsLWxvY2tpbmcKc2tpcC1uYW1lLXJlc29sdmU9MQoKYmluZC1hZGRyZXNzICAgICAgICAgICAgPSAqCmtleV9idWZmZXJfc2l6ZSA9IDEyOE0KCm15aXNhbV9zb3J0X2J1ZmZlcl9zaXplID0gNE0KbWF4X2FsbG93ZWRfcGFja2V0ICAgICAgPSA2NE0KbXlpc2FtLXJlY292ZXItb3B0aW9ucyA9IEJBQ0tVUAptYXhfbGVuZ3RoX2Zvcl9zb3J0X2RhdGEgPSA4MTkyCnF1ZXJ5X2NhY2hlX2xpbWl0ICAgICAgID0gNE0KcXVlcnlfY2FjaGVfc2l6ZSAgICAgICAgPSAwCnF1ZXJ5X2NhY2hlX3R5cGUJPSAwCgpleHBpcmVfbG9nc19kYXlzICAgICAgICA9IDEwCm1heF9iaW5sb2dfc2l6ZSAgICAgICAgID0gMTAwTQoKbWF4X2Nvbm5lY3Rpb25zICA9IDIwMDAgI3JlY29tbWVuZGVkIGZvciAxNkdCIHJhbSAKYmFja19sb2cgPSA0MDk2Cm9wZW5fZmlsZXNfbGltaXQgPSAxNjM4NAppbm5vZGJfb3Blbl9maWxlcyA9IDE2Mzg0Cm1heF9jb25uZWN0X2Vycm9ycyA9IDMwNzIKdGFibGVfb3Blbl9jYWNoZSA9IDQwOTYKdGFibGVfZGVmaW5pdGlvbl9jYWNoZSA9IDQwOTYKCgp0bXBfdGFibGVfc2l6ZSA9IDFHCm1heF9oZWFwX3RhYmxlX3NpemUgPSAxRwoKaW5ub2RiX2J1ZmZlcl9wb29sX3NpemUgPSAxMkcgI3JlY29tbWVuZGVkIGZvciAxNkdCIHJhbQppbm5vZGJfYnVmZmVyX3Bvb2xfaW5zdGFuY2VzID0gMQppbm5vZGJfcmVhZF9pb190aHJlYWRzID0gNjQKaW5ub2RiX3dyaXRlX2lvX3RocmVhZHMgPSA2NAppbm5vZGJfdGhyZWFkX2NvbmN1cnJlbmN5ID0gMAppbm5vZGJfZmx1c2hfbG9nX2F0X3RyeF9jb21taXQgPSAwCmlubm9kYl9mbHVzaF9tZXRob2QgPSBPX0RJUkVDVApwZXJmb3JtYW5jZV9zY2hlbWEgPSBPTgppbm5vZGItZmlsZS1wZXItdGFibGUgPSAxCmlubm9kYl9pb19jYXBhY2l0eT0yMDAwMAppbm5vZGJfdGFibGVfbG9ja3MgPSAwCmlubm9kYl9sb2NrX3dhaXRfdGltZW91dCA9IDAKaW5ub2RiX2RlYWRsb2NrX2RldGVjdCA9IDAKaW5ub2RiX2xvZ19maWxlX3NpemUgPSA1MTJNCgpzcWwtbW9kZT0iTk9fRU5HSU5FX1NVQlNUSVRVVElPTiIKCltteXNxbGR1bXBdCnF1aWNrCnF1b3RlLW5hbWVzCm1heF9hbGxvd2VkX3BhY2tldCAgICAgID0gMTZNCgpbbXlzcWxdCgpbaXNhbWNoa10Ka2V5X2J1ZmZlcl9zaXplICAgICAgICAgICAgICA9IDE2TQo=")

rVersions = {
    "20.04": "focal",
    "22.04": "jammy", 
    "24.04": "noble"
}

class col:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m' # orange on some systems
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    LIGHT_GRAY = '\033[37m'
    DARK_GRAY = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

def generate(length=19): return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def getVersion():
    try: return os.popen("lsb_release -d").read().split(":")[-1].strip()
    except: return ""

def getCPUCount():
    try: return int(os.popen("nproc").read().strip())
    except: return 2

def printc(rText, rColour=col.BRIGHT_GREEN, rPadding=0, rLimit=46):
    print("%s ┌─────────────────────────────────────────────────┐ %s" % (rColour, col.ENDC))
    for i in range(rPadding): print("%s │                                                 │ %s" % (rColour, col.ENDC))
    array = [rText[i:i+rLimit] for i in range(0, len(rText), rLimit)]
    for i in array : print("%s │ %s%s%s │ %s" % (rColour, " "*round(23-(len(i)/2)), i, " "*round(46-(22-(len(i)/2))-len(i)), col.ENDC))
    for i in range(rPadding): print("%s │                                                 │ %s" % (rColour, col.ENDC))
    print("%s └─────────────────────────────────────────────────┘ %s" % (rColour, col.ENDC))
    print(" ")

def compile_nginx():
    """Compilează nginx 1.26 cu RTMP module"""
    printc("Compiling nginx %s with RTMP module" % NGINX_VERSION)
    
    # Creează directorul de build
    build_dir = "/tmp/nginx_build"
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    
    # Download nginx source
    nginx_url = f"http://nginx.org/download/nginx-{NGINX_VERSION}.tar.gz"
    os.system(f'cd {build_dir} && wget -q "{nginx_url}"')
    if not os.path.exists(f"{build_dir}/nginx-{NGINX_VERSION}.tar.gz"):
        printc("Failed to download nginx source", col.BRIGHT_RED)
        return False
    
    # Extract nginx
    os.system(f'cd {build_dir} && tar -xzf nginx-{NGINX_VERSION}.tar.gz')
    nginx_src = f"{build_dir}/nginx-{NGINX_VERSION}"
    
    # Download RTMP module
    os.system(f'cd {nginx_src} && git clone --depth 1 https://github.com/arut/nginx-rtmp-module.git')
    
    # Configurează nginx pentru main server
    printc("Configuring main nginx")
    main_config = [
        f"--prefix=/home/xtreamcodes/iptv_xtream_codes/nginx/",
        "--with-http_ssl_module",
        "--with-http_realip_module", 
        "--with-http_flv_module",
        "--with-http_mp4_module",
        "--with-http_secure_link_module",
        "--with-http_v2_module",
        "--with-http_gzip_static_module"
    ]
    
    config_cmd = f'cd {nginx_src} && ./configure {" ".join(main_config)}'
    if os.system(config_cmd + " > /dev/null 2>&1") != 0:
        printc("nginx main configuration failed", col.BRIGHT_RED)
        return False
    
    # Compilează main nginx
    printc("Compiling main nginx (this may take a few minutes)")
    cpu_count = getCPUCount()
    if os.system(f'cd {nginx_src} && make -j{cpu_count} > /dev/null 2>&1') != 0:
        printc("nginx main compilation failed", col.BRIGHT_RED)
        return False
    
    # Salvează main nginx binary
    main_binary = f"{nginx_src}/objs/nginx"
    main_backup = "/tmp/nginx_main_backup"
    if os.path.exists(main_binary):
        shutil.copy(main_binary, main_backup)
    else:
        printc("Main nginx binary not found", col.BRIGHT_RED)
        return False
    
    # Clean pentru RTMP nginx
    os.system(f'cd {nginx_src} && make clean > /dev/null 2>&1')
    
    # Configurează nginx pentru RTMP
    printc("Configuring RTMP nginx")
    rtmp_config = [
        f"--prefix=/home/xtreamcodes/iptv_xtream_codes/nginx_rtmp/",
        "--add-module=./nginx-rtmp-module",
        "--with-pcre"
    ]
    
    config_cmd = f'cd {nginx_src} && ./configure {" ".join(rtmp_config)}'
    if os.system(config_cmd + " > /dev/null 2>&1") != 0:
        printc("nginx RTMP configuration failed", col.BRIGHT_RED)
        return False
    
    # Compilează RTMP nginx  
    printc("Compiling RTMP nginx")
    if os.system(f'cd {nginx_src} && make -j{cpu_count} > /dev/null 2>&1') != 0:
        printc("nginx RTMP compilation failed", col.BRIGHT_RED)
        return False
    
    # Salvează RTMP nginx binary
    rtmp_binary = f"{nginx_src}/objs/nginx"
    rtmp_backup = "/tmp/nginx_rtmp_backup"
    if os.path.exists(rtmp_binary):
        shutil.copy(rtmp_binary, rtmp_backup)
    else:
        printc("RTMP nginx binary not found", col.BRIGHT_RED)
        return False
    
    printc("nginx compilation completed successfully")
    
    # Cleanup build directory
    try:
        shutil.rmtree(build_dir)
    except:
        pass
        
    return True

def install_compiled_nginx():
    """Instalează nginx-urile compilate peste cele din pachet"""
    printc("Installing compiled nginx binaries")
    
    # Creează directoarele necesare
    nginx_dirs = [
        "/home/xtreamcodes/iptv_xtream_codes/nginx/sbin",
        "/home/xtreamcodes/iptv_xtream_codes/nginx_rtmp/sbin"
    ]
    
    for dir_path in nginx_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    # Instalează main nginx
    main_backup = "/tmp/nginx_main_backup"
    if os.path.exists(main_backup):
        target_main = "/home/xtreamcodes/iptv_xtream_codes/nginx/sbin/nginx"
        shutil.copy(main_backup, target_main)
        os.chmod(target_main, 0o755)
        printc("Main nginx binary installed")
    else:
        printc("Main nginx backup not found", col.BRIGHT_RED)
        return False
    
    # Instalează RTMP nginx
    rtmp_backup = "/tmp/nginx_rtmp_backup"
    if os.path.exists(rtmp_backup):
        target_rtmp = "/home/xtreamcodes/iptv_xtream_codes/nginx_rtmp/sbin/nginx_rtmp"
        shutil.copy(rtmp_backup, target_rtmp)
        os.chmod(target_rtmp, 0o755)
        printc("RTMP nginx binary installed")
    else:
        printc("RTMP nginx backup not found", col.BRIGHT_RED)
        return False
    
    # Cleanup backup files
    try:
        os.remove(main_backup)
        os.remove(rtmp_backup)
    except:
        pass
    
    # Verifică instalarea
    main_test = os.system("/home/xtreamcodes/iptv_xtream_codes/nginx/sbin/nginx -v > /dev/null 2>&1")
    if main_test == 0:
        printc("nginx binaries installed successfully")
        return True
    else:
        printc("nginx binary verification failed", col.BRIGHT_RED)
        return False

def install_ioncube():
    """Instalează ionCube Loader pentru PHP"""
    printc("Installing ionCube Loader")
    
    # Detectează versiunea PHP
    try:
        php_version_output = os.popen("php -v").read()
        if "PHP 8.1" in php_version_output:
            ioncube_file = "ioncube_loader_lin_8.1.so"
        elif "PHP 8.0" in php_version_output:
            ioncube_file = "ioncube_loader_lin_8.0.so"
        elif "PHP 7.4" in php_version_output:
            ioncube_file = "ioncube_loader_lin_7.4.so"
        else:
            ioncube_file = "ioncube_loader_lin_8.1.so"  # default
    except:
        ioncube_file = "ioncube_loader_lin_8.1.so"
    
    # Găsește directorul de extensii PHP
    try:
        ext_dir = os.popen("php -i | grep extension_dir | head -1").read().split("=>")[-1].strip()
        if not ext_dir or not os.path.exists(ext_dir):
            ext_dir = "/usr/lib/php/20210902"  # fallback pentru PHP 8.1
    except:
        ext_dir = "/usr/lib/php/20210902"
    
    # Creează directorul dacă nu există
    os.makedirs(ext_dir, exist_ok=True)
    
    # Download și instalează ionCube
    temp_dir = "/tmp/ioncube_install"
    os.makedirs(temp_dir, exist_ok=True)
    
    ioncube_url = "https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz"
    
    if os.system(f'cd {temp_dir} && wget -q "{ioncube_url}"') == 0:
        if os.system(f'cd {temp_dir} && tar -xzf ioncube_loaders_lin_x86-64.tar.gz') == 0:
            ioncube_path = f"{temp_dir}/ioncube/{ioncube_file}"
            if os.path.exists(ioncube_path):
                target_path = f"{ext_dir}/{ioncube_file}"
                shutil.copy(ioncube_path, target_path)
                os.chmod(target_path, 0o755)
                
                # Adaugă ionCube în php.ini
                try:
                    # Găsește php.ini
                    php_ini_path = os.popen("php --ini | grep 'Loaded Configuration File'").read().split(":")[-1].strip()
                    if php_ini_path and os.path.exists(php_ini_path):
                        with open(php_ini_path, "r") as f:
                            ini_content = f.read()
                        
                        if "ioncube_loader" not in ini_content:
                            with open(php_ini_path, "a") as f:
                                f.write(f"\n; ionCube Loader\nzend_extension = {target_path}\n")
                            printc("ionCube Loader configured successfully")
                        else:
                            printc("ionCube already configured")
                    else:
                        printc("Could not find php.ini file", col.BRIGHT_YELLOW)
                except Exception as e:
                    printc(f"Warning: Could not configure ionCube in php.ini: {e}", col.BRIGHT_YELLOW)
                
                # Cleanup
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
                
                return True
            else:
                printc(f"ionCube file {ioncube_file} not found", col.BRIGHT_RED)
        else:
            printc("Failed to extract ionCube archive", col.BRIGHT_RED)
    else:
        printc("Failed to download ionCube", col.BRIGHT_RED)
    
    # Cleanup on failure
    try:
        shutil.rmtree(temp_dir)
    except:
        pass
    
    return False

def prepare(rType="MAIN"):
    global rPackages
    if rType != "MAIN": rPackages = rPackages[:-1]
    printc("Preparing Installation")
    if os.path.isfile('/home/xtreamcodes/iptv_xtream_codes/config'):
        shutil.copyfile('/home/xtreamcodes/iptv_xtream_codes/config', '/tmp/config.xtmp')
    if os.path.isfile('/home/xtreamcodes/iptv_xtream_codes/config'):    
        os.system('chattr -i /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb > /dev/null')
    for rFile in ["/var/lib/dpkg/lock-frontend", "/var/cache/apt/archives/lock", "/var/lib/dpkg/lock"]:
        try: os.remove(rFile)
        except: pass
    printc("Updating Operating System")
    os.system("apt-get update > /dev/null")
    os.system("apt-get -y full-upgrade > /dev/null")
    if rType == "MAIN":
        printc("Install MariaDB 10.5 repository")
        os.system("apt-get install -y software-properties-common > /dev/null")
        os.system("apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8 >/dev/null 2>&1")
        os.system("add-apt-repository 'deb [arch=amd64,arm64,ppc64el] http://mirror.lstn.net/mariadb/repo/10.5/ubuntu focal main'  > /dev/null")
        os.system("apt-get update > /dev/null")
    for rPackage in rPackages:
        printc("Installing %s" % rPackage)
        os.system("apt-get install %s -y > /dev/null" % rPackage)
    printc("Installing pip2 and python2 paramiko")
    os.system("add-apt-repository universe > /dev/null 2>&1 && curl https://github.com/sabiralipsl/Xtream-UI-R22F-ubuntu20.04lts-2025/releases/download/xtream1/get-pip.py --output get-pip.py > /dev/null 2>&1 && python2 get-pip.py > /dev/null 2>&1 && pip2 install paramiko > /dev/null 2>&1")
    os.system("apt-get install -f > /dev/null") # Clean up above
    
    # Instalează ionCube Loader
    install_ioncube()
    
    try:
        subprocess.check_output("getent passwd xtreamcodes > /dev/null".split())
    except:
        # Create User
        printc("Creating user xtreamcodes")
        os.system("adduser --system --shell /bin/false --group --disabled-login xtreamcodes > /dev/null")
    if not os.path.exists("/home/xtreamcodes"): os.mkdir("/home/xtreamcodes")
    return True

def install(rType="MAIN"):
    global rInstall, rDownloadURL
    
    # Compilează nginx înainte de instalarea software-ului
    if rType == "MAIN":
        if not compile_nginx():
            printc("nginx compilation failed", col.BRIGHT_RED)
            return False
    
    printc("Downloading Software")
    try: rURL = rDownloadURL[rInstall[rType]]
    except:
        printc("Invalid download URL!", col.BRIGHT_RED)
        return False
    os.system('wget -q -O "/tmp/xtreamcodes.zip" "%s"' % rURL)
    if os.path.exists("/tmp/xtreamcodes.zip"):
        printc("Installing Software")
        os.system('unzip "/tmp/xtreamcodes.zip" -d "/home/xtreamcodes/" > /dev/null')
        
        # Instalează nginx-urile compilate peste cele din pachet
        if rType == "MAIN":
            if not install_compiled_nginx():
                printc("Failed to install compiled nginx", col.BRIGHT_RED)
                return False
        
        try: os.remove("/tmp/xtreamcodes.zip")
        except: pass
        return True
    printc("Failed to download installation file!", col.BRIGHT_RED)
    return False
    
def update(rType="MAIN"):
    if rType == "UPDATE":
        printc("Enter the link of release_xyz.zip file:", col.BRIGHT_RED)
        rlink = input('Example: https://github.com/sabiralipsl/Xtream-UI-R22F-ubuntu20.04lts-2025/releases/download/xtream1/release_22f.zip\n\nNow enter the link:\n\n')
    else:
        rlink = "https://github.com/sabiralipsl/Xtream-UI-R22F-ubuntu20.04lts-2025/releases/download/xtream1/release_22f.zip"
        printc("Downloading Software Update")  
    os.system('wget -q -O "/tmp/update.zip" "%s"' % rlink)
    if os.path.exists("/tmp/update.zip"):
        try: is_ok = zipfile.ZipFile("/tmp/update.zip")
        except:
            printc("Invalid link or zip file is corrupted!", col.BRIGHT_RED)
            os.remove("/tmp/update.zip")
            return False
    rURL = rlink
    printc("Installing Admin Panel")
    if os.path.exists("/tmp/update.zip"):
        try: is_ok = zipfile.ZipFile("/tmp/update.zip")
        except:
            printc("Invalid link or zip file is corrupted!", col.BRIGHT_RED)
            os.remove("/tmp/update.zip")
            return False
        
        # Backup nginx binaries before update
        backup_files = {}
        nginx_files = {
            "main": "/home/xtreamcodes/iptv_xtream_codes/nginx/sbin/nginx",
            "rtmp": "/home/xtreamcodes/iptv_xtream_codes/nginx_rtmp/sbin/nginx_rtmp"
        }
        
        for name, path in nginx_files.items():
            if os.path.exists(path):
                backup_path = f"/tmp/{name}_nginx_update_backup"
                shutil.copy(path, backup_path)
                backup_files[name] = backup_path
        
        printc("Updating Software")
        os.system('chattr -i /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb > /dev/null && rm -rf /home/xtreamcodes/iptv_xtream_codes/admin > /dev/null && rm -rf /home/xtreamcodes/iptv_xtream_codes/pytools > /dev/null && unzip /tmp/update.zip -d /tmp/update/ > /dev/null && cp -rf /tmp/update/XtreamUI-master/* /home/xtreamcodes/iptv_xtream_codes/ > /dev/null && rm -rf /tmp/update/XtreamUI-master > /dev/null && rm -rf /tmp/update > /dev/null && chown -R xtreamcodes:xtreamcodes /home/xtreamcodes/ > /dev/null && chmod +x /home/xtreamcodes/iptv_xtream_codes/permissions.sh > /dev/null && chattr +i /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb > /dev/null')
        
        # Restore compiled nginx binaries
        for name, backup_path in backup_files.items():
            target_path = nginx_files[name]
            if os.path.exists(backup_path):
                shutil.copy(backup_path, target_path)
                os.chmod(target_path, 0o755)
                os.remove(backup_path)
                printc(f"Restored compiled {name} nginx binary")
        
        if not "sudo chmod 400 /home/xtreamcodes/iptv_xtream_codes/config" in open("/home/xtreamcodes/iptv_xtream_codes/permissions.sh").read(): os.system('echo "#!/bin/bash\nsudo chmod -R 777 /home/xtreamcodes 2>/dev/null\nsudo find /home/xtreamcodes/iptv_xtream_codes/admin/ -type f -exec chmod 644 {} \; 2>/dev/null\nsudo find /home/xtreamcodes/iptv_xtream_codes/admin/ -type d -exec chmod 755 {} \; 2>/dev/null\nsudo find /home/xtreamcodes/iptv_xtream_codes/wwwdir/ -type f -exec chmod 644 {} \; 2>/dev/null\nsudo find /home/xtreamcodes/iptv_xtream_codes/wwwdir/ -type d -exec chmod 755 {} \; 2>/dev/null\nsudo chmod +x /home/xtreamcodes/iptv_xtream_codes/nginx/sbin/nginx 2>/dev/null\nsudo chmod +x /home/xtreamcodes/iptv_xtream_codes/nginx_rtmp/sbin/nginx_rtmp 2>/dev/null\nsudo chmod 400 /home/xtreamcodes/iptv_xtream_codes/config 2>/dev/null" > /home/xtreamcodes/iptv_xtream_codes/permissions.sh')
        os.system("/home/xtreamcodes/iptv_xtream_codes/permissions.sh > /dev/null")
        try: os.remove("/tmp/update.zip")
        except: pass
        return True
    printc("Failed to download installation file!", col.BRIGHT_RED)
    return False

def mysql(rUsername, rPassword):
    global rMySQLCnf
    printc("Configuring MySQL")
    rCreate = True
    if os.path.exists("/etc/mysql/my.cnf"):
        if open("/etc/mysql/my.cnf", "r").read(14) == "# Xtream Codes": rCreate = False
    if rCreate:
        shutil.copy("/etc/mysql/my.cnf", "/etc/mysql/my.cnf.xc")
        rFile = open("/etc/mysql/my.cnf", "wb")
        rFile.write(rMySQLCnf)
        rFile.close()
        os.system("systemctl restart mariadb > /dev/null")
    #printc("Enter MySQL Root Password:", col.BRIGHT_RED)
    for i in range(5):
        rMySQLRoot = "" #raw_input("  ")
        print(" ")
        if len(rMySQLRoot) > 0: rExtra = " -p%s" % rMySQLRoot
        else: rExtra = ""
        rDrop = True
        try:
            if rDrop:
                os.system('mysql -u root%s -e "DROP DATABASE IF EXISTS xtream_iptvpro; CREATE DATABASE IF NOT EXISTS xtream_iptvpro;" > /dev/null' % rExtra)
                os.system('mysql -u root%s -e "USE xtream_iptvpro; DROP USER IF EXISTS \'%s\'@\'%%\';" > /dev/null' % (rExtra, rUsername))
                os.system("mysql -u root%s xtream_iptvpro < /home/xtreamcodes/iptv_xtream_codes/database.sql > /dev/null" % rExtra)
                os.system('mysql -u root%s -e "USE xtream_iptvpro; UPDATE settings SET live_streaming_pass = \'%s\', unique_id = \'%s\', crypt_load_balancing = \'%s\';" > /dev/null' % (rExtra, generate(20), generate(10), generate(20)))
                os.system('mysql -u root%s -e "USE xtream_iptvpro; REPLACE INTO streaming_servers (id, server_name, domain_name, server_ip, vpn_ip, ssh_password, ssh_port, diff_time_main, http_broadcast_port, total_clients, system_os, network_interface, latency, status, enable_geoip, geoip_countries, last_check_ago, can_delete, server_hardware, total_services, persistent_connections, rtmp_port, geoip_type, isp_names, isp_type, enable_isp, boost_fpm, http_ports_add, network_guaranteed_speed, https_broadcast_port, https_ports_add, whitelist_ips, watchdog_data, timeshift_only) VALUES (1, \'Main Server\', \'\', \'%s\', \'\', NULL, NULL, 0, 25461, 1000, \'%s\', \'eth0\', 0, 1, 0, \'\', 0, 0, \'{}\', 3, 0, 25462, \'low_priority\', \'\', \'low_priority\', 0, 1, \'\', 1000, 25463, \'\', \'[\"127.0.0.1\",\"\"]\', \'{}\', 0);" > /dev/null' % (rExtra, getIP(), getVersion()))
                os.system('mysql -u root%s -e "USE xtream_iptvpro; REPLACE INTO reg_users (id, username, password, email, member_group_id, verified, status) VALUES (1, \'admin\', \'\$6\$rounds=20000\$xtreamcodes\$XThC5OwfuS0YwS4ahiifzF14vkGbGsFF1w7ETL4sRRC5sOrAWCjWvQJDromZUQoQuwbAXAFdX3h3Cp3vqulpS0\', \'admin@website.com\', 1, 1, 1);" > /dev/null'  % rExtra)
                os.system('mysql -u root%s -e "CREATE USER \'%s\'@\'%%\' IDENTIFIED BY \'%s\'; GRANT ALL PRIVILEGES ON xtream_iptvpro.* TO \'%s\'@\'%%\' WITH GRANT OPTION; GRANT SELECT, LOCK TABLES ON *.* TO \'%s\'@\'%%\';FLUSH PRIVILEGES;" > /dev/null' % (rExtra, rUsername, rPassword, rUsername, rUsername))
                os.system('mysql -u root%s -e "USE xtream_iptvpro; CREATE TABLE IF NOT EXISTS dashboard_statistics (id int(11) NOT NULL AUTO_INCREMENT, type varchar(16) NOT NULL DEFAULT \'\', time int(16) NOT NULL DEFAULT \'0\', count int(16) NOT NULL DEFAULT \'0\', PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1; INSERT INTO dashboard_statistics (type, time, count) VALUES(\'conns\', UNIX_TIMESTAMP(), 0),(\'users\', UNIX_TIMESTAMP(), 0);\" > /dev/null' % rExtra)
            try: os.remove("/home/xtreamcodes/iptv_xtream_codes/database.sql")
            except: pass
            return True
        except: printc("Invalid password! Try again", col.BRIGHT_RED)
    return False

def encrypt(rHost="127.0.0.1", rUsername="user_iptvpro", rPassword="", rDatabase="xtream_iptvpro", rServerID=1, rPort=7999):
    if os.path.isfile('/home/xtreamcodes/iptv_xtream_codes/config'):
        rDecrypt = decrypt()
        rHost = rDecrypt["host"]
        rPassword = rDecrypt["db_pass"]
        rServerID = int(rDecrypt["server_id"])
        rUsername = rDecrypt["db_user"]
        rDatabase = rDecrypt["db_name"]
        rPort = int(rDecrypt["db_port"])
    printc("Encrypting...")
    try: os.remove("/home/xtreamcodes/iptv_xtream_codes/config")
    except: pass

    rf = open('/home/xtreamcodes/iptv_xtream_codes/config', 'wb')
    lestring=''.join(chr(ord(c)^ord(k)) for c,k in zip('{\"host\":\"%s\",\"db_user\":\"%s\",\"db_pass\":\"%s\",\"db_name\":\"%s\",\"server_id\":\"%d\", \"db_port\":\"%d\"}' % (rHost, rUsername, rPassword, rDatabase, rServerID, rPort), cycle('5709650b0d7806074842c6de575025b1')))
    rf.write(base64.b64encode(bytes(lestring, 'ascii')))
    rf.close()


def decrypt():
    rConfigPath = "/home/xtreamcodes/iptv_xtream_codes/config"
    try: return json.loads(''.join(chr(c^ord(k)) for c,k in zip(base64.b64decode(open(rConfigPath, 'rb').read()), cycle('5709650b0d7806074842c6de575025b1'))))
    except: return None

def configure():
    printc("Configuring System")
    if not "/home/xtreamcodes/iptv_xtream_codes/" in open("/etc/fstab").read():
        rFile = open("/etc/fstab", "a")
        rFile.write("tmpfs /home/xtreamcodes/iptv_xtream_codes/streams tmpfs defaults,noatime,nosuid,nodev,noexec,mode=1777,size=90% 0 0\ntmpfs /home/xtreamcodes/iptv_xtream_codes/tmp tmpfs defaults,noatime,nosuid,nodev,noexec,mode=1777,size=2G 0 0")
        rFile.close()
    if not "xtreamcodes" in open("/etc/sudoers").read():
        os.system('echo "xtreamcodes ALL = (root) NOPASSWD: /sbin/iptables, /usr/bin/chattr" >> /etc/sudoers')
    if not os.path.exists("/etc/init.d/xtreamcodes"):
        rFile = open("/etc/init.d/xtreamcodes", "w")
        rFile.write("#! /bin/bash\n/home/xtreamcodes/iptv_xtream_codes/start_services.sh")
        rFile.close()
        os.system("chmod +x /etc/init.d/xtreamcodes > /dev/null")
    try: os.remove("/usr/bin/ffmpeg")
    except: pass
    if not os.path.exists("/home/xtreamcodes/iptv_xtream_codes/tv_archive"): os.mkdir("/home/xtreamcodes/iptv_xtream_codes/tv_archive/")
    os.system("ln -s /home/xtreamcodes/iptv_xtream_codes/bin/ffmpeg /usr/bin/")
    if not os.path.exists("/home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb"): os.system("wget -q https://github.com/sabiralipsl/Xtream-UI-R22F-ubuntu20.04lts-2025/releases/download/xtream1/GeoLite2.mmdb -O /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb")
    if not os.path.exists("/home/xtreamcodes/iptv_xtream_codes/crons/pid_monitor.php"): os.system("wget -q https://github.com/sabiralipsl/Xtream-UI-R22F-ubuntu20.04lts-2025/releases/download/xtream1/pid_monitor.php -O /home/xtreamcodes/iptv_xtream_codes/crons/pid_monitor.php")
    os.system("chown xtreamcodes:xtreamcodes -R /home/xtreamcodes > /dev/null")
    os.system("chmod -R 0777 /home/xtreamcodes > /dev/null")
    os.system("chattr -ai /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb > /dev/null")
    os.system("sudo chmod 0777 /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb > /dev/null")
    os.system("sed -i 's|chown -R xtreamcodes:xtreamcodes /home/xtreamcodes|chown -R xtreamcodes:xtreamcodes /home/xtreamcodes 2>/dev/null|g' /home/xtreamcodes/iptv_xtream_codes/start_services.sh")
    os.system("chmod +x /home/xtreamcodes/iptv_xtream_codes/start_services.sh > /dev/null")
    os.system("mount -a")
    os.system("chmod 0700 /home/xtreamcodes/iptv_xtream_codes/config > /dev/null")
    os.system("sed -i 's|echo \"Xtream Codes Reborn\";|header(\"Location: https://www.google.com/\");|g' /home/xtreamcodes/iptv_xtream_codes/wwwdir/index.php")
    if not "api.xtream-codes.com" in open("/etc/hosts").read(): os.system('echo "127.0.0.1    api.xtream-codes.com" >> /etc/hosts')
    if not "downloads.xtream-codes.com" in open("/etc/hosts").read(): os.system('echo "127.0.0.1    downloads.xtream-codes.com" >> /etc/hosts')
    if not "xtream-codes.com" in open("/etc/hosts").read(): os.system('echo "127.0.0.1    xtream-codes.com" >> /etc/hosts')
    if not "@reboot root /home/xtreamcodes/iptv_xtream_codes/start_services.sh" in open("/etc/crontab").read(): os.system('echo "@reboot root /home/xtreamcodes/iptv_xtream_codes/start_services.sh" >> /etc/crontab')

def start(first=True):
    if first: printc("Starting Xtream Codes")
    else: printc("Restarting Xtream Codes")
    os.system("/home/xtreamcodes/iptv_xtream_codes/start_services.sh > /dev/null")

def modifyNginx():
    printc("Modifying Nginx")
    rPath = "/home/xtreamcodes/iptv_xtream_codes/nginx/conf/nginx.conf"
    rPrevData = open(rPath, "r").read()
    if not "listen 25500;" in rPrevData:
        shutil.copy(rPath, "%s.xc" % rPath)
        rData = "}".join(rPrevData.split("}")[:-1]) + "    server {\n        listen 25500;\n        index index.php index.html index.htm;\n        root /home/xtreamcodes/iptv_xtream_codes/admin/;\n\n        location ~ \.php$ {\n			limit_req zone=one burst=8;\n            try_files $uri =404;\n			fastcgi_index index.php;\n			fastcgi_pass php;\n			include fastcgi_params;\n			fastcgi_buffering on;\n			fastcgi_buffers 96 32k;\n			fastcgi_buffer_size 32k;\n			fastcgi_max_temp_file_size 0;\n			fastcgi_keep_conn on;\n			fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;\n			fastcgi_param SCRIPT_NAME $fastcgi_script_name;\n        }\n    }\n}"
        rFile = open(rPath, "w")
        rFile.write(rData)
        rFile.close()

def verify_installation():
    """Verifică instalarea"""
    printc("Verifying installation")
    
    # Verifică nginx binaries
    main_nginx = "/home/xtreamcodes/iptv_xtream_codes/nginx/sbin/nginx"
    rtmp_nginx = "/home/xtreamcodes/iptv_xtream_codes/nginx_rtmp/sbin/nginx_rtmp"
    
    if os.path.exists(main_nginx) and os.access(main_nginx, os.X_OK):
        version_output = os.popen(f"{main_nginx} -v 2>&1").read()
        if NGINX_VERSION in version_output:
            printc(f"✓ Main nginx {NGINX_VERSION} installed correctly")
        else:
            printc("✗ Main nginx version mismatch", col.BRIGHT_YELLOW)
    else:
        printc("✗ Main nginx binary not found or not executable", col.BRIGHT_RED)
    
    if os.path.exists(rtmp_nginx) and os.access(rtmp_nginx, os.X_OK):
        printc("✓ RTMP nginx installed correctly")
    else:
        printc("✗ RTMP nginx binary not found or not executable", col.BRIGHT_RED)
    
    # Verifică ionCube
    php_test = os.popen("php -m | grep -i ioncube").read().strip()
    if php_test:
        printc("✓ ionCube Loader is active")
    else:
        printc("✗ ionCube Loader not detected", col.BRIGHT_YELLOW)
    
    # Verifică serviciile
    time.sleep(3)
    services_status = []
    
    # MariaDB
    mariadb_status = os.system("systemctl is-active mariadb > /dev/null 2>&1")
    if mariadb_status == 0:
        services_status.append("✓ MariaDB")
    else:
        services_status.append("✗ MariaDB")
    
    # nginx processes
    nginx_procs = os.popen("pgrep -f nginx").read().strip()
    if nginx_procs:
        services_status.append("✓ nginx")
    else:
        services_status.append("✗ nginx")
    
    # PHP-FPM
    phpfpm_procs = os.popen("pgrep -f php-fpm").read().strip()
    if phpfpm_procs:
        services_status.append("✓ PHP-FPM")
    else:
        services_status.append("✗ PHP-FPM")
    
    printc("Service status: " + " | ".join(services_status))

if __name__ == "__main__":
    try: rVersion = os.popen('lsb_release -sr').read().strip()
    except: rVersion = None
    if not rVersion in rVersions:
        printc("Unsupported Operating System. Supported: Ubuntu 20.04, 22.04, 24.04", col.BRIGHT_RED)
        sys.exit(1)
    printc("Xtream UI R22F + nginx %s Installer" % NGINX_VERSION, col.GREEN, 2)
    print(" ")
    rType = input("  Installation Type [MAIN, LB, UPDATE]: ")
    print(" ")
    if rType.upper() in ["MAIN", "LB"]:
        if rType.upper() == "LB":
            rHost = input("  Main Server IP Address: ")
            rPassword = input("  MySQL Password: ")
            try: rServerID = int(input("  Load Balancer Server ID: "))
            except: rServerID = -1
            print(" ")
        else:
            rHost = "127.0.0.1"
            rPassword = generate()
            rServerID = 1
        rUsername = "user_iptvpro"
        rDatabase = "xtream_iptvpro"
        rPort = 7999
        if len(rHost) > 0 and len(rPassword) > 0 and rServerID > -1:
            printc("Start installation? Y/N", col.BRIGHT_YELLOW)
            if input("  ").upper() == "Y":
                print(" ")
                rRet = prepare(rType.upper())
                if not install(rType.upper()): sys.exit(1)
                if rType.upper() == "MAIN":
                    if not mysql(rUsername, rPassword): sys.exit(1)
                encrypt(rHost, rUsername, rPassword, rDatabase, rServerID, rPort)
                configure()
                if rType.upper() == "MAIN": 
                    modifyNginx()
                    update(rType.upper())
                start()
                verify_installation()
                printc("Installation completed!", col.GREEN, 2)
                if rType.upper() == "MAIN":
                    printc("Please store your MySQL password: %s" % rPassword, col.BRIGHT_YELLOW)
                    printc("Admin UI Wan IP: http://%s:25500" % getIP(), col.BRIGHT_YELLOW)
                    printc("User Panel: http://%s:25461" % getIP(), col.BRIGHT_YELLOW)
                    printc("Admin UI default login is admin/admin", col.BRIGHT_YELLOW)
                    printc("nginx version: %s with RTMP module" % NGINX_VERSION, col.BRIGHT_GREEN)
                    printc("Save Credentials is file to /root/credentials.txt", col.BRIGHT_YELLOW)
                    rFile = open("/root/credentials.txt", "w")
                    rFile.write("MySQL password: %s\n" % rPassword)
                    rFile.write("Admin UI: http://%s:25500\n" % getIP())
                    rFile.write("User Panel: http://%s:25461\n" % getIP())
                    rFile.write("Admin UI default login is admin/admin\n")
                    rFile.write("nginx version: %s with RTMP module\n" % NGINX_VERSION)
                    rFile.close()
            else: printc("Installation cancelled", col.BRIGHT_RED)
        else: printc("Invalid entries", col.BRIGHT_RED)
    elif rType.upper() == "UPDATE":
        if os.path.exists("/home/xtreamcodes/iptv_xtream_codes/wwwdir/api.php"):
            printc("Update Admin Panel? Y/N?", col.BRIGHT_YELLOW)
            if input("  ").upper() == "Y":
                if not update(rType.upper()): sys.exit(1)
                printc("Installation completed!", col.GREEN, 2)
                start()
            else: printc("Install Xtream Codes Main first!", col.BRIGHT_RED)
    else: printc("Invalid installation type", col.BRIGHT_RED)

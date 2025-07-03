#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Xtream UI R22F Hybrid Installer
Dragon Shield Edition
Ubuntu 22.04/24.04 + nginx 1.26.2 + PHP 8.3 + MariaDB 10.5

Author: Stefan2512
Version: 4.0 - Ultimate Hybrid
Date: July 2025
"""

import subprocess, os, random, string, sys, shutil, socket, zipfile, urllib.request, urllib.error, urllib.parse, json, base64, time, re, signal
from itertools import cycle
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from zipfile import ZipFile

# ============================================================================
# CONFIGURATION
# ============================================================================

# Software versions
NGINX_VERSION = "1.26.2"
PHP_VERSION = "8.3"
MARIADB_VERSION = "10.5"

# Download URLs
DOWNLOAD_URLS = {
    "main": "https://github.com/sabiralipsl/Xtream-UI-R22F-ubuntu20.04lts-2025/releases/download/xtream1/main_xui_xoceunder.zip",
    "sub": "https://github.com/sabiralipsl/Xtream-UI-R22F-ubuntu20.04lts-2025/releases/download/xtream1/sub_xui_xoceunder.zip",
    "update": "https://github.com/sabiralipsl/Xtream-UI-R22F-ubuntu20.04lts-2025/releases/download/xtream1/release_22f.zip",
    "geolite": "https://github.com/sabiralipsl/Xtream-UI-R22F-ubuntu20.04lts-2025/releases/download/xtream1/GeoLite2.mmdb",
    "pid_monitor": "https://github.com/sabiralipsl/Xtream-UI-R22F-ubuntu20.04lts-2025/releases/download/xtream1/pid_monitor.php"
}

# Ubuntu versions support matrix
UBUNTU_SUPPORT = {
    "22.04": {"codename": "jammy", "eol": False, "mariadb_repo": "jammy"},
    "24.04": {"codename": "noble", "eol": False, "mariadb_repo": "jammy"}  # Use jammy for compatibility
}

# Required packages
PACKAGES = [
    "libcurl4", "libxslt1-dev", "libgeoip-dev", "libonig-dev", "e2fsprogs", 
    "wget", "mcrypt", "nscd", "htop", "zip", "unzip", "mc", "mariadb-server", 
    "libpng16-16", "libzip5", "python3-paramiko", "python-is-python3",
    "build-essential", "gcc", "make", "git", "curl", "software-properties-common",
    "libpcre3-dev", "libssl-dev", "zlib1g-dev", "libxml2-dev", "pkg-config",
    "libgd-dev", "libgeoip-dev", "ca-certificates", "gnupg", "lsb-release"
]

# Global variables
TEMP_DIRS = []
INSTALLATION_STATE = {
    "step": 0,
    "total_steps": 12,
    "start_time": 0,
    "errors": [],
    "warnings": []
}

# ============================================================================
# COLORS AND DISPLAY
# ============================================================================

class Colors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

def printc(text, color=Colors.BRIGHT_GREEN, padding=0, limit=46):
    """Enhanced print with box formatting"""
    print("%s ┌─────────────────────────────────────────────────┐ %s" % (color, Colors.ENDC))
    for i in range(padding):
        print("%s │                                                 │ %s" % (color, Colors.ENDC))
    
    array = [text[i:i+limit] for i in range(0, len(text), limit)]
    for line in array:
        spaces_left = round(23-(len(line)/2))
        spaces_right = round(46-(22-(len(line)/2))-len(line))
        print("%s │ %s%s%s │ %s" % (color, " "*spaces_left, line, " "*spaces_right, Colors.ENDC))
    
    for i in range(padding):
        print("%s │                                                 │ %s" % (color, Colors.ENDC))
    print("%s └─────────────────────────────────────────────────┘ %s" % (color, Colors.ENDC))
    print("")

def log_step(message, step_type="INFO"):
    """Enhanced logging with progress"""
    colors = {
        "INFO": Colors.BRIGHT_CYAN,
        "SUCCESS": Colors.BRIGHT_GREEN,
        "WARNING": Colors.BRIGHT_YELLOW,
        "ERROR": Colors.BRIGHT_RED,
        "PROGRESS": Colors.BRIGHT_BLUE
    }
    
    color = colors.get(step_type, Colors.WHITE)
    timestamp = time.strftime("%H:%M:%S")
    
    if step_type == "PROGRESS":
        current_step = INSTALLATION_STATE["step"]
        total_steps = INSTALLATION_STATE["total_steps"]
        percentage = int((current_step / total_steps) * 100)
        progress_bar = "█" * (percentage // 5) + "░" * (20 - (percentage // 5))
        print(f"{color}[{current_step:2d}/{total_steps}] [{progress_bar}] {percentage:3d}% - {message}{Colors.ENDC}")
    else:
        print(f"{color}[{step_type}] [{timestamp}] {message}{Colors.ENDC}")
    
    # Track errors and warnings
    if step_type == "ERROR":
        INSTALLATION_STATE["errors"].append(message)
    elif step_type == "WARNING":
        INSTALLATION_STATE["warnings"].append(message)

def next_step(message):
    """Move to next step"""
    INSTALLATION_STATE["step"] += 1
    log_step(message, "PROGRESS")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_password(length=19):
    """Generate secure password"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

def get_ip():
    """Get server IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_system_info():
    """Get system information"""
    try:
        ubuntu_version = subprocess.check_output("lsb_release -sr 2>/dev/null || echo 'unknown'", shell=True).decode().strip()
        ubuntu_codename = subprocess.check_output("lsb_release -sc 2>/dev/null || echo 'unknown'", shell=True).decode().strip()
        ubuntu_description = subprocess.check_output("lsb_release -d 2>/dev/null || echo 'Unknown'", shell=True).decode().split(":")[-1].strip()
        
        # Memory info
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            mem_total_kb = int([line for line in meminfo.split('\n') if 'MemTotal:' in line][0].split()[1])
            mem_total_gb = round(mem_total_kb / 1024 / 1024, 1)
        except:
            mem_total_gb = 1.0
        
        # CPU count
        cpu_count = os.cpu_count() or 2
        
        return {
            'ubuntu_version': ubuntu_version,
            'ubuntu_codename': ubuntu_codename,
            'ubuntu_description': ubuntu_description,
            'memory_total_gb': mem_total_gb,
            'cpu_count': cpu_count,
            'server_ip': get_ip()
        }
    except Exception as e:
        log_step(f"Error getting system info: {e}", "ERROR")
        return None

def run_command(cmd, description="", timeout=300, allow_failure=False, retry_count=0):
    """Enhanced command execution"""
    if description:
        log_step(description, "INFO")
    
    for attempt in range(max(1, retry_count + 1)):
        try:
            if attempt > 0:
                log_step(f"Retry attempt {attempt}/{retry_count}", "INFO")
                time.sleep(2)
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return True
            elif allow_failure:
                log_step(f"Command failed but continuing: {cmd[:50]}...", "WARNING")
                return False
            else:
                if attempt == retry_count:
                    log_step(f"Command failed: {cmd[:50]}...", "ERROR")
                    if result.stderr:
                        log_step(f"Error: {result.stderr.strip()[:100]}...", "ERROR")
                    return False
                    
        except subprocess.TimeoutExpired:
            if attempt == retry_count:
                log_step(f"Command timed out: {cmd[:50]}...", "ERROR")
                return False
        except Exception as e:
            if attempt == retry_count:
                log_step(f"Command execution error: {e}", "ERROR")
                return False
    
    return False

def cleanup_temp_files():
    """Clean up temporary files"""
    for temp_dir in TEMP_DIRS:
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

def signal_handler(signum, frame):
    """Handle interruption signals"""
    log_step("Installation interrupted by user", "ERROR")
    cleanup_temp_files()
    sys.exit(1)

# ============================================================================
# VALIDATION AND PREREQUISITES
# ============================================================================

def check_root_privileges():
    """Check if running as root"""
    if os.geteuid() != 0:
        printc("This installer must be run as root!", Colors.BRIGHT_RED)
        printc("Please run: sudo python3 installer.py", Colors.BRIGHT_YELLOW)
        return False
    return True

def check_system_requirements(sys_info):
    """Check system requirements"""
    if sys_info['ubuntu_version'] not in UBUNTU_SUPPORT:
        printc(f"Unsupported Ubuntu version: {sys_info['ubuntu_version']}", Colors.BRIGHT_RED)
        printc("Supported versions: " + ", ".join(UBUNTU_SUPPORT.keys()), Colors.BRIGHT_YELLOW)
        return False
    
    if sys_info['memory_total_gb'] < 0.5:
        printc(f"Insufficient memory: {sys_info['memory_total_gb']}GB", Colors.BRIGHT_RED)
        return False
    elif sys_info['memory_total_gb'] < 1.0:
        log_step(f"Low memory detected: {sys_info['memory_total_gb']}GB", "WARNING")
    
    return True

def check_existing_installation():
    """Check for existing installation"""
    if os.path.exists("/home/xtreamcodes/iptv_xtream_codes"):
        printc("Existing Xtream installation detected", Colors.BRIGHT_YELLOW)
        while True:
            response = input("Continue and overwrite? [Y/N]: ").strip().upper()
            if response in ['Y', 'N']:
                return response == 'Y'
            print("Please enter Y or N")
    return True

# ============================================================================
# SYSTEM PREPARATION AND REPAIR FUNCTIONS
# ============================================================================

def kill_conflicting_processes():
    """Kill processes that might conflict - from repair script"""
    log_step("Stopping conflicting processes", "INFO")
    
    # Critical ports
    critical_ports = [25500, 25461, 25463, 25462, 31210, 7999]
    for port in critical_ports:
        try:
            result = subprocess.run(f"lsof -t -i:{port}", shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                pid = result.stdout.strip()
                log_step(f"Killing process on port {port} (PID: {pid})", "INFO")
                run_command(f"kill -9 {pid}", allow_failure=True)
        except:
            pass
    
    # Kill Xtream processes
    xtream_processes = ["xtreamcodes", "nginx_rtmp", "signal_receiver", "pipe_reader"]
    for process in xtream_processes:
        run_command(f"pkill -f {process}", allow_failure=True)
    
    # Remove socket files
    socket_files = [
        "/home/xtreamcodes/iptv_xtream_codes/php/*.sock",
        "/home/xtreamcodes/iptv_xtream_codes/php/*.pid"
    ]
    for pattern in socket_files:
        run_command(f"rm -f {pattern}", allow_failure=True)
    
    time.sleep(3)

def prepare_system():
    """Prepare system for installation"""
    next_step("Preparing system")
    
    # Set signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Kill conflicting processes
    kill_conflicting_processes()
    
    # Remove package locks
    lock_files = [
        "/var/lib/dpkg/lock-frontend",
        "/var/cache/apt/archives/lock", 
        "/var/lib/dpkg/lock"
    ]
    
    for lock_file in lock_files:
        try:
            os.remove(lock_file)
        except FileNotFoundError:
            pass
    
    # Fix broken packages
    run_command("dpkg --configure -a", allow_failure=True)
    run_command("apt --fix-broken install -y", allow_failure=True)
    run_command("apt-get update", "Updating package lists")
    run_command("apt-get -y full-upgrade", "Upgrading system", allow_failure=True)
    
    return True

def setup_repositories(sys_info):
    """Setup package repositories"""
    next_step("Setting up repositories")
    
    ubuntu_version = sys_info['ubuntu_version']
    ubuntu_info = UBUNTU_SUPPORT[ubuntu_version]
    
    # Install repository tools
    base_tools = ["software-properties-common", "ca-certificates", "curl", "gnupg", "lsb-release", "wget"]
    for tool in base_tools:
        run_command(f"apt-get install {tool} -y", allow_failure=True)
    
    # Add PHP repository
    log_step(f"Adding PHP {PHP_VERSION} repository", "INFO")
    run_command("add-apt-repository ppa:ondrej/php -y", retry_count=2)
    
    # Add MariaDB repository
    log_step(f"Adding MariaDB {MARIADB_VERSION} repository", "INFO")
    
    # MariaDB key and repository
    mariadb_commands = [
        "apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8",
        f"add-apt-repository 'deb [arch=amd64,arm64,ppc64el] http://mirror.lstn.net/mariadb/repo/{MARIADB_VERSION}/ubuntu {ubuntu_info['mariadb_repo']} main'"
    ]
    
    for cmd in mariadb_commands:
        run_command(f"{cmd}", allow_failure=True)
    
    # Final package update
    run_command("apt-get update", "Updating package lists after repository setup")
    
    return True

def install_packages():
    """Install required packages"""
    next_step("Installing packages")
    
    # Install packages in groups
    essential_packages = PACKAGES[:10]
    php_packages = [f"php{PHP_VERSION}", f"php{PHP_VERSION}-fpm", f"php{PHP_VERSION}-cli", 
                   f"php{PHP_VERSION}-mysql", f"php{PHP_VERSION}-curl", f"php{PHP_VERSION}-gd",
                   f"php{PHP_VERSION}-mbstring", f"php{PHP_VERSION}-xml", f"php{PHP_VERSION}-zip"]
    
    all_packages = essential_packages + php_packages + PACKAGES[10:]
    
    installed_count = 0
    for package in all_packages:
        if run_command(f"apt-get install {package} -y", f"Installing {package}", allow_failure=True):
            installed_count += 1
        else:
            log_step(f"Failed to install {package}", "WARNING")
    
    log_step(f"Installed {installed_count}/{len(all_packages)} packages", "SUCCESS")
    
    # Install pip2 and python2 paramiko (from original script)
    log_step("Installing pip2 and python2 paramiko", "INFO")
    pip2_commands = [
        "add-apt-repository universe",
        "curl https://github.com/sabiralipsl/Xtream-UI-R22F-ubuntu20.04lts-2025/releases/download/xtream1/get-pip.py --output get-pip.py",
        "python2 get-pip.py",
        "pip2 install paramiko"
    ]
    
    for cmd in pip2_commands:
        run_command(cmd, allow_failure=True)
    
    # Create xtreamcodes user
    try:
        subprocess.check_output("getent passwd xtreamcodes", shell=True)
        log_step("User xtreamcodes already exists", "INFO")
    except subprocess.CalledProcessError:
        log_step("Creating user xtreamcodes", "INFO")
        run_command("adduser --system --shell /bin/false --group --disabled-login xtreamcodes")
    
    if not os.path.exists("/home/xtreamcodes"):
        os.makedirs("/home/xtreamcodes", exist_ok=True)
    
    return True

# ============================================================================
# MARIADB INSTALLATION
# ============================================================================

def generate_mariadb_config(sys_info):
    """Generate optimized MariaDB configuration with intelligent scaling for all server sizes"""
    memory_gb = sys_info['memory_total_gb']
    
    # Intelligent memory allocation based on server size
    if memory_gb <= 1:
        # Very small servers
        innodb_buffer = '128M'
        max_connections = 100
        tmp_table_size = '64M'
        max_heap_table_size = '64M'
        key_buffer_size = '16M'
        
    elif memory_gb <= 2:
        # Small servers  
        innodb_buffer = '256M'
        max_connections = 200
        tmp_table_size = '128M'
        max_heap_table_size = '128M'
        key_buffer_size = '32M'
        
    elif memory_gb <= 4:
        # Medium servers
        innodb_buffer = '512M'
        max_connections = 300
        tmp_table_size = '256M'
        max_heap_table_size = '256M'
        key_buffer_size = '64M'
        
    elif memory_gb <= 8:
        # Large servers
        innodb_buffer = '2G'
        max_connections = 500
        tmp_table_size = '512M'
        max_heap_table_size = '512M'
        key_buffer_size = '128M'
        
    elif memory_gb <= 16:
        # Very large servers
        innodb_buffer = '6G'  # ~40% of RAM
        max_connections = 1000
        tmp_table_size = '1G'
        max_heap_table_size = '1G'
        key_buffer_size = '256M'
        
    elif memory_gb <= 32:
        # Enterprise servers
        innodb_buffer = '12G'  # ~40% of RAM
        max_connections = 2000
        tmp_table_size = '2G'
        max_heap_table_size = '2G'
        key_buffer_size = '512M'
        
    elif memory_gb <= 64:
        # High-end enterprise servers
        innodb_buffer = '24G'  # ~40% of RAM (leaving space for nginx, PHP, OS)
        max_connections = 3000
        tmp_table_size = '4G'
        max_heap_table_size = '4G'
        key_buffer_size = '1G'
        
    else:
        # Monster servers (64GB+)
        # Use 40% of RAM for InnoDB buffer pool
        buffer_size_gb = int(memory_gb * 0.4)
        innodb_buffer = f'{buffer_size_gb}G'
        max_connections = 5000
        tmp_table_size = '8G'
        max_heap_table_size = '8G'
        key_buffer_size = '2G'
    
    # Calculate additional optimizations for high-memory servers
    if memory_gb >= 16:
        # Enable multiple buffer pool instances for better concurrency
        buffer_pool_instances = min(16, max(1, int(memory_gb // 4)))
        # Increase log file size for better performance
        log_file_size = '1G' if memory_gb >= 32 else '512M'
        # Increase read/write threads for high-end servers
        read_threads = min(64, max(4, int(memory_gb // 2)))
        write_threads = min(64, max(4, int(memory_gb // 2)))
        # Better concurrency settings
        back_log = min(900, max_connections // 2)
        table_cache = min(4096, max(1024, int(memory_gb * 64)))
    else:
        buffer_pool_instances = 1
        log_file_size = '128M'
        read_threads = 4
        write_threads = 4
        back_log = max_connections // 2
        table_cache = 1024

    config = f"""# Xtream UI MariaDB Configuration
# Generated for {memory_gb}GB RAM server
# InnoDB Buffer Pool: {innodb_buffer} (~{int((float(innodb_buffer.replace('G', '').replace('M', '')) if 'G' in innodb_buffer else float(innodb_buffer.replace('M', ''))/1024) / memory_gb * 100) if memory_gb > 0 else 0}% of total RAM)
# Optimized for high-performance IPTV streaming workloads

[client]
port = 3306

[mysqld_safe]
nice = 0

[mysqld]
user = mysql
port = 7999
basedir = /usr
datadir = /var/lib/mysql
tmpdir = /tmp
skip-external-locking
skip-name-resolve = 1

# Network settings
bind-address = 127.0.0.1
max_connections = {max_connections}
max_allowed_packet = 64M
back_log = {back_log}

# Connection timeouts
connect_timeout = 30
wait_timeout = 600
interactive_timeout = 600

# Memory settings optimized for {memory_gb}GB RAM
key_buffer_size = {key_buffer_size}
table_open_cache = {table_cache}
table_definition_cache = {table_cache}
sort_buffer_size = 2M
read_buffer_size = 1M
read_rnd_buffer_size = 2M

# Temporary tables
tmp_table_size = {tmp_table_size}
max_heap_table_size = {max_heap_table_size}

# InnoDB settings - optimized for high-performance IPTV streaming
innodb_buffer_pool_size = {innodb_buffer}
innodb_buffer_pool_instances = {buffer_pool_instances}
innodb_read_io_threads = {read_threads}
innodb_write_io_threads = {write_threads}
innodb_thread_concurrency = 0
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT
innodb_file_per_table = 1
innodb_log_file_size = {log_file_size}
innodb_log_buffer_size = 32M
innodb_lock_wait_timeout = 50

# Query cache disabled for better performance with many connections
query_cache_type = 0
query_cache_size = 0

# Binary logging
expire_logs_days = 3
max_binlog_size = 100M

# SQL mode for Xtream compatibility
sql-mode = "NO_ENGINE_SUBSTITUTION"

# MyISAM settings
myisam_sort_buffer_size = 8M
myisam_recover_options = BACKUP

[mysqldump]
quick
quote-names
max_allowed_packet = 16M

[mysql]

[isamchk]
key_buffer_size = 16M
"""
    
    # Log the configuration for transparency
    log_step(f"MariaDB optimized for {memory_gb}GB RAM:", "SUCCESS")
    log_step(f"  - InnoDB Buffer Pool: {innodb_buffer}", "INFO")
    log_step(f"  - Max Connections: {max_connections}", "INFO")
    if memory_gb >= 16:
        log_step(f"  - Buffer Pool Instances: {buffer_pool_instances}", "INFO")
        log_step(f"  - I/O Threads: {read_threads}R/{write_threads}W", "INFO")
    
    return config

def install_mariadb(sys_info):
    """Install and configure MariaDB"""
    next_step("Installing MariaDB")
    
    # Stop existing MySQL/MariaDB
    stop_commands = ["systemctl stop mariadb", "systemctl stop mysql", "pkill -f mysqld"]
    for cmd in stop_commands:
        run_command(cmd, allow_failure=True)
    
    time.sleep(3)
    
    # Install MariaDB
    if not run_command("apt-get install mariadb-server mariadb-client -y", "Installing MariaDB packages"):
        return False
    
    # Generate and write configuration
    mariadb_config = generate_mariadb_config(sys_info)
    
    # Backup existing config
    if os.path.exists("/etc/mysql/my.cnf"):
        shutil.copy("/etc/mysql/my.cnf", "/etc/mysql/my.cnf.backup")
    
    with open("/etc/mysql/my.cnf", "w") as f:
        f.write(mariadb_config)
    
    # Start MariaDB
    run_command("systemctl daemon-reload")
    run_command("systemctl enable mariadb")
    
    if not run_command("systemctl start mariadb", "Starting MariaDB"):
        return False
    
    # Wait for MariaDB to be ready
    for attempt in range(30):
        if run_command("mysql -u root -e 'SELECT 1;'", allow_failure=True):
            log_step("MariaDB is ready", "SUCCESS")
            break
        time.sleep(2)
        if attempt == 29:
            log_step("MariaDB not responding", "ERROR")
            return False
    
    return True

def setup_database():
    """Setup Xtream database"""
    next_step("Setting up database")
    
    # Generate credentials
    db_password = generate_password(20)
    db_username = "user_iptvpro"
    db_name = "xtream_iptvpro"
    
    # Database setup SQL
    sql_commands = f"""
DROP DATABASE IF EXISTS {db_name};
CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
DROP USER IF EXISTS '{db_username}'@'localhost';
DROP USER IF EXISTS '{db_username}'@'127.0.0.1';
CREATE USER '{db_username}'@'localhost' IDENTIFIED BY '{db_password}';
CREATE USER '{db_username}'@'127.0.0.1' IDENTIFIED BY '{db_password}';
GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_username}'@'localhost';
GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_username}'@'127.0.0.1';
GRANT SELECT, LOCK TABLES ON *.* TO '{db_username}'@'localhost';
GRANT SELECT, LOCK TABLES ON *.* TO '{db_username}'@'127.0.0.1';
FLUSH PRIVILEGES;
"""
    
    # Execute SQL commands
    sql_file = "/tmp/db_setup.sql"
    try:
        with open(sql_file, "w") as f:
            f.write(sql_commands)
        
        if not run_command(f"mysql -u root < {sql_file}", "Setting up database"):
            return False, None
        
        return True, {
            'host': '127.0.0.1',
            'port': 7999,
            'username': db_username,
            'password': db_password,
            'database': db_name
        }
        
    finally:
        try:
            os.remove(sql_file)
        except:
            pass

# ============================================================================
# NGINX COMPILATION
# ============================================================================

def compile_nginx(sys_info):
    """Compile nginx with RTMP module"""
    next_step("Compiling nginx")
    
    # Create build directory
    build_dir = f"/tmp/nginx_build_{int(time.time())}"
    TEMP_DIRS.append(build_dir)
    os.makedirs(build_dir, exist_ok=True)
    
    # Download nginx source
    nginx_url = f"http://nginx.org/download/nginx-{NGINX_VERSION}.tar.gz"
    if not run_command(f'cd {build_dir} && wget -q "{nginx_url}"', "Downloading nginx source"):
        return False
    
    if not run_command(f'cd {build_dir} && tar -xzf nginx-{NGINX_VERSION}.tar.gz', "Extracting nginx"):
        return False
    
    nginx_src_dir = f"{build_dir}/nginx-{NGINX_VERSION}"
    
    # Download RTMP module
    if not run_command(f'cd {nginx_src_dir} && git clone --depth 1 https://github.com/arut/nginx-rtmp-module.git', "Downloading RTMP module"):
        return False
    
    # Create nginx directories
    nginx_dirs = [
        "/home/xtreamcodes/iptv_xtream_codes/nginx/sbin",
        "/home/xtreamcodes/iptv_xtream_codes/nginx/conf",
        "/home/xtreamcodes/iptv_xtream_codes/nginx_rtmp/sbin",
        "/home/xtreamcodes/iptv_xtream_codes/nginx_rtmp/conf",
        "/home/xtreamcodes/iptv_xtream_codes/logs",
        "/home/xtreamcodes/iptv_xtream_codes/tmp"
    ]
    
    for directory in nginx_dirs:
        os.makedirs(directory, exist_ok=True)
    
    # Compile main nginx
    main_configure_options = [
        f"--prefix=/home/xtreamcodes/iptv_xtream_codes/nginx/",
        "--with-http_ssl_module",
        "--with-http_realip_module",
        "--with-http_flv_module",
        "--with-http_mp4_module",
        "--with-http_secure_link_module",
        "--with-http_v2_module"
    ]
    
    configure_cmd = f'cd {nginx_src_dir} && ./configure {" ".join(main_configure_options)}'
    if not run_command(configure_cmd, "Configuring main nginx", timeout=600):
        return False
    
    cpu_count = sys_info.get('cpu_count', 2)
    if not run_command(f'cd {nginx_src_dir} && make -j{cpu_count}', "Compiling main nginx", timeout=1200):
        return False
    
    # Copy main nginx binary
    main_binary = f"{nginx_src_dir}/objs/nginx"
    if os.path.exists(main_binary):
        shutil.copy(main_binary, "/home/xtreamcodes/iptv_xtream_codes/nginx/sbin/nginx")
        os.chmod("/home/xtreamcodes/iptv_xtream_codes/nginx/sbin/nginx", 0o755)
    
    # Clean and compile RTMP nginx
    run_command(f'cd {nginx_src_dir} && make clean', allow_failure=True)
    
    rtmp_configure_options = [
        f"--prefix=/home/xtreamcodes/iptv_xtream_codes/nginx_rtmp/",
        "--add-module=./nginx-rtmp-module",
        "--with-pcre"
    ]
    
    configure_cmd = f'cd {nginx_src_dir} && ./configure {" ".join(rtmp_configure_options)}'
    if not run_command(configure_cmd, "Configuring RTMP nginx", timeout=600):
        return False
    
    if not run_command(f'cd {nginx_src_dir} && make -j{cpu_count}', "Compiling RTMP nginx", timeout=1200):
        return False
    
    # Copy RTMP nginx binary
    rtmp_binary = f"{nginx_src_dir}/objs/nginx"
    if os.path.exists(rtmp_binary):
        shutil.copy(rtmp_binary, "/home/xtreamcodes/iptv_xtream_codes/nginx_rtmp/sbin/nginx_rtmp")
        os.chmod("/home/xtreamcodes/iptv_xtream_codes/nginx_rtmp/sbin/nginx_rtmp", 0o755)
    
    log_step("nginx compilation completed", "SUCCESS")
    return True

# ============================================================================
# XTREAM SOFTWARE INSTALLATION
# ============================================================================

def download_and_install_xtream(install_type="MAIN"):
    """Download and install Xtream software"""
    next_step("Installing Xtream software")
    
    # Backup nginx binaries if they exist
    nginx_backups = {}
    nginx_files = {
        "main": "/home/xtreamcodes/iptv_xtream_codes/nginx/sbin/nginx",
        "rtmp": "/home/xtreamcodes/iptv_xtream_codes/nginx_rtmp/sbin/nginx_rtmp"
    }
    
    for name, path in nginx_files.items():
        if os.path.exists(path):
            backup_path = f"/tmp/{name}_nginx_backup"
            shutil.copy(path, backup_path)
            nginx_backups[name] = backup_path
    
    # Download software
    download_url = DOWNLOAD_URLS["main"] if install_type == "MAIN" else DOWNLOAD_URLS["sub"]
    
    if not run_command(f'wget -q -O "/tmp/xtreamcodes.zip" "{download_url}"', "Downloading Xtream software"):
        return False
    
    # Install software
    if not run_command('unzip "/tmp/xtreamcodes.zip" -d "/home/xtreamcodes/"', "Installing Xtream software"):
        return False
    
    # Restore nginx binaries
    for name, backup_path in nginx_backups.items():
        target_path = nginx_files[name]
        if os.path.exists(backup_path):
            shutil.copy(backup_path, target_path)
            os.chmod(target_path, 0o755)
            os.remove(backup_path)
    
    # Clean up
    try:
        os.remove("/tmp/xtreamcodes.zip")
    except:
        pass
    
    return True

def update_xtream():
    """Update Xtream software"""
    log_step("Updating Xtream software", "INFO")
    
    # Download update
    if not run_command(f'wget -q -O "/tmp/update.zip" "{DOWNLOAD_URLS["update"]}"', "Downloading update"):
        return False
    
    # Validate zip file
    try:
        with zipfile.ZipFile("/tmp/update.zip", 'r') as zip_file:
            zip_file.testzip()
    except:
        log_step("Invalid update zip file", "ERROR")
        return False
    
    # Apply update
    update_commands = [
        "chattr -i /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb",
        "rm -rf /home/xtreamcodes/iptv_xtream_codes/admin",
        "rm -rf /home/xtreamcodes/iptv_xtream_codes/pytools",
        "unzip /tmp/update.zip -d /tmp/update/",
        "cp -rf /tmp/update/XtreamUI-master/* /home/xtreamcodes/iptv_xtream_codes/",
        "rm -rf /tmp/update/",
        "chown -R xtreamcodes:xtreamcodes /home/xtreamcodes/",
        "chattr +i /home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb"
    ]
    
    for cmd in update_commands:
        run_command(cmd, allow_failure=True)
    
    # Clean up
    try:
        os.remove("/tmp/update.zip")
    except:
        pass
    
    return True

# ============================================================================
# CONFIGURATION AND ENCRYPTION
# ============================================================================

def encrypt_config(host="127.0.0.1", username="user_iptvpro", password="", database="xtream_iptvpro", server_id=1, port=7999):
    """Encrypt Xtream configuration"""
    next_step("Encrypting configuration")
    
    # Remove existing config
    config_file = "/home/xtreamcodes/iptv_xtream_codes/config"
    try:
        os.remove(config_file)
    except:
        pass
    
    # Create config data
    config_data = json.dumps({
        "host": host,
        "db_user": username,
        "db_pass": password,
        "db_name": database,
        "server_id": server_id,
        "db_port": port
    }, separators=(',', ':'))
    
    # Encrypt using XOR cipher
    encryption_key = '5709650b0d7806074842c6de575025b1'
    encrypted = ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(config_data, cycle(encryption_key)))
    
    # Write encrypted config
    try:
        with open(config_file, 'wb') as f:
            f.write(base64.b64encode(bytes(encrypted, 'ascii')))
        
        os.chmod(config_file, 0o700)
        run_command(f"chown xtreamcodes:xtreamcodes {config_file}")
        
        return True
    except Exception as e:
        log_step(f"Failed to encrypt config: {e}", "ERROR")
        return False

def configure_system():
    """Configure system settings"""
    next_step("Configuring system")
    
    # Setup fstab entries
    fstab_entries = [
        "tmpfs /home/xtreamcodes/iptv_xtream_codes/streams tmpfs defaults,noatime,nosuid,nodev,noexec,mode=1777,size=90% 0 0",
        "tmpfs /home/xtreamcodes/iptv_xtream_codes/tmp tmpfs defaults,noatime,nosuid,nodev,noexec,mode=1777,size=2G 0 0"
    ]
    
    with open("/etc/fstab", "r") as f:
        fstab_content = f.read()
    
    for entry in fstab_entries:
        if entry not in fstab_content:
            with open("/etc/fstab", "a") as f:
                f.write(entry + "\n")
    
    # Setup sudoers
    sudoers_entry = "xtreamcodes ALL = (root) NOPASSWD: /sbin/iptables, /usr/bin/chattr"
    with open("/etc/sudoers", "r") as f:
        sudoers_content = f.read()
    
    if sudoers_entry not in sudoers_content:
        with open("/etc/sudoers", "a") as f:
            f.write(f"\n{sudoers_entry}\n")
    
    # Create init script
    init_script = """#!/bin/bash
/home/xtreamcodes/iptv_xtream_codes/start_services.sh"""
    
    with open("/etc/init.d/xtreamcodes", "w") as f:
        f.write(init_script)
    os.chmod("/etc/init.d/xtreamcodes", 0o755)
    
    # Setup hosts entries
    hosts_entries = [
        "127.0.0.1    api.xtream-codes.com",
        "127.0.0.1    downloads.xtream-codes.com",
        "127.0.0.1    xtream-codes.com"
    ]
    
    with open("/etc/hosts", "r") as f:
        hosts_content = f.read()
    
    for entry in hosts_entries:
        if entry.split()[1] not in hosts_content:
            with open("/etc/hosts", "a") as f:
                f.write(entry + "\n")
    
    # Setup crontab
    cron_entry = "@reboot root /home/xtreamcodes/iptv_xtream_codes/start_services.sh"
    with open("/etc/crontab", "r") as f:
        crontab_content = f.read()
    
    if cron_entry not in crontab_content:
        with open("/etc/crontab", "a") as f:
            f.write(f"{cron_entry}\n")
    
    # Create required directories
    required_dirs = [
        "/home/xtreamcodes/iptv_xtream_codes/tv_archive",
        "/home/xtreamcodes/iptv_xtream_codes/streams",
        "/home/xtreamcodes/iptv_xtream_codes/tmp"
    ]
    
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)
    
    # Download additional files
    additional_files = {
        "GeoLite2.mmdb": "/home/xtreamcodes/iptv_xtream_codes/GeoLite2.mmdb",
        "pid_monitor.php": "/home/xtreamcodes/iptv_xtream_codes/crons/pid_monitor.php"
    }
    
    for filename, target in additional_files.items():
        if not os.path.exists(target):
            url_key = filename.replace('.', '_').replace('_php', '')
            download_url = DOWNLOAD_URLS.get(url_key)
            if download_url:
                run_command(f'wget -q "{download_url}" -O "{target}"', allow_failure=True)
    
    # Set permissions
    run_command("chown -R xtreamcodes:xtreamcodes /home/xtreamcodes/")
    run_command("chmod -R 755 /home/xtreamcodes/")
    run_command("chmod 700 /home/xtreamcodes/iptv_xtream_codes/config")
    
    # Mount filesystems
    run_command("mount -a", allow_failure=True)
    
    return True

# ============================================================================
# AUTO-REPAIR FUNCTIONS (from repair script)
# ============================================================================

def auto_repair_ioncube():
    """Auto-repair ionCube Loader"""
    log_step("Repairing ionCube Loader", "INFO")
    
    php_ext_path = f"/home/xtreamcodes/iptv_xtream_codes/php/lib/php/extensions/no-debug-non-zts-20190902"
    
    if not os.path.exists(php_ext_path):
        os.makedirs(php_ext_path, exist_ok=True)
    
    # Create temporary directory
    temp_dir = "/tmp/ioncube_repair"
    os.makedirs(temp_dir, exist_ok=True)
    TEMP_DIRS.append(temp_dir)
    
    # Download ionCube loaders
    ioncube_url = "https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz"
    
    if run_command(f'cd {temp_dir} && wget -q "{ioncube_url}"', allow_failure=True):
        if run_command(f'cd {temp_dir} && tar -xzf ioncube_loaders_lin_x86-64.tar.gz', allow_failure=True):
            # Copy all loaders
            run_command(f'cp {temp_dir}/ioncube/ioncube_loader_lin_*.so {php_ext_path}/', allow_failure=True)
            log_step("ionCube loaders installed", "SUCCESS")
        else:
            log_step("Failed to extract ionCube loaders", "WARNING")
    else:
        log_step("Failed to download ionCube loaders", "WARNING")
    
    return True

def verify_services():
    """Verify that all services are running"""
    log_step("Verifying services", "INFO")
    
    services_status = {}
    
    # Check MariaDB
    services_status['MariaDB'] = run_command("systemctl is-active mariadb", allow_failure=True)
    
    # Check nginx processes
    services_status['nginx'] = run_command("pgrep -f 'nginx.*master.*xtream'", allow_failure=True)
    services_status['nginx_rtmp'] = run_command("pgrep -f 'nginx_rtmp.*master'", allow_failure=True)
    
    # Check PHP-FPM
    services_status['PHP-FPM'] = run_command(f"pgrep -f 'php{PHP_VERSION}-fpm.*master'", allow_failure=True)
    
    # Check ports
    ports_status = {}
    for port in [25500, 25461, 25463, 7999]:
        ports_status[port] = run_command(f"netstat -tuln | grep ':{port} '", allow_failure=True)
    
    # Report status
    running_services = sum(services_status.values())
    active_ports = sum(ports_status.values())
    
    log_step(f"Services running: {running_services}/{len(services_status)}", "INFO")
    log_step(f"Ports active: {active_ports}/{len(ports_status)}", "INFO")
    
    return running_services >= 3 and active_ports >= 3

# ============================================================================
# MAIN INSTALLATION ORCHESTRATOR
# ============================================================================

def populate_database(db_config, sys_info):
    """Populate database with initial data"""
    log_step("Populating database", "INFO")
    
    # Import database structure if exists
    db_structure_file = "/home/xtreamcodes/iptv_xtream_codes/database.sql"
    if os.path.exists(db_structure_file):
        import_cmd = f"mysql -u {db_config['username']} -p{db_config['password']} -h {db_config['host']} -P {db_config['port']} {db_config['database']} < {db_structure_file}"
        run_command(import_cmd, allow_failure=True)
        
        try:
            os.remove(db_structure_file)
        except:
            pass
    
    # Insert initial data
    sql_commands = f"""
INSERT IGNORE INTO settings (live_streaming_pass, unique_id, crypt_load_balancing) 
VALUES ('{generate_password(20)}', '{generate_password(10)}', '{generate_password(20)}');

REPLACE INTO streaming_servers (
    id, server_name, domain_name, server_ip, vpn_ip, ssh_password, ssh_port,
    diff_time_main, http_broadcast_port, total_clients, system_os, network_interface,
    latency, status, enable_geoip, geoip_countries, last_check_ago, can_delete,
    server_hardware, total_services, persistent_connections, rtmp_port, geoip_type,
    isp_names, isp_type, enable_isp, boost_fpm, http_ports_add, network_guaranteed_speed,
    https_broadcast_port, https_ports_add, whitelist_ips, watchdog_data, timeshift_only
) VALUES (
    1, 'Main Server', '', '{sys_info['server_ip']}', '', NULL, NULL,
    0, 25461, 1000, '{sys_info['ubuntu_description']}', 'eth0',
    0, 1, 0, '', 0, 0,
    '{{}}', 3, 0, 25462, 'low_priority',
    '', 'low_priority', 0, 1, '', 1000,
    25463, '', '["127.0.0.1",""]', '{{}}', 0
);

REPLACE INTO reg_users (
    id, username, password, email, member_group_id, verified, status
) VALUES (
    1, 'admin',
    '$6$rounds=20000$xtreamcodes$XThC5OwfuS0YwS4ahiifzF14vkGbGsFF1w7ETL4sRRC5sOrAWCjWvQJDromZUQoQuwbAXAFdX3h3Cp3vqulpS0',
    'admin@website.com', 1, 1, 1
);

INSERT IGNORE INTO member_groups (group_id, group_name, is_admin, total_credits, allowed_ips, allowed_ua)
VALUES (1, 'Administrators', 1, -1, '', '');
"""
    
    sql_file = "/tmp/initial_data.sql"
    try:
        with open(sql_file, "w") as f:
            f.write(sql_commands)
        
        import_cmd = f"mysql -u {db_config['username']} -p{db_config['password']} -h {db_config['host']} -P {db_config['port']} {db_config['database']} < {sql_file}"
        run_command(import_cmd, allow_failure=True)
        
    finally:
        try:
            os.remove(sql_file)
        except:
            pass
    
    return True

def start_services():
    """Start all Xtream services"""
    next_step("Starting services")
    
    # Start MariaDB
    run_command("systemctl start mariadb")
    
    # Start PHP-FPM
    run_command(f"systemctl start php{PHP_VERSION}-fpm", allow_failure=True)
    
    # Start services via script if exists
    start_script = "/home/xtreamcodes/iptv_xtream_codes/start_services.sh"
    if os.path.exists(start_script):
        os.chmod(start_script, 0o755)
        run_command(start_script, allow_failure=True)
    
    time.sleep(5)
    
    return True

def main_installation():
    """Main installation orchestrator"""
    INSTALLATION_STATE["start_time"] = time.time()
    
    try:
        # Clear screen and show header
        os.system('clear')
        printc("Xtream UI R22F Hybrid Installer", Colors.BRIGHT_CYAN, 2)
        printc(f"nginx {NGINX_VERSION} + PHP {PHP_VERSION} + MariaDB {MARIADB_VERSION}", Colors.BRIGHT_GREEN)
        
        # Prerequisites
        if not check_root_privileges():
            sys.exit(1)
        
        sys_info = get_system_info()
        if not sys_info:
            printc("Failed to get system information", Colors.BRIGHT_RED)
            sys.exit(1)
        
        printc(f"Ubuntu {sys_info['ubuntu_version']} detected", Colors.BRIGHT_YELLOW)
        printc(f"Memory: {sys_info['memory_total_gb']}GB | CPU: {sys_info['cpu_count']} cores", Colors.BRIGHT_YELLOW)
        printc(f"Server IP: {sys_info['server_ip']}", Colors.BRIGHT_YELLOW)
        
        if not check_system_requirements(sys_info):
            sys.exit(1)
        
        if not check_existing_installation():
            sys.exit(1)
        
        # Get installation type
        print("\nInstallation Type:")
        print("  [1] MAIN SERVER (Complete installation)")
        print("  [2] LOAD BALANCER (Secondary server)")
        print("  [3] UPDATE (Update existing installation)")
        
        while True:
            choice = input("\nEnter choice [1-3]: ").strip()
            if choice in ['1', '2', '3']:
                break
            print("Please enter 1, 2, or 3")
        
        install_type = {"1": "MAIN", "2": "LB", "3": "UPDATE"}[choice]
        
        if install_type == "LB":
            main_server_ip = input("Main Server IP: ").strip()
            db_password = input("MySQL Password: ").strip()
            server_id = input("Load Balancer Server ID: ").strip()
            
            if not all([main_server_ip, db_password, server_id]):
                printc("All fields are required for Load Balancer setup", Colors.BRIGHT_RED)
                sys.exit(1)
        
        elif install_type == "UPDATE":
            if not os.path.exists("/home/xtreamcodes/iptv_xtream_codes"):
                printc("Xtream UI not found. Install main server first!", Colors.BRIGHT_RED)
                sys.exit(1)
        
        # Confirmation
        printc(f"Ready to install Xtream UI ({install_type})", Colors.BRIGHT_YELLOW)
        confirm = input("Continue? [Y/N]: ").strip().upper()
        if confirm != 'Y':
            printc("Installation cancelled", Colors.BRIGHT_RED)
            sys.exit(1)
        
        # Installation process
        INSTALLATION_STATE["total_steps"] = 12 if install_type == "MAIN" else 8
        
        # System preparation
        if not prepare_system():
            sys.exit(1)
        
        if not setup_repositories(sys_info):
            sys.exit(1)
        
        if not install_packages():
            sys.exit(1)
        
        if install_type == "UPDATE":
            # Update process
            if not update_xtream():
                sys.exit(1)
            
            if not start_services():
                sys.exit(1)
                
            printc("Update completed successfully!", Colors.BRIGHT_GREEN, 2)
            
        else:
            # Full installation
            if install_type == "MAIN":
                if not install_mariadb(sys_info):
                    sys.exit(1)
                
                success, db_config = setup_database()
                if not success:
                    sys.exit(1)
                
                if not compile_nginx(sys_info):
                    sys.exit(1)
            
            if not download_and_install_xtream(install_type):
                sys.exit(1)
            
            # Configuration
            if install_type == "MAIN":
                encrypt_config(
                    host="127.0.0.1",
                    username=db_config['username'],
                    password=db_config['password'],
                    database=db_config['database'],
                    server_id=1,
                    port=db_config['port']
                )
                
                if not populate_database(db_config, sys_info):
                    log_step("Database population had issues", "WARNING")
            
            else:  # Load Balancer
                encrypt_config(
                    host=main_server_ip,
                    username="user_iptvpro",
                    password=db_password,
                    database="xtream_iptvpro",
                    server_id=int(server_id),
                    port=7999
                )
                db_config = None
            
            if not configure_system():
                sys.exit(1)
            
            # Auto-repair
            auto_repair_ioncube()
            
            if install_type == "MAIN":
                if not update_xtream():
                    log_step("Update had issues", "WARNING")
            
            if not start_services():
                log_step("Service startup had issues", "WARNING")
            
            # Verification
            time.sleep(5)
            services_ok = verify_services()
            
            # Final report
            elapsed_time = int(time.time() - INSTALLATION_STATE["start_time"])
            time_str = f"{elapsed_time // 60}m {elapsed_time % 60}s"
            
            if services_ok:
                printc("Installation completed successfully!", Colors.BRIGHT_GREEN, 2)
            else:
                printc("Installation completed with warnings", Colors.BRIGHT_YELLOW, 2)
            
            printc(f"Installation time: {time_str}", Colors.BRIGHT_CYAN)
            
            if install_type == "MAIN":
                printc("ACCESS INFORMATION", Colors.BRIGHT_CYAN)
                printc(f"Admin Panel: http://{sys_info['server_ip']}:25500", Colors.BRIGHT_YELLOW)
                printc(f"User Panel: http://{sys_info['server_ip']}:25461", Colors.BRIGHT_YELLOW)
                printc("Default Login: admin / admin", Colors.BRIGHT_YELLOW)
                
                if db_config:
                    printc(f"MySQL Password: {db_config['password']}", Colors.BRIGHT_MAGENTA)
                    
                    # Save credentials
                    with open("/root/xtream_credentials.txt", "w") as f:
                        f.write(f"MySQL Password: {db_config['password']}\n")
                        f.write(f"Admin Panel: http://{sys_info['server_ip']}:25500\n")
                        f.write(f"User Panel: http://{sys_info['server_ip']}:25461\n")
                        f.write("Default Login: admin / admin\n")
                    
                    printc("Credentials saved to /root/xtream_credentials.txt", Colors.BRIGHT_GREEN)
            
            printc("IMPORTANT: Change default admin password!", Colors.BRIGHT_RED)
        
    except KeyboardInterrupt:
        print("\n")
        printc("Installation interrupted", Colors.BRIGHT_RED)
        cleanup_temp_files()
        sys.exit(1)
    except Exception as e:
        printc(f"Installation failed: {e}", Colors.BRIGHT_RED)
        import traceback
        traceback.print_exc()
        cleanup_temp_files()
        sys.exit(1)
    finally:
        cleanup_temp_files()

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main_installation()

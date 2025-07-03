# 🚀 Xtream UI R22F Hybrid Installer

[![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04%20|%2024.04-orange.svg)](https://ubuntu.com/)
[![nginx](https://img.shields.io/badge/nginx-1.26.2-green.svg)](https://nginx.org/)
[![PHP](https://img.shields.io/badge/PHP-8.3-blue.svg)](https://php.net/)
[![MariaDB](https://img.shields.io/badge/MariaDB-10.5-brown.svg)](https://mariadb.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **The Ultimate Xtream UI R22F Installer - Combining Power, Reliability, and Simplicity**

A comprehensive, production-ready installer that combines the best features from multiple installation scripts, providing a bulletproof setup for Xtream UI R22F with modern software stack and auto-repair capabilities.

## ✨ Features

### 🔧 **Modern Software Stack**
- **nginx 1.26.2** (compiled from source with RTMP module)
- **PHP 8.3** with all required extensions and optimizations
- **MariaDB 10.5** with performance tuning for IPTV workloads
- **Ubuntu 22.04/24.04** support with automatic compatibility detection

### 🛡️ **Production-Ready Reliability**
- **Auto-repair functionality** - fixes common post-installation issues
- **ionCube Loader** automatic detection and installation
- **Port conflict resolution** - automatically handles busy ports
- **Process management** - intelligent service startup and monitoring
- **Comprehensive error handling** with retry logic and fallbacks

### 🎯 **Installation Types**
- **🏠 Main Server** - Complete standalone installation
- **⚖️ Load Balancer** - Secondary server setup for scaling
- **🔄 Update Mode** - Update existing installations safely

### 📊 **Advanced Management**
- **Real-time progress tracking** with visual progress bars
- **Comprehensive logging** with color-coded status messages
- **Service verification** - ensures all components are running correctly
- **Automatic credentials management** - saves important passwords securely
- **System optimization** - memory and CPU tuning based on hardware

## 🎯 Quick Start

### Prerequisites
- Fresh Ubuntu 22.04 or 24.04 server
- Root access or sudo privileges
- Minimum 512MB RAM (1GB+ recommended)
- 3GB+ free disk space
- Internet connection

### One-Line Installation

```bash
wget -O installer.py https://raw.githubusercontent.com/Stefan2512/Xtream-UI-R22F-ubuntu20.04lts-2025/master/xtream_hybrid_installer.py && sudo python3 installer.py
```

### Manual Installation

```bash
# 1. Download the installer
wget https://raw.githubusercontent.com/Stefan2512/Xtream-UI-R22F-ubuntu20.04lts-2025/master/xtream_hybrid_installer.py

# 2. Make it executable
chmod +x xtream_hybrid_installer.py

# 3. Run as root
sudo python3 xtream_hybrid_installer.py
```

## 📋 Installation Guide

### 🏠 Main Server Installation

1. **Run the installer:**
   ```bash
   sudo python3 xtream_hybrid_installer.py
   ```

2. **Select installation type:**
   ```
   Installation Type:
     [1] MAIN SERVER (Complete installation)     ← Choose this
     [2] LOAD BALANCER (Secondary server)
     [3] UPDATE (Update existing installation)
   
   Enter choice [1-3]: 1
   ```

3. **Confirm installation:**
   ```
   Ready to install Xtream UI (MAIN)
   Continue? [Y/N]: Y
   ```

4. **Wait for completion** (10-15 minutes)

5. **Access your panels:**
   - **Admin Panel:** `http://YOUR_SERVER_IP:25500`
   - **User Panel:** `http://YOUR_SERVER_IP:25461`
   - **Default Login:** `admin` / `admin`

### ⚖️ Load Balancer Setup

1. **Run installer and select option 2**
2. **Provide main server details:**
   ```
   Main Server IP: 192.168.1.100
   MySQL Password: [your_main_server_mysql_password]
   Load Balancer Server ID: 2
   ```

### 🔄 Update Existing Installation

1. **Run installer and select option 3**
2. **Installer will safely update your existing setup**

## 🔧 Advanced Configuration

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 512MB | 2GB+ |
| **CPU** | 1 Core | 2+ Cores |
| **Storage** | 3GB | 10GB+ |
| **OS** | Ubuntu 22.04 | Ubuntu 24.04 |

### Memory Optimization

The installer automatically optimizes MariaDB based on available RAM:

- **≤1GB RAM:** Conservative settings (128M buffer pool)
- **2-4GB RAM:** Balanced settings (256M-512M buffer pool)  
- **4GB+ RAM:** Performance settings (1G+ buffer pool)

### Port Configuration

| Service | Port | Description |
|---------|------|-------------|
| **Admin Panel** | 25500 | Web administration interface |
| **User Panel** | 25461 | End-user streaming interface |
| **RTMP Streaming** | 25462 | Real-time streaming protocol |
| **Statistics** | 25463 | Server monitoring and stats |
| **Database** | 7999 | MariaDB (localhost only) |

## 🛠️ Auto-Repair Features

The installer includes intelligent auto-repair functionality:

### 🔄 **Process Management**
- Automatically kills conflicting processes on installation ports
- Handles nginx, PHP-FPM, and database service conflicts
- Removes stale socket files and PID locks

### 💎 **ionCube Loader Repair**
- Automatically detects PHP version and installs correct ionCube loader
- Downloads latest ionCube loaders if missing
- Updates PHP configuration with correct loader path

### 🔌 **Port Conflict Resolution**
- Scans for processes using required ports (25500, 25461, 25463, 25462, 7999)
- Safely terminates conflicting processes
- Verifies port availability before service startup

### 📁 **Permission Management**
- Sets correct ownership for all Xtream files (`xtreamcodes:xtreamcodes`)
- Applies proper file permissions (755 for directories, 644 for files)
- Secures configuration files with restricted access (700)

## 📊 Service Management

### Starting Services
```bash
# Start all services
sudo /home/xtreamcodes/iptv_xtream_codes/start_services.sh

# Or use init script
sudo /etc/init.d/xtreamcodes start
```

### Checking Service Status
```bash
# Check MariaDB
sudo systemctl status mariadb

# Check PHP-FPM
sudo systemctl status php8.3-fpm

# Check nginx processes
ps aux | grep nginx

# Check active ports
netstat -tuln | grep -E ':(25500|25461|25463|7999)'
```

### Log Files
```bash
# Main logs
tail -f /home/xtreamcodes/iptv_xtream_codes/logs/error.log

# nginx logs
tail -f /home/xtreamcodes/iptv_xtream_codes/nginx/logs/error.log

# MariaDB logs
tail -f /var/log/mysql/error.log
```

## 🔐 Security & Credentials

### Default Credentials
- **Username:** `admin`
- **Password:** `admin`

> ⚠️ **IMPORTANT:** Change the default admin password immediately after installation!

### Saved Credentials
Installation credentials are automatically saved to:
```bash
/root/xtream_credentials.txt
```

### Security Hardening
```bash
# Configure firewall (recommended)
sudo ufw allow 25500/tcp  # Admin panel
sudo ufw allow 25461/tcp  # User panel  
sudo ufw allow 25462/tcp  # RTMP streaming
sudo ufw deny 7999/tcp    # Database (localhost only)
sudo ufw enable

# Change default passwords
# 1. Admin panel password (via web interface)
# 2. Database root password
sudo mysql_secure_installation
```

## 🚨 Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check service status
sudo systemctl status mariadb php8.3-fpm

# Check for port conflicts
sudo netstat -tuln | grep -E ':(25500|25461|25463|7999)'

# Check process conflicts
sudo ps aux | grep -E '(nginx|php-fpm|mysql)'

# Restart services
sudo /home/xtreamcodes/iptv_xtream_codes/start_services.sh
```

#### Database Connection Issues
```bash
# Test database connection
mysql -u user_iptvpro -p -h 127.0.0.1 -P 7999 xtream_iptvpro

# Check MariaDB logs
sudo tail -f /var/log/mysql/error.log

# Restart MariaDB
sudo systemctl restart mariadb
```

#### ionCube Loader Issues
```bash
# Check PHP version and ionCube status
/home/xtreamcodes/iptv_xtream_codes/php/bin/php -v

# Re-run auto repair
sudo python3 xtream_hybrid_installer.py
# Choose UPDATE option to trigger auto-repair
```

#### Permission Issues
```bash
# Fix permissions
sudo chown -R xtreamcodes:xtreamcodes /home/xtreamcodes/
sudo chmod -R 755 /home/xtreamcodes/
sudo chmod 700 /home/xtreamcodes/iptv_xtream_codes/config
```

### Getting Help

1. **Check the logs** first - most issues are logged with clear error messages
2. **Run the UPDATE option** - triggers auto-repair functionality
3. **Verify system requirements** - ensure Ubuntu version and resources are adequate
4. **Open an issue** on GitHub with detailed error information

## 📁 File Structure

```
/home/xtreamcodes/iptv_xtream_codes/
├── admin/                  # Admin panel files
├── wwwdir/                # User panel files  
├── nginx/                 # Main nginx installation
│   ├── sbin/nginx         # Main nginx binary
│   └── conf/nginx.conf    # Main nginx config
├── nginx_rtmp/            # RTMP nginx installation
│   ├── sbin/nginx_rtmp    # RTMP nginx binary
│   └── conf/nginx.conf    # RTMP nginx config
├── php/                   # PHP installation and configs
├── logs/                  # Application logs
├── streams/               # Streaming content (tmpfs)
├── tmp/                   # Temporary files (tmpfs)
├── config                 # Encrypted database config
├── start_services.sh      # Service startup script
└── GeoLite2.mmdb         # GeoIP database
```

## 🎯 Performance Tuning

### For High-Performance Setups

#### Increase File Limits
```bash
# Add to /etc/security/limits.conf
echo "xtreamcodes soft nofile 65536" >> /etc/security/limits.conf
echo "xtreamcodes hard nofile 65536" >> /etc/security/limits.conf
```

#### Optimize nginx
```bash
# Edit /home/xtreamcodes/iptv_xtream_codes/nginx/conf/nginx.conf
worker_processes auto;
worker_connections 8192;
worker_rlimit_nofile 65535;
```

#### Optimize MariaDB
```bash
# For servers with 8GB+ RAM, edit /etc/mysql/my.cnf
innodb_buffer_pool_size = 2G
max_connections = 1000
```

## 🤝 Contributing

We welcome contributions! Please:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)  
5. **Open** a Pull Request

## 📝 Changelog

### v4.0 (Latest)
- ✅ Added Ubuntu 24.04 support
- ✅ Upgraded to nginx 1.26.2, PHP 8.3, MariaDB 10.5
- ✅ Integrated auto-repair functionality
- ✅ Enhanced error handling and retry logic
- ✅ Added comprehensive service verification
- ✅ Improved user interface with progress tracking

### v3.0
- ✅ Production-ready installer with comprehensive features
- ✅ Advanced logging and monitoring
- ✅ Memory-based optimization

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Original Xtream UI developers** for the core platform
- **nginx and RTMP module developers** for excellent streaming capabilities  
- **PHP and MariaDB teams** for robust backend technologies
- **Ubuntu community** for the solid foundation
- **All contributors** who helped improve this installer

## ⭐ Support

If this installer helped you, please:
- ⭐ **Star** this repository
- 🍴 **Fork** it for your own modifications
- 🐛 **Report issues** to help improve it
- 💬 **Share** with others who might benefit

---

**Made with ❤️ for the IPTV community**

*For professional support and custom installations, feel free to open an issue or contribute to the project.*




# Xtream-UI-R22F-ubuntu20.04lts-2025
sudo apt install python -y && rm -rf install.py && wget https://github.com/sabiralipsl/Xtream-UI-R22F-ubuntu20.04lts-2025/raw/master/install.py && sudo python3 install.py



# Xtream UI R22F Complete Static Installer

![Xtream UI](https://img.shields.io/badge/Xtream%20UI-R22F-blue.svg)
![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04%20%7C%2024.04-orange.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![License](https://img.shields.io/badge/License-Educational-red.svg)

**Production-ready installer for Xtream UI R22F with static binaries compilation**

> ⚠️ **DISCLAIMER**: This software is for educational purposes only. Users are responsible for compliance with all applicable laws and regulations in their jurisdiction.

## 🚀 Features

### 🔧 Static Compilation
- **nginx 1.26.2** compiled from source with RTMP module
- **PHP 8.3** static compilation with all required extensions
- **ionCube Loader** integration for encrypted PHP files
- **MariaDB 10.5** optimized for IPTV streaming workloads

### 🎯 Advanced Capabilities
- **Auto-scaling configuration** based on server RAM (1GB to 128GB+)
- **Zero system dependencies** - completely static binaries
- **Intelligent memory optimization** for different server sizes
- **Complete auto-repair functionality**
- **Multi-server support** (Main server + Load balancers)

### 📊 Supported Configurations
- **Main Server**: Complete installation with database
- **Load Balancer**: Secondary servers connecting to main
- **Update Mode**: Update existing installations

## 📋 System Requirements

### Minimum Requirements
- **OS**: Ubuntu 22.04 LTS or 24.04 LTS
- **RAM**: 1GB minimum (2GB+ recommended)
- **CPU**: 2 cores minimum
- **Storage**: 10GB free space
- **Root access** required

### Recommended Specifications
| Server Type | RAM | CPU Cores | Use Case |
|------------|-----|-----------|----------|
| Small | 2-4GB | 2-4 cores | Up to 500 users |
| Medium | 8-16GB | 4-8 cores | Up to 2000 users |
| Large | 32-64GB | 8-16 cores | Up to 5000 users |
| Enterprise | 64GB+ | 16+ cores | 5000+ users |

## 🛠 Installation

### Quick Start
```bash
# Download the installer
wget https://raw.githubusercontent.com/your-repo/xtream-installer/main/installer.py

# Make it executable
chmod +x installer.py

# Run as root
sudo python3 installer.py
```

### Installation Types

#### 1. Main Server Installation
```bash
sudo python3 installer.py
# Select option [1] MAIN SERVER
```
**Installs**: Complete Xtream UI stack with database, web panels, and streaming services.

#### 2. Load Balancer Installation  
```bash
sudo python3 installer.py
# Select option [2] LOAD BALANCER
# Provide: Main server IP, MySQL password, Server ID
```
**Installs**: Streaming-only server that connects to main database.

#### 3. Update Existing Installation
```bash
sudo python3 installer.py
# Select option [3] UPDATE
```
**Updates**: Existing Xtream UI installation to latest R22F version.

## 🔧 Configuration Details

### Automatic Optimizations

The installer automatically configures services based on your server specifications:

#### Memory-Based Scaling
- **1GB RAM**: Basic configuration, 100 max connections
- **2-4GB RAM**: Standard configuration, 200-300 max connections  
- **8-16GB RAM**: High-performance, 1000-2000 max connections
- **32GB+ RAM**: Enterprise configuration, 3000+ max connections

#### Service Ports
- **25500**: Admin Panel
- **25461**: User Panel  
- **25462**: RTMP Streaming
- **25463**: HLS/DASH Streaming
- **7999**: MariaDB Database

### Static Binary Locations
```
/home/xtreamcodes/iptv_xtream_codes/
├── nginx/sbin/nginx                    # Main nginx binary
├── nginx_rtmp/sbin/nginx_rtmp         # RTMP nginx binary  
├── php/bin/php                        # PHP CLI binary
├── php/sbin/php-fpm                   # PHP-FPM binary
└── config                             # Encrypted configuration
```

## 🚦 Service Management

### Manual Service Control
```bash
# Start all services
/home/xtreamcodes/iptv_xtream_codes/start_services.sh

# Stop services
pkill -f "php-fpm.*xtreamcodes"
pkill -f "nginx.*master.*xtream"  
pkill -f "nginx_rtmp.*master"

# Check service status
pgrep -f "php-fpm.*xtreamcodes"
pgrep -f "nginx.*master.*xtream"
netstat -tuln | grep -E ":(25461|25500|25462|25463|7999)"
```

### Auto-Start Configuration
Services automatically start on boot via:
- `/etc/init.d/xtreamcodes`
- `/etc/crontab` entry
- `systemd` MariaDB service

## 📊 Default Access Information

After successful installation:

### Admin Panel
- **URL**: `http://YOUR_SERVER_IP:25500`
- **Username**: `admin`
- **Password**: `admin`

### User Panel  
- **URL**: `http://YOUR_SERVER_IP:25461`

### Database Access
- **Host**: `127.0.0.1`
- **Port**: `7999`
- **Username**: `user_iptvpro`
- **Password**: Generated during installation (saved to `/root/xtream_credentials.txt`)

> 🔒 **IMPORTANT**: Change the default admin password immediately after installation!

## 🔍 Troubleshooting

### Common Issues

#### PHP-FPM Not Starting
```bash
# Check PHP-FPM configuration
/home/xtreamcodes/iptv_xtream_codes/php/sbin/php-fpm -t

# Check permissions
chown -R xtreamcodes:xtreamcodes /home/xtreamcodes/
```

#### nginx Configuration Errors
```bash
# Test nginx configuration
/home/xtreamcodes/iptv_xtream_codes/nginx/sbin/nginx -t -c /home/xtreamcodes/iptv_xtream_codes/nginx/conf/nginx.conf
```

#### Database Connection Issues
```bash
# Test MariaDB connection
mysql -u user_iptvpro -p -h 127.0.0.1 -P 7999 xtream_iptvpro

# Check MariaDB status
systemctl status mariadb
```

#### ionCube Loader Issues
```bash
# Test ionCube loading
/home/xtreamcodes/iptv_xtream_codes/php/bin/php -m | grep -i ioncube

# Reinstall ionCube if needed
# The installer includes auto-repair functionality
```

### Log Files
- **nginx**: `/home/xtreamcodes/iptv_xtream_codes/logs/error.log`
- **PHP-FPM**: `/home/xtreamcodes/iptv_xtream_codes/php/var/log/php-fpm.log`
- **MariaDB**: `/var/log/mysql/error.log`

### Performance Monitoring
```bash
# Check active connections
netstat -an | grep :25461 | wc -l

# Monitor resource usage  
htop

# Check service memory usage
ps aux | grep -E "(nginx|php-fpm|mysql)"
```

## 📈 Performance Tuning

### For High-Traffic Servers
The installer automatically optimizes for your server size, but manual tuning options:

#### nginx Tuning
- Edit `/home/xtreamcodes/iptv_xtream_codes/nginx/conf/nginx.conf`
- Adjust `worker_connections` based on expected load
- Modify buffer sizes for your content type

#### PHP-FPM Tuning  
- Edit `/home/xtreamcodes/iptv_xtream_codes/php/etc/php-fpm.conf`
- Adjust `pm.max_children` based on RAM
- Tune `pm.start_servers` and `pm.spare_servers`

#### MariaDB Tuning
- Configuration auto-generated in `/etc/mysql/my.cnf`
- InnoDB buffer pool automatically sized to ~40% of RAM
- Connection limits scale with available memory

## 🤝 Contributing

This installer is a collaboration between Stefan and Claude AI. Contributions are welcome!

### Development Setup
```bash
git clone https://github.com/your-repo/xtream-installer.git
cd xtream-installer
```

### Reporting Issues
Please include:
- Ubuntu version (`lsb_release -a`)
- Server specifications (RAM, CPU)
- Installation type attempted
- Complete error messages
- Relevant log files

## 📝 Version History

### v4.1 (Current)
- ✅ Complete static compilation working
- ✅ Intelligent memory scaling (1GB to 128GB+) 
- ✅ Auto-repair functionality
- ✅ Ubuntu 22.04/24.04 support
- ✅ ionCube integration
- ✅ RTMP module compilation
- ✅ Production-ready stability

### Key Improvements
- Zero system dependencies
- Faster compilation with multi-core support
- Enhanced error handling and retry logic
- Comprehensive service monitoring
- Automatic optimization based on hardware

## ⚖️ Legal Notice

This software is provided for **educational purposes only**. Users must:
- Comply with all local laws and regulations
- Respect intellectual property rights  
- Use only with legally obtained content
- Not use for piracy or copyright infringement

The authors assume no responsibility for misuse of this software.

## 📧 Support

- **Author**: Stefan + Claude AI Collaboration
- **Contact**: Stefan@outlook.ie
- **Documentation**: This README and inline code comments
- **Issues**: GitHub Issues section

---

**Made with ❤️ for the IPTV community**

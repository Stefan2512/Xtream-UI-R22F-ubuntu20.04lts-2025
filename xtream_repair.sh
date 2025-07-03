#!/bin/bash

# =============================================================================
# Xtream UI Auto Repair Script
# Rezolva problemele comune de dupa instalare
# =============================================================================

echo "=== Xtream UI Auto Repair Script ==="
echo "Pornesc repara?iile..."

# Variabile
XTREAM_PATH="/home/xtreamcodes/iptv_xtream_codes"
PHP_EXT_PATH="$XTREAM_PATH/php/lib/php/extensions/no-debug-non-zts-20190902"
TEMP_DIR="/tmp/xtream_repair"

# Func?ie pentru logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Verifica daca scriptul ruleaza ca root
if [[ $EUID -ne 0 ]]; then
   echo "Acest script trebuie rulat ca root!"
   exit 1
fi

# Verifica daca Xtream UI este instalat
if [ ! -d "$XTREAM_PATH" ]; then
    log "EROARE: Xtream UI nu este instalat în $XTREAM_PATH"
    exit 1
fi

log "Xtream UI gasit în $XTREAM_PATH"

# =============================================================================
# 1. OPRE?TE TOATE SERVICIILE
# =============================================================================
log "Opresc toate serviciile Xtream UI..."

# Opre?te procese pe porturile critice (for?at)
CRITICAL_PORTS=(25500 25461 25463 25462 31210)
for PORT in "${CRITICAL_PORTS[@]}"; do
    PID=$(lsof -t -i:$PORT 2>/dev/null)
    if [ ! -z "$PID" ]; then
        log "Opresc procesul pe portul $PORT (PID: $PID)"
        kill -9 $PID 2>/dev/null
    fi
done

# Opre?te procese Xtream UI
pkill -f xtreamcodes 2>/dev/null
pkill -f nginx_rtmp 2>/dev/null
pkill -f signal_receiver 2>/dev/null
pkill -f pipe_reader 2>/dev/null

# Opre?te nginx ?i PHP-FPM specific pentru xtreamcodes
pgrep -f "$XTREAM_PATH/nginx/sbin/nginx" | xargs -r kill -9 2>/dev/null
pgrep -f "$XTREAM_PATH/php/sbin/php-fpm" | xargs -r kill -9 2>/dev/null

# ?terge socket-urile PHP-FPM ramase
rm -f $XTREAM_PATH/php/*.sock 2>/dev/null
rm -f $XTREAM_PATH/php/*.pid 2>/dev/null

sleep 5
log "Servicii oprite ?i porturi eliberate"

# =============================================================================
# 2. REPARA ionCube LOADER
# =============================================================================
log "Încep repararea ionCube Loader..."

# Detecteaza versiunea PHP
PHP_VERSION=$($XTREAM_PATH/php/bin/php -v 2>/dev/null | head -n1 | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
log "Versiune PHP detectata: $PHP_VERSION"

# Creeaza director temporar
mkdir -p $TEMP_DIR
cd $TEMP_DIR

# Descarca ionCube Loaders daca nu exista deja
if [ ! -f "ioncube_loaders_lin_x86-64.tar.gz" ]; then
    log "Descarc ionCube Loaders..."
    wget -q https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz
    if [ $? -ne 0 ]; then
        log "EROARE: Nu am putut descarca ionCube Loaders"
        exit 1
    fi
fi

# Extrage arhiva
if [ ! -d "ioncube" ]; then
    log "Extrag ionCube Loaders..."
    tar -xzf ioncube_loaders_lin_x86-64.tar.gz
fi

# Copiaza loader-ul corect
IONCUBE_FILE="ioncube_loader_lin_${PHP_VERSION}.so"
if [ -f "ioncube/$IONCUBE_FILE" ]; then
    log "Copiez $IONCUBE_FILE..."
    cp "ioncube/$IONCUBE_FILE" "$PHP_EXT_PATH/"
    
    # Copiaza toate versiunile pentru siguran?a
    cp ioncube/ioncube_loader_lin_*.so "$PHP_EXT_PATH/"
    
    # Actualizeaza php.ini sa foloseasca versiunea corecta
    log "Actualizez php.ini..."
    sed -i "s/zend_extension=ioncube_loader_lin_[0-9]\+\.[0-9]\+\.so/zend_extension=ioncube_loader_lin_${PHP_VERSION}.so/g" "$XTREAM_PATH/php/lib/php.ini"
    
    # Verifica daca exista linia în php.ini, daca nu o adauga
    if ! grep -q "zend_extension=ioncube_loader_lin_${PHP_VERSION}.so" "$XTREAM_PATH/php/lib/php.ini"; then
        echo "zend_extension=ioncube_loader_lin_${PHP_VERSION}.so" >> "$XTREAM_PATH/php/lib/php.ini"
    fi
    
    log "ionCube Loader actualizat pentru PHP $PHP_VERSION"
else
    log "EROARE: Nu gasesc loader-ul pentru PHP $PHP_VERSION"
    exit 1
fi

# =============================================================================
# 3. REZOLVA CONFLICTE DE PORTURI
# =============================================================================
log "Verific conflicte de porturi..."

# Lista porturilor importante pentru Xtream UI
PORTS=(25500 25461 25463 31210)

for PORT in "${PORTS[@]}"; do
    PID=$(lsof -t -i:$PORT 2>/dev/null)
    if [ ! -z "$PID" ]; then
        log "Port $PORT este folosit de procesul $PID - îl opresc"
        kill -9 $PID 2>/dev/null
        sleep 1
    fi
done

# =============================================================================
# 4. REPARA PERMISIUNI
# =============================================================================
log "Repar permisiunile..."

chown -R xtreamcodes:xtreamcodes /home/xtreamcodes/ 2>/dev/null
chmod -R 755 $XTREAM_PATH
chmod +x $XTREAM_PATH/nginx/sbin/nginx 2>/dev/null
chmod +x $XTREAM_PATH/nginx_rtmp/sbin/nginx_rtmp 2>/dev/null
chmod +x $XTREAM_PATH/*.sh 2>/dev/null
chmod 400 $XTREAM_PATH/config 2>/dev/null

# Creeaza directoare necesare daca lipsesc
mkdir -p $XTREAM_PATH/logs
mkdir -p $XTREAM_PATH/php
mkdir -p /var/log/xtreamcodes

chown -R xtreamcodes:xtreamcodes $XTREAM_PATH/logs
chown -R xtreamcodes:xtreamcodes /var/log/xtreamcodes 2>/dev/null

log "Permisiuni reparate"

# =============================================================================
# 5. VERIFICA ?I REPARA CONFIGURA?IA
# =============================================================================
log "Verific configura?ia..."

# Verifica daca exista fi?ierele de configurare critice
CONFIG_FILES=("$XTREAM_PATH/nginx/conf/nginx.conf" "$XTREAM_PATH/php/lib/php.ini")

for CONFIG in "${CONFIG_FILES[@]}"; do
    if [ ! -f "$CONFIG" ]; then
        log "ATEN?IE: Lipse?te fi?ierul de configurare $CONFIG"
    fi
done

# =============================================================================
# 6. TESTEAZA ionCube
# =============================================================================
log "Testez încarcarea ionCube..."

TEST_OUTPUT=$($XTREAM_PATH/php/bin/php -v 2>&1)
if echo "$TEST_OUTPUT" | grep -q "Failed loading.*ioncube"; then
    log "EROARE: ionCube înca nu se încarca corect"
    echo "$TEST_OUTPUT"
    exit 1
else
    log "ionCube se încarca corect"
fi

# =============================================================================
# 7. PORNE?TE SERVICIILE
# =============================================================================
log "Pornesc serviciile Xtream UI..."

cd $XTREAM_PATH

# Ruleaza scriptul de pornire
if [ -f "start_services.sh" ]; then
    chmod +x start_services.sh
    ./start_services.sh > /tmp/xtream_start.log 2>&1 &
    
    # A?teapta pu?in pentru pornire
    sleep 5
    
    # Verifica daca au pornit serviciile critice
    log "Verific serviciile..."
    
    SERVICES_OK=true
    
    # Verifica nginx
    if ! pgrep -f "$XTREAM_PATH/nginx/sbin/nginx" > /dev/null; then
        log "ATEN?IE: nginx nu ruleaza"
        SERVICES_OK=false
    fi
    
    # Verifica nginx_rtmp  
    if ! pgrep -f "$XTREAM_PATH/nginx_rtmp/sbin/nginx_rtmp" > /dev/null; then
        log "ATEN?IE: nginx_rtmp nu ruleaza"
        SERVICES_OK=false
    fi
    
    # Verifica PHP-FPM
    if ! pgrep -f "$XTREAM_PATH/php/sbin/php-fpm" > /dev/null; then
        log "ATEN?IE: PHP-FPM nu ruleaza"
        SERVICES_OK=false
    fi
    
    # Verifica serviciile de streaming
    if ! pgrep -f "signal_receiver.php" > /dev/null; then
        log "ATEN?IE: signal_receiver.php nu ruleaza"
        SERVICES_OK=false
    fi
    
    if ! pgrep -f "pipe_reader.php" > /dev/null; then
        log "ATEN?IE: pipe_reader.php nu ruleaza"
        SERVICES_OK=false
    fi
    
    if [ "$SERVICES_OK" = true ]; then
        log "? Toate serviciile ruleaza corect"
    else
        log "?? Unele servicii nu ruleaza - verifica logurile"
    fi
    
else
    log "EROARE: Nu gasesc start_services.sh"
    exit 1
fi

# =============================================================================
# 8. TESTEAZA CONECTIVITATEA
# =============================================================================
log "Testez conectivitatea..."

# Testeaza porturile
for PORT in 25500 25461 25463; do
    if netstat -tuln | grep -q ":$PORT "; then
        log "? Portul $PORT este activ"
    else
        log "? Portul $PORT nu raspunde"
    fi
done

# Testeaza HTTP
HTTP_TEST=$(curl -s -I http://localhost:25500 2>/dev/null | head -n1)
if echo "$HTTP_TEST" | grep -q "200\|302\|301"; then
    log "? Admin panel raspunde pe http://localhost:25500"
else
    log "? Admin panel nu raspunde corect"
fi

# =============================================================================
# 9. CLEANUP
# =============================================================================
log "Cura? fi?ierele temporare..."
rm -rf $TEMP_DIR

# =============================================================================
# 10. RAPORT FINAL
# =============================================================================
echo ""
echo "=== RAPORT FINAL ==="
echo "Timp: $(date)"
echo "Xtream UI Path: $XTREAM_PATH"
echo "PHP Version: $PHP_VERSION"
echo ""

# Afi?eaza procesele care ruleaza
echo "Procese active:"
ps aux | grep -E "(nginx|php-fpm|signal_receiver|pipe_reader)" | grep -v grep | while read line; do
    echo "  ? $line"
done

echo ""
echo "Porturi active:"
netstat -tuln | grep -E ":(25500|25461|25463|31210) " | while read line; do
    echo "  ? $line"
done

echo ""
echo "=== REPARA?II COMPLETE ==="
echo "Admin Panel: http://$(hostname -I | awk '{print $1}'):25500"
echo "API Endpoint: http://$(hostname -I | awk '{print $1}'):25461"
echo ""
echo "Daca întâmpini probleme, verifica logurile în:"
echo "  - $XTREAM_PATH/logs/"
echo "  - $XTREAM_PATH/nginx/logs/"
echo "  - /tmp/xtream_start.log"
echo ""

log "Script finalizat cu succes! ??"
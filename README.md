# pkgsync

Herramienta de sincronización de paquetes automatizada

## Descripción 📋

pkgsync es una herramienta que permite mantener una uniformidad en el software de un conjunto de máquinas, garantizando que se instalen o desinstalen los paquetes especificados en tres tipos de listas:
- musthave
- mayhave
- maynothave

En los ficheros **musthave** se deben incluir los nombres de los paquetes que pkgsync **debe** instalar. En los ficheros **mayhave** se debem agregar los nombres de los paquetes que **pueden** instalarse. Por último, en los ficheros **maynothave** se deben añadir los nombres de los paquetes que **no deben instalarse**.
 
## Funcionamiento ⚙️
**pkgsync** se encargará de cumplir con las demandas establecidas en las listas, instalando los paquetes que se encuentren en los ficheros **musthave**, manteniendo instalado lo que se encuentre en los ficheros **mayhave** y desintalando lo que se encuentre en los ficheros **maynothave**.

Para permitir una administración compartida de paquetes, **pkgsync** maneja tres listas de paquetes:
- **/etc/pkgsync/musthave**: Lista de paquetes que deben estar instalados en la máquina.
- **/etc/pkgsync/mayhave**: Lista de paquetes que pueden instalarse en la máquina.
- **/etc/pkgsync/maynothave**: Lista de paquetes que no deben estar instalados en la máquina.

Los tres ficheros anteriores se fusionan con los siguientes ficheros:
- **/etc/pkgsync/musthave.ies**: Lista de paquetes que deben estar instalados en la máquina.
- **/etc/pkgsync/mayhave.ies**: Lista de paquetes que pueden instalarse en la máquina.
- **/etc/pkgsync/maynothave.ies**: Lista de paquetes que no deben estar instalados en la máquina.

Para garantizar una administración compartida, en los centros educativos de Extremadura, la sección de administración de sistemas gestiona los ficheros musthave, mayhave y maynothave. Y el administrador informático de cada centro gestiona los ficheros musthave.ies, mayhave.ies y maynothave.ies

Por otro lado, es posible crear ficheros con listas de paquetes en los siguientes directorios:
- **/etc/pkgsync/musthave.d/**
- **/etc/pkgsync/maythave.d/**
- **/etc/pkgsync/maynothave.d/**

Para garantizar la instalación/desinstalación de los paquetes especificados, **pkgsync** fusionará:
- Por un lado, el contenido de los ficheros /etc/pkgsync/musthave, /etc/pkgsync/musthave.ies y los ficheros incluidos dentro del directorio /etc/pkgsync/musthave.d/
- Por otro lado, el contenido de los ficheros /etc/pkgsync/mayhave, /etc/pkgsync/mayhave.ies y los ficheros incluidos dentro del directorio /etc/pkgsync/mayhave.d/
- Y, por otro, el contenido de los los ficheros /etc/pkgsync/maynothave, /etc/pkgsync/maynothave.ies y los ficheros incluidos dentro del directorio /etc/pkgsync/maynothave.d/

Es **importante** destacar que los ficheros **maynothave** tienen prioridad sobre los **musthave**. De este modo, cuando se especifique un nombre de paquete en un fichero **maynothave**, pkgsync no lo instalará aunque se encuentre incluido dentro de alguno de los ficheros **musthave**.

**pkgsync** se ejecuta, por defecto, de forma desatendida diariamente mediante **anacron** con el script **/etc/cron.daily/nightly-pkgsync**.

El script **nightly-pkgsync** bloquea el apagado del equipo mientras se está realizando el pkgsync. Ésto es realmente importante porque evita que el usuario apague el equipo mientras pkgsync esté instalando/desinstalando paquetes.
Para lograr el bloqueo, **nightly-pkgsync** comprueba que exista la herramienta **systemd-inhibit**, lo que significa que debe estar instalado systemd en el sistema.

## Configuración 🔧
**/etc/default/pkgsync** es el fichero de configuración de pkgsync. Podemos modificar su comportamiento por defecto modificando los valores definidos en él:

```
# Defaults for pkgsync
#
# See /usr/share/doc/pkgsync/README.Debian for information about options
# of managing pkgsync.

# Ignorar ficheros de configuración musthave, mayhave o maynothave
IGNORE_MUSTHAVE="no"
IGNORE_MAYHAVE="no"
IGNORE_MAYNOTHAVE="no"

# Activar o desactivar pkgsync:
#  ENABLE="yes": activa pkgsync (opción por defecto)
#  ENABLE="no": desactiva pkgsync
#  ENABLE="onlyupgrade": no instala ni desinstala paquetes. Tan sólo actualiza los ya instalados
#  Si no existe la variable ENABLE o no tiene valor, es equivalente al valor 'yes'.
ENABLE="yes"

# Eliminar kernels antiguos (por defecto deja los dos últimos)
# PURGE_OLD_KERNELS="no": no elimina kernels antiguos (opción por defecto)
# PURGE_OLD_KERNELS="yes": elimina kernels antiguos
PURGE_OLD_KERNELS="yes"

# Número de kernels que se desea conservar (por defecto deja los dos últimos)
# Si no existe la variable KEEP_LAST_KERNELS o no tiene valor, es equivalente al valor '2'.
# KEEP_LAST_KERNELS="2"
KEEP_LAST_KERNELS="3"

# Eliminar dependencias de paquetes desinstalados, purgar paquetes desinstalados y limpiar la cache
# CLEAN="no": no hacer limpieza (opción por defecto)
# CLEAN="yes": hacer limpieza
CLEAN="no"

# Iniciar sinc_puppet antes de lanzar pkgsync para garantizar que los ficheros de pkgsync 
# se encuentren actualizados
# LAUNCH_SINC_PUPPET="no": no iniciar sinc_puppet antes de hacer pkgsync
# LAUNCH_SINC_PUPPET="yes": iniciar sinc_puppet antes de hacer pkgsync (opción por defecto)
LAUNCH_SINC_PUPPET="yes"

# Nombre o IP del servidor puppet
# Si optamos por iniciar sinc_puppet antes de hacer pkgsync (LAUNCH_SINC_PUPPET="yes"), es 
# conveniente indicar en PUPPET_SERVER el nombre o la IP del servidor puppet. 
# De este modo, si el servidor puppet no responde a un ping, no se iniciará sinc_puppet.
# PUPPET_SERVER="puppetinstituto"
PUPPET_SERVER="puppetinstituto"

# Tiempo máximo en minutos que puede estar corriendo sinc_puppet antes de matarlo
TIMEOUT_FOR_SINC_PUPPET="5"

# Apagar automáticamente el equipo después de ejecutar pkgsync en el intervalo especificado
# AUTOMATIC_SHUTDOWN_BETWEEN="22:00-06:00"
AUTOMATIC_SHUTDOWN_BETWEEN=""

# Reiniciar automáticamente el equipo después de ejecutar pkgsync en el intervalo especificado
# AUTOMATIC_REBOOT_BETWEEN="06:01-08:00"

# Iniciar Windows al reiniciar el equipo automáticamente en el intervalo especificado
# AUTOMATIC_REBOOT_INTO_WINDOWS="no": no iniciar windows tras el reinicio en el intervalo especificado
# AUTOMATIC_REBOOT_INTO_WINDOWS="yes": iniciar windows tras el reinicio en el intervalo especificado
AUTOMATIC_REBOOT_INTO_WINDOWS="no"

# Obtener claves de repositorios mediante launchpad-getkeys si launchpad-getkeys se encuentra
# instalado
# LAUNCHPAD_GETKEYS="no": no tratar de obtener claves mediante launchpad-getkeys
# LAUNCHPAD_GETKEYS="yes": tratar de obtener claves mediante launchpad-getkeys (opción por defecto)
LAUNCHPAD_GETKEYS="yes"

# Es posible indicar un proxy a launchpad-getkeys para obtener las claves de repositorios
# LAUNCHPAD_GETKEYS_PROXY="": no utilizar proxy
# LAUNCHPAD_GETKEYS_PROXY="http://servidor:3128": utilizar un proxy específico
LAUNCHPAD_GETKEYS_PROXY="http://servidor:3128"

# Es posible indicar a launchpad-getkeys que elimine claves públicas de repositorios caducadas
# LAUNCHPAD_GETKEYS_REMOVE_EXPIRED_KEYS="yes": indicar a launchpad-getkeys que elimine claves públicas caducadas
# LAUNCHPAD_GETKEYS_REMOVE_EXPIRED_KEYS="no": no indicar a launchpad-getkeys que elimine claves públicas caducadas (opción por defecto)
LAUNCHPAD_GETKEYS_REMOVE_EXPIRED_KEYS="yes"

# Definimos un tiempo máximo de espera a que dpkg o apt hayan terminado antes de realizar pkgsync
# Este parámetro sirve para evitar evitar que pkgsync quede bloqueado por un fallo anterior de dpkg o apt
# Este ajuste puede definirse en segundos (30 o 30s), minutos (10m), horas (6h) o días (2d).
# TIMEOUT_FOR_DPKG_OR_APT="3m": Esperar un tiempo máximo de 3 minutos (valor por defecto)
TIMEOUT_FOR_DPKG_OR_APT="3m"

# ABORT_ON_FAILED_REPOS nos permite elegir entre abortar la ejecución de pkgsync cuando alguno de 
# los repositorios falle o continuar la ejecución ignorando los repositorios que fallan.
# ABORT_ON_FAILED_REPOS="yes": abortar la ejecución si alguno de los repositorios da error (opción por defecto)
# ABORT_ON_FAILED_REPOS="no": continuar la ejecución ignorando los repositorios que fallan
ABORT_ON_FAILED_REPOS="yes"

# AUTO_TEST_FILES permite elegir si queremos que pkgsync chequee automáticamente los ficheros
# de listas de paquetes.
# AUTO_TEST_FILES="yes": Habilitar la revisión automática de las listas de paquetes
# AUTO_TEST_FILES="no": Deshabilitar la revisión automática de las listas de paquetes (opción por defecto)
AUTO_TEST_FILES="no"

# ALERT_EMAIL_RECEIVER permite definir una dirección de email a la que enviar una alerta
# ALERT_EMAIL_RECEIVER="miusuario@midominio.es"
# Es necesario tener configurado un servicio como postfix o ssmtp en el equipo
ALERT_EMAIL_RECEIVER=""

# ALERT_EMAIL_ON_ERROR permite habilitar el envío de un email al destinatario definido en 
# ALERT_EMAIL_RECEIVER cuando se produzca algún error
# ALERT_EMAIL_ON_ERROR="yes": Realizar el envío de una alerta por email cuando se produzca un error
# ALERT_EMAIL_ON_ERROR="no": No realizar el envío de una alerta por email cuando se produzca un error
# Es necesario tener configurado un servicio como postfix o ssmtp en el equipo
ALERT_EMAIL_ON_ERROR="no"

# ENSURE_ESSENTIAL permite asegurar que no se desinstalen paquetes con prioridad required,
# important y standard
# ENSURE_ESSENTIAL="yes": Garantizar que no se desinstalan paquetes esenciales
# ENSURE_ESSENTIAL="no": No controlar la desinstalación de paquetes esenciales (opción por defecto)
ENSURE_ESSENTIAL="no"

# Definimos un tiempo mínimo en segundos entre operaciones de aptitude update
# Si no existe la variable THRESHOLD_FOR_APT_UPDATE o no tiene valor, es equivalente al valor '1800',
# es decir, 30 minutos
# THRESHOLD_FOR_APT_UPDATE="1800"
THRESHOLD_FOR_APT_UPDATE="900"
```

## Opciones  🚀 
Para consultar las opciones disponibles, podéis ejecutar **pkgsync** con el parámetro **-h**:

```
pkgsync 2.42
Automated package synchronization tool

Usage: pkgsync [OPTIONS]
Recognized options:
  -h,  --help			display this help and exit
  -v,  --version		display pkgsync version and exit
  -k,  --keep-unused		don't remove unused packages
  -e,  --ensure-essential	don't remove required, important and standard packages
  -s,  --simulate		don't do anything, just print out what would have happened
  -t,  --test-files		test pkgsync files
  -tr, --test-files r		test and remove packages from pkgsync files lists
  -d,  --delete-files		delete all pkgsync files
  -b,  --build-files		build musthave and create empty mayhave and maynothave if they don't exist
  -f,  --force			force pkgsync
  -c,  --clean			remove uninstalled packages dependencies,
				purge uninstalled packages and clean cache
  -p,  --purge-old-kernels	remove old kernels keeping the last two (by default)
				or the number specified in /etc/default/pkgsync file
  -n,  --no-sincpuppet		don't launch sinc_puppet from pkgsync
  -i,  --ignore-failed-repos	ignore failed repositories
  -g,  --get-keys		exec launchpad-keys to get repositories keys
  -S,  --shutdown		shutdown machine after pkgsync
  -R,  --reboot			reboot machine after pkgsync
  -Rw, --reboot w		reboot machine and boot into windows on EFI computers

Complete documentation can be found in /usr/share/doc/pkgsync/README.Debian.
```

## Herramientas adicionales 🛠️
Al instalar el paquete pkgsync, se instalan los siguientes scripts adicionales en el directorio **/usr/local/sbin/**:

- **apt-list-expired-keys**: Muestra un listado de claves de repositorios expiradas, si las hay.

- **apt-remove-expired-keys**: Elimina las claves de repositorios que han expirado.
- ***backup-repositories***: Realiza un backup de los repositorios almacenados en el fichero **/etc/apt/sources.list** junto con los repositorios almacenados en el directorio **/etc/apt/sources.list.d/** y lo guarda en el archivo comprimido **/var/backups/sources.list.tar.gz**.
- **list-backup-repositories**: Lista los repositorios incluidos en el fichero de backup **/var/backups/sources.list.tar.gz**.
- **restore-backup-repositories**: Restaura fichero **/etc/apt/sources.list** y los ficheros alojados en el directorio **/etc/apt/sources.list.d/** a partir del backup almacenado en el fichero **/var/backups/sources.list.tar.gz**.
- **remove-backup-repositories**: Elimina el fichero de backup de repositorios **/var/backups/sources.list.tar.gz**.
- **clean-pkgsync-files**: Chequea los ficheros de listas de paquetes y elimina los nombres de los paquetes que no se encuentran en los repositorios.
- **disable-failed-repositories**: Deshabilita los repositorios que fallan añadiéndoles la extensión **.disabled**.
- **enable-disabled-repositories**: Permite habilitar los repositorios deshabilitados quitándoles la extensión **.disabled**.
- **enable-non-failed-repositories**: Habilita repositorios deshabilitados en **/etc/apt/sources.list.d/** quitando a los ficheros **.list** la extensión **.disabled** pero manteniendo deshabilitados aquellos que fallan.
- **list-disabled-repositories**: Muestra un listado de los repositorios que han sido deshabilitados añadiéndoles la extensión **.disabled**.
- **list-failed-repositories**: Muestra los repositorios de **/etc/apt/sources.list.d/** que fallan.
- **remove-all-repositories**: Elimina todos los repositorios alojados dentro del directorio **/etc/apt/souces.list.d/**.
- **remove-failed-repositories**: Elimina de **/etc/apt/sources.list.d/** los repositorios que fallan.
- **disable-pkgsync-terminal**: Al instalar pkgsync, se crea un terminal **tty12** en el que se inicia sesión automáticamente con el usuario **pkgsync**. Este usuario tiene privilegios para ejecutar todos los scripts definidos en el fichero **/etc/sudoers.d/pkgsync**.
- **enable-pkgsync-terminal**: Si se ha deshabilitado el terminal **tty12** en el que se inicia sesión automáticamente con el usuario **pkgsync**, este script permite habilitarlo de nuevo.
- **download_pkg_and_deps**: Permite descargar un paquete y sus dependencias.
- **get-package-dependencies**: Lista las dependencias de un paquete que pasemos como parámetro al script.
- **launchpad-getkeys**: Intenta descargar las claves GPG de los repositorios que falten en la máquina.
- **limpiapaquetes:**: Hace limpieza purgando paquetes desinstalados y limpia la cache de apt.
- **musthave-build**: Create un fichero **/etc/pkgsync/musthave** a partir de la lista de paquetes instalados en el sistema en el momento de ejecutar el script. También crea los ficheros **/etc/pkgsync/mayhave** y **/etc/pkgsync/maynothave** si no existen.
- **musthave-minimize**: Reduce la lista de paquetes incluidos en el fichero **/etc/pkgsync/musthave** eliminando aquellos nombres de paquetes ya incluidos en los ficheros alojados en el directorio **/etc/pkgsync/musthave.d/** y sus dependencias.
- **purge-old-kernels**: Permite eliminar viejos kernels instalados en el sistema. Por defecto, desinstala todos, salvo los dos más recientes. Es posible indicar mediante parámetro el número de kernels que queramos conservar.
- **softwareupdate**: Actualiza paquetes instalados mediante apt, flatpak, snap y realiza limpieza.
- **solve-apt-errors**: Trata de resolver posibles errores en los paquetes instalados.
- **wait_for_apt_or_dpkg**: Permite realizar una espera mientras se esté realizando una actualización de índices o una actualización de paquetes.

## Autores ✒️

* 2004-2007 **Steinar H. Gunderson** <sgunderson@bigfoot.com>.
* 2013-2025 **Esteban M. Navas Martín** <algodelinux@gmail.com>.


## Licencia 📄

Este proyecto se encuentra publicado bajo la **licencia GNU GPL version 2**. En sistemas Debian, el texto completo de la licencia GPL v2 puede ser encontrado en **/usr/share/common-licenses/GPL-2**.


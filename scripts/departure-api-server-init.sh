#! /bin/bash

### BEGIN INIT INFO
# Provides:          departure
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: departure service
# Description:       Run departure board service
### END INIT INFO


DAEMON="/home/pi/departure/start_api_server.sh"
daemon_USER="pi"
daemon_NAME="departure"
daemon_PID="/run/${daemon_NAME}.pid"
daemon_LOG="/var/log/${daemon_NAME}.log"

PATH="/sbin:/bin:/usr/sbin:/usr/bin"

test -x $DAEMON || exit 0

. /lib/lsb/init-functions

d_start () {
	log_daemon_msg "Starting system $daemon_NAME Daemon"
	start-stop-daemon --start --background --pidfile $daemon_PID --make-pidfile --startas /bin/bash -- -c "exec $DAEMON >> $daemon_LOG 2>&1"
	log_end_msg $?
}

d_stop () {
	log_daemon_msg "Stopping system $daemon_NAME Daemon"
	start-stop-daemon --stop --pidfile $daemon_PID --retry 5  --remove-pidfile
	log_end_msg $?
}

case "$1" in

	start|stop)
		d_${1}
		;;

	restart|reload|force-reload)
		d_stop
		d_start
		;;

	*)
		echo "Usage: /etc/init.d/$daemon_NAME {start|stop|restart|reload|force-reload}"
		exit 1
		;;
esac
exit 0

#! /bin/bash

# terminate gracefully on interrupt
_term() {
  echo "Terminating API server"
  kill $child_pid
  exit 0
}

trap _term SIGTERM SIGINT

# start API server
cd /home/pi/departure/python
source ../set_env_vars.sh
source ../set_board.sh
source .venv/bin/activate
departure-web &
child_pid=$!
wait $child_pid

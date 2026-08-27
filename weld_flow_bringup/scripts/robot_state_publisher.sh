#!/bin/bash
# script is responsible for launching RSP for visualization purposes

set -e

source ~/ros2_ws/install/setup.bash
source /opt/ros/jazzy/setup.bash

ROBOT_TYPE="ur" # Use env var to switch between robot types
ROBOT_MODEL=$(yq eval ".${ROBOT_TYPE}.robot_state_publisher.robot_model" ../config/bringup_params.yaml)


export ROBOT_TYPE

echo "----------------------------------------------------"
echo "Launching RSP with parameters:"
echo "  robot_type: $ROBOT_TYPE"
echo "  robot_model: $ROBOT_MODEL"
echo "----------------------------------------------------"

ros2 launch weld_flow_bringup robot_state_publisher.launch.py 

cleanup() {
  echo "Cleaning up..."
  trap - INT TERM EXIT
  kill 0
}

trap cleanup INT TERM EXIT

wait

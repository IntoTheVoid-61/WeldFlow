#!/bin/bash
# script is responsible for launching hardware with moveit framework

set -e

source ~/ros2_ws/install/setup.bash
source /opt/ros/jazzy/setup.bash

ROBOT_TYPE="kuka" # Use env var to switch between robot types, currently only kuka supported

export ROBOT_TYPE

ROBOT_MODEL=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_hardware.robot_model" ../config/bringup_params.yaml) # kr6_r1820_arc_hw
ROBOT_FAMILY=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_hardware.robot_family" ../config/bringup_params.yaml) # cybertech
X=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_hardware.x" ../config/bringup_params.yaml)
Y=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_hardware.y" ../config/bringup_params.yaml)
Z=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_hardware.z" ../config/bringup_params.yaml)
ROLL=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_hardware.roll" ../config/bringup_params.yaml)
PITCH=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_hardware.pitch" ../config/bringup_params.yaml)
YAW=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_hardware.yaw" ../config/bringup_params.yaml)
NAMESPACE=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_hardware.namespace" ../config/bringup_params.yaml)


echo "----------------------------------------------------"
echo "Launching MoveIt with real hardware with parameters:"
echo "  robot_model: $ROBOT_MODEL"
echo "  robot_family: $ROBOT_FAMILY"
echo "  position of base_link relative to world:"
echo "      x: $X"
echo "      y: $Y"
echo "      z: $Z"
echo "      roll: $ROLL"
echo "      pitch: $PITCH"
echo "      yaw: $YAW"
echo "----------------------------------------------------"

ros2 launch weld_flow_bringup moveit_bringup_hardware.launch.py \
    robot_model:=$ROBOT_MODEL \
    robot_family:=$ROBOT_FAMILY \
    #namespace:=$NAMESPACE \ #issues with namespace, fix later
    x:=$X \
    y:=$Y \
    z:=$Z \
    roll:=$ROLL \
    pitch:=$PITCH \
    yaw:=$YAW &

cleanup() {
  echo "Cleaning up..."
  trap - INT TERM EXIT
  kill 0
}

trap cleanup INT TERM EXIT

wait

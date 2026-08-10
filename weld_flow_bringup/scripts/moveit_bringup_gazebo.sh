#!/bin/bash
# script is responsible for launching Gazebo simulation with moveit framework.

set -e

source ~/ros2_ws/install/setup.bash
source /opt/ros/jazzy/setup.bash

export GZ_SIM_RESOURCE_PATH=$HOME/ros2_ws/src/WeldFlow/weld_flow_gazebo/models:$GZ_SIM_RESOURCE_PATH

ROBOT_TYPE="ur" # Use env var to switch between robot types

export ROBOT_TYPE

ROBOT_MODEL=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_gazebo.robot_model" ../config/bringup_params.yaml)
ROBOT_FAMILY=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_gazebo.robot_family" ../config/bringup_params.yaml)
X=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_gazebo.x" ../config/bringup_params.yaml)
Y=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_gazebo.y" ../config/bringup_params.yaml)
Z=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_gazebo.z" ../config/bringup_params.yaml)
ROLL=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_gazebo.roll" ../config/bringup_params.yaml)
PITCH=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_gazebo.pitch" ../config/bringup_params.yaml)
YAW=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_gazebo.yaw" ../config/bringup_params.yaml)
NAMESPACE=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_gazebo.namespace" ../config/bringup_params.yaml)
GZ_WORLD=$(yq eval ".${ROBOT_TYPE}.moveit_bringup_gazebo.gz_world" ../config/bringup_params.yaml)


echo "----------------------------------------------------"
echo "Launching MoveIt Gazebo with parameters:"
echo "  robot_model: $ROBOT_MODEL"
echo "  robot_family: $ROBOT_FAMILY"
echo "  namespace: $NAMESPACE"
echo "  gazebo_world: $GZ_WORLD"
echo "  position of base_link relative to world:"
echo "      x: $X"
echo "      y: $Y"
echo "      z: $Z"
echo "      roll: $ROLL"
echo "      pitch: $PITCH"
echo "      yaw: $YAW"
echo "----------------------------------------------------"

ros2 launch weld_flow_bringup moveit_gazebo.launch.py \
    gz_world:=$GZ_WORLD \
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

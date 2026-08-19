#!/bin/bash
# script is responsible for copying the kr6_r1820_arc_hw files to existing kuka_robot_descriptions repository.
# set the PATH_TO_DESC_PKG variable to absolute path of folder containing the kuka_robot_descriptions repository.
set -e

PATH_TO_DESC_PKG='/home/ziga/ros2_ws/src/kuka_robot_descriptions'
#PATH_TO_DESC_PKG='/home/ziga/Downloads'

# copy config
cp ../files/config/kr6_r1820_arc_hw_joint_limits.yaml $PATH_TO_DESC_PKG/kuka_cybertech_support/config

# copy meshes folder
cp -r ../files/meshes/kr6_r1820_arc_hw $PATH_TO_DESC_PKG/kuka_cybertech_support/meshes

# copy urdf
cp -a ../files/urdf/. $PATH_TO_DESC_PKG/kuka_cybertech_support/urdf  

exit 0
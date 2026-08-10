from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from moveit_configs_utils import MoveItConfigsBuilder
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os
from ament_index_python.packages import get_package_share_directory
import yaml
from pathlib import Path

"""
Hardware launch is currently supported only for kuka-drivers rsi
"""

def generate_launch_description(robot_model="kuka"):

    declare_x_cmd = DeclareLaunchArgument(
        name="x",
        default_value="0",
    )

    declare_y_cmd = DeclareLaunchArgument(
        name="y",
        default_value="0",
    )

    declare_z_cmd = DeclareLaunchArgument(
        name="z",
        default_value="0",
    )

    declare_roll_cmd = DeclareLaunchArgument(
        name="roll",
        default_value="0",
    )

    declare_pitch_cmd = DeclareLaunchArgument(
        name="pitch",
        default_value="0",
    )

    declare_yaw_cmd = DeclareLaunchArgument(
        name="yaw",
        default_value="0",
    )

    declare_ns_cmd = DeclareLaunchArgument(
        name="namespace",
        default_value="",
    )



    # load config params
    bringup_config_path = (
        Path(get_package_share_directory("weld_flow_bringup"))
        / "config"
        / "bringup_params.yaml"
    )
    with open(bringup_config_path, "r") as f:
        config_params = yaml.load(f, Loader=yaml.SafeLoader)


    rviz_config_path=PathJoinSubstitution(
        [FindPackageShare('weld_flow_description'),'rviz','visualize.rviz']
    )



    robot_model=config_params['kuka']['moveit_bringup_hardware']['robot_model']
    robot_family=config_params['kuka']['moveit_bringup_hardware']['robot_family'] 

    if(robot_family == "cybertech"): # quick fix, for preliminary dev, generalize later
        moveit_config_pkg="kuka_kr"

    # hardcoded for now, generalize later
    driver_pkg="kuka_rsi_driver"

    moveit_config = (
        MoveItConfigsBuilder(moveit_config_pkg)
        .robot_description(
            file_path=get_package_share_directory(f"kuka_{robot_family}_support")
            + f"/urdf/{robot_model}.urdf.xacro",
            mappings={
                "x": LaunchConfiguration("x"),
                "y": LaunchConfiguration("y"),
                "z": LaunchConfiguration("z"),
                "roll": LaunchConfiguration("roll"),
                "pitch": LaunchConfiguration("pitch"),
                "yaw": LaunchConfiguration("yaw"),
                "prefix": LaunchConfiguration("namespace"),
            },
        )
        .robot_description_semantic(
            get_package_share_directory(f"{moveit_config_pkg}_moveit_config")
            + f"/urdf/{robot_model}.srdf"
        )
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_scene_monitor(
            publish_robot_description=True, publish_robot_description_semantic=True
        )
        .joint_limits(
            file_path=get_package_share_directory(f"kuka_{robot_family}_support")
            + f"/config/{robot_model}_joint_limits.yaml"
        )
        .to_moveit_configs()
    )


    startup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [get_package_share_directory(f"{driver_pkg}"), "/launch/startup.launch.py"]
        ),
    )

    move_group_configuration = {
        "publish_robot_description_semantic": True,
        "allow_trajectory_execution": True,
        "capabilities": "move_group/ExecuteTaskSolutionCapability",
        "disable_capabilities": "",
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
        "monitor_dynamics": False,
    }

    move_group_params = [
        moveit_config.to_dict(),
        move_group_configuration,
    ]

    start_move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=move_group_params,
    )

    rviz_parameters = [
        moveit_config.robot_description,
        moveit_config.robot_description_semantic,
        moveit_config.planning_pipelines,
        moveit_config.robot_description_kinematics,
    ]

    start_rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        parameters=rviz_parameters,
        arguments=['-d', rviz_config_path]
    )

    return LaunchDescription(
        [
            declare_x_cmd,
            declare_y_cmd,
            declare_z_cmd,
            declare_roll_cmd,
            declare_pitch_cmd,
            declare_yaw_cmd,
            declare_ns_cmd,
            startup_launch,
            #start_robot_state_publisher,
            start_move_group,
            start_rviz_cmd,
        ]
    )

    
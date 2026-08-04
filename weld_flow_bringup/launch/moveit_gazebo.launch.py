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


def generate_launch_description(robot_model="ur10e"):
    """
    Generates launch description for MoveIt-Gazebo pipeline
    Controller manager is already started in gazebo_sim.urdf.xacro
    """

    pkg_share_gazebo = FindPackageShare('weld_flow_gazebo')
    pkg_ros_gz_sim = FindPackageShare(package='ros_gz_sim').find('ros_gz_sim')
    pkg_share_description = FindPackageShare(f"{robot_model}_moveit_config")

    rviz_config_path = PathJoinSubstitution(
        [pkg_share_description,'rviz','visualize.rviz']
    )

    ros_gz_bridge_config_path = PathJoinSubstitution(
        [pkg_share_gazebo,'config','ros_gz_bridge.yaml']
    )

    world_path = PathJoinSubstitution(
        [pkg_share_gazebo,'worlds','empty.world']
    )


    moveit_config = (
        MoveItConfigsBuilder(f"{robot_model}", package_name=f"{robot_model}_moveit_config")
        .robot_description(
            file_path=f"config/{robot_model}.urdf.xacro",
            mappings={
                "use_gazebo": "true",
                "use_mock_hardware": "false"
            },
        )
        .to_moveit_configs()
    )



    #--Nodes to start--#
    #-Robot State Publisher-#
    start_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        respawn=True,
        name='robot_state_publisher',
        output='screen',
        parameters=[
            moveit_config.robot_description,
            {
                "publish_frequency": 15.0,
            },
        ]             
    )

    #-MoveGroup-#
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
    move_group_params.append({"use_sim_time": True})

    start_move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        #
        output="screen",
        parameters=move_group_params,
    )


    #-Rviz-#

    rviz_parameters = [
        moveit_config.robot_description,
        moveit_config.robot_description_semantic,
        moveit_config.planning_pipelines,
        moveit_config.robot_description_kinematics,
    ]
    rviz_parameters.append({"use_sim_time": True})

    start_rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        parameters=rviz_parameters,
        arguments=['-d', rviz_config_path]
    )

    #--Start Gazebo--#
    start_gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments=[('gz_args', [' -r -v 4 ', world_path])])

    # Bridge ROS topics and Gazebo messages for establishing communication
    start_gazebo_ros_bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': ros_gz_bridge_config_path,
        }],
        output='screen'
    )

    # Spawn the robot
    start_gazebo_ros_spawner_cmd = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-topic', '/robot_description',
            '-name', robot_model,
            '-allow_renaming', 'true',
        ])

    # Load controllers
    load_controllers = []
    for controller in [
        "arm_controller",
        "joint_state_broadcaster"
    ]:
        load_controllers += [
            ExecuteProcess(
                cmd=["ros2 run controller_manager spawner {}".format(controller)],
                shell=True,
                output="screen",
            )
        ]

    return LaunchDescription(
        [
            start_robot_state_publisher,
            start_move_group,
            start_rviz_cmd,
            start_gazebo_cmd,
            start_gazebo_ros_bridge_cmd,
            start_gazebo_ros_spawner_cmd,
        ]
        + load_controllers
    )
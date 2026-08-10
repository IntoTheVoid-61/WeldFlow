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


def generate_launch_description():
    """
    Generates launch description for MoveIt-Gazebo pipeline
    Controller manager is already started in gazebo_sim.urdf.xacro
    """

    robot_type=os.environ.get("ROBOT_TYPE")

    # Add launch configurations
    declare_world_cmd = DeclareLaunchArgument(
        name="gz_world",
        default_value="empty",
        choices=["empty","lab"],
        description="Name of world to load"
    )

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


        

    pkg_share_gazebo = FindPackageShare('weld_flow_gazebo')
    pkg_ros_gz_sim = FindPackageShare(package='ros_gz_sim').find('ros_gz_sim')

    rviz_config_path = PathJoinSubstitution(
        [pkg_share_gazebo,'rviz','visualize.rviz']
    )

    ros_gz_bridge_config_path = PathJoinSubstitution(
        [pkg_share_gazebo,'config','ros_gz_bridge.yaml']
    )

    world_path = PathJoinSubstitution([
        pkg_share_gazebo,
        'worlds',
        [LaunchConfiguration("gz_world"), ".world"]
    ])

    if (robot_type=="ur"):
        #pkg_share_description = FindPackageShare(f"{robot_type}_moveit_config")

        robot_model=config_params['ur']['moveit_bringup_gazebo']['robot_model']

        moveit_config = (
            MoveItConfigsBuilder(f"{robot_model}", package_name=f"{robot_model}_moveit_config")
            .robot_description(
                file_path=f"config/{robot_model}.urdf.xacro",
                mappings={
                    "use_gazebo": "true",
                    "use_mock_hardware": "false",
                    "prefix": LaunchConfiguration("namespace"),
                    "ur_type": robot_model,
                    "force_abs_paths": "true",
                    "x": LaunchConfiguration("x"),
                    "y": LaunchConfiguration("y"),
                    "z": LaunchConfiguration("z"),
                    "roll": LaunchConfiguration("roll"),
                    "pitch": LaunchConfiguration("pitch"),
                    "yaw": LaunchConfiguration("yaw")
                },
            )
            .to_moveit_configs()
        )

    elif (robot_type=="kuka"):
        robot_model=config_params['kuka']['moveit_bringup_gazebo']['robot_model']
        robot_family=config_params['kuka']['moveit_bringup_gazebo']['robot_family']

        if(robot_family == "cybertech"): # quick fix, for preliminary dev, generalize later
            moveit_config_pkg="kuka_kr"


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
                    "mode": "gazebo" # mode gazebo => initializes gazebo plugin
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
            '-name', robot_type,
            '-allow_renaming', 'true',
        ])

    # Load controllers, different names for ur and kuka
    load_controllers = []
    if (robot_type == "ur"):
        controllers=["arm_controller","joint_state_broadcaster"]
    elif (robot_type == "kuka"):
        controllers=["joint_trajectory_controller","joint_state_broadcaster"]

    for controller in controllers:
        load_controllers += [
            ExecuteProcess(
                cmd=["ros2 run controller_manager spawner {}".format(controller)],
                shell=True,
                output="screen",
            )
        ]

    return LaunchDescription(
        [
            declare_world_cmd,
            declare_x_cmd,
            declare_y_cmd,
            declare_z_cmd,
            declare_roll_cmd,
            declare_pitch_cmd,
            declare_yaw_cmd,
            declare_ns_cmd,
            start_robot_state_publisher,
            start_move_group,
            start_rviz_cmd,
            start_gazebo_cmd,
            start_gazebo_ros_bridge_cmd,
            start_gazebo_ros_spawner_cmd,
        ]
        + load_controllers
    )
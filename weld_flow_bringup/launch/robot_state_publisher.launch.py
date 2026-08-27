from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
import yaml
from pathlib import Path
import os


def generate_launch_description(robot_type="kuka"):
    """ 
    Generates the launch description for robot visualization in RViz.
    This file launches:
        - robot_state_publisher node (to publish TF and /robot_description)
        - joint_state_publisher node 
        - joint_state_publisher_gui node
        - rviz (for visualization purposes)



    """

    #---Setting paths for importing files---#

    robot_type=os.environ.get("ROBOT_TYPE")

    # Find urdf package
    pkg_share_description = FindPackageShare('weld_flow_description')

    # Building the path to rviz config file
    rviz_config_path= PathJoinSubstitution(
        [pkg_share_description,'rviz','visualize.rviz']
    )

    #--Define dynamic launch configurations (values can be changed at runtime)--#
    # Each declaration of LaunchConfiguration is followed by DeclareLaunchArgument, where we declare the names (equivalent as in LaunchConfiguration) and define default and possible values

    #--Declare command-line arguments--#
    # Add them in command line launch arguments (DeclareLaunchArguments) .add_action() section


    # load config params
    bringup_config_path = (
        Path(get_package_share_directory("weld_flow_bringup"))
        / "config"
        / "bringup_params.yaml"
    )
    with open(bringup_config_path, "r") as f:
        config_params = yaml.load(f, Loader=yaml.SafeLoader)

    if (robot_type=="ur"):
        robot_model=config_params['ur']['robot_state_publisher']['robot_model']

        #--Defining top level urdf based on argument--#
        urdf_model_path = PathJoinSubstitution(
            [
                pkg_share_description,
                'urdf',
                'robots',
                [robot_model, ".urdf.xacro"]
            ])   

        robot_description_content = ParameterValue(Command([
            'xacro', ' ', urdf_model_path, ' ',
        ]), value_type=str)

    elif (robot_type=="kuka"):
        robot_model=config_params['kuka']['robot_state_publisher']['robot_model']
        robot_family=config_params['kuka']['robot_state_publisher']['robot_family']


        urdf_model_path = PathJoinSubstitution([
            FindPackageShare(f"kuka_{robot_family}_support"),
            "urdf",
            f"{robot_model}.urdf.xacro"
        ])

        # Generate the description parameter by processing xacro file
        robot_description_content = ParameterValue(Command([
            'xacro', ' ', urdf_model_path, ' ',
            "mode:=mock", " ",
            "use_gpio:=false", " "
        ]), value_type=str)
        

    #--Defining nodes--#

    # Node publishes the TF tree and the /robot_description parameter to the ROS2 system

    start_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}]
                     
    )

    start_joint_state_publisher_cmd = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
        )
    

    start_joint_state_publisher_gui_cmd = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        )
    
    start_rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path]
    )

    

    # Create launch description and populate with arguments
    ld = LaunchDescription()

    # Add command line launch arguments (DeclareLaunchArguments)
    #ld.add_action(declare_robot_model_cmd)
    #ld.add_action(declare_prefix_cmd)

    # Add nodes to launch (Node)
    ld.add_action(start_robot_state_publisher)
    ld.add_action(start_joint_state_publisher_cmd)
    ld.add_action(start_joint_state_publisher_gui_cmd)
    ld.add_action(start_rviz_cmd)


    return ld
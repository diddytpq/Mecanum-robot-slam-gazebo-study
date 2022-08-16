# Mecanum-robot-slam-gazebo

## Dependencies
#### ceres-solver-1.14.0

### build && Setup
```bash
catkin_make_isolated --install --use-ninja -DPYTHON_EXECUTABLE=/usr/bin/python3
. install_isolated/setup.bash
```


### Gazebo simulation
```bash
roslaunch mecanum_robot_gazebo mecanum_slam_world.launch
```


### Gazebo simulation
```bash
roslaunch mecanum_robot_slam mecanum_gmapping.launch

roslaunch mecanum_robot_slam mecanum_cartographer.launch

```

### Save Map
```bash
rosrun map_server map_server mymap.yaml
```


### mecanum navigation
```bash
roslaunch mecanum_robot_navigation mecanum_navigation.launch
```


### far planner example
```bash
roslaunch vehicle_simulator system_campus.launch
roslaunch far_planner far_planner.launch
```


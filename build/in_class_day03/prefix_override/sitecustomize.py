import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/aditilagisetty/ros2_ws/src/class_activities_and_resources/install/in_class_day03'

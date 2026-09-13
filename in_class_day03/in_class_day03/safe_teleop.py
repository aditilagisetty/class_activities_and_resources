import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from neato2_interfaces.msg import Bump

# gz-sim's contact sensor only publishes while contact is ongoing -- it goes
# silent (no "cleared" message) once contact ends, so a bump can't be treated
# as clear just because no new message arrived. Instead treat it as cleared
# once this long has passed since the last bump reading.
BUMP_TIMEOUT_SEC = 0.3

class SafeTeleopNode(Node):
    """Sits between teleop and the robot: passes commands through from
    'cmd_vel_raw' to 'cmd_vel', but blocks forward motion while something is
    within stop_distance in front of the robot (laser) or the robot is
    currently touching something (bump). Turning and backing up are always
    allowed, so you can steer away from what you got too close to or bumped.
    """

    def __init__(self):
        super().__init__('safe_teleop_node')
        self.stop_distance = 0.5
        self.too_close = False
        self.bumped = False
        self.last_bump_time = None
        self.create_subscription(Twist, 'cmd_vel_raw', self.process_cmd, 10)
        self.create_subscription(LaserScan, 'scan', self.process_scan, 10)
        self.create_subscription(Bump, 'bump', self.process_bump, 10)
        self.vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.create_timer(0.1, self.check_bump_timeout)

    def process_scan(self, msg):
        front_range = msg.ranges[0]
        was_too_close = self.too_close
        self.too_close = 0.0 < front_range < self.stop_distance
        if self.too_close and not was_too_close:
            print(f"Obstacle detected {front_range:.2f}m ahead, blocking forward motion!")
        elif was_too_close and not self.too_close and not self.bumped:
            print("Clear, forward motion allowed again.")

    def process_bump(self, msg):
        if msg.left_front or msg.left_side or msg.right_front or msg.right_side:
            self.last_bump_time = time.monotonic()
            if not self.bumped:
                self.bumped = True
                print("Bump detected, blocking forward motion!")

    def check_bump_timeout(self):
        if self.bumped and time.monotonic() - self.last_bump_time > BUMP_TIMEOUT_SEC:
            self.bumped = False
            if not self.too_close:
                print("Clear, forward motion allowed again.")

    def process_cmd(self, msg):
        out = Twist()
        out.angular.z = msg.angular.z
        if (self.too_close or self.bumped) and msg.linear.x > 0.0:
            out.linear.x = 0.0
        else:
            out.linear.x = msg.linear.x
        print(f"linear.x={out.linear.x:.2f}  angular.z={out.angular.z:.2f}")
        self.vel_pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = SafeTeleopNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

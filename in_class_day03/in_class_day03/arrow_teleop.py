import os
import select
import sys
import termios
import tty
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

HELP = """
Arrow key teleop
---------------------------
Up / Down    : drive forward / backward
Left / Right : turn left / right
Space        : stop
CTRL-C       : quit

Publishes to 'cmd_vel_raw' (goes through safe_teleop's obstacle check).
"""

# arrow keys arrive as a 3-byte escape sequence, either CSI (ESC [ A/B/C/D,
# the common case) or SS3 (ESC O A/B/C/D, sent by some terminals depending on
# cursor-key mode) -- handle both so this isn't terminal-dependent.
MOVE_BINDINGS = {
    '\x1b[A': (1, 0),
    '\x1bOA': (1, 0),
    '\x1b[B': (-1, 0),
    '\x1bOB': (-1, 0),
    '\x1b[C': (0, -1),
    '\x1bOC': (0, -1),
    '\x1b[D': (0, 1),
    '\x1bOD': (0, 1),
}

def get_key(fd, timeout):
    # Read straight from the raw file descriptor with os.read(), not
    # sys.stdin.read() -- sys.stdin is a buffered TextIOWrapper, and mixing
    # select() (which watches the kernel buffer) with a buffered read()
    # desyncs them: TextIOWrapper can silently slurp extra already-arrived
    # bytes of an escape sequence into its own internal buffer, so a
    # follow-up select() sees the kernel buffer as empty and reports
    # "nothing to read" even though the rest of the sequence already arrived.
    rlist, _, _ = select.select([fd], [], [], timeout)
    if not rlist:
        return ''
    key = os.read(fd, 1).decode()
    if key == '\x1b':
        rlist, _, _ = select.select([fd], [], [], 0.1)
        if rlist:
            key += os.read(fd, 2).decode()
    return key

def main(args=None):
    fd = sys.stdin.fileno()
    settings = termios.tcgetattr(fd)
    rclpy.init(args=args)
    node = rclpy.create_node('arrow_teleop')
    pub = node.create_publisher(Twist, 'cmd_vel_raw', 10)

    speed = 0.2
    turn = 1.0
    print(HELP)
    try:
        tty.setraw(fd)
        while True:
            key = get_key(fd, 0.5)
            if key == '':
                continue
            twist = Twist()
            if key in MOVE_BINDINGS:
                linear, angular = MOVE_BINDINGS[key]
                twist.linear.x = linear * speed
                twist.angular.z = angular * turn
            elif key == ' ':
                print("stop")
            elif key == '\x03':
                break
            else:
                print(f"unrecognized key: {key!r}")
                continue
            pub.publish(twist)
    finally:
        pub.publish(Twist())
        termios.tcsetattr(fd, termios.TCSADRAIN, settings)
        rclpy.shutdown()

if __name__ == '__main__':
    main()

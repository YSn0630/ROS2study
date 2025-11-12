import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import termios
import tty
import select

class TurtleTeleop(Node):
    def __init__(self):
        super().__init__('turtle_teleop')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.linear_speed = 2.0
        self.angular_speed = 2.0
        self.twist = Twist()
        self.get_logger().info("Turtle Teleop 시작 (W/A/S/D로 조작, Space:정지, Q:종료)")

    def get_key(self, timeout=0.1):
        """Non-blocking getch for WSL terminal"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if rlist:
                key = sys.stdin.read(1)
            else:
                key = ''
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

    def run(self):
        try:
            while rclpy.ok():
                key = self.get_key()
                if key:
                    key = key.lower()
                    if key == 'w':       # 앞으로
                        self.twist.linear.x = self.linear_speed
                        self.twist.angular.z = 0.0
                    elif key == 's':     # 뒤로
                        self.twist.linear.x = -self.linear_speed
                        self.twist.angular.z = 0.0
                    elif key == 'a':     # 좌회전
                        self.twist.linear.x = 0.0
                        self.twist.angular.z = self.angular_speed
                    elif key == 'd':     # 우회전
                        self.twist.linear.x = 0.0
                        self.twist.angular.z = -self.angular_speed
                    elif key == ' ':     # 정지
                        self.twist.linear.x = 0.0
                        self.twist.angular.z = 0.0
                    elif key == 'q':     # 종료
                        self.get_logger().info("Teleop 종료 중...")
                        break

                    self.publisher.publish(self.twist)

                # 약간의 sleep으로 CPU 점유율 낮춤
                rclpy.spin_once(self, timeout_sec=0.01)

        except KeyboardInterrupt:
            self.get_logger().info("KeyboardInterrupt로 종료")
        finally:
            self.twist.linear.x = 0.0
            self.twist.angular.z = 0.0
            self.publisher.publish(self.twist)
            self.destroy_node()
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = TurtleTeleop()
    node.run()


if __name__ == '__main__':
    main()

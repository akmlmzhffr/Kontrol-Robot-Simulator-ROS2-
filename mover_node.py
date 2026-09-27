import math

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist
from rosgraph_msgs.msg import Clock


class MoverNode(Node):
    def __init__(self):
        super().__init__('mover_node')

        # Gunakan simulation time dari /clock.
        self.set_parameters([
            Parameter('use_sim_time', Parameter.Type.BOOL, True)
        ])

        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.clock_sub_ = self.create_subscription(
            Clock, '/clock', self.clock_callback, 10
        )
        self.timer = self.create_timer(0.02, self.timer_callback)

        # Kecepatan
        self.linear_speed = 1.0       # m/s
        self.angular_speed = 0.5      # rad/s

        # Ukuran persegi panjang
        self.length = 6.0             # meter
        self.width = 3.0              # meter

        # Jeda agar robot benar-benar berhenti sebelum belok / maju lagi
        self.pause_time = 0.35        # detik simulasi

        # Durasi gerakan
        self.forward_length_time = self.length / self.linear_speed
        self.forward_width_time = self.width / self.linear_speed
        self.turn_90_time = (math.pi / 2.0) / self.angular_speed

        # State:
        # 0 = MAJU 6 m
        # 1 = STOP
        # 2 = PUTAR 90
        # 3 = STOP
        # 4 = MAJU 3 m
        # 5 = STOP
        # 6 = PUTAR 90
        # 7 = STOP
        # 8 = MAJU 6 m
        # 9 = STOP
        # 10 = PUTAR 90
        # 11 = STOP
        # 12 = MAJU 3 m
        # 13 = SELESAI
        self.state = 0
        self.state_start = None
        self.last_log_state = None
        self.started = False
        self.finished = False

        self.get_logger().info('Mover Node siap.')
        self.get_logger().info('Lintasan: 6 m -> 90 -> 3 m -> 90 -> 6 m -> 90 -> 3 m')
        self.get_logger().info('Gerakan PERTAMA dipastikan MAJU 6 meter.')

    @staticmethod
    def clock_to_sec(clock_msg):
        return float(clock_msg.clock.sec) + float(clock_msg.clock.nanosec) * 1e-9

    def clock_callback(self, msg):
        # Hanya digunakan untuk mengambil waktu simulasi terbaru.
        self.sim_time = self.clock_to_sec(msg)

        if not self.started:
            self.started = True
            self.state_start = self.sim_time
            self.state = 0
            self.publish_command(self.linear_speed, 0.0)
            self.log_state()

    def elapsed(self):
        if self.state_start is None:
            return 0.0
        return self.sim_time - self.state_start

    def change_state(self, new_state):
        self.state = new_state
        self.state_start = self.sim_time
        self.log_state()

    def log_state(self):
        if self.state == self.last_log_state:
            return
        self.last_log_state = self.state

        messages = {
            0: '1. MAJU 6 meter',
            1: '2. STOP sebelum belok',
            2: '3. PUTAR 90 derajat',
            3: '4. STOP setelah belok',
            4: '5. MAJU 3 meter',
            5: '6. STOP sebelum belok',
            6: '7. PUTAR 90 derajat',
            7: '8. STOP setelah belok',
            8: '9. MAJU 6 meter',
            9: '10. STOP sebelum belok',
            10: '11. PUTAR 90 derajat',
            11: '12. STOP setelah belok',
            12: '13. MAJU 3 meter',
            13: '14. SELESAI - ROBOT BERHENTI',
        }
        self.get_logger().info(messages.get(self.state, 'State tidak dikenal'))

    def publish_command(self, linear_x, angular_z):
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        self.publisher_.publish(msg)

    def timer_callback(self):
        if not hasattr(self, 'sim_time') or not self.started or self.finished:
            self.publish_command(0.0, 0.0)
            return

        e = self.elapsed()

        # MAJU 6 m — fase pertama selalu dimulai dari sini.
        if self.state == 0:
            self.publish_command(self.linear_speed, 0.0)
            if e >= self.forward_length_time:
                self.change_state(1)

        # STOP sebelum belok
        elif self.state == 1:
            self.publish_command(0.0, 0.0)
            if e >= self.pause_time:
                self.change_state(2)

        # PUTAR 90 derajat di tempat
        elif self.state == 2:
            self.publish_command(0.0, self.angular_speed)
            if e >= self.turn_90_time:
                self.change_state(3)

        # STOP setelah belok
        elif self.state == 3:
            self.publish_command(0.0, 0.0)
            if e >= self.pause_time:
                self.change_state(4)

        # MAJU 3 m
        elif self.state == 4:
            self.publish_command(self.linear_speed, 0.0)
            if e >= self.forward_width_time:
                self.change_state(5)

        # STOP sebelum belok
        elif self.state == 5:
            self.publish_command(0.0, 0.0)
            if e >= self.pause_time:
                self.change_state(6)

        # PUTAR 90 derajat di tempat
        elif self.state == 6:
            self.publish_command(0.0, self.angular_speed)
            if e >= self.turn_90_time:
                self.change_state(7)

        # STOP setelah belok
        elif self.state == 7:
            self.publish_command(0.0, 0.0)
            if e >= self.pause_time:
                self.change_state(8)

        # MAJU 6 m
        elif self.state == 8:
            self.publish_command(self.linear_speed, 0.0)
            if e >= self.forward_length_time:
                self.change_state(9)

        # STOP sebelum belok
        elif self.state == 9:
            self.publish_command(0.0, 0.0)
            if e >= self.pause_time:
                self.change_state(10)

        # PUTAR 90 derajat di tempat
        elif self.state == 10:
            self.publish_command(0.0, self.angular_speed)
            if e >= self.turn_90_time:
                self.change_state(11)

        # STOP setelah belok
        elif self.state == 11:
            self.publish_command(0.0, 0.0)
            if e >= self.pause_time:
                self.change_state(12)

        # MAJU 3 m
        elif self.state == 12:
            self.publish_command(self.linear_speed, 0.0)
            if e >= self.forward_width_time:
                self.change_state(13)

        # SELESAI
        elif self.state == 13:
            self.publish_command(0.0, 0.0)
            self.finished = True
            self.timer.cancel()
            self.get_logger().info('Lintasan persegi panjang selesai.')


def main(args=None):
    rclpy.init(args=args)
    node = MoverNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Pastikan robot berhenti.
        node.publish_command(0.0, 0.0)
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()

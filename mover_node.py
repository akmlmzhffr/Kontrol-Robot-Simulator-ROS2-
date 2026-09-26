import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import math

class MoverNode(Node):
    def __init__(self):
        super().__init__('mover_node')
        
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.start_time = time.time()

        # Pengaturan Kecepatan
        self.linear_speed = 1.0   # m/s (5 cm/s)
        self.angular_speed = 1.0   # rad/s

        # Perhitungan Durasi Waktu (Waktu = Jarak / Kecepatan)
        t_maju_5 = 5.0 / self.linear_speed              # Maju 5m
        t_maju_10 = 10.0 / self.linear_speed             # Maju 10m
        t_putar_90 = (math.pi / 2) / self.angular_speed  # Putar 90° (~1.57 rad)

        # Akumulasi batas waktu untuk setiap langkah
        self.t1 = t_maju_5
        self.t2 = self.t1 + t_putar_90
        self.t3 = self.t2 + t_maju_10
        self.t4 = self.t3 + t_putar_90
        self.t5 = self.t4 + t_maju_5
        self.t6 = self.t5 + t_putar_90
        self.t7 = self.t6 + t_maju_10

    def timer_callback(self):
        msg = Twist()
        elapsed_time = time.time() - self.start_time

        if elapsed_time < self.t1:
            msg.linear.x = self.linear_speed
            msg.angular.z = 0.0
            self.get_logger().info('1. Maju 5m')
            
        elif elapsed_time < self.t2:
            msg.linear.x = 0.0
            msg.angular.z = self.angular_speed
            self.get_logger().info('2. Putar 90 derajat')
            
        elif elapsed_time < self.t3:
            msg.linear.x = self.linear_speed
            msg.angular.z = 0.0
            self.get_logger().info('3. Maju 10m')
            
        elif elapsed_time < self.t4:
            msg.linear.x = 0.0
            msg.angular.z = self.angular_speed
            self.get_logger().info('4. Putar 90 derajat')
            
        elif elapsed_time < self.t5:
            msg.linear.x = self.linear_speed
            msg.angular.z = 0.0
            self.get_logger().info('5. Maju 5m')
            
        elif elapsed_time < self.t6:
            msg.linear.x = 0.0
            msg.angular.z = self.angular_speed
            self.get_logger().info('6. Putar 90 derajat')
            
        elif elapsed_time < self.t7:
            msg.linear.x = self.linear_speed
            msg.angular.z = 0.0
            self.get_logger().info('7. Maju 10m')
            
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info('8. Berhenti.')
            self.publisher_.publish(msg)
            
            self.timer.cancel()
            rclpy.shutdown()
            return

        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MoverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()

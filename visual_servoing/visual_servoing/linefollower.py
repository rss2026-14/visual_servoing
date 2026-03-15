#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import numpy as np

from vs_msgs.msg import ConeLocation, ParkingError
from ackermann_msgs.msg import AckermannDriveStamped

class LineFollower(Node):
    """
    A controller for parking in front of a cone.
    Listens for a relative cone location and publishes control commands.
    Can be used in the simulator and on the real robot.
    """

    def __init__(self):
        super().__init__("line_follower")

        self.declare_parameter("drive_topic")
        DRIVE_TOPIC = self.get_parameter("drive_topic").value  # set in launch file; different for simulator vs racecar

        self.declare_parameter("angle_multiplier", 2.5)
        self.declare_parameter("velocity", 0.7)
        self.declare_parameter("reverse_range", 0.1)
        self.angle_multiplier = self.get_parameter("angle_multiplier").value
        self.reverse_range = self.get_parameter("reverse_range").value
        self.velocity = self.get_parameter("velocity").value

        self.drive_pub = self.create_publisher(AckermannDriveStamped, DRIVE_TOPIC, 10)
        self.error_pub = self.create_publisher(ParkingError, "/parking_error", 10)

        self.create_subscription(
            ConeLocation, "/relative_cone", self.relative_cone_callback, 1)

        self.parking_distance = .75  # meters; try playing with this number!
        self.relative_x = 0.0
        self.relative_y = 0.0
        self.lookahead_distance = 1.5

        self.get_logger().info("Line Follower Initialized")

    def relative_cone_callback(self, msg):
        # pretend cone is ahead
        self.relative_x = self.lookahead_distance

        # lateral offset from line
        self.relative_y = msg.y_pos * 0.5

        drive_cmd = AckermannDriveStamped()

        #################################

        # YOUR CODE HERE
        # Use relative position and your control law to set drive_cmd

        #################################
        angle = np.arctan2(self.relative_y, self.relative_x)

        # always drive forward
        velocity = self.velocity
        
        # steer toward the "virtual cone"
        steering_angle = self.angle_multiplier * angle

        steering_angle = np.clip(steering_angle, -0.34, 0.34)

        drive_cmd.header.stamp = self.get_clock().now().to_msg()
        drive_cmd.header.frame_id = 'base_link'
        drive_cmd.drive.speed = velocity
        drive_cmd.drive.steering_angle = steering_angle
        self.drive_pub.publish(drive_cmd)
        self.error_publisher()

    def error_publisher(self):
        """
        Publish the error between the car and the cone. We will view this
        with rqt_plot to plot the success of the controller
        """
        error_msg = ParkingError()

        #################################

        # YOUR CODE HERE
        # Populate error_msg with relative_x, relative_y, sqrt(x^2+y^2)

        #################################

        error_msg.x_error = self.relative_x - self.parking_distance
        error_msg.y_error = self.relative_y
        error_msg.distance_error = np.sqrt(self.relative_x**2 + self.relative_y**2) - self.parking_distance

        self.error_pub.publish(error_msg)


def main(args=None):
    rclpy.init(args=args)
    lf = LineFollower()
    rclpy.spin(lf)
    rclpy.shutdown()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import numpy as np

import cv2
from cv_bridge import CvBridge, CvBridgeError

from sensor_msgs.msg import Image
from geometry_msgs.msg import Point #geometry_msgs not in CMake file
from vs_msgs.msg import ConeLocationPixel

# import your color segmentation algorithm; call this function in ros_image_callback!
import color_segmentation
from color_segmentation import cd_color_segmentation


class ConeDetector(Node):
    """
    A class for applying your cone detection algorithms to the real robot.
    Subscribes to: /zed/zed_node/rgb/image_rect_color (Image) : the live RGB image from the onboard ZED camera.
    Publishes to: /relative_cone_px (ConeLocationPixel) : the coordinates of the cone in the image frame (units are pixels).
    """

    def __init__(self):
        super().__init__("cone_detector")
        # toggle line follower vs cone parker
        self.LineFollower = False

        # Subscribe to ZED camera RGB frames
        self.cone_pub = self.create_publisher(ConeLocationPixel, "/relative_cone_px", 10)
        self.debug_pub = self.create_publisher(Image, "/cone_debug_img", 10)
        self.image_sub = self.create_subscription(Image, "/zed/zed_node/rgb/image_rect_color", self.image_callback, 5)
        self.bridge = CvBridge()  # Converts between ROS images and OpenCV Images

        self.get_logger().info("Cone Detector Initialized")

    def image_callback(self, image_msg):
        # Apply your imported color segmentation function (cd_color_segmentation) to the image msg here
        # From your bounding box, take the center pixel on the bottom
        # (We know this pixel corresponds to a point on the ground plane)
        # publish this pixel (u, v) to the /relative_cone_px topic; the homography transformer will
        # convert it to the car frame.

        #################################
        # YOUR CODE HERE
        # detect the cone and publish its
        # pixel location in the image.
        # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        #################################
        # Convert ROS image message to OpenCV image
        try:
            image = self.bridge.imgmsg_to_cv2(image_msg, "bgr8")
        except CvBridgeError as e:
            self.get_logger().error(f"Failed to convert image: {e}")
            return

        # Get bounding box from color segmentation
        # The function returns ((x1, y1), (x2, y2))
        bounding_box = cd_color_segmentation(image)

        # Create message to publish
        cone_px_msg = ConeLocationPixel()

        if bounding_box is not None:
            # Extract bounding box coordinates from the tuple of tuples format
            (x_min, y_min), (x_max, y_max) = bounding_box

            # Calculate bottom center pixel
            # This point is on the ground plane where the cone touches the ground
            u = (x_min + x_max) // 2  # center x coordinate
            v = y_max  # bottom y coordinate

            # Fill the message
            cone_px_msg.u = float(u)
            cone_px_msg.v = float(v)

            # Draw debug visualization
            # Draw bounding box
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            # Draw bottom center point
            cv2.circle(image, (u, v), 5, (0, 0, 255), -1)
            # Add text
            cv2.putText(image, f"({u}, {v})", (u + 10, v - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            self.get_logger().info(f"Detected cone at pixel: ({u}, {v})")
        else:
            # No cone detected, publish sentinel values
            cone_px_msg.u = -1.0
            cone_px_msg.v = -1.0

            self.get_logger().info("No cone detected")

        # Publish cone pixel location
        self.cone_pub.publish(cone_px_msg)

        # Publish debug image
        try:
            debug_msg = self.bridge.cv2_to_imgmsg(image, "bgr8")
            self.debug_pub.publish(debug_msg)
        except CvBridgeError as e:
            self.get_logger().error(f"Failed to convert debug image: {e}")



def main(args=None):
    rclpy.init(args=args)
    cone_detector = ConeDetector()
    rclpy.spin(cone_detector)
    rclpy.shutdown()


if __name__ == '__main__':
    main()

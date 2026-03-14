#!/usr/bin/env python3
"""
Publishes pixel coordinates (u, v) as PointStamped when you click on the image.
Use this to test the homography transformer when rqt_image_view's mouse topic
doesn't work.

Usage:
  ros2 run visual_servoing image_click_publisher

Then click on the image window. Each click publishes to the output topic
(default: /image_click) which the homography_transformer can subscribe to.
"""

import rclpy
from rclpy.node import Node
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from geometry_msgs.msg import PointStamped


class ImageClickPublisher(Node):
    def __init__(self):
        super().__init__("image_click_publisher")

        self.image_topic = (
            self.declare_parameter(
                "image_topic",
                "/zed/zed_node/left/image_rect_color",
            )
            .get_parameter_value()
            .string_value
        )
        self.output_topic = (
            self.declare_parameter(
                "output_topic",
                "/image_click",
            )
            .get_parameter_value()
            .string_value
        )

        self.bridge = CvBridge()
        self.latest_image = None
        self.window_name = "Click on image (close window to exit)"

        self.sub = self.create_subscription(
            Image, self.image_topic, self.image_callback, 10
        )
        self.pub = self.create_publisher(PointStamped, self.output_topic, 10)

        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.on_mouse)

        self.timer = self.create_timer(0.033, self.display_callback)  # ~30 Hz
        self.shutdown = False

        self.get_logger().info(
            f"Subscribed to {self.image_topic}, publishing clicks to {self.output_topic}"
        )
        self.get_logger().info("Click on the image, then check RViz for the marker.")

    def image_callback(self, msg):
        try:
            self.latest_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"cv_bridge error: {e}")

    def on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and self.latest_image is not None:
            msg = PointStamped()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "zed_left_camera_optical_frame"
            msg.point.x = float(x)
            msg.point.y = float(y)
            msg.point.z = 0.0
            self.pub.publish(msg)
            self.get_logger().info(f"Published click: u={x}, v={y}")

    def display_callback(self):
        if self.latest_image is not None:
            cv2.imshow(self.window_name, self.latest_image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            self.shutdown = True
        try:
            if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                self.shutdown = True
        except cv2.error:
            pass


def main(args=None):
    rclpy.init(args=args)
    node = ImageClickPublisher()
    try:
        while rclpy.ok() and not node.shutdown:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

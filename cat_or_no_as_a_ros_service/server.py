#!/usr/bin/env python3

import rclpy, random, requests
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from cat_or_no_as_a_ros_service.srv import CatOrNo
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2 as cv
import numpy as np

class CatOrNoAsARosServiceNode(Node):
    def __init__(self):
        super().__init__('cat_or_no_as_a_ros_service')
        self.srv = self.create_service(CatOrNo, 'cat_or_no', self.cat_or_no_callback)
        qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE
        )
        self.topic = self.create_publisher(Image, '/cat', qos)
        self.bridge = CvBridge()
        self.log = self.get_logger()
        self.log.info('meow')
    
    def cat_or_no_callback(self, request: CatOrNo, response: CatOrNo):
        def no():
            res = requests.get('https://naas.isalman.dev/no')
            reason = res.json()['reason']
            response.no = reason

            msg = Image()
            msg.header.stamp = stamp
            msg.header.frame_id = frame_id

            self.log.info(reason)
            return msg

        choice = random.randint(0, 1)
        response.result_type = choice
        stamp = self.get_clock().now().to_msg()
        frame_id = 'cat'

        if choice == 1: # cat
            try:
                res = requests.get('https://cataas.com/cat', headers={'accept': 'application/json'})
                img_url = res.json()['url']
                res = requests.get(img_url)
                img_bytes = res.content
                np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
                cv_img = cv.imdecode(np_arr, cv.IMREAD_COLOR)
                ros_img = self.bridge.cv2_to_imgmsg(cv_img, encoding='bgr8')

                response.cat.image = ros_img
                response.cat.image.header.stamp = stamp
                response.cat.image.header.frame_id = frame_id
                response.cat.url = img_url

                msg = ros_img
                msg.header.stamp = stamp
                msg.header.frame_id = frame_id

                self.log.info('meow')
            except Exception as e:
                self.log.info(e)
                msg = no()
        else: # no
            msg = no()

        self.topic.publish(msg)
        return response


def main(args=None):
    rclpy.init(args=args)

    node = CatOrNoAsARosServiceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
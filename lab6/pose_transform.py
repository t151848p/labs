#!/usr/bin/env python3

'''
This is starter code for Lab 6 on Coordinate Frame transforms.

'''

import asyncio
import cozmo
import time
import numpy
from cozmo.util import degrees
import math
import numpy as np

def get_relative_pose(object_pose, reference_frame_pose):
	# ####
	# TODO: Implement computation of the relative frame using numpy.
	# Try to derive the equations yourself and verify by looking at
	# the books or slides before implementing.
	# ####

	# print("Absolute cube pose: x %i y %i" % (object_pose.position.x, object_pose.position.y))
	# # print("Absolute cube rotation: %i" % object_pose.rotation.euler_angles[1])
	# print("Absolute cube rotation angle z: %s" % object_pose.rotation.angle_z)
    
    # (x0,y0,z0) (last column in translation matrix) marks the origin, by subtracting the x/y/z from the reference point
	translation = np.matrix([[1, 0, 0, -reference_frame_pose.position.x],
							 [0, 1, 0, -reference_frame_pose.position.y],
							 [0, 0, 1, -reference_frame_pose.position.z],
							 [0, 0, 0, 1]])

	objectVector = np.matrix([[object_pose.position.x,
								object_pose.position.y,
								object_pose.position.z,
								1]]).T

	originRotationRadians = -reference_frame_pose.rotation.angle_z.radians
	rotation = np.matrix([[math.cos(originRotationRadians), -math.sin(originRotationRadians), 0, 0],
							[math.sin(originRotationRadians), math.cos(originRotationRadians), 0, 0],
							[0, 0, 1, 0],
							[0, 0, 0, 1]])

	objectRelativeReference = (rotation * translation * objectVector).A1
	return cozmo.util.pose_z_angle(objectRelativeReference[0],
								   objectRelativeReference[1],
								   objectRelativeReference[2],
								   cozmo.util.radians(object_pose.rotation.angle_z.radians + originRotationRadians))

def find_relative_cube_pose(robot: cozmo.robot.Robot):
	'''Looks for a cube while sitting still, prints the pose of the detected cube
	in world coordinate frame and relative to the robot coordinate frame.'''

	robot.move_lift(-3)
	robot.set_head_angle(degrees(0)).wait_for_completed()
	cube = None

	while True:
		try:
			cube = robot.world.wait_for_observed_light_cube(timeout=30)
			if cube:
				get_relative_pose(cube.pose, robot.pose)
				time.sleep(1)
				print("Robot pose: %s" % robot.pose)
				print("Cube pose: %s" % cube.pose)
				print("Cube pose in the robot coordinate frame: %s" % get_relative_pose(cube.pose, robot.pose))
		except asyncio.TimeoutError:
			print("Didn't find a cube")


if __name__ == '__main__':

	cozmo.run_program(find_relative_cube_pose)

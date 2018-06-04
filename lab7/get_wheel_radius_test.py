#!/usr/bin/env python3

'''
This is starter code for Lab 6 on Coordinate Frame transforms.

'''

import asyncio
import cozmo
import time
import numpy
from cozmo.util import degrees

def drive_test(robot: cozmo.robot.Robot):
	"""Returns the radius of the Cozmo robot's front wheel in millimeters."""
	# Kept driving over and over, changing the distance/speed to see how far one rotation is
	robot.drive_straight(distance=cozmo.util.distance_mm(3*83.73), speed=cozmo.util.speed_mmps(200), should_play_anim=False).wait_for_completed()
	# One rotation is around 82mm (at faster speeds, slower speeds have to deal with static friction

	# ####
	# TODO: Empirically determine the radius of the robot's front wheel using the
	# cozmo_drive_straight() function. You can write a separate script for doing 
	# experiments to determine the radius. This function should return the radius
	# in millimeters. Write a comment that explains how you determined it and any
	# computation you do as part of this function.
	# ####

def get_distance_between_wheels_test(robot: cozmo.robot.Robot):
	"""Returns the distance between the wheels of the Cozmo robot in millimeters."""
	# ####
	# TODO: Empirically determine the distance between the wheels of the robot using
	# robot.drive_wheels() function. Write a comment that explains how you determined
	# it and any computation you do as part of this function.
	# ####
	
	initialAngleZ = robot.pose.rotation.angle_z
	robot.drive_wheels(100,-100)
	time.sleep(3.33623)
	robot.drive_wheels(0,0)

if __name__ == '__main__':

	# cozmo.run_program(drive_test)
	cozmo.run_program(get_distance_between_wheels_test)
	# cozmo.run_program(find_relative_cube_pose)

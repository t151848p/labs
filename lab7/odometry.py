#!/usr/bin/env python3

'''
Stater code for Lab 7.

'''

import cozmo
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps
import math
import time

# Wrappers for existing Cozmo navigation functions

def cozmo_drive_straight(robot, dist, speed):
	"""Drives the robot straight.
		Arguments:
		robot -- the Cozmo robot instance passed to the function
		dist -- Desired distance of the movement in millimeters
		speed -- Desired speed of the movement in millimeters per second
	"""
	robot.drive_straight(distance_mm(dist), speed_mmps(speed)).wait_for_completed()

def cozmo_turn_in_place(robot, angle, speed):
	"""Rotates the robot in place.
		Arguments:
		robot -- the Cozmo robot instance passed to the function
		angle -- Desired distance of the movement in degrees
		speed -- Desired speed of the movement in degrees per second
	"""
	robot.turn_in_place(degrees(angle), speed=degrees(speed)).wait_for_completed()

def cozmo_go_to_pose(robot, x, y, angle_z):
	"""Moves the robot to a pose relative to its current pose.
		Arguments:
		robot -- the Cozmo robot instance passed to the function
		x,y -- Desired position of the robot in millimeters
		angle_z -- Desired rotation of the robot around the vertical axis in degrees
	"""
	robot.go_to_pose(Pose(x, y, 0, angle_z=degrees(angle_z)), relative_to_robot=True).wait_for_completed()

# Functions to be defined as part of the labs

def get_front_wheel_radius():
	"""Returns the radius of the Cozmo robot's front wheel in millimeters."""
	# ####
	# TODO: Empirically determine the radius of the robot's front wheel using the
	# cozmo_drive_straight() function. You can write a separate script for doing 
	# experiments to determine the radius. This function should return the radius
	# in millimeters. Write a comment that explains how you determined it and any
	# computation you do as part of this function.
	# ####

	# Kept driving over and over, changing the distance/speed to see how far one rotation is (see get_wheel_radius_test.py)
	# One rotation is 2pi * radius distance, I empircally found that a rotation goes about 83.73mm.
	# I used a piece of paper stuck in the wheel to visually notice when a rotation had completed.
	return 83.73 / (2 * math.pi)

def get_distance_between_wheels():
	"""Returns the distance between the wheels of the Cozmo robot in millimeters."""
	# ####
	# TODO: Empirically determine the distance between the wheels of the robot using
	# robot.drive_wheels() function. Write a comment that explains how you determined
	# it and any computation you do as part of this function.
	# ####
	
	# I spun the robot in a point turn so both left/right motors go in equal magnitude/opposite direction.
	# The circle it makes has a diameter of the distance between the wheels. Found that at 100mms, it finished the circle in 3.33623s.
	# The full distance of the circumference of the circle is diameter * pi and it traveled 100mm/s * 3.33623s = 333.623mm.
	# That means the diameter (distance between the wheels) is 333.623mm / pi
	return 333.623 / math.pi

def rotate_front_wheel(robot, angle_deg):
	"""Rotates the front wheel of the robot by a desired angle.
		Arguments:
		robot -- the Cozmo robot instance passed to the function
		angle_deg -- Desired rotation of the wheel in degrees
	"""
	# ####
	# TODO: Implement this function.
	# ####
	robot.drive_straight(distance=cozmo.util.distance_mm(2*math.pi*get_front_wheel_radius() * (angle_deg / 360.0)), speed=cozmo.util.speed_mmps(200), should_play_anim=False).wait_for_completed()

def my_drive_straight(robot, dist, speed):
	"""Drives the robot straight.
		Arguments:
		robot -- the Cozmo robot instance passed to the function
		dist -- Desired distance of the movement in millimeters
		speed -- Desired speed of the movement in millimeters per second
	"""
	# ####
	# TODO: Implement your version of a driving straight function using the
	# robot.drive_wheels() function.
	# ####
	timeToWait = dist / abs(speed)
	robot.drive_wheels(speed, speed, duration=timeToWait)
	# time.sleep(timeToWait)
	robot.stop_all_motors()
	# robot.drive_wheels(0, 0)

def my_turn_in_place(robot, angle, speed):
	"""Rotates the robot in place.
		Arguments:
		robot -- the Cozmo robot instance passed to the function
		angle -- Desired distance of the movement in degrees
		speed -- Desired speed of the movement in degrees per second
	"""
	# ####
	# TODO: Implement your version of a rotating in place function using the
	# robot.drive_wheels() function.
	# ####
	normalizedAngle = angle % 360
	turnLeft = normalizedAngle <= 180
	innerAngle = normalizedAngle if turnLeft else 360 - normalizedAngle

	dist = get_distance_between_wheels() * math.pi * (innerAngle/360.0)
	timeToWait = dist / (speed * 1.0)
	
	turnLeftTransformation = -1 if turnLeft else 1
	robot.drive_wheels(turnLeftTransformation * speed, -1 * turnLeftTransformation * speed, duration=timeToWait)
	# time.sleep(timeToWait)
	robot.drive_wheels(0, 0)
	robot.stop_all_motors()

def my_go_to_pose1(robot, x, y, angle_z):
	"""Moves the robot to a pose relative to its current pose.
		Arguments:
		robot -- the Cozmo robot instance passed to the function
		x,y -- Desired position of the robot in millimeters
		angle_z -- Desired rotation of the robot around the vertical axis in degrees
	"""
	# ####
	# TODO: Implement a function that makes the robot move to a desired pose
	# using the my_drive_straight and my_turn_in_place functions. This should
	# include a sequence of turning in place, moving straight, and then turning
	# again at the target to get to the desired rotation (Approach 1).
	# ####
	firstRotationInRadians = (0 if y == 0 else 90) if x == 0 else math.atan(y/x)
	firstRotation = firstRotationInRadians * 360.0/ (2.0 * math.pi)
	my_turn_in_place(robot, firstRotation, 30)
	robot.stop_all_motors()
	# robot.drive_wheels(0, 0, duration=1)
	# time.sleep(1)
	my_drive_straight(robot, math.sqrt(x*x + y*y), (-1 if x < 0 else 1) * 30)
	robot.stop_all_motors()
	# robot.drive_wheels(0, 0, duration=1)
	# time.sleep(1)
	my_turn_in_place(robot, angle_z - firstRotation , 30)
	time.sleep(1)

def my_go_to_pose2(robot, x, y, angle_z):
	"""Moves the robot to a pose relative to its current pose.
		Arguments:
		robot -- the Cozmo robot instance passed to the function
		x,y -- Desired position of the robot in millimeters
		angle_z -- Desired rotation of the robot around the vertical axis in degrees
	"""
	# ####
	# TODO: Implement a function that makes the robot move to a desired pose
	# using the robot.drive_wheels() function to jointly move and rotate the 
	# robot to reduce distance between current and desired pose (Approach 2).
	# ####
	
	absoluteTargetPosition = (robot.pose.position.x + x, robot.pose.position.y + y, robot.pose.rotation.angle_z.degrees + angle_z)
	
	while(math.sqrt(x*x + y*y) > 50.0):
		# print("(x, y, angle_z) = (%i,%i,%i)" % (x, y, angle_z))
		firstRotationInRadians = (0 if y == 0 else 90) if x == 0 else math.atan(y/x)
		leftMotor = 10 * (2 * x - angle_z * (2 * math.pi / 360.0) * get_distance_between_wheels() * math.cos(firstRotationInRadians)) / (2 * get_front_wheel_radius() * math.cos(firstRotationInRadians))
		rightMotor = 10 * (2 * x + angle_z * (2 * math.pi / 360.0) * get_distance_between_wheels() * math.cos(firstRotationInRadians)) / (2 * get_front_wheel_radius() * math.cos(firstRotationInRadians))
		# print("(leftMotor, rightMotor) = (%i,%i)" % (leftMotor, rightMotor))
		angle_delta = get_front_wheel_radius() * (rightMotor - leftMotor) / get_distance_between_wheels()
		x_delta = get_front_wheel_radius() * math.cos(angle_z * 2.0 * math.pi / 360.0) * (leftMotor + rightMotor) / 2.0
		y_delta = get_front_wheel_radius() * math.sin(angle_z * 2.0 * math.pi / 360.0) * (leftMotor + rightMotor) / 2.0
		# print("angle_delta %i" % angle_delta)
		# x = x - get_front_wheel_radius() * math.cos(angle_delta) * (leftMotor + rightMotor) / 2.0
		# y = y - get_front_wheel_radius() * math.sin(angle_delta) * (leftMotor + rightMotor) / 2.0
		# print("(x, y, angle_z) = (%i,%i,%i)" % (x, y, angle_z))
		# angle_z = angle_z + angle_delta * (360.0/(2 * math.pi))
		# print("(x, y, angle_z) = (%i,%i,%i)" % (x, y, angle_z))
		robot.drive_wheels(leftMotor, rightMotor, duration = 1)
		robot.stop_all_motors()
		# time.sleep(1)
		x = absoluteTargetPosition[0] - robot.pose.position.x
		y = absoluteTargetPosition[1] - robot.pose.position.y
		angle_z = absoluteTargetPosition[2] - robot.pose.rotation.angle_z.degrees
		# print("(x, y, angle_z) = (%i,%i,%i)" % (x, y, angle_z))
		robot.stop_all_motors()
		# robot.drive_wheels(0,0)

def my_go_to_pose3(robot, x, y, angle_z):
	"""Moves the robot to a pose relative to its current pose.
		Arguments:
		robot -- the Cozmo robot instance passed to the function
		x,y -- Desired position of the robot in millimeters
		angle_z -- Desired rotation of the robot around the vertical axis in degrees
	"""
	# ####
	# TODO: Implement a function that makes the robot move to a desired pose
	# as fast as possible. You can experiment with the built-in Cozmo function
	# (cozmo_go_to_pose() above) to understand its strategy and do the same.
	# ####
	if angle_z > 90 or angle_z < -90: # if it's beyond a simple differential drive towards the pose (e.g. involves a turn at the end), then just drive to it and turn.
		my_go_to_pose1(robot, x, y, angle_z)
		# my_go_to_pose1(robot, 0, 0, angle_z)
		# my_go_to_pose2(robot, x, y, 0)
	else:
		my_go_to_pose2(robot, x, y, angle_z)

def run(robot: cozmo.robot.Robot):

	print("***** Front wheel radius: " + str(get_front_wheel_radius()))
	print("***** Distance between wheels: " + str(get_distance_between_wheels()))

	## Example tests of the functions

	# cozmo_drive_straight(robot, 62, 50)
	# cozmo_turn_in_place(robot, 60, 30)
	# cozmo_go_to_pose(robot, 100, -100, 45)
	# cozmo_go_to_pose(robot, 100, 100, 45)
	# cozmo_go_to_pose(robot, 100, -100, 45)

	# rotate_front_wheel(robot, 90)
	# my_drive_straight(robot, 62, 50)
	# my_turn_in_place(robot, 90, 30)

	# my_go_to_pose1(robot, 100, 100, 45)
	my_go_to_pose2(robot, 100, 100, 45)
	# my_go_to_pose2(robot, 100, -100, 45)
	# my_go_to_pose2(robot, 100, 100, 45)
	# my_go_to_pose3(robot, 100, 100, 45)
	# my_go_to_pose2(robot, -10, 100, 45)
	# my_go_to_pose2(robot, 100, -100, 45)


if __name__ == '__main__':

	cozmo.run_program(run)




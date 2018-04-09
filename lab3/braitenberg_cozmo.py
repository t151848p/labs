#!/usr/bin/env python3

'''Make Cozmo behave like a Braitenberg machine with virtual light sensors and wheels as actuators.

The following is the starter code for lab.
'''

import asyncio
import time
import cozmo
import cv2
import numpy as np
import sys
from enum import Enum

class BraitenbergVehicleType(Enum):
	Vehicle1 = 1
	Vehicle2a = 2
	Vehicle2b = 3
	Vehicle3a = 4
	Vehicle3b = 5

def sense_brightness(image, columns):
	'''Maps a sensor reading to a wheel motor command'''
	## TODO: Test that this function works and decide on the number of columns to use

	h = image.shape[0]
	w = image.shape[1]
	avg_brightness = 0

	for y in range(0, h):
		for x in columns:
			avg_brightness += image[y,x]

	avg_brightness /= (h*columns.shape[0])

	return avg_brightness

def mapping_funtion(sensor_value, braitenbergVehicleType):
	'''Maps a sensor reading to a wheel motor command'''
	## TODO: Define the mapping to obtain different behaviors.
	if braitenbergVehicleType == BraitenbergVehicleType.Vehicle3a or braitenbergVehicleType == BraitenbergVehicleType.Vehicle3b:
		motor_value = 255.0/sensor_value
	else:
		motor_value = 0.5*sensor_value
	return motor_value

async def braitenberg_machine(robot: cozmo.robot.Robot):
	'''The core of the braitenberg machine program'''
	# Move lift down and tilt the head up
	vehicleType = BraitenbergVehicleType.Vehicle3a
	robot.move_lift(-3)
	handleHead = robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE)
	await handleHead.wait_for_completed()
	print("Press CTRL-C to quit")
	textToSay = "Hello! Cozmo is now %s" % vehicleType
	robot.say_text(textToSay, voice_pitch=0.5, duration_scalar=0.6).wait_for_completed()

	while True:
		
		#get camera image
		event = await robot.world.wait_for(cozmo.camera.EvtNewRawCameraImage, timeout=30)

		#convert camera image to opencv format
		opencv_image = cv2.cvtColor(np.asarray(event.image), cv2.COLOR_RGB2GRAY)
		# Determine the w/h of the new image
		h = opencv_image.shape[0]
		w = opencv_image.shape[1]
		# sensor_n_columns = 20
		sensor_n_columns = w / 2

		# Sense the current brightness values on the right and left of the image.
		sensor_right = sense_brightness(opencv_image, columns=np.arange(sensor_n_columns))
		sensor_left = sense_brightness(opencv_image, columns=np.arange(w-sensor_n_columns, w))

		print("sensor_right: " + str(sensor_right))
		print("sensor_left: " + str(sensor_left))

		# Map the sensors to actuators
		## TODO: You might want to switch which sensor is mapped to which motor.
		if vehicleType == BraitenbergVehicleType.Vehicle1:
			sensor_single = (sensor_left + sensor_right)/2.0 # vehicle 1 only has one sensor, merge the two to emulate one
			motor_right = mapping_funtion(sensor_single, vehicleType)
			motor_left = mapping_funtion(sensor_single, vehicleType)
		elif vehicleType == BraitenbergVehicleType.Vehicle2a or vehicleType == BraitenbergVehicleType.Vehicle3a:
			motor_right = mapping_funtion(sensor_right, vehicleType)
			motor_left = mapping_funtion(sensor_left, vehicleType)
		elif vehicleType == BraitenbergVehicleType.Vehicle2b or vehicleType == BraitenbergVehicleType.Vehicle3b:
			motor_right = mapping_funtion(sensor_left, vehicleType)
			motor_left = mapping_funtion(sensor_right, vehicleType)

		print("motor_right: " + str(motor_right))
		print("motor_left: " + str(motor_left))

		# Send commands to the robot
		await robot.drive_wheels(motor_right, motor_left)

		# time.sleep(10)
		time.sleep(.1)


cozmo.run_program(braitenberg_machine, use_viewer=True, force_viewer_on_top=True)

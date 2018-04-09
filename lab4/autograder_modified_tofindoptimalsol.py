#!/usr/bin/env python3
 
import cv2
import os
import math
import find_ball
import numpy as np

np.set_printoptions(threshold=np.inf)

# load ground truth
with open('./imgs/ground_truth.txt') as f:
	grid_data = [i.split() for i in f.readlines()]
	 
# print(grid_data)
 
# thresh hold to accept circle and give credit per circle
center_err_thresh = 20.0
radius_err_thresh = 10.0
score = 0;
 
# check each image
bestScore = 0
bestParams = (0,0)
scores = np.zeros((50,50))

for param1value in range(30, 50):
	for param2value in range(15, 50):
		score = 0
		for filedata in grid_data:
			file = filedata[0]

			#read in image as grayscale
			opencv_image = cv2.imread("./imgs/" + file, cv2.COLOR_GRAY2RGB)

			#try to find the ball in the image
			ball = find_ball.find_ball(opencv_image, param1value, param2value)
			# print(file, ball)
			
			if ball is None:
				ball = np.array([0, 0, 0])

			# get center err
			center_err = math.sqrt((ball[0] - float(filedata[1]))**2 + (
				ball[1] - float(filedata[2]))**2)
			
			# get radius err
			r_err = math.fabs(ball[2] - float(filedata[3]))
				 
			# print("circle center err =", center_err, "pixel")
			# print("circle radius err =", r_err, "pixel")
			if center_err <= center_err_thresh and r_err <= radius_err_thresh:
				score += 1;
			# else:
				# print("failed this")
				# print(filedata)
		 
		print("(param1,param2) = (%d,%d) score = %d" % (param1value, param2value, score))
		scores[param1value,param2value] = score
		if score > bestScore:
			bestScore = score
			bestParams = (param1value, param2value)
			# print(scores)
			# np.savetxt('test.out', scores, delimiter=',', fmt='%d')
		print("BEST: (param1,param2) = (%d,%d) score = %d" % (bestParams[0], bestParams[1], bestScore))

print(scores)
np.savetxt('test.out', scores, delimiter=',', fmt='%d')

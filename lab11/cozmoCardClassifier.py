#!/usr/bin/env python3

import asyncio
import time
import cozmo
import cv2
import numpy as np
import sys
from enum import Enum
from imgclassification import ImageClassifier
from itertools import groupby

async def cozmoCardClassifier(robot: cozmo.robot.Robot):
    ''' Cozmo Card classifier implementation - gathers 10 images then runs a prediction on them to see if it saw a familiar card '''

    robot.move_lift(-3)
    robot.set_head_angle(cozmo.util.degrees(0)).wait_for_completed()
    imgClassifier = ImageClassifier()
    imgClassifier.train_model()

    while True:
        images = []
        for iterN in range(10):
            #get camera image
            event = await robot.world.wait_for(cozmo.camera.EvtNewRawCameraImage, timeout=30)
            #convert camera image to opencv format
            opencv_image = cv2.cvtColor(np.asarray(event.image), cv2.COLOR_RGB2GRAY)
            images.append(opencv_image)

        predictions = [prediction[0] for prediction in imgClassifier.predict_labels(imgClassifier.extract_image_features(images))]

        (mostLikelyCardType, mostLikelyCardFrequency) = max([(key,len(list(group))) for key, group in groupby(predictions)], key=lambda x: x[1])
        
        if mostLikelyCardType in ['drone', 'hands', 'inspection'] and mostLikelyCardFrequency > 5:
            textToSay = "I think I see '%s'" % mostLikelyCardType
            await robot.say_text(textToSay, voice_pitch=0.5, duration_scalar=0.6).wait_for_completed()

            if mostLikelyCardType == 'drone':
                await robot.play_anim(name="anim_reacttoface_unidentified_02").wait_for_completed()
            elif mostLikelyCardType == 'hands':
                await robot.play_anim(name="anim_speedtap_wingame_intensity02_01").wait_for_completed()
            elif mostLikelyCardType == 'inspection':
                await robot.play_anim(name="anim_poked_giggle").wait_for_completed()

cozmo.run_program(cozmoCardClassifier, use_viewer=True, force_viewer_on_top=True)

#!/usr/bin/env python3

import asyncio
import sys

import cv2
import numpy as np

sys.path.insert(0, '../lab4')
import find_ball

import cozmo

from cozmo.util import degrees, distance_mm, speed_mmps

try:
    from PIL import ImageDraw, ImageFont
except ImportError:
    sys.exit('run `pip3 install --user Pillow numpy` to run this example')


# Define a decorator as a subclass of Annotator; displays battery voltage
class BatteryAnnotator(cozmo.annotate.Annotator):
    def apply(self, image, scale):
        d = ImageDraw.Draw(image)
        bounds = (0, 0, image.width, image.height)
        batt = self.world.robot.battery_voltage
        text = cozmo.annotate.ImageText('BATT %.1fv' % batt, color='green')
        text.render(d, bounds)

# Define a decorator as a subclass of Annotator; displays the ball
class BallAnnotator(cozmo.annotate.Annotator):

    ball = None

    def apply(self, image, scale):
        d = ImageDraw.Draw(image)
        bounds = (0, 0, image.width, image.height)

        if BallAnnotator.ball is not None:

            #double size of bounding box to match size of rendered image
            BallAnnotator.ball = np.multiply(BallAnnotator.ball,2)

            #define and display bounding box with params:
            #msg.img_topLeft_x, msg.img_topLeft_y, msg.img_width, msg.img_height
            box = cozmo.util.ImageBox(BallAnnotator.ball[0]-BallAnnotator.ball[2],
                                      BallAnnotator.ball[1]-BallAnnotator.ball[2],
                                      BallAnnotator.ball[2]*2, BallAnnotator.ball[2]*2)
            cozmo.annotate.add_img_box_to_image(image, box, "green", text=None)

            BallAnnotator.ball = None


async def run(robot: cozmo.robot.Robot):
    '''The run method runs once the Cozmo SDK is connected.'''

    #add annotators for battery level and ball bounding box
    robot.world.image_annotator.add_annotator('battery', BatteryAnnotator)
    robot.world.image_annotator.add_annotator('ball', BallAnnotator)
    
    await robot.set_head_angle(degrees(0)).wait_for_completed()
    # await robot.set_head_angle(0).wait_for_completed()

    textToSay = "One way, or another, I'm going to find you, I'm going to get you get you Mr. Ball"
    await robot.say_text(textToSay, voice_pitch=0.8, duration_scalar=0.5).wait_for_completed()
    
    foundBall = False

    try:

        while True:
            #get camera image
            event = await robot.world.wait_for(cozmo.camera.EvtNewRawCameraImage, timeout=30)

            #convert camera image to opencv format
            opencv_image = cv2.cvtColor(np.asarray(event.image), cv2.COLOR_RGB2GRAY)

            #find the ball
            ball = find_ball.find_ball(opencv_image)

            #set annotator ball
            BallAnnotator.ball = ball

            ## TODO: ENTER YOUR SOLUTION HERE
            # Determine the w/h of the new image
            h = opencv_image.shape[0]
            w = opencv_image.shape[1]

            if not foundBall and ball is None:
                await robot.turn_in_place(degrees(30)).wait_for_completed()
            elif foundBall and ball is None:
                await robot.drive_wheels(0, 0)
                textToSay = "You disappeared Mr. Ball, or should I call you Mr. Houdini!"
                await robot.say_text(textToSay, voice_pitch=0.3, duration_scalar=0.5).wait_for_completed()
                foundBall = False
            elif not foundBall and not ball is None:
                await robot.drive_wheels(0, 0)
                textToSay = "Like I said, I found you Mr. Ball, now I will get you"
                await robot.say_text(textToSay, voice_pitch=0.8, duration_scalar=0.4).wait_for_completed()
                foundBall = True
                x = ball[0]
                r = ball[2]
                
                if r > 0.7 * w/2.0:
                    await robot.drive_wheels(5, 5)
                    textToSay = "Goodbye Mr. Ball, it was nice knowing you"
                    await robot.say_text(textToSay, voice_pitch=0.9, duration_scalar=0.4).wait_for_completed()
                    await robot.play_anim_trigger(cozmo.anim.Triggers.PounceFace).wait_for_completed()
                    await robot.play_anim_trigger(cozmo.anim.Triggers.PounceInitial).wait_for_completed()
                    await robot.play_anim_trigger(cozmo.anim.Triggers.PouncePounce).wait_for_completed()
                    await robot.play_anim_trigger(cozmo.anim.Triggers.PounceSuccess).wait_for_completed()
                    return
                
                await robot.drive_wheels(50.0 * x/w, 50.0 * (w-x)/w)

            else: # foundBall and not ball is None
                x = ball[0]
                r = ball[2]
                
                if r > 0.7 * w/2.0:
                    await robot.drive_wheels(5, 5)
                    textToSay = "Goodbye Mr. Ball, it was nice knowing you"
                    await robot.say_text(textToSay, voice_pitch=0.5, duration_scalar=0.6).wait_for_completed()
                    await robot.play_anim_trigger(cozmo.anim.Triggers.PounceFace).wait_for_completed()
                    await robot.play_anim_trigger(cozmo.anim.Triggers.PounceInitial).wait_for_completed()
                    await robot.play_anim_trigger(cozmo.anim.Triggers.PouncePounce).wait_for_completed()
                    await robot.play_anim_trigger(cozmo.anim.Triggers.PounceSuccess).wait_for_completed()
                    return
                
                await robot.drive_wheels(50.0 * x/w, 50.0 * (w-x)/w)


    except KeyboardInterrupt:
        print("")
        print("Exit requested by user")
    except cozmo.RobotBusy as e:
        print(e)



if __name__ == '__main__':
    cozmo.run_program(run, use_viewer = True, force_viewer_on_top = True)


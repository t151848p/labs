
#author1: Thayalan Pirapakaran (t151848p)
#author2:

from grid import *
from visualizer import *
import threading
from queue import PriorityQueue
import math
import cozmo
from cozmo.util import degrees, Pose, distance_mm, speed_mmps
import time
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id

def astar(grid, heuristic):
    """Perform the A* search algorithm on a defined grid

        Arguments:
        grid -- CozGrid instance to perform search on
        heuristic -- supplied heuristic function
    """
    parents = {}
    lowestCosts = {}
    closed = set()
    
    curr = start = grid.getStart()
    frontier = PriorityQueue()
    goal = grid.getGoals()[0]
    frontier.put((0 + heuristic(curr, goal), 0, curr))
    parents[curr] = None
    lowestCosts[curr] = 0
    while not frontier.empty():
        (currNodeAStarCost, currNodeCostSoFar, currNode) = frontier.get()
        if currNodeCostSoFar < lowestCosts[currNode]:
            lowestCosts[currNode] = currNodeCostSoFar
        if currNode in grid.getVisited():
            continue # skip visited nodes because there's nothing new to learn here
        grid.addVisited(currNode)
        if currNode == goal:
            # Found the goal
            thePath = []
            while currNode in parents:
                thePath.insert(0, currNode)
                currNode = parents[currNode]
            grid.setPath(thePath)
            return
        # Expand the neighbors of currNode and set priority accordingly to A*
        neighborsToCurr = grid.getNeighbors(currNode)
        for neighborToCurr in neighborsToCurr:
            (neighborCoord, neighborWeight) = neighborToCurr
            if neighborCoord not in lowestCosts or currNodeCostSoFar + neighborWeight < lowestCosts[neighborCoord]:
            # if neighborCoord not in grid.getVisited():
                parents[neighborCoord] = currNode
                lowestCosts[neighborCoord] = currNodeCostSoFar + neighborWeight
                frontier.put((currNodeCostSoFar + neighborWeight + heuristic(neighborCoord, goal), currNodeCostSoFar + neighborWeight, neighborCoord))

def heuristic(current, goal):
    """Heuristic function for A* algorithm

        Arguments:
        current -- current cell
        goal -- desired goal cell
    """
    # return 0
    # print(current)
    # print(goal)
    euclideanDist = math.sqrt(math.pow(current[0] - goal[0], 2) + math.pow(current[1] - goal[1], 2))
    # print(euclideanDist)
    return euclideanDist # Your code here

def world_to_grid(worldPose, grid):
    return (int(worldPose.position.x/grid.scale), int(worldPose.position.y/grid.scale))

def addObstaclesAround(grid, obstacleCoord):
    grid.addObstacles([(x + obstacleCoord[0], y + obstacleCoord[1]) for y in range(-1,2) for x in range(-2,3)])

def closeEnough(start, goal):
    return heuristic(start, goal) <= 6

def addObstaclesIfSeen(robot, originalPose, grid):
    visibleObjectCount = robot.world.visible_object_count(object_type=None)
    visibleObjects = robot.world.visible_objects
    if visibleObjectCount > 0:
        for visibleObject in visibleObjects:
            if isinstance(visibleObject, cozmo.objects.LightCube) and visibleObject.object_id != 1:
                addObstaclesAround(grid, world_to_grid(visibleObject.pose.define_pose_relative_this(originalPose), grid))

def cozmoBehavior(robot: cozmo.robot.Robot):
    """Cozmo search behavior. See assignment description for details

        Has global access to grid, a CozGrid instance created by the main thread, and
        stopevent, a threading.Event instance used to signal when the main thread has stopped.
        You can use stopevent.is_set() to check its status or stopevent.wait() to wait for the
        main thread to finish.

        Arguments:
        robot -- cozmo.robot.Robot instance, supplied by cozmo.run_program
    """
        
    global grid, stopevent
    
    while not stopevent.is_set():
        # Step 1: Update Map: Update the map to correctly represent all cubes detected by the robot.
        robot.set_head_angle(cozmo.util.degrees(0)).wait_for_completed()
        cube1 = robot.world.get_light_cube(LightCube1Id)
        if cube1 is not None:
            cube1.set_lights(cozmo.lights.red_light)
        else:
            cozmo.logger.warning("Cozmo is not connected to a LightCube1Id cube - check the battery.")
        
        foundCube1 = False
        cubesFound = {}
        # from_global_to_grid_position()
        # from_grid_position_to_global()
        originalPose = robot.pose
        
        while not foundCube1:
            visibleObjectCount = robot.world.visible_object_count(object_type=None)
            visibleObjects = robot.world.visible_objects
            if visibleObjectCount > 0:
                for visibleObject in visibleObjects:
                    if isinstance(visibleObject, cozmo.objects.LightCube):
                        cubesFound[visibleObject.object_id] = visibleObject.pose.define_pose_relative_this(originalPose)
                    if visibleObject.object_id == 1:
                        foundCube1 = True
            if not foundCube1:
                robot.turn_in_place(degrees(10)).wait_for_completed()
                # time.sleep(1)
        
        if cube1 is not None:
            cube1.set_lights(cozmo.lights.green_light)
        grid.clearVisited()
        grid.clearGoals()
        grid.clearStart()
        grid.clearPath()
        
        grid.setStart((0,0))
        
        cubePositions = [(cubeId, cubeToAdd.position.x, cubeToAdd.position.y, cubeToAdd.position.z, cubeToAdd.rotation.angle_z.degrees) for cubeId, cubeToAdd in cubesFound.items()]
        print(cubePositions)
        
        cubeObstacles = [(int(cubeX/grid.scale), int(cubeY/grid.scale)) for cubeId, cubeX, cubeY, cubeZ, cubeAngle in cubePositions if cubeId != 1]
        print(cubeObstacles)
        
        for cubeObstacle in cubeObstacles:
            addObstaclesAround(grid, cubeObstacle)
        # grid.addObstacles(cubeObstacles)
        goalCube = [(int(cubeX/grid.scale), int(cubeY/grid.scale)) for cubeId, cubeX, cubeY, cubeZ, cubeAngle in cubePositions if cubeId == 1][0]
        print("goalCube")
        print(goalCube)
        grid.addGoal(goalCube)
        # cube_1_pose = cubesFound[1].pose
        
        while not closeEnough(grid.getStart(), grid.getGoals()[0]):
            newStart = robot.pose.define_pose_relative_this(originalPose)
            print("newStart")
            print(newStart)
            grid.clearStart()
            grid.setStart(world_to_grid(newStart, grid))
            addObstaclesIfSeen(robot, originalPose, grid)
            grid.clearVisited()
            grid.clearPath()
            astar(grid, heuristic)
            if not grid.checkPath():
                print("CONFUSED")
                return
            nextStep = grid.getPath()[1] # go one steps ahead
            stepAfter = grid.getPath()[2] # go two steps ahead
            print(nextStep)
            delta_x = (stepAfter[0]*grid.scale - nextStep[0]*grid.scale)
            delta_y = (stepAfter[1]*grid.scale - nextStep[1]*grid.scale)
            nextPose = Pose(nextStep[0]*grid.scale, nextStep[1]*grid.scale, originalPose.position.z, angle_z=degrees(90 if delta_x == 0 else 180.0 * math.atan(delta_y/delta_x) / math.pi))
            robot.go_to_pose(nextPose, relative_to_robot=False).wait_for_completed()

        # Step 2: Navigate to Goal: Successfully navigate the robot from a known start location to Cube 1 and stop within 10cm of Cube 1.
        # Step 3: Cube Orientation: Extend your navigation code to consider which side of the cube the robot is approaching. Have the robot approach the side of the cube that looks like Figure 1. The orientation of the cube can be accessed with cube.pose.rotation.angle_z. The robot should stop within 10cm of the cube, facing toward the correct side of the cube but without touching it. 
        goalPose = Pose(cube1.pose.position.x + 100 * math.cos(cube1.pose.rotation.angle_z.radians), cube1.pose.position.y + 100 * math.sin(cube1.pose.rotation.angle_z.radians), cube1.pose.position.z, angle_z=degrees((720 + cube1.pose.rotation.angle_z.degrees - 180) % 360))
        robot.go_to_pose(goalPose, relative_to_robot=False).wait_for_completed()


######################## DO NOT MODIFY CODE BELOW THIS LINE ####################################


class RobotThread(threading.Thread):
    """Thread to run cozmo code separate from main thread
    """
        
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)

    def run(self):
        cozmo.run_program(cozmoBehavior)


# If run as executable, start RobotThread and launch visualizer with empty grid file
if __name__ == "__main__":
    global grid, stopevent
    stopevent = threading.Event()
    grid = CozGrid("emptygrid.json")
    visualizer = Visualizer(grid)
    updater = UpdateThread(visualizer)
    updater.start()
    robot = RobotThread()
    robot.start()
    visualizer.start()
    stopevent.set()


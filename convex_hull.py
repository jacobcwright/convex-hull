from turtle import left
import time
from which_pyqt import PYQT_VER

if PYQT_VER == "PYQT6":
    from PyQt6.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == "PYQT4":
    from PyQt4.QtCore import QLineF, QPointF, QObject
else:
    raise Exception("Unsupported Version of PyQt: {}".format(PYQT_VER))



# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.


    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    def max_slope_clockwise(self, right_best_point, start, hull):
        best_slope_index = start
        prev_slope = None
        curr = start
        
        while True:
            curr_slope = (hull[curr].y() - right_best_point.y()) / (hull[curr].x() - right_best_point.x())
            if prev_slope == None or curr_slope > prev_slope:
                prev_slope = curr_slope
                best_slope_index = curr
            else:
                best_slope_index = (curr - 1) % len(hull)
                break
            curr = (curr + 1) % len(hull)
        return best_slope_index

    def max_slope_counter_clockwise(self, left_best_point, start, hull):
        best_slope_index = start
        prev_slope = None
        curr = start

        while True:
            curr_slope = (hull[curr].y() - left_best_point.y()) / (hull[curr].x() - left_best_point.x())
            if prev_slope == None or curr_slope < prev_slope:
                prev_slope = curr_slope
                best_slope_index = curr
            else:
                best_slope_index = (curr + 1) % len(hull)
                break
            curr = (curr - 1) % len(hull)
        return best_slope_index

    def get_upper_tangent(self, leftmost, rightmost, left_hull, right_hull):
        # start upper tangent points at leftmost and rightmost
        upper_left = leftmost
        upper_right = rightmost

        # From pseudocode from slides
        done = False
        while not done:
            next_left = self.max_slope_clockwise(left_hull[upper_right], upper_left, right_hull)
            next_right = self.max_slope_counter_clockwise(right_hull[next_left], upper_right, left_hull)

            # if the next left and right points are the same as the current left and right points, we are done
            if next_left == upper_left and next_right == upper_right:
                done = True
            else:
                upper_left = next_left
                upper_right = next_right
            
        return upper_left, upper_right

    def get_lower_tangent(self, leftmost, rightmost, left_hull, right_hull):
        # start lower tangent points at leftmost and rightmost
        lower_left = leftmost
        lower_right = rightmost

        # From pseudocode from slides
        done = False
        while not done:
            next_left = self.max_slope_counter_clockwise(left_hull[lower_right], lower_left, right_hull)
            next_right = self.max_slope_clockwise(right_hull[next_left], lower_right, left_hull)

            # if the next left and right points are the same as the current left and right points, we are done
            if next_left == lower_left and next_right == lower_right:
                done = True
            else:
                lower_left = next_left
                lower_right = next_right

        return lower_left, lower_right

    def merge_hulls(self, left_hull, right_hull):
        # get leftmost and rightmost points
        leftmost = 0
        rightmost = left_hull.index(max(left_hull, key=lambda point:point.x()))

        # get points from upper and lower tangents
        upper_right, upper_left = self.get_upper_tangent(leftmost, rightmost, left_hull, right_hull)
        lower_right, lower_left = self.get_lower_tangent(leftmost, rightmost, left_hull, right_hull)
        
        # create new hull to return
        merged_hull = []

        # add points from in left_hull from x=0 to upper left point
        for x in range(0, upper_left):
            merged_hull.append(left_hull[x])
        merged_hull.append(left_hull[upper_left])

        i = 0
        curr = upper_right

        # add points from right_hull from upper right point to lower right point
        while i < len(right_hull):
            merged_hull.append(right_hull[curr])
            if curr == lower_right:
                break
            i += 1
            curr = (curr + 1) % len(right_hull)

        # add points from in left_hull from lower left point to x=0
        if lower_left != upper_left and lower_left != 0:
            for x in range(lower_left, len(left_hull)):
                merged_hull.append(left_hull[x])
        return merged_hull

    def convex_hull_helper(self, points):
        # base case
        if len(points) <= 2:
            return points
        
        # get left half of points and right half of points
        left_points = points[:len(points) // 2]
        right_points = points[len(points) // 2:]

        # compute left and right hulls recursively
        left_hull = self.convex_hull_helper(left_points)
        right_hull = self.convex_hull_helper(right_points)

        # merge the two hulls
        return self.merge_hulls(left_hull, right_hull)


    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert type(points) == list and type(points[0]) == QPointF

        t1 = time.time()

        # sort points by x coordinate
        points.sort(key=lambda point:point.x())
        
        t2 = time.time()
        t3 = time.time()

        hull = self.convex_hull_helper(points)
        # print("hull: ", hull.__str__())

        polygon = [QLineF(hull[i], hull[(i + 1) % len(hull)]) for i in range(0,len(hull))]

        # print("Polygon: ", polygon.__str__())

        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText("Time Elapsed (Convex Hull): {:3.3f} sec".format(t4 - t3))

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

    def get_rightmost(self, hull_points):
        rightmost_point = max(hull_points, key=lambda point:point.x())
        return hull_points.index(rightmost_point)

    def get_best_slope_index(self, best_point, start_index, hull, increment):  # 1 if clockwise, -1 if counterclockwise
        if len(hull) == 1:
            return 0
        best_index = start_index
        prev_slope = None
        index = start_index
        for i in range(len(hull)):
            curr_slope = (hull[index].y() - best_point.y()) / (hull[index].x() - best_point.x())
            if prev_slope is None:
                prev_slope = curr_slope
            elif (curr_slope > prev_slope and increment == 1) or (curr_slope < prev_slope and increment == -1):
                prev_slope = curr_slope
                best_index = index
            else:
                best_index = (index - increment) % len(hull)
                break
            index = (index + increment) % len(hull)
        return best_index

    def get_top_points(self, leftmost_index, rightmost_index, left_hull, right_hull):
        best_left = leftmost_index  # best leftmost point of right hull
        best_right = rightmost_index  # best rightmost point of left hull
        flag = True
        while flag:
            next_left = self.get_best_slope_index(left_hull[best_right], best_left, right_hull, 1)
            next_right = self.get_best_slope_index(right_hull[next_left], best_right, left_hull, -1)
            if next_left == best_left and next_right == best_right:
                flag = False
            else:
                best_left = next_left
                best_right = next_right
        return best_left, best_right

    def get_bottom_points(self, leftmost_index, rightmost_index, left_hull, right_hull):
        best_left = leftmost_index
        best_right = rightmost_index
        flag = True
        while flag:
            next_left = self.get_best_slope_index(left_hull[best_right], best_left, right_hull, -1)
            next_right = self.get_best_slope_index(right_hull[next_left], best_right, left_hull, 1)
            if next_left == best_left and next_right == best_right:
                flag = False
            else:
                best_left = next_left
                best_right = next_right
        return best_left, best_right

    def merge_hulls(self, left_hull, right_hull):
        rightmost = self.get_rightmost(left_hull)
        leftmost = 0  
        top_right, top_left = self.get_top_points(leftmost, rightmost, left_hull, right_hull)
        bottom_right, bottom_left = self.get_bottom_points(leftmost, rightmost, left_hull, right_hull)
        new_hull = []

        for x in range(0, top_left + 1):
            new_hull.append(left_hull[x])
        i = 0
        index = top_right
        while i < len(right_hull):
            new_hull.append(right_hull[index])
            if index == bottom_right:
                break
            i += 1
            index = (index + 1) % len(right_hull)

        if bottom_left != top_left and bottom_left != 0:
            for x in range(bottom_left, len(left_hull)):
                new_hull.append(left_hull[x])
        return new_hull

    def convex_hull_helper(self, points):
        if len(points) == 1 or len(points) == 2:
            return points
        left_side = points[:len(points) // 2]
        right_side = points[len(points) // 2:]
        left_hull = self.convex_hull_helper(left_side)
        right_hull = self.convex_hull_helper(right_side)
        return self.merge_hulls(left_hull, right_hull)


    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert type(points) == list and type(points[0]) == QPointF

        t1 = time.time()

        points.sort(key=lambda point:point.x())
        t2 = time.time()
        t3 = time.time()

        hull = self.convex_hull_helper(points)
        print("hull: ", hull.__str__())

        polygon = [QLineF(hull[i], hull[(i + 1) % len(hull)]) for i in range(0,len(hull))]

        print("Polygon: ", polygon.__str__())


        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText("Time Elapsed (Convex Hull): {:3.3f} sec".format(t4 - t3))

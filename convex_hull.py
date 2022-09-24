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

    def find_upper_tangent(self, leftmost, rightmost, left_hull, right_hull):

        upper_tangent = QLineF(left_hull[rightmost], right_hull[leftmost])
        done = False
        while not done:
            done = True
            next_right = leftmost
            next_left = rightmost
            upper_tangent = QLineF(left_hull[next_left], right_hull[next_left])
            prev_slope = 0
            while upper_tangent.angle() > prev_slope:
                prev_slope = upper_tangent.angle()
                next_left = (rightmost - 1) % len(left_hull)
                upper_tangent = QLineF(left_hull[next_left], right_hull[next_right])
                done = False

            prev_slope = 0
            while upper_tangent.angle() < prev_slope:
                prev_slope = upper_tangent.angle()
                next_right = (leftmost + 1) % len(right_hull)
                upper_tangent = QLineF(left_hull[next_left], right_hull[next_right])
                done = False
            return upper_tangent
            
        

    def find_lower_tangent(self, leftmost, rightmost, left_hull, right_hull):
        lower_tangent = QLineF(left_hull[rightmost], right_hull[leftmost])
        done = False
        while not done:
            done = True
            next_right = leftmost
            next_left = rightmost
            lower_tangent = QLineF(left_hull[next_left], right_hull[next_left])
            prev_slope = 0
            while lower_tangent.angle() < prev_slope:
                prev_slope = lower_tangent.angle()
                next_left = (rightmost + 1) % len(left_hull)
                lower_tangent = QLineF(left_hull[next_left], right_hull[next_right])
                done = False

            prev_slope = 0
            while lower_tangent.angle() > prev_slope:
                prev_slope = lower_tangent.angle()
                next_right = (leftmost - 1) % len(right_hull)
                lower_tangent = QLineF(left_hull[next_left], right_hull[next_right])
                done = False
            return lower_tangent

    def merge_hulls(self, left_hull, right_hull):
        # find the leftmost point of the right hull
        rightmost = left_hull.index(max(left_hull, key=lambda x: x.x()))
        leftmost = right_hull.index(min(right_hull, key=lambda x: x.x()))

        # find the upper tangent
        upper_tangent = self.find_upper_tangent(leftmost, rightmost, left_hull, right_hull)
        # find the lower tangent
        lower_tangent = self.find_lower_tangent(leftmost, rightmost, left_hull, right_hull)
        # merge the hulls using upper and lower tangent
        merged_hull = [upper_tangent.p1()]
        upper_tangent_point = upper_tangent.p2()
        lower_tangent_point = lower_tangent.p2()
        while upper_tangent_point != merged_hull[0]:
            merged_hull.append(upper_tangent_point)
            upper_tangent_point = self.find_upper_tangent(merged_hull.index(upper_tangent_point), rightmost, left_hull, right_hull).p2()
        while lower_tangent_point != merged_hull[0]:
            merged_hull.append(lower_tangent_point)
            lower_tangent_point = self.find_lower_tangent(leftmost, merged_hull.index(lower_tangent_point), left_hull, right_hull).p2()
        return merged_hull

    def convex_hull_helper(self, points):
        if(len(points) <= 3):
            return points
        # split left and right points
        left = points[:len(points)//2]
        right = points[len(points)//2:]
        # find hulls for left and right
        left_hull = self.convex_hull_helper(left)
        right_hull = self.convex_hull_helper(right)
        # merge the hulls and return new set of points
        return self.merge_hulls(left_hull, right_hull)

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert type(points) == list and type(points[0]) == QPointF

        t1 = time.time()

        # TODO: SORT THE POINTS BY INCREASING X-VALUE
        points.sort(key=lambda point:point.x())
        t2 = time.time()
        t3 = time.time()

        # this is a dummy polygon of the first 3 unsorted points
        # polygon = [QLineF(points[i], points[(i + 1) % 3]) for i in range(3)]
        # TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER **********************
        hull = self.convex_hull_helper(points)

        polygon = [QLineF(hull[i], hull[(i + 1) % len(hull)]) for i in range(len(hull))]


        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText("Time Elapsed (Convex Hull): {:3.3f} sec".format(t4 - t3))

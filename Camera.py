import math
import operator
import cv2
from pygrabber.dshow_graph import FilterGraph
import ChessBoardCorners
from ChessBoardCorners import ChessBoardCorners


class Camera:

    camera = 0
    points = []
    rotations = 0

    def __init__(self):
        self.camera = 0

    # Get all available cameras that are connected to the device
    # credit: https://stackoverflow.com/questions/70886225/get-camera-device-name-and-port-for-opencv-videostream-python
    def get_all_cameras(self):
        devices = FilterGraph().get_input_devices()

        available_cameras = {}

        for device_index, device_name in enumerate(devices):
            available_cameras[device_index] = device_name

        return available_cameras

    # Display a camera
    # credit: https://stackoverflow.com/questions/2601194/displaying-a-webcam-feed-using-opencv-and-python/11449901#11449901
    def display_camera(self, camera_function):
        cv2.namedWindow("Camera")
        vc = cv2.VideoCapture(self.camera, cv2.CAP_DSHOW)

        if vc.isOpened():  # try to get the first frame
            rval, frame = vc.read()
        else:
            rval = False

        stop = False

        while rval or stop:
            cv2.imshow("Camera", frame)
            cv2.setWindowProperty("Camera", cv2.WND_PROP_TOPMOST, 1)
            rval, frame = vc.read()
            key = cv2.waitKey(20)
            stop = camera_function(key, frame)

        cv2.destroyWindow("Camera")
        vc.release()

    def get_four_corners_camera(self):
        cv2.namedWindow("Click Four Corners")
        vc = cv2.VideoCapture(self.camera, cv2.CAP_DSHOW)

        if vc.isOpened():  # try to get the first frame
            rval, frame = vc.read()
        else:
            rval = False

        if(not rval): raise Exception("Could not read camera")

        self.points = []

        cbc = ChessBoardCorners()

        while rval:
            cv2.imshow("Click Four Corners", frame)
            cv2.setWindowProperty("Click Four Corners", cv2.WND_PROP_TOPMOST, 1)
            cv2.setMouseCallback("Click Four Corners", self.corners_click_event)
            rval, frame = vc.read()
            frame = cbc.apply_int_points(frame, self.points)
            if (len(self.points) > 3): break
            cv2.waitKey(20)

        cv2.destroyWindow("Click Four Corners")
        vc.release()

        bottom_right, _ = max(enumerate([pt[0] + pt[1] for pt in self.points]), key=operator.itemgetter(1))
        top_left, _ = min(enumerate([pt[0] + pt[1] for pt in self.points]), key=operator.itemgetter(1))
        bottom_left, _ = min(enumerate([pt[0] - pt[1] for pt in self.points]), key=operator.itemgetter(1))
        top_right, _ = max(enumerate([pt[0] - pt[1] for pt in self.points]), key=operator.itemgetter(1))

        return [self.points[top_left], self.points[top_right], self.points[bottom_left], self.points[bottom_right]], frame

    def capture_frame_from_camera(self):
        vc = cv2.VideoCapture(self.camera, cv2.CAP_DSHOW)

        if vc.isOpened():  # try to get the first frame
            rval, frame = vc.read()
            vc.release()
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        vc.release()
        raise Exception("Unable to find camera")

    def capture_colored_frame_from_camera(self):
        vc = cv2.VideoCapture(self.camera, cv2.CAP_DSHOW)

        if vc.isOpened():  # try to get the first frame
            rval, frame = vc.read()
            vc.release()
            return frame
        vc.release()
        raise Exception("Unable to find camera")


    def rotate_image(self, image):
        rots = self.rotations
        while (rots > 0):
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            rots = rots - 1
        return image

    def setup_rotations(self, func):
        cv2.namedWindow("Rotation Selection")
        vc = cv2.VideoCapture(self.camera, cv2.CAP_DSHOW)

        if vc.isOpened():  # try to get the first frame
            rval, frame = vc.read()
        else:
            rval = False

        frame = func(frame)
        frame = self.rotate_image(frame)

        stop = False

        while rval and not stop:
            cv2.imshow("Rotation Selection", frame)
            cv2.setWindowProperty("Rotation Selection", cv2.WND_PROP_TOPMOST, 1)
            cv2.setMouseCallback("Rotation Selection", self.rotate_click_event)
            rval, frame = vc.read()
            frame = func(frame)
            frame = self.rotate_image(frame)
            key = cv2.waitKey(20)
            stop = self.camera_function(key, frame)

        cv2.destroyWindow("Rotation Selection")
        vc.release()

    def camera_function(self, key_input, frame):
        if key_input == 13:
            return True
        return False


    def corners_click_event(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:

            # Delete closest point near where you click (less than 20 away), else add them
            min_distance = 100000000
            closest = None

            for point in self.points:
                distance = math.sqrt((point[0] - x) ** 2 + (point[1] - y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    closest = point

            if(closest is not None):
                if min_distance < 30:
                    self.points.remove(closest)
                    return

            self.points.append((x, y))


    def rotate_click_event(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            if(self.rotations == 3):
                self.rotations = 0
            else:
                self.rotations += 1
import math
import operator
import cv2
from pygrabber.dshow_graph import FilterGraph
import ChessBoardCorners
from ChessBoardCorners import ChessBoardCorners

"""
Handles camera input, corner selection, and rotation setup for the chessboard.
"""
class Camera:

    camera = 0 # Index corresponding to selected camera
    points = []
    rotations = 0

    def __init__(self):
        self.camera = 0

    def get_all_cameras(self):
        """
        Detect and list all available camera devices connected to the system.
        Returns:
            dict: {index: camera_name}
        """
        devices = FilterGraph().get_input_devices()

        available_cameras = {}

        for device_index, device_name in enumerate(devices):
            available_cameras[device_index] = device_name

        return available_cameras

    def display_camera(self, camera_function):
        """
        Display a live camera feed and pass each frame to a provided callback.
        Pressing Enter or custom logic in `camera_function` can stop the feed.
        """
        cv2.namedWindow("Camera")
        vc = cv2.VideoCapture(self.camera, cv2.CAP_DSHOW)

        if vc.isOpened():  # try to get the first frame
            rval, frame = vc.read()
        else:
            rval = False

        stop = False

        while rval or stop: # show the camera until escape is pressed
            cv2.imshow("Camera", frame)
            cv2.setWindowProperty("Camera", cv2.WND_PROP_TOPMOST, 1)
            rval, frame = vc.read()
            key = cv2.waitKey(20)
            stop = camera_function(key, frame)

        cv2.destroyWindow("Camera")
        vc.release()

    def get_four_corners_camera(self):
        """
        Allow user to manually click four corners of the chessboard in the camera feed.
        Returns:
            list[tuple], frame - ordered corners and final frame
        """
        cv2.namedWindow("Click Four Corners")
        vc = cv2.VideoCapture(self.camera, cv2.CAP_DSHOW)

        if vc.isOpened():  # try to get the first frame
            rval, frame = vc.read()
        else:
            rval = False

        if(not rval): raise Exception("Could not read camera")

        self.points = []

        cbc = ChessBoardCorners()

        # Show the camera until all four corners are pressed (destroy any that are clicked again)
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

        # Sort corners based on their position
        bottom_right, _ = max(enumerate([pt[0] + pt[1] for pt in self.points]), key=operator.itemgetter(1))
        top_left, _ = min(enumerate([pt[0] + pt[1] for pt in self.points]), key=operator.itemgetter(1))
        bottom_left, _ = min(enumerate([pt[0] - pt[1] for pt in self.points]), key=operator.itemgetter(1))
        top_right, _ = max(enumerate([pt[0] - pt[1] for pt in self.points]), key=operator.itemgetter(1))

        return [self.points[top_left], self.points[top_right], self.points[bottom_left], self.points[bottom_right]], frame

    def capture_frame_from_camera(self):
        """
        Capture a single grayscale frame from the active camera
        """
        vc = cv2.VideoCapture(self.camera, cv2.CAP_DSHOW)

        if vc.isOpened():  # try to get the first frame
            rval, frame = vc.read()
            vc.release()
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        vc.release()
        raise Exception("Unable to find camera")

    def capture_colored_frame_from_camera(self):
        """
        Capture a single colored frame from the active camera
        """
        vc = cv2.VideoCapture(self.camera, cv2.CAP_DSHOW)

        if vc.isOpened():  # try to get the first frame
            rval, frame = vc.read()
            vc.release()
            return frame
        vc.release()
        raise Exception("Unable to find camera")


    def rotate_image(self, image):
        """
        Rotate image clockwise by 90 degrees 'rotations' times.
        """
        rots = self.rotations
        while (rots > 0):
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            rots = rots - 1
        return image

    def setup_rotations(self, func):
        """
        Allow user to visually adjust camera rotation interactively.
        Clicking increments rotation by 90° until the desired orientation is reached.
        """
        cv2.namedWindow("Rotation Selection")
        vc = cv2.VideoCapture(self.camera, cv2.CAP_DSHOW)

        if vc.isOpened():  # try to get the first frame
            rval, frame = vc.read()
        else:
            rval = False

        frame = func(frame)
        frame = self.rotate_image(frame)

        stop = False

        while rval and not stop: #Show camera with rotations applied until escape is pressed
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
        """Return True to stop camera loop when Enter (key=13) is pressed."""
        if key_input == 13:
            return True
        return False


    def corners_click_event(self, event, x, y, flags, params):
        """
        Mouse event: add or remove clicked points representing chessboard corners.
        """
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
        """
        Mouse event: rotate image 90° clockwise per click (cycles every 4).
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            if(self.rotations == 3):
                self.rotations = 0
            else:
                self.rotations += 1
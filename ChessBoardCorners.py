import numpy as np
import cv2
import operator


class ChessBoardCorners:
    chessboard_corners = None

    def __init__(self):
        self.chessboard_corners = [(0,0), (0,0), (0,0), (0,0)]

    # Unify lines using rho and theta
    # credit to: https://stackoverflow.com/questions/43664328/remove-similar-lines-provided-by-hough-transform
    def unify_lines(self, lines, rho_threshold=10, theta_threshold=np.pi / 180 * 10):
        grouped_lines = []

        # For each line, if the angle between two lines or the distance between two lines is between the threshold
        # add them into a list together and repeat.
        for line in lines:
            for rho, theta in line:
                matched_group = None
                for group in grouped_lines:
                    for u_rho, u_theta in group:
                        if (abs(u_rho - rho) < rho_threshold and abs(u_theta - theta) < theta_threshold) or \
                                (abs(u_rho + rho) < rho_threshold and abs(u_theta - (theta + np.pi)) % (
                                        2 * np.pi) < theta_threshold):
                            matched_group = group
                            break
                    if matched_group:
                        break
                if matched_group:
                    matched_group.append((rho, theta))
                else:
                    grouped_lines.append([(rho, theta)])

        # For each group of lines, compute the median line
        unified_lines = []
        for group in grouped_lines:
            median_rho, median_theta = self.get_median_rho_theta(group)
            unified_lines.append((median_rho, median_theta))

        return np.array([[line] for line in unified_lines], dtype=np.float32)

    # Calculate the median angle of a group of lines
    def get_median_rho_theta(self, group):
        group.sort(key=lambda a: a[1])
        index = (len(group) - 1) // 2
        return group[index]

    # Segment lines using theta
    # credit to: https://stackoverflow.com/questions/43664328/remove-similar-lines-provided-by-hough-transform
    def segment_lines_by_angle(self, lines, theta_threshold=np.pi / 180 * 10):
        grouped_lines = []

        # Step 1: Group lines by angle
        for line in lines:
            for rho, theta in line:
                matched_group = None
                for group in grouped_lines:
                    for u_rho, u_theta in group:
                        if ((abs(u_theta - theta) < theta_threshold) or
                                abs(u_theta - (theta + np.pi)) % (2 * np.pi) < theta_threshold or
                                abs(u_theta - (np.pi - theta)) < theta_threshold or
                                abs(theta - (np.pi - u_theta)) < theta_threshold):
                            matched_group = group
                            break
                    if matched_group:
                        break
                if matched_group:
                    matched_group.append((rho, theta))
                else:
                    grouped_lines.append([(rho, theta)])

        # Step 2: Find the top 2 most common angle groups
        grouped_lines = sorted(grouped_lines, key=len, reverse=True)

        if (len(grouped_lines) < 2):
            raise Exception("There are less than 2 lines detected")

        # Get most common two angles of lines (they should usually be nearly 90* apart from each other)
        vert_lines = np.array([[line] for line in grouped_lines[0]], dtype=np.float32)
        hoz_lines = np.array([[line] for line in grouped_lines[1]], dtype=np.float32)
        return (vert_lines, hoz_lines)

    # Calculate the intersections of two horizontal and vertical lines
    def get_intersections_of_hoz_vert_lines(self, hoz_line, vert_line, image):
        list_of_points = []
        for xLine in hoz_line:
            for yLine in vert_line:
                # Find the intersection point of two lines
                point = self.get_intersection_point(xLine, yLine)
                h, w = image.shape
                # If the point is in the range of the image shape +-400, add the point
                if (point[0] >= -400 and point[1] >= -400 and point[0] <= w + 400 and point[1] <= h + 400):
                    list_of_points.append(point)

        if (len(list_of_points) < 4):
            raise Exception("There are less than 4 intersecting lines, board was not detected")

        return list_of_points

    # credit to: https://stackoverflow.com/questions/46565975/find-intersection-point-of-two-lines-drawn-using-houghlines-opencv
    def get_intersection_point(self, line1, line2):
        rho1, theta1 = line1[0]
        rho2, theta2 = line2[0]

        A = np.array([
            [np.cos(theta1), np.sin(theta1)],
            [np.cos(theta2), np.sin(theta2)]
        ])

        b = np.array([[rho1], [rho2]])

        x0, y0 = np.linalg.solve(A, b)
        x0, y0 = int(np.round(x0)), int(np.round(y0))
        return [x0, y0]

    # Finds the outer 4 corners from a list of points
    # credit: https://medium.com/@neshpatel/solving-sudoku-part-ii-9a7019d196a2
    def get_chessboard_corner_points(self, points):
        bottom_right, _ = max(enumerate([pt[0] + pt[1] for pt in points]), key=operator.itemgetter(1))
        top_left, _ = min(enumerate([pt[0] + pt[1] for pt in points]), key=operator.itemgetter(1))
        bottom_left, _ = min(enumerate([pt[0] - pt[1] for pt in points]), key=operator.itemgetter(1))
        top_right, _ = max(enumerate([pt[0] - pt[1] for pt in points]), key=operator.itemgetter(1))
        return [points[top_left], points[top_right], points[bottom_left], points[bottom_right]]

    def get_chessboard_corners(self):
        return self.chessboard_corners

    # |----------------------------------------|
    # |HOUGH TRANSFORMS AND IMAGE MANIPULATIONS|
    # |----------------------------------------|

    # Calculate hough transform over an image
    def hough_transform_lines(self, image):
        # Segment image using adaptive threshold
        adaptive_threshold = self.apply_adaptive_threshold(image)

        # Apply edge detector using cannyEdge (not used)
        # edges = self.apply_canny(image)

        # Apply both?
        adaptive_canny = self.apply_canny(adaptive_threshold)

        # Get Hough Lines
        lines = cv2.HoughLines(image=adaptive_canny, rho=1, theta=np.pi / 180, threshold=150, lines=np.array([]))

        return lines

    # Preprocess the image (makes image brightness invariant)
    def apply_adaptive_threshold(self, image):
        copy_image = image.copy()

        # Blur the image to remove any small imperfections
        blur = cv2.GaussianBlur(copy_image, (9, 9), 0)
        # Remove any "salt and pepper" from an image
        # blur = cv2.medianBlur(copy_image, 5)

        # Apply an adaptive thresholding to make a binary image
        blur = blur.astype(np.uint8)
        adapt_type = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        thresh_type = cv2.THRESH_BINARY_INV
        bin_img = cv2.adaptiveThreshold(blur, 255, adapt_type, thresh_type, 11, 2)
        return bin_img

    # Apply a canny edge detector
    # credit: https://stackoverflow.com/questions/41893029/opencv-canny-edge-detection-not-working-properly
    def apply_canny(self, image):
        copyImage = image.copy()

        # Use an upper and lower limit defined below
        v = np.median(copyImage)
        sigma = 0.33
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        canny = cv2.Canny(copyImage, lower, upper, apertureSize=3)
        return canny

    # Warps an image using perspective transform
    # credit: https://medium.com/@neshpatel/solving-sudoku-part-ii-9a7019d196a2
    def warp_image(self, image, board_corners):
        top_left, top_right, bottom_left, bottom_right = board_corners[0], board_corners[1], board_corners[2], board_corners[3]

        warp_src = np.array([top_left, top_right, bottom_right, bottom_left], dtype='float32')

        side = max([
            self.distance_between(bottom_right, top_right),
            self.distance_between(top_left, bottom_left),
            self.distance_between(bottom_right, bottom_left),
            self.distance_between(top_left, top_right)
        ])

        warp_dst = np.array([[0, 0], [side - 1, 0], [side - 1, side - 1], [0, side - 1]], dtype='float32')

        # Calculate the perspective transformation
        m = cv2.getPerspectiveTransform(warp_src, warp_dst)

        # Apply the perspective transform onto the image
        return cv2.warpPerspective(image, m, (int(side), int(side)))

    # Calculate the distance between two points using a^2 + b^2 = c^2
    def distance_between(self, p1, p2):
        a = p2[0] - p1[0]
        b = p2[1] - p1[1]
        return np.sqrt((a ** 2) + (b ** 2))

    def apply_lines(self, image, lines, colour=(0, 255, 0)):
        newImage = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)

        for line in lines:
            for rho, theta in line:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 2000 * (-b))
                y1 = int(y0 + 2000 * (a))
                x2 = int(x0 - 2000 * (-b))
                y2 = int(y0 - 2000 * (a))
                cv2.line(newImage, (x1, y1), (x2, y2), colour, 2)
        return newImage

    def apply_hoz_vert_lines(self, image, hozLines, vertLines):
        newImage = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
        for line in hozLines:
            for rho, theta in line:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 2000 * (-b))
                y1 = int(y0 + 2000 * a)
                x2 = int(x0 - 2000 * (-b))
                y2 = int(y0 - 2000 * a)
                cv2.line(newImage, (x1, y1), (x2, y2), (0, 255, 0), 2)

        for line in vertLines:
            for rho, theta in line:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 2000 * (-b))
                y1 = int(y0 + 2000 * a)
                x2 = int(x0 - 2000 * (-b))
                y2 = int(y0 - 2000 * a)
                cv2.line(newImage, (x1, y1), (x2, y2), (0, 0, 255), 2)
        return newImage

    def apply_int_points(self, image, points):
        new_image = image.copy()
        for point in points:
            cv2.circle(new_image, point, 4, (0, 255, 255), 4)
        return new_image

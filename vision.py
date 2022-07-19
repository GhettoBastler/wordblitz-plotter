#! /usr/bin/env python


import time
import cv2
import numpy as np
from picamera import PiCamera
from io import BytesIO


class ROIExtractor:
    """
    Capture images and process them to extract a region of interest"""

    def __init__(self, cam_res, cam_mat, dist_coeffs, board, board_size,
                 roi_bounds, px_per_mm):

        self.cam_res = cam_res
        self.cam_mat = cam_mat
        self.dist_coeffs = dist_coeffs
        self.board = board
        self.board_size = board_size  # in mm
        self.roi_bounds = roi_bounds  # in mm
        self.px_per_mm = px_per_mm
        self.cam_res = self.cam_res

        self._aruco_params = cv2.aruco.DetectorParameters_create()
        self._camera = PiCamera()
        time.sleep(0.1)  # Allow camera to warmup
        self._camera.resolution = self.cam_res

    def _capture_image(self):
        """
        Snap a picture with the RPi camera module"""

        img_buffer = BytesIO()
        self._camera.capture(img_buffer, 'jpeg')
        img_buffer.seek(0)
        array = np.asarray(bytearray(img_buffer.read()), dtype=np.uint8)
        return cv2.imdecode(array, cv2.IMREAD_COLOR)

    def _get_perspective_matrix(self, img):
        """
        Use the AruCo board to calculate the perspective matrix"""

        # Detecting the markers
        corners, ids, rejected = cv2.aruco.detectMarkers(
            img, self.board.dictionary, parameters=self._aruco_params)
        if ids is None:
            raise Exception('No marker detected.')

        # Estimating camera pose
        retval, rvec, tvec = cv2.aruco.estimatePoseBoard(
            corners, ids, self.board, self.cam_mat, self.dist_coeffs,
            None, None)

        if retval == 0:
            raise Exception('Failed to estimate pose')

        # Projecting board corners using the estimated pose
        board_corners_mm = np.array([
            [0, 0, 0],
            [self.board_size[0], 0, 0],
            [self.board_size[0], self.board_size[1], 0],
            [0, self.board_size[1], 0]
        ], dtype=np.float32)

        projected, _ = cv2.projectPoints(board_corners_mm, rvec, tvec,
                                         self.cam_mat, self.dist_coeffs)
        board_corners_px = (np.array([c[:2] for c in board_corners_mm],
                                     dtype=np.float32)
                            * self.px_per_mm)

        return cv2.getPerspectiveTransform(projected, board_corners_px)

    def _warp_perspective(self, img, matrix):
        """
        Warp an image using the given perspective matrix"""

        size = tuple(self.px_per_mm * np.array(self.board_size))
        return cv2.warpPerspective(img, matrix, size)

    def _crop_roi(self, img):
        """
        Crop the markers out of a warped image"""

        minX, minY, maxX, maxY = self.px_per_mm * np.array(self.roi_bounds)
        return img[minX:maxX, minY:maxY]

    def get_roi(self):
        """
        Capture, warp and crop an image of the ROI"""

        img = self._capture_image()
        matrix = self._get_perspective_matrix(img)
        warped = self._warp_perspective(img, matrix)
        cropped = self._crop_roi(warped)
        return cropped

    def __exit__(self):
        self._camera.close()

#!/usr/bin/env python

import cv2
import numpy as np


def detect_rectangles(cropped, min_area, max_area):
    res = []
    rects = []
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

    # Detecting contours
    blurred = cv2.GaussianBlur(gray, (31, 31), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    raw_contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Discard contours that are too small or too large
    contours = [c for c in raw_contours if cv2.contourArea(c) > min_area and cv2.contourArea(c) < max_area]

    # Approximating polygons
    for cont in contours:
        epsilon = 0.01 * cv2.arcLength(cont, True)
        approx = cv2.approxPolyDP(cont, epsilon, True)

        # Discard shapes that are not 4 sided
        if len(approx) != 4:
            continue

        # Get the best fitting rectangle (from : https://theailearner.com/2020/11/03/opencv-minimum-area-rectangle/)
        rect = cv2.minAreaRect(approx)
        points = cv2.boxPoints(rect)
        points = np.int0(points)
        # Add the points to the list
        res.append(points)
        rects.append(rect)

    return res, rects


def get_transform_matrix(rect):
    src_w, src_h = rect[1]
    src_points = np.array([
        (0, src_h),
        (0, 0),
        (src_w, 0),
    ]).astype(np.float32)

    dst_points = cv2.boxPoints(rect)[:3]

    return cv2.getAffineTransform(src_points, dst_points)

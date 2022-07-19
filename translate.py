#! /usr/bin/env python

import numpy as np


class Translator:
    """
    Translates pixel coordinates from the ROI image to mm for
    the plotter to use"""

    def __init__(self, roi_bounds, px_per_mm):
        self.roi_bounds = roi_bounds  # (minX, minY, maxX, maxY) in mm
        self.px_per_mm = px_per_mm

    def pt_px_to_mm(self, point):
        """
        Convert pixel coordinates to mm, inverting Y axis"""

        # Convert pixels to mm
        x, y = np.array(point) / self.px_per_mm

        # Inverting Y axis
        roi_height = self.roi_bounds[3] - self.roi_bounds[1]
        y = roi_height - y

        return (x, y)

    def path_px_to_mm(self, path):
        """
        Convert all points in a path to mm"""
        res = []
        for pt in path:
            res.append(self.pt_px_to_mm(pt))

        return res

#!/usr/bin/env python

import yaml
import cv2
import numpy as np
from vision import ROIExtractor
from plotter import Plotter
from translate import Translator

PARAM_FILENAME = 'params.yaml'

with open(PARAM_FILENAME) as f:
    params = yaml.safe_load(f)

cam_res = params['camera']['resolution']
cam_mat = np.array(params['camera']['matrix'], dtype=np.float32)
dist_coeffs = np.array(params['camera']['dist_coeffs'], dtype=np.float32)

board_obj_pts = np.array(params['board']['object_points'], dtype=np.float32)
board_ids = np.array(params['board']['ids'])
board_dict_name = params['board']['dict_name']
board_size = params['board']['size']
roi_bounds = params['board']['roi_bounds']

plotter_port = params['plotter']['port']
plotter_baudrate = params['plotter']['baudrate']
plotter_commands = params['plotter']['commands']
plotter_away = params['plotter']['away']

px_per_mm = params['px_per_mm']

board_dict = cv2.aruco.Dictionary_get(cv2.aruco.__getattribute__(board_dict_name))
board = cv2.aruco.Board_create(board_obj_pts, board_dict, board_ids)

EXTRACTOR = ROIExtractor(cam_res, cam_mat, dist_coeffs, board, board_size, roi_bounds, px_per_mm)
TRANSLATOR = Translator(roi_bounds, px_per_mm)
PLOTTER = Plotter(plotter_port, plotter_baudrate, plotter_commands, plotter_away)
PLOTTER.set_position(PLOTTER.away) # Assume that the plotter is already in the top left corner

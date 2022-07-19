#!/usr/bin/env python

import numpy as np
import cv2
import json
import time
from tesserocr import PyTessBaseAPI, PSM
from PIL import Image

from machine import EXTRACTOR, TRANSLATOR, PLOTTER
from utils import detect_rectangles, get_transform_matrix
from boggle_solver import get_paths


TREEFILE = 'tree.json'


class NoRectangleError(Exception):
    """
    Raised when no rectangle is detected in the ROI"""
    pass

class TooManyRectanglesError(Exception):
    """
    Raised more than one rectangle is detected in the ROI"""
    pass

def extract_grid(roi, min_area=50000, max_area=150000):
    """
    Returns the straightened grid with the corresponding affine
    transform matrix"""

    
    # Detecting rectangles
    points, rects = detect_rectangles(roi, min_area, max_area)

    if len(rects) < 1:
        # No rectangle detected
        raise NoRectangleError
    elif len(rects) > 1:
        # More than one rectangle detected
        raise TooManyRectanglesError

    # Getting transform matrix
    matrix = get_transform_matrix(rects[0])

    # Performing inverse affine transform to extract the grid
    inv_matrix = cv2.invertAffineTransform(matrix)
    size = tuple(map(int, rects[0][1]))
    extracted = cv2.warpAffine(roi, inv_matrix, size)

    return extracted, matrix


def process_grid(img, api):
    """
    Perform OCR on the grid image to extract the letters"""

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Calculating cell positions
    grid_w = gray.shape[0]  # Assuming the grid is square
    roi_w = grid_w / (4 * 1.5)
    start_offset = grid_w / (4 * 4.5)

    letters = []

    for i in range(4):
        for j in range(4):
            # Extracting one cell
            min_x = start_offset + i * grid_w / 4
            min_y = start_offset + j * grid_w / 4
            max_x = min_x + roi_w
            max_y = min_y + roi_w

            roi = gray[int(min_x):int(max_x), int(min_y):int(max_y)]

            # Preprocessing the image
            blur = cv2.GaussianBlur(roi.copy(), (5, 5), 0)
            _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            processed = thresh
            kernel = np.ones((3,3),np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

            # Performing OCR
            api.SetImage(Image.fromarray(processed))
            api.SetVariable('tessedit_char_whitelist', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1lo05s|$°')
            detected = api.GetUTF8Text()

            if detected.strip():
                if detected.strip()[0] in ('1', 'l', '|'):
                    #print(f'J\'ai cru que c\'était un {detected.strip()}, mais c\'est probablement un I')
                    letter = 'I'
                elif detected.strip()[0] in ('o', '0', '°'):
                    #print(f'J\'ai cru que c\'était un {detected.strip()}, mais c\'est probablement un O')
                    letter = 'O'
                elif detected.strip()[0] in ('5', 's', '$'):
                    #print(f'J\'ai cru que c\'était un {detected.strip()}, mais c\'est probablement un S')
                    letter = 'S'
                else:
                    letter = detected.strip()[0]
            else:
                letter = '_' # If we dont know what letter it is, replace with '_'

            letters.append(letter[0])

    grid = [letters[i*4:(i+1)*4] for i in range(4)]

    return grid


def run(extractor, translator, plotter):
    """
    Main thing"""

    # Importing words
    with open(TREEFILE) as f:
        word_tree = json.load(f)

    # Loading Tesseract
    with PyTessBaseAPI(psm=PSM.SINGLE_CHAR) as api:
        while True:
            input('Ready. Press Enter to start')
            start_time = time.time()

            extracted = False
            while not extracted:
                try:
                    roi = extractor.get_roi()
                    min_area = 2000 * extractor.px_per_mm**2
                    max_area = 6000 * extractor.px_per_mm**2
                    grid_img, matrix = extract_grid(roi, min_area, max_area)

                except NoRectangleError:
                    print('Error: No rectangle was detected. Try adjusting the screen brightness.')
                    input('Press Enter to retry')
                    continue

                except TooManyRectanglesError:
                    print('Error: More than one rectangle was detected in the ROI. Try clearing the workspace of anything other than the phone.')
                    input('Press Enter to retry')
                    continue

                extracted = True

            grid = process_grid(grid_img, api)
            for line in grid:
                print(' '.join(line))

            n_unknown = 0
            for line in grid:
                n_unknown += line.count('_')

            print(f'{n_unknown} letter were not recognized')
            size = sum(grid_img.shape[:2])/2

            paths = get_paths(grid, word_tree, size)

            # Transforming back to ROI
            paths_roi = []
            for path in paths:
                curr_path = []
                for pt in path:
                    curr_path.append(np.matmul(matrix, np.array(pt + (1,)).T))
                paths_roi.append(curr_path)

            # Converting to mm
            paths_mm = []
            for path in paths_roi:
                paths_mm.append(translator.path_px_to_mm(path))

            # Moving plotter
            for path in paths_mm:
                ret = plotter.trace(path)
                if not ret:
                    print('Interrupted')
                    break
                if time.time() - start_time >= 80:
                    print('Out of time')
                    break

            # Moving the plotter out of the way
            plotter.pen_up()
            plotter.move_away()
            plotter.pen_down()


if __name__ == '__main__':
    run(EXTRACTOR, TRANSLATOR, PLOTTER)

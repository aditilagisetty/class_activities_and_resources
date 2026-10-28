#!/usr/bin/env python3

""" Live version of the tutorial's Undistortion step: original vs. undistorted webcam
    frames side by side, using the remapping method (maps computed once, reused every frame). """

import argparse
from os import path

import numpy as np
import cv2 as cv

parser = argparse.ArgumentParser()
parser.add_argument("--camera", type=int, default=0, help="webcam index (/dev/videoN)")
parser.add_argument("--alpha", type=float, default=1.0,
                    help="0 = minimum unwanted pixels, 1 = all pixels retained (black borders)")
parser.add_argument("--crop", action="store_true", help="crop the result to roi like the tutorial")
args = parser.parse_args()

enclosing_dir = path.dirname(path.realpath(__file__))
data = np.load(path.join(enclosing_dir, 'calibration.npz'))
mtx, dist = data['mtx'], data['dist']

cap = cv.VideoCapture(args.camera)
mapx = None
while True:
    ret, img = cap.read()
    if not ret:
        break
    if mapx is None:
        h, w = img.shape[:2]
        newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), args.alpha, (w, h))
        mapx, mapy = cv.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w, h), 5)

    dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)
    if args.crop:
        # crop the image, then resize back so it can sit next to the original
        x, y, rw, rh = roi
        dst = cv.resize(dst[y:y+rh, x:x+rw], (w, h))

    cv.imshow('original | undistorted   [q]=quit', np.hstack((img, dst)))
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()

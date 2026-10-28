#!/usr/bin/env python3

""" Camera calibration following the OpenCV tutorial section by section:
    https://docs.opencv.org/4.13.0/dc/dbb/tutorial_py_calibration.html

    Setup -> Calibration -> Undistortion (both methods) -> Re-projection Error
    Run capture_images.py first to fill calib_images/ with checkerboard photos. """

import argparse
import glob
from os import path

import numpy as np
import cv2 as cv

parser = argparse.ArgumentParser()
parser.add_argument("--cols", type=int, default=9, help="inner corners per row (squares - 1)")
parser.add_argument("--rows", type=int, default=6, help="inner corners per column (squares - 1)")
parser.add_argument("--square", type=float, default=25.0, help="measured square size in mm")
args = parser.parse_args()

enclosing_dir = path.dirname(path.realpath(__file__))
pattern_size = (args.cols, args.rows)

# ---------------------------------------------------------------- Setup

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(cols-1,rows-1,0)
# multiplied by the square size so the results come out in mm
objp = np.zeros((args.rows*args.cols, 3), np.float32)
objp[:, :2] = np.mgrid[0:args.cols, 0:args.rows].T.reshape(-1, 2) * args.square

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.

images = sorted(glob.glob(path.join(enclosing_dir, 'calib_images', '*.png')))
if not images:
    raise SystemExit("No images in calib_images/ -- run capture_images.py first")

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, pattern_size, None)
    print(f"{path.basename(fname)}: {'found' if ret else 'NOT found'}")

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        cv.drawChessboardCorners(img, pattern_size, corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(500)

cv.destroyAllWindows()

# the tutorial asks for at least 10 test patterns
if len(objpoints) < 10:
    print(f"WARNING: only {len(objpoints)} usable images, tutorial recommends at least 10")

# ---------------------------------------------------------------- Calibration

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

np.set_printoptions(suppress=True, precision=4)
print("\ncamera matrix (mtx):\n", mtx)
print(f"  fx={mtx[0, 0]:.1f}  fy={mtx[1, 1]:.1f}  cx={mtx[0, 2]:.1f}  cy={mtx[1, 2]:.1f}")
print("distortion coefficients (k1 k2 p1 p2 k3):\n", dist.ravel())

# ---------------------------------------------------------------- Undistortion

# take one of the calibration images and undistort it
img = cv.imread(images[0])
h, w = img.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

# 1. Using cv.undistort()
dst = cv.undistort(img, mtx, dist, None, newcameramtx)

# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite(path.join(enclosing_dir, 'calibresult.png'), dst)

# 2. Using remapping (gives the same result as method 1)
h, w = img.shape[:2]
mapx, mapy = cv.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w, h), 5)
dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)

# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite(path.join(enclosing_dir, 'calibresult_remap.png'), dst)
print("\nwrote calibresult.png (cv.undistort) and calibresult_remap.png (remap)")

# store the camera matrix and distortion coefficients for future uses
np.savez(path.join(enclosing_dir, 'calibration.npz'), mtx=mtx, dist=dist)
print("wrote calibration.npz")

# ---------------------------------------------------------------- Re-projection Error

mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    # reshape both to Nx2: OpenCV 5 rejects the tutorial's (N,1,2) vs (N,2) comparison
    error = cv.norm(imgpoints[i].reshape(-1, 2), imgpoints2.reshape(-1, 2), cv.NORM_L2)/len(imgpoints2)
    mean_error += error

print("\ntotal error: {}".format(mean_error/len(objpoints)))

#!/usr/bin/env python3

""" Grab checkerboard photos from your webcam (the approach suggested in the tutorial's
    first note: check each live frame for the pattern, keep the good ones).
    SPACE saves the current frame to calib_images/ (detected or not), q quits. """

import argparse
import os

import cv2 as cv

parser = argparse.ArgumentParser()
parser.add_argument("--cols", type=int, default=9, help="inner corners per row")
parser.add_argument("--rows", type=int, default=6, help="inner corners per column")
parser.add_argument("--camera", type=int, default=0, help="webcam index (/dev/videoN)")
args = parser.parse_args()

out_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "calib_images")
os.makedirs(out_dir, exist_ok=True)
pattern = (args.cols, args.rows)
cap = cv.VideoCapture(args.camera)
if not cap.isOpened():
    raise SystemExit(f"Could not open camera {args.camera}")

count = len([f for f in os.listdir(out_dir) if f.endswith(".png")])
while True:
    ok, frame = cap.read()
    if not ok:
        break
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # FAST_CHECK keeps the live preview responsive when no board is visible
    found, corners = cv.findChessboardCorners(gray, pattern, cv.CALIB_CB_FAST_CHECK)
    preview = frame.copy()
    cv.drawChessboardCorners(preview, pattern, corners, found)
    cv.putText(preview, f"saved: {count}  found: {found}  [SPACE]=save [q]=quit",
                (10, 25), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if found else (0, 0, 255), 2)
    cv.imshow("capture", preview)

    key = cv.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    if key == ord(" "):
        # save even when the board isn't detected; calibrate.py skips frames it can't use
        if not found:
            print("Board not detected -- saving anyway")
        path = os.path.join(out_dir, f"img_{count:02d}.png")
        cv.imwrite(path, frame)  # save the clean frame, not the annotated one
        print("saved", path)
        count += 1

cap.release()
cv.destroyAllWindows()

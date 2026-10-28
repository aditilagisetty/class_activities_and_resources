# In-class Day 15 — Camera Calibration

Activity: https://comprobo26.github.io/in-class/day15
`calibrate.py` follows the OpenCV tutorial section by section: https://docs.opencv.org/4.13.0/dc/dbb/tutorial_py_calibration.html

Plain Python + OpenCV (no ROS needed).

1. Print a checkerboard (https://calib.io/pages/camera-calibration-pattern-generator), print at 100% scale,
   tape it flat, and measure one square in mm.
2. `python3 capture_images.py --cols 9 --rows 6` — SPACE saves a frame when corners are drawn, q quits. Get 15–20 varied views.
3. `python3 calibrate.py --cols 9 --rows 6 --square <mm>` — shows each detection, prints the camera matrix + distortion coefficients and the total re-projection error;
   writes `calibresult.png` (cv.undistort), `calibresult_remap.png` (remap), and `calibration.npz` (mtx, dist).
4. `python3 undistort_live.py` — original vs. undistorted side by side (remap method; `--crop` crops to roi).

`--cols/--rows` are **inner corners**, i.e. (squares − 1) in each direction.

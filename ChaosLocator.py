import pyautogui
import cv2
import numpy as np
import time

# ---- CONFIG ----
CROP_X1, CROP_Y1, CROP_X2, CROP_Y2 = 100, 200, 1800, 900

# Normal lighting colors (BGR)
NORMAL_COLORS = [
    np.array([237, 238, 231]),  # skin
    np.array([134, 134, 129]),  # shaded skin
    np.array([46, 56, 219]),    # hair
    np.array([18, 199, 245]),   # gun
]

# Shaded lighting colors (BGR)
SHADED_COLORS = [
    np.array([200, 203, 192]),  # skin
    np.array([219, 57, 46]),    # hair
    np.array([72, 79, 153]),    # dark hair/body
    np.array([80, 167, 196]),   # gun
]

PLAYER_COLORS_BGR = NORMAL_COLORS + SHADED_COLORS
PLAYER_TOL = 8
PROX_RADIUS = 8
SIDE_MARGIN = 0.05
SMOOTH_ALPHA = 0.6

# Size filtering for torso+hair
MIN_WIDTH, MAX_WIDTH = 50, 250
MIN_HEIGHT, MAX_HEIGHT = 100, 300

# ---- HELPERS ----
def make_mask(img, color, tol):
    lower = np.clip(color - tol, 0, 255).astype(np.uint8)
    upper = np.clip(color + tol, 0, 255).astype(np.uint8)
    return cv2.inRange(img, lower, upper)

def find_player_blob(crop_bgr, last_cx=None, last_cy=None):
    # build masks
    masks = [make_mask(crop_bgr, c, PLAYER_TOL) for c in PLAYER_COLORS_BGR]
    combined_mask = masks[0]
    for m in masks[1:]:
        combined_mask = cv2.bitwise_or(combined_mask, m)

    # merge nearby blobs
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (PROX_RADIUS, PROX_RADIUS))
    prox = cv2.dilate(combined_mask, k, iterations=1)
    prox = cv2.morphologyEx(prox, cv2.MORPH_CLOSE, k)
    prox = cv2.morphologyEx(prox, cv2.MORPH_OPEN, k)

    # connected components
    num, labels, stats, cents = cv2.connectedComponentsWithStats(prox, connectivity=8)
    if num <= 1:
        return None, None, prox, labels

    # largest component within size limits
    valid_idx = None
    for i in range(1, num):
        w, h = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
        if MIN_WIDTH <= w <= MAX_WIDTH and MIN_HEIGHT <= h <= MAX_HEIGHT:
            if valid_idx is None or stats[i, cv2.CC_STAT_AREA] > stats[valid_idx, cv2.CC_STAT_AREA]:
                valid_idx = i

    if valid_idx is None:
        return None, None, prox, labels

    idx = valid_idx
    cx, cy = cents[idx]
    x, y, w, h = stats[idx, 0], stats[idx, 1], stats[idx, 2], stats[idx, 3]

    if last_cx is not None and last_cy is not None:
        cx = SMOOTH_ALPHA * cx + (1 - SMOOTH_ALPHA) * last_cx
        cy = SMOOTH_ALPHA * cy + (1 - SMOOTH_ALPHA) * last_cy

    return (int(cx), int(cy), x, y, w, h), idx, prox, labels

# ---- MAIN ----
if __name__ == "__main__":
    cv2.namedWindow("Debug", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Debug", 1100, 600)

    last_cx = last_cy = None
    last_side = None

    print("Running… press 'q' to quit.")
    while True:
        frame = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
        crop = frame[CROP_Y1:CROP_Y2, CROP_X1:CROP_X2]

        centroid, label_idx, prox_mask, labels = find_player_blob(crop, last_cx, last_cy)

        vis_crop = crop.copy()
        mask_vis = cv2.cvtColor(prox_mask, cv2.COLOR_GRAY2BGR)
        side_text = "Player not found"

        if centroid:
            cx, cy, x, y, w, h = centroid
            last_cx, last_cy = cx, cy

            # highlight blob
            mask_vis[labels == label_idx] = (0, 0, 255)
            cv2.rectangle(vis_crop, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.circle(vis_crop, (cx, cy), 6, (0, 255, 0), -1)

            width = crop.shape[1]
            margin = width * SIDE_MARGIN
            if cx < width / 2 - margin:
                side_text = "You are on the LEFT, opponent is on the RIGHT"
                last_side = side_text
            elif cx > width / 2 + margin:
                side_text = "You are on the RIGHT, opponent is on the LEFT"
                last_side = side_text
            else:
                side_text = last_side if last_side else "Undetermined"

        cv2.putText(vis_crop, side_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (30, 220, 30), 2)
        debug = np.hstack([vis_crop, mask_vis])
        cv2.imshow("Debug", debug)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.005)

    cv2.destroyAllWindows()

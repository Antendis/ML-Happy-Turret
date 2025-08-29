import pyautogui
import cv2
import numpy as np
import time

# ---- CONFIG ----
CROP_X1, CROP_Y1, CROP_X2, CROP_Y2 = 100, 200, 1800, 900

# Player colors (BGR)
PLAYER_COLORS = [
    np.array([20, 27, 27]),   # rgba(27,27,20,255)
    np.array([30, 39, 38]),   # rgba(38,39,30,255)
    np.array([56, 64, 92]),   # rgba(92,64,56,255)
]
PLAYER_TOL = 8
PROX_RADIUS = 7

SIDE_MARGIN = 0.05
SMOOTH_ALPHA = 0.6

# ---- HELPERS ----
def make_mask(img, color, tol):
    lower = np.clip(color - tol, 0, 255).astype(np.uint8)
    upper = np.clip(color + tol, 0, 255).astype(np.uint8)
    return cv2.inRange(img, lower, upper)

def find_player_blob(crop_bgr, last_cx=None, last_cy=None):
    # build masks for each player color
    masks = [make_mask(crop_bgr, c, PLAYER_TOL) for c in PLAYER_COLORS]

    # combine masks using OR
    combined_mask = masks[0]
    for m in masks[1:]:
        combined_mask = cv2.bitwise_or(combined_mask, m)

    # proximity between colors
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (PROX_RADIUS, PROX_RADIUS))
    prox = combined_mask.copy()
    prox = cv2.morphologyEx(prox, cv2.MORPH_CLOSE, k)
    prox = cv2.morphologyEx(prox, cv2.MORPH_OPEN, k)

    # connected components
    num, labels, stats, cents = cv2.connectedComponentsWithStats(prox, connectivity=8)
    if num <= 1:
        return None, None, prox, labels

    # largest blob
    idx = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    if stats[idx, cv2.CC_STAT_AREA] < 100:
        return None, None, prox, labels

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

    print("Running… press 'q' in the window to quit.")
    while True:
        frame = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
        crop = frame[CROP_Y1:CROP_Y2, CROP_X1:CROP_X2]

        result = find_player_blob(crop, last_cx, last_cy)
        centroid, label_idx, prox_mask, labels = result

        vis_crop = crop.copy()
        mask_vis = cv2.cvtColor(prox_mask, cv2.COLOR_GRAY2BGR)
        side_text = "Player not found"

        if centroid:
            cx, cy, x, y, w, h = centroid
            last_cx, last_cy = cx, cy

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

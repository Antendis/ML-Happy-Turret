import pyautogui
import cv2
import numpy as np

# Updated left HP bar coordinates
x1, y1 = 150, 113
x2, y2 = 866, 115

# Target red color in BGR (OpenCV uses BGR)
target_red_bgr = np.array([9, 11, 185])  # converted from RGBA(185,11,9,255)
color_tolerance = 20  # allows slight variation

def extract_left_hp_red():
    # Take screenshot
    frame = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)

    # Crop left HP bar
    hp_crop = frame[y1:y2, x1:x2]

    # Calculate difference from target red
    diff = np.linalg.norm(hp_crop.astype(np.int16) - target_red_bgr, axis=2)

    # Pixels close enough to red are considered "damage flash"
    red_mask = diff < color_tolerance

    # Fraction of the bar that is currently red
    red_fraction = np.sum(red_mask) / hp_crop.shape[1]

    # Optional visualization
    vis = (red_mask.astype(np.uint8) * 255)
    cv2.imshow("Red Pixels", vis)
    cv2.waitKey(1)

    return float(np.clip(red_fraction, 0.0, 1.0))

if __name__ == "__main__":
    while True:
        left_hp_red = extract_left_hp_red()
        print("Left HP red fraction:", left_hp_red)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

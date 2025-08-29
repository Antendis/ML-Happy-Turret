import pyautogui
import cv2
import numpy as np

# Left HP bar coordinates
x1, y1 = 150, 113
x2, y2 = 866, 115

# Target red color in BGR
target_red_bgr = np.array([9, 11, 185])
color_tolerance = 20

# Initialize HP tracking
current_hp = 1.0
max_red_in_window = 0.0

def extract_left_hp_red():
    frame = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
    hp_crop = frame[y1:y2, x1:x2]

    diff = np.linalg.norm(hp_crop.astype(np.int16) - target_red_bgr, axis=2)
    red_mask = diff < color_tolerance

    red_fraction = np.sum(red_mask) / hp_crop.shape[1]

    # Optional visualization
    vis = (red_mask.astype(np.uint8) * 255)
    cv2.imshow("Red Pixels", vis)
    cv2.waitKey(1)

    return float(np.clip(red_fraction, 0.0, 1.0))

if __name__ == "__main__":

    
    while True:
        red_fraction = extract_left_hp_red()

        if red_fraction > 0:
            # Update max red seen during this "damage flash"
            max_red_in_window = max(max_red_in_window, red_fraction)
        else:
            # Flash ended, subtract the biggest red fraction from current HP
            if max_red_in_window > 0:
                current_hp -= max_red_in_window
                current_hp = max(current_hp, 0.0)
                max_red_in_window = 0.0

        print(f"Current HP: {current_hp:.3f}, Red fraction: {red_fraction:.3f}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
# capture_image.py

import os

def capture_image(filename='intruder.jpg'):
    # Import cv2 only when function is called (lazy import)
    # This allows Django to start without OpenCV if this function isn't used
    import cv2
    
    # Open the webcam
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    
    if ret:
        # Save the captured image
        if not os.path.exists('captured_images'):
            os.makedirs('captured_images')
        image_path = os.path.join('captured_images', filename)
        cv2.imwrite(image_path, frame)
    else:
        image_path = None
        
    cam.release()
    return image_path

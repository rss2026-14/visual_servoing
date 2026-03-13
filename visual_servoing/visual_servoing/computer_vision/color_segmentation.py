
import cv2
import numpy as np

#################### X-Y CONVENTIONS #########################
# 0,0  X  > > > > >
#
#  Y
#
#  v  This is the image. Y increases downwards, X increases rightwards
#  v  Please return bounding boxes as ((xmin, ymin), (xmax, ymax))
#  v
#  v
#  v
###############################################################


def image_print(img):
    """
    Helper function to print out images, for debugging. Pass them in as a list.
    Press any key to continue.
    """
    cv2.imshow("image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def cd_color_segmentation(img, template):
    """
    Implement the cone detection using color segmentation algorithm
    Input:
        img: np.3darray; the input image with a cone to be detected. BGR.
        template: Not required, but can optionally be used to automate setting hue filter values.
    Return:
        bbox: ((x1, y1), (x2, y2)); the bounding box of the cone, unit in px
            (x1, y1) is the top left of the bbox and (x2, y2) is the bottom right of the bbox
    """
    ########## YOUR CODE STARTS HERE ##########
    HSV_img=cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_bound = np.array([5, 150, 90])
    upper_bound = np.array([50, 255, 255])
    cone_mask=cv2.inRange(HSV_img,lower_bound,upper_bound) #Masks image - any orange pixel is 1(white), and everything else is 0(black)

    kernel = np.ones((5, 5), np.uint8) #5x5 of 1s
    eroded = cv2.erode(cone_mask, kernel, iterations=2) #For each pixel, if any neighbor in a 5x5 isn't included in the mask, removes pixel from mask
    dilated = cv2.dilate(eroded, kernel, iterations=2) #For each pixel, if any neighbor in a 5x5 is still included in the mask, adds pixel to mask

    contours, hierarchy = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) #makes contour of object boundary
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    x1, y1, w, h = cv2.boundingRect(contours[0]) #makes rectangle around contour

    bounding_box = ((x1, y1), (x1+w, y1+h))

    ########### YOUR CODE ENDS HERE ###########

    # Return bounding box
    return bounding_box

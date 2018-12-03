# -*- coding: utf-8 -*-
"""
Last Update: 2018/12/03
Version 0.4.7
@author: Moritz Lürig
"""

#%% import

import copy
import cv2
import math
import numpy as np
import sys

from phenopype.utils import (red, green, blue, white)

#%% modules

class label_finder:
    def __init__(self):

        # setting up temporary variables
        self.done = False 
        self.current = (0, 0) 
        self.points = [] # List of points defining our polygon
        
    def on_mouse(self, event, x, y, buttons, user_param):
        if self.done: # Nothing more to do
            return
        if event == cv2.EVENT_MOUSEMOVE:
            self.current = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            print("Adding point #%d to label outline" % (len(self.points)+1))
            self.points.append((x, y))
        if event == cv2.EVENT_RBUTTONDOWN:
            if len(self.points) > 0:
                self.points = self.points[:-1]
                print("Removing point #%d from label outline" % (len(self.points)+1))

    def draw(self, image_path, mode, **kwargs): 
        
        # initialize # ----------------
        image = cv2.imread(image_path)       
        if not len(image.shape)==3:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        

        # =============================================================================
        # dirdirdraw label outline
        # =============================================================================

        print("\nMark the outline of the label by left clicking, finish by right clicking:")
        cv2.namedWindow("phenopype", flags=cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("phenopype", self.on_mouse)
        temp_canvas_1 = copy.deepcopy(image)
        
        if mode == "polygon":
            while(not self.done):
                if (len(self.points) > 0):
                    cv2.polylines(temp_canvas_1, np.array([self.points]), False, green, 2)
                    cv2.line(temp_canvas_1, self.points[-1], self.current, blue, 2)
                cv2.imshow("phenopype", temp_canvas_1)
                temp_canvas_1 = copy.deepcopy(image)
                if cv2.waitKey(50) & 0xff == 13:
                    self.done = True
                    cv2.destroyWindow("phenopype")
                elif cv2.waitKey(50) & 0xff == 27:
                    cv2.destroyWindow("phenopype")
                    break
                    sys.exit("phenopype process stopped")            
                
        elif mode == "box":
            cv2.namedWindow("phenopype", flags=cv2.WINDOW_NORMAL)
            (x,y,w,h) = cv2.selectROI("phenopype", image, fromCenter=False)
            if any([cv2.waitKey(50) & 0xff == 27, cv2.waitKey(50) & 0xff == 13]):
                cv2.destroyWindow("phenopype")  
            self.points = [(x, y), (x, y+h), (x+w, y+h), (x+w, y)]


        # create colour mask to show scale outline
        colour_mask = np.zeros(image.shape, np.uint8)
        colour_mask[:,:,1] = 255 # all area green
        cv2.fillPoly(colour_mask, np.array([self.points]), red) # red = excluded area
        temp_canvas_1 = cv2.addWeighted(copy.deepcopy(image), .7, colour_mask, 0.3, 0) # combine
        
        self.contour = np.array(self.points).reshape((-1,1,2)).astype(np.int32)
        
        # create template image for SIFT
        rx,ry,w,h = cv2.boundingRect(np.array(self.points, dtype=np.int32))
        self.image_original_template = image[ry:ry+h,rx:rx+w]
        
        # create mask for SIFT
        self.mask_original_template = np.zeros(image.shape[0:2], np.uint8)
        cv2.fillPoly(self.mask_original_template, np.array([self.points]), white) 
        self.mask_original_template = self.mask_original_template[ry:ry+h,rx:rx+w]

        if kwargs.get('show', True):
            cv2.namedWindow("phenopype", flags=cv2.WINDOW_NORMAL)
            cv2.imshow("phenopype", self.image_original_template)    
            if any([cv2.waitKey(0) & 0xff == 27, cv2.waitKey(0) & 0xff == 13]):
                cv2.destroyWindow("phenopype")


    def find(self, image_path, **kwargs):
        
        # initialize ------------------
        self.image_target = cv2.imread(image_path)
        image_target = copy.deepcopy(self.image_target)
        image_original = copy.deepcopy(self.image_original_template)
        
        show = kwargs.get('show', False)
        min_matches = kwargs.get('min_matches', 10)

        if (image_target.shape[0] + image_target.shape[1])/2 > 2000:
            factor = kwargs.get('resize', 0.5)
            image_target = cv2.resize(image_target, (0,0), fx=1*factor, fy=1*factor) 
            self.resized = True
        else:
            self.resized = False
        
        if not len(image_target.shape)==3:
            image_target = cv2.cvtColor(image_target, cv2.COLOR_GRAY2BGR)
            
    
        # =============================================================================
        # SIFT detector
        # =============================================================================
        # sift = cv2.xfeatures2d.SIFT_create()
        # kp1, des1 = sift.detectAndCompute(img1,self.mask_original_template)
        # kp2, des2 = sift.detectAndCompute(img2,None)
         
        # =============================================================================
        # ORB detector
        # =============================================================================
#        orb = cv2.ORB_create()
#        kp1, des1 = orb.detectAndCompute(img1,self.mask_original_template)
#        kp2, des2 = orb.detectAndCompute(img2,None)
#        des1 = np.asarray(des1, np.float32)
#       des2 = np.asarray(des2, np.float32)
        
#        FLANN_INDEX_KDTREE = 0
#        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
#        search_params = dict(checks = 50)
#        flann = cv2.FlannBasedMatcher(index_params, search_params)
#        matches = flann.knnMatch(des1,des2,k=2)
        
        # =============================================================================
        # AKAZE detector
        # =============================================================================
        
        akaze = cv2.AKAZE_create()
        kp1, des1 = akaze.detectAndCompute(image_original,self.mask_original_template)
        kp2, des2 = akaze.detectAndCompute(image_target,None)       
        matcher = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_BRUTEFORCE_HAMMING)
        matches = matcher.knnMatch(des1, des2, 2)

        # keep only good matches
        good = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                good.append(m)
        self.nkp = len(good)
        
        # find and transpose coordinates of matches
        if self.nkp >= min_matches:
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
            
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
            ret, contours, hierarchy = cv2.findContours(self.mask_original_template,cv2.RETR_EXTERNAL ,cv2.CHAIN_APPROX_TC89_L1)
            box = contours[0].astype(np.float32)
            
            self.M = M
            
            cnt = lf.contour - lf.contour[0]
            cnt = cnt.astype(np.float32)

            rect = cv2.perspectiveTransform(cnt,lf.M).astype(np.int32)
            
            image_target = cv2.polylines(image_target,[rect],True,red,5, cv2.LINE_AA)
            
            if show == True:
                cv2.namedWindow("phenopype", flags=cv2.WINDOW_NORMAL)
                cv2.imshow("phenopype", image_target)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                
            self.rect = rect
                
            if self.resized:
                rect = rect/factor               
            
            # MASK
            zeros = np.zeros(self.image_target.shape[0:2], np.uint8)
            self.mask = cv2.fillPoly(zeros, [np.array(rect, dtype=np.int32)], white)

            # TARGET SNIPPET
            (rx,ry,w,h) = cv2.boundingRect(rect)
            self.image_found = self.image_target[ry:ry+h,rx:rx+w]

            
            print("\n")
            print("--------------------------------------")
            print("Label found with %d keypoint matches" % self.nkp)
            print("--------------------------------------")
            print("\n")

            return self.image_found, self.mask      
        
        else:
            print("\n")
            print("----------------------------------------------")
            print("Label not found - only %d/%d keypoint matches" % (self.nkp, min_matches))
            print("----------------------------------------------")
            print("\n")
            
            return "no current label", "no label mask"



def rotate_image(image, angle, **kwargs):
      
    height, width = image.shape[:2]
    image_center = (width / 2, height / 2)

    rotation_matrix = cv2.getRotationMatrix2D(image_center, angle, 1)

    radians = math.radians(angle)
    sin = math.sin(radians)
    cos = math.cos(radians)
    
    bound_w = int((height * abs(sin)) + (width * abs(cos)))
    bound_h = int((height * abs(cos)) + (width * abs(sin)))
    
    rotation_matrix[0, 2] += ((bound_w / 2) - image_center[0])
    rotation_matrix[1, 2] += ((bound_h / 2) - image_center[1])

    rotated_image = cv2.warpAffine(image, rotation_matrix, (bound_w, bound_h), borderValue = white)
    return rotated_image
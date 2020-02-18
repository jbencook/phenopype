#%% modules
import cv2, copy, os, sys, warnings
import numpy as np
import pandas as pd

from datetime import datetime
from ruamel.yaml.comments import CommentedMap as ordereddict

from phenopype.settings import colours
from phenopype.utils import load_image, load_meta_data, show_image, save_image
from phenopype.utils_lowlevel import _image_viewer, _create_mask_bin, _load_masks
from phenopype.utils_lowlevel import _load_yaml, _show_yaml, _save_yaml, _yaml_file_monitor

#%% functions

def create_mask(obj_input, **kwargs):
    """Mask maker method to draw rectangle or polygon mask onto image.
    
    Parameters
    ----------        
    
    include (optional): bool (default: True)
        determine whether resulting mask is to include or exclude objects within
    label(optional): str (default: "mask1")
        passes a label to the mask
    max_dim (optional): int (default: 1000)
        maximum dimension of the window along any axis in pixel
    overwrite (optional): bool (default: False)
        if working using a container, or from a phenopype project directory, should
        existing masks with the same label be overwritten
    show (otpional): bool (default: False)
        should the drawn mask be shown as an overlay on the image
    tool (optional): str (default: "rectangle")
        draw mask by draging a rectangle (option: "rectangle") or by settings 
        points for a polygon (option: "polygon").
        
    """

    ## kwargs
    label = kwargs.get("label","mask1")
    max_dim = kwargs.get("max_dim", 1000)
    include = kwargs.get("include",True)
    flag_show = kwargs.get("show",False)
    flag_tool = kwargs.get("tool","rectangle")
    flag_overwrite = kwargs.get("overwrite", False)
    
    ## load image and check if pp-project
    if obj_input.__class__.__name__ == "ndarray":
        image = obj_input
    elif obj_input.__class__.__name__ == "container":
        image = obj_input.image_copy

    ## load mask and check if exists
    masks, mask_list = _load_masks(obj_input, label)

    while True:
        if len(masks) == 1 and flag_overwrite == False: 
            mask = masks[0]
            if len(eval(mask["coords"]))==0:
                warnings.warn("mask " + mask["label"] + " has no coordinates - redo mask")
                break
            else:
                return mask
        elif len(masks) == 1 and flag_overwrite == True:
            break
        elif len(masks) == 0:
            break

    ## method
    iv_object = _image_viewer(image, 
                              mode="interactive", 
                              max_dim = max_dim, 
                              tool=flag_tool)
    coords = []
    if flag_tool == "rectangle" or flag_tool == "box":
        for rect in iv_object.rect_list:
            pts = [(rect[0], rect[1]), (rect[2], rect[1]), (rect[2], rect[3]), (rect[0], rect[3]),(rect[0], rect[1])]
            coords.append(pts)
    elif flag_tool == "polygon" or flag_tool == "free":
        for poly in iv_object.poly_list:
            # pts = np.array(poly, dtype=np.int32)
            coords.append(poly)

    ## create mask
    mask = {"label": label,
            "include": include,
            "created_on": datetime.today().strftime('%Y%m%d_%H%M%S'),
            "coords": str(coords)}

    ## show image with window control
    if flag_show:
        overlay = np.zeros(image.shape, np.uint8) # make overlay
        overlay[:,:,2] = 200 # start with all-red overlay
        mask_bin = _create_mask_bin(image, coords)
        mask_bool = np.array(mask_bin, dtype=bool)
        if include:
            overlay[mask_bool,1], overlay[mask_bool,2] = 200, 0
        else:
            overlay[np.invert(mask_bool),1], overlay[np.invert(mask_bool),2] = 200, 0
        mask_overlay = cv2.addWeighted(image, .7, overlay, 0.5, 0)
        show_image(mask_overlay)

    ## return 
    if obj_input.__class__.__name__ == "container":
        obj_input.masks[label] = mask
        obj_input.masks_copy[label] = mask
    else:
        return mask



def invert_image(obj_input, **kwargs):
    """
    

    Parameters
    ----------
    obj_input : TYPE
        DESCRIPTION.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    image : TYPE
        DESCRIPTION.

    """
    
    ## load image and check if pp-project
    if obj_input.__class__.__name__ == "ndarray":
        image = obj_input
    elif obj_input.__class__.__name__ == "container":
        image = obj_input.image

    ## method
    image = cv2.bitwise_not(image)

    ## return 
    if obj_input.__class__.__name__ == "container":
        obj_input.image = image
    else:
        return image

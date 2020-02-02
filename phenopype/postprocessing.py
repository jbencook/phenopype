#%% modules
import cv2
import copy
import numpy as np
import os
import sys 

from ruamel.yaml.comments import CommentedMap as ordereddict

from phenopype.settings import colours
from phenopype.utils import show_img, load_yaml, save_yaml, show_yaml
from phenopype.utils_lowlevel import _image_viewer, _load_image

#%% methods

def save_results(obj_input, **kwargs):
    """Save a pandas dataframe to csv. 
    
    Parameters
    ----------
    df: df
        object_finder outpur (pandas data frame) to save
    name: str
        name for saved df
    save_dir: str
        location to save df
    append: str (optional)
        append df name with string to prevent overwriting
    overwrite: bool (optional, default: False)
        overwrite df if name exists
    """
    ## kwargs
    flag_overwrite = kwargs.get("overwrite", False)
    keep = kwargs.get("keep",None)
    ## load image
    image, flag_input = _load_image(obj_input)

    if flag_input == "pype_container":
        dirpath = obj_input.dirpath
        df = obj_input.df_result
        name = df["pype_name"].iloc[0]

    if keep:
        df = df.loc[df["order"]=="parent"]

    df = df.fillna(-9999)
    df = df.round(1)
    df = df.astype(str)

    save_path = os.path.join(dirpath, name + "_result.csv")

    if os.path.exists(save_path):
        if flag_overwrite == True:
            df.to_csv(path_or_buf=save_path, sep=",")
    else:
        df.to_csv(path_or_buf=save_path, sep=",")
        
        
def save_overlay(obj_input, **kwargs):
    """Save a pandas dataframe to csv. 
    
    Parameters
    ----------
    df: df
        object_finder outpur (pandas data frame) to save
    name: str
        name for saved df
    save_dir: str
        location to save df
    append: str (optional)
        append df name with string to prevent overwriting
    overwrite: bool (optional, default: False)
        overwrite df if name exists
    """
    ## kwargs
    flag_overwrite = kwargs.get("overwrite", False)
    resize = kwargs.get("resize", 1)
        
    ## load image
    image, flag_input = _load_image(obj_input)

    if flag_input == "pype_container":
        dirpath = obj_input.dirpath
        img = obj_input.canvas
        name = obj_input.df_result["pype_name"].iloc[0] + "_result"

    img = cv2.resize(img, (0,0), fx=1*resize, fy=1*resize) 


    save_path = os.path.join(dirpath, name + ".jpg")

    if os.path.exists(save_path):
        if flag_overwrite == True:
            cv2.imwrite(save_path, img)
    else:
        cv2.imwrite(save_path, img)
        
        
def save_contours(obj_input, **kwargs):
    """Save a pandas dataframe to csv. 
    
    Parameters
    ----------
    df: df
        object_finder outpur (pandas data frame) to save
    name: str
        name for saved df
    save_dir: str
        location to save df
    append: str (optional)
        append df name with string to prevent overwriting
    overwrite: bool (optional, default: False)
        overwrite df if name exists
    """
    ## kwargs
    flag_overwrite = kwargs.get("overwrite", False)
        
    ## load input
    image, flag_input = _load_image(obj_input)

    if flag_input == "pype_container":
        dirpath = obj_input.dirpath
        df = obj_input.df_result
        name = df["pype_name"].iloc[0]

    obj_output = {}
    obj_output["filename"] = obj_input.df_result["filename"][1]
    obj_output["project"] = obj_input.df_result["project"][1]
    obj_output["size_px_xy"] = obj_input.df_result["size_px_xy"][1]
    obj_output["contours"] = {}
    
    for contour in obj_input.contours.keys():
        contour_dict = {}
        contour_dict["label"] = contour
        contour_dict["center"] = str(obj_input.contours[contour]["center"])
        contour_dict["order"] = str(obj_input.contours[contour]["order"])
        contour_dict["idx_child"] = 1 # str(obj_input.contours[contour]["idx_child"])
        contour_dict["idx_parent"] = str(obj_input.contours[contour]["idx_parent"])
        x_coords, y_coords = [], []
        for coord in obj_input.contours[contour]["coords"]:
            x_coords.append(coord[0][0])
            y_coords.append(coord[0][1])
        contour_dict["x_coords"], contour_dict["y_coords"] = str(x_coords), str(y_coords)
        obj_output["contours"][contour] = contour_dict

    save_path = os.path.join(dirpath, "contours.yml")

    if os.path.exists(save_path):
        if flag_overwrite == True:
             save_yaml(obj_output, save_path)
    else:
         save_yaml(obj_output, save_path)

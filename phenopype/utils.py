#%% modules

import cv2, copy, os, sys, warnings
import numpy as np
import pandas as pd

from pprint import PrettyPrinter
from PIL import Image, ExifTags
from ruamel.yaml import YAML

from phenopype.utils_lowlevel import _image_viewer 
from phenopype.utils_lowlevel import _load_yaml, _show_yaml, _save_yaml, _yaml_file_monitor
from phenopype.settings import *

#%% settings

Image.MAX_IMAGE_PIXELS = 999999999
pretty = PrettyPrinter(width=30)

def custom_formatwarning(msg, *args, **kwargs):
    # ignore everything except the message
    return "WARNING: " + str(msg) + '\n'
warnings.formatwarning = custom_formatwarning
warnings.simplefilter('always', UserWarning)

#%% classes

class container(object):
    def __init__(self, image, df_image_data, **kwargs):
        """
        Parameters
        ----------
        image : TYPE
            DESCRIPTION.
        df : TYPE
            DESCRIPTION.
        **kwargs : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.image = image
        self.image_copy = copy.deepcopy(self.image)
        self.image_mod = copy.deepcopy(self.image)
        self.image_bin = None
        self.image_gray = None
        self.canvas = None
        
        self.df_image_data = df_image_data
        self.df_image_data_copy = copy.deepcopy(self.df_image_data)


        
        ## attributes
        self.dirpath = None
        self.save_suffix = default_save_suffix

    def reset(self):
        """
        Parameters
        ----------
        components : TYPE, optional
            DESCRIPTION. The default is [].

        Returns
        -------
        None.

        """
        self.image = copy.deepcopy(self.image_copy)
        self.canvas = None
        
        

    def load(self):
        """
        

        Parameters
        ----------
        components : TYPE, optional
            DESCRIPTION. The default is [].

        Returns
        -------
        None.

        """
        if hasattr(self, "df_contours"):
            print("Load contours not yet implemented")

        ## landmarks
        if not hasattr(self, "df_landmarks"):
            path = os.path.join(self.dirpath, "landmarks_" + self.save_suffix + ".csv")
            if os.path.isfile(path):
                self.df_landmarks = pd.read_csv(path) 

        ## polylines
        if not hasattr(self, "df_polyline"):
            path = os.path.join(self.dirpath, "polylines_" + self.save_suffix + ".csv")
            if os.path.isfile(path):
                self.df_polylines = pd.read_csv(path) 
            
        if hasattr(self, "masks"):
            if self.dirpath:
                mask_path = os.path.join(self.dirpath, "masks.yaml")
                if os.path.isfile(mask_path):
                    masks = _load_yaml(mask_path)
                    if masks:
                        masks_l = []
                        for mask in masks.values():
                            self.masks[mask["label"]] = mask
                            masks_l.append(mask["label"])
                        print("Loaded masks " + ", ".join(masks_l) + " from file.")
                        self.masks_copy = copy.deepcopy(self.masks)
                    else:
                        self.masks = {}
                        self.masks_copy = {}
                        
    def save(self, **kwargs):
        """
        

        Parameters
        ----------
        components : TYPE, optional
            DESCRIPTION. The default is [].
        **kwargs : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        cfg = "pype_config_v1.yaml"
        cfg[cfg.rindex('_')+1:cfg.rindex('.')]

        """
        ## kwargs

        
        if hasattr(self, "df_contours"):
            print("Save contours not yet implemented")
            
        ## landmarks
        if hasattr(self, "df_landmarks"):
            path = os.path.join(self.dirpath, "landmarks_" + self.save_suffix + ".csv")
            while True:
                if os.path.isfile(path):
                    saved_df_landmarks = pd.read_csv(path) 
                    if saved_df_landmarks["date_phenopyped"][0] == self.df_landmarks["date_phenopyped"][0]:
                        return
                    else:
                        print("Saved landmarks (overwritten)")
                        break
                else:
                    print("Saved landmarks")
                    break
            self.df_landmarks.to_csv(path_or_buf=path, sep=",",index=False)

        ## polylines
        if hasattr(self, "df_polylines") and hasattr(self, "ov_polylines"):
            while True:
                path = os.path.join(self.dirpath, "polylines_" + self.save_suffix + ".csv")
                if os.path.isfile(path) and not self.ov_polylines:
                    warnings.warn("polylines already saved (overwrite=False)")
                    break
                elif os.path.isfile(path) and self.ov_polylines:
                    print("Saved polylines (overwritten)")
                    pass
                elif not os.path.isfile(path):
                    print("Saved polylines")
                    pass
                self.df_polylines.to_csv(path_or_buf=path, sep=",",index=False)
                break

        if hasattr(self, "masks"):
            mask_path = os.path.join(self.dirpath, "masks.yaml")
            if os.path.isfile(mask_path):
                saved_masks = _load_yaml(mask_path)
                if not saved_masks:
                    saved_masks = {}
            else:
                saved_masks = {}
            for mask in self.masks.items():
                if mask[0] in saved_masks and not flag_overwrite:
                    if len(eval(saved_masks[mask[0]]["coords"])) == 0:
                        saved_masks[mask[0]]=mask[1]
                        print("Saved mask " + mask[0] + " (missing coords replaced).")
                    # else:
                    #     warnings.warn("Mask " +  mask[0] + " already exists - cannot save (overwrite=False).")
                elif mask[0] in saved_masks and flag_overwrite:
                    print("Saved mask " + mask[0] + " (overwritten).")
                    saved_masks[mask[0]]=mask[1]
                else:
                    saved_masks[mask[0]]=mask[1]
                    print("Saved mask " + mask[0])
            _save_yaml(saved_masks, mask_path)



#%% functions
            
def load_directory(obj_input, **kwargs):
    """
    

    Parameters
    ----------
    obj_input : TYPE
        DESCRIPTION.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    ## kwargs
    flag_container = kwargs.get("container", True)
    flag_df = kwargs.get("df", False)
    flag_meta = kwargs.get("meta", True)
    exif_fields = kwargs.get("fields", default_meta_data_fields)
    if not exif_fields.__class__.__name__ == "list":
        exif_fields = [exif_fields]
        
    if not os.path.isdir(obj_input):
        sys.exit("Not a valid phenoype directory - cannot load files.")
        
    attr = _load_yaml(os.path.join(obj_input, "attributes.yaml"))
    image = cv2.imread(attr["project"]["raw_path"])
    df = pd.DataFrame({"filename": attr["image"]["filename"],
                       "width": attr["image"]["width"],
                       "height": attr["image"]["height"]
                       }, index=[0])

    ## add meta-data 
    if flag_meta:
        exif_data_all, exif_data = attr["meta"], {}
        for field in exif_fields:
            if field in exif_data_all:
                exif_data[field] = exif_data_all[field]
        exif_data = dict(sorted(exif_data.items()))
        df = pd.concat([df.reset_index(drop=True), pd.DataFrame(exif_data, index=[0])], axis=1)

    ## return
    if flag_container == True:
        ct = container(image, df)
        ct.dirpath = obj_input
        ct.image_data = attr["image"]
        
    ## check for masks
    masks_path = os.path.join(obj_input, "masks.yaml")
    if os.path.isfile(masks_path):
        ct.masks = _load_yaml(masks_path)

    ## for future release 
    # ==> here, other objects from directory can be loaded and injected to container

    if flag_container == True:
        return ct
    elif flag_container == False:
        if flag_df:
            return image, df
        else:
            return image



def load_image(obj_input, **kwargs):
    """
    

    Parameters
    ----------
    obj_input : TYPE
        DESCRIPTION.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    ## kwargs 
    flag_container = kwargs.get("container", False)
    flag_df = kwargs.get("df", False)
    flag_meta = kwargs.get("meta", False)
    exif_fields = kwargs.get("fields", default_meta_data_fields)
    if not exif_fields.__class__.__name__ == "list":
        exif_fields = [exif_fields]

    ## method
    if obj_input.__class__.__name__ == "str":
        if os.path.isfile(obj_input):
            image = cv2.imread(obj_input)
        else:
            sys.exit("Invalid image path - cannot load image from str.")
    elif obj_input.__class__.__name__ == "ndarray":
        image = obj_input
    else:
        sys.exit("Invalid input format - cannot load image.")

    ## load image data
    image_data = load_image_data(obj_input)
    df_image_data = pd.DataFrame({"filename": image_data["filename"],
          "width": image_data["width"],
          "height": image_data["height"]}, index=[0])

    ## add meta-data 
    if flag_meta:
        meta_data = load_meta_data(obj_input, fields=exif_fields)        
        df_image_data = pd.concat([df_image_data.reset_index(drop=True), pd.DataFrame(meta_data, index=[0])], axis=1)

    ## return
    if flag_container == True:
        ct = container(image, df_image_data)
        ct.image_data = image_data
        ct.dirpath = os.getcwd()
        return ct
    elif flag_container == False:
        if flag_df:
            return image, df
        else:
            return image



def load_image_data(obj_input):
    """
    

    Parameters
    ----------
    obj_input : TYPE
        DESCRIPTION.

    Returns
    -------
    image_data : TYPE
        DESCRIPTION.

    """
    if obj_input.__class__.__name__ == "str":
        if os.path.isfile(obj_input):
            path = obj_input
        elif os.path.isdir(obj_input):
            attr = _load_yaml(os.path.join(obj_input, "attributes.yaml"))
            path = attr["project"]["raw_path"]
        image = Image.open(path)
        width, height = image.size
        image.close()
        image_data = {
            "filename": os.path.split(obj_input)[1],
            "filepath": obj_input,
            "filetype": os.path.splitext(obj_input)[1],
            "width": width,
            "height": height
            }
    elif obj_input.__class__.__name__ == "ndarray":
        image = obj_input
        width, height = image.shape[0:2]
        image_data = {
                "filename": "unknown",
                "filepath": "unkown",
                "filetype": "array_type",
                "width": width,
                "height": height
            }
    else:
        warnings.warn("Not a valid image file - cannot read image data.")

    ## issue warnings for large images
    if width*height > 125000000:
        warnings.warn("Large image - expect slow processing and consider resizing.")
    elif width*height > 250000000:
        warnings.warn("Extremely large image - expect very slow processing and consider resizing.")

    ## return image data
    return image_data



def load_meta_data(obj_input, **kwargs):
    """
    

    Parameters
    ----------
    obj_input : TYPE
        DESCRIPTION.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    ## kwargs
    flag_show = kwargs.get("show_fields", False)
    exif_fields = kwargs.get("fields", default_meta_data_fields)
    if not exif_fields.__class__.__name__ == "list":
        exif_fields = [exif_fields]
        
    # ## check if basic fields are present
    # if exif_fields.__class__.__name__ == "list":
    #     if not len(exif_fields) == 0:
    #         prepend = list(set(default_fields) - set(exif_fields))
    #         exif_fields = prepend + exif_fields

    ## read image
    if obj_input.__class__.__name__ == "str":
        if os.path.isfile(obj_input):
            image = Image.open(obj_input)
        else:
            warnings.warn("Not a valid image file - cannot read exif data.")
            return {}
    else:
        warnings.warn("Not a valid image file - cannot read exif data.")
        return {}

    ## populate dictionary
    exif_data_all = {}
    exif_data = {}
    try:
        for k, v in image._getexif().items():
            if k in ExifTags.TAGS:
                exif_data_all[ExifTags.TAGS[k]] = v
        exif_data_all = dict(sorted(exif_data_all.items()))
    except Exception:
        warnings.warn("No exif data found.")

    if flag_show:
        print("--------------------------------------------")
        print("Available exif-tags:\n")
        pretty.pprint(exif_data_all)
        print("\n")
        print("Default exif-tags (append list using \"fields\" argument):\n")
        print(default_meta_data_fields)
        print("--------------------------------------------")

    ## subset exif_data
    for field in exif_fields:
        if field in exif_data_all:
            exif_data[field] = str(exif_data_all[field])
    exif_data = dict(sorted(exif_data.items()))

    ## close image and return meta data
    image.close()
    return exif_data






def show_image(image, **kwargs):
    """Show one or multiple images by providing path string or array or list of either.
    
    Parameters
    ----------
    image: str, array, or list
        the image or list of images to be displayed. can be path to image (string), array-type, or list of strings or arrays
    window_aspect: str (default: "fixed")
        "fixed" or "free" aspect ratio
    position_reset: bool
        flag whether image positions should be reset when reopening list of images
    position_offset: int 
        if image is list, the distance in pixels betweeen the positions of each newly opened window (only works in conjunction with "position_reset")
    """
    
    ## kwargs
    max_dim = kwargs.get("max_dim", 1200)
    pos_offset = kwargs.get("position_offset", 25)
    pos_reset = kwargs.get("position_reset", False)
    window_aspect = kwargs.get("aspect", "free")
    if window_aspect == "free":
        window_aspect = cv2.WINDOW_NORMAL
    elif window_aspect == "fixed":
        window_aspect = cv2.WINDOW_AUTOSIZE

    
    ## open images list or single images
    while True:
        if isinstance(image, list):
            if len(image)>10:
                warning_banner = np.zeros((30,900,3))
                warning_string = "WARNING: trying to open " + str(len(image)) + " images - proceed (Enter) or stop (Esc)?"
                warning_image = cv2.putText(warning_banner,  warning_string ,(11,22), cv2.FONT_HERSHEY_SIMPLEX  , 0.75, colours.green,1,cv2.LINE_AA)
                cv2.namedWindow('phenopype' ,cv2.WINDOW_AUTOSIZE )
                cv2.imshow('phenopype', warning_image)
                k = cv2.waitKey(0)
                cv2.destroyAllWindows()
                if k == 27:
                    print("Stop - terminating.")
                    break
                elif k == 13:
                    print("Proceed - Opening images ...")
            idx=0
            for i in image:
                idx+=1
                _image_viewer(i, 
                              mode = "", 
                              window_aspect = window_aspect, 
                              window_name='phenopype' + " - " + str(idx), 
                              window_control="external",
                              max_dim=max_dim)
                if pos_reset == True:
                    cv2.moveWindow('phenopype' + " - " + str(idx),idx+idx*pos_offset,idx+idx*pos_offset)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            break
        else:
            _image_viewer(image, 
                  mode = "", 
                  window_aspect = window_aspect, 
                  window_name='phenopype', 
                  window_control="internal",
                  max_dim=max_dim)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            break





def save_image(image, name, **kwargs):
    """Save an image (array) to jpg.
    
    Parameters
    ----------
    image: array
        image to save
    name: str
        name for saved image
    save_dir: str
        location to save image
    append: str ("")
        append image name with string to prevent overwriting
    extension: str ("")
        file extension to save image with
    overwrite: bool (optional, default: False)
        overwrite images if name exists
    """
    # set dir and names
    out_dir = kwargs.get('save_dir', os.getcwd())     
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    app = kwargs.get('append',"")
    new_name = os.path.splitext(name)[0] + app
        
    ext = kwargs.get('extension',os.path.splitext(name)[1])
    new_name = new_name + ext
    
    im_path=os.path.join(out_dir , new_name)
    
    if "resize" in kwargs:
        factor = kwargs.get('resize')
        image = cv2.resize(image, (0,0), fx=1*factor, fy=1*factor) 
    
    if kwargs.get('overwrite',False) == False:
        if not os.path.exists(im_path):
            cv2.imwrite(im_path, image)
    else:
        cv2.imwrite(im_path, image)



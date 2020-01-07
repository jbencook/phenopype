#%% modules

import copy
import cv2
import datetime
import numpy as np
import os
import pickle
import pandas as pd
import platform
import pprint
import ruamel.yaml
import shutil
import subprocess
import sys 

from shutil import copyfile
from ruamel.yaml.comments import CommentedMap as ordereddict

from phenopype.utils import yaml_file_monitor, load_yaml, save_yaml, exif_data
from phenopype.utils_lowlevel import _image_viewer, _del_rw, _make_pype_template
from phenopype.settings import pype_presets, colours
from phenopype import preprocessing, segmentation, extraction, visualization, postprocessing

#%% settings

pd.options.display.max_rows = 10 # how many rows of pd-dataframe to show
pretty = pprint.PrettyPrinter(width=30) # pretty print short strings
ruamel.yaml.Representer.add_representer(ordereddict, ruamel.yaml.Representer.represent_dict) # suppress !!omap node info


#%% methods

class project: 
    """
    Initialize a phenopype project with a name.
    
    Parameters
    ----------

    root_dir: str (default: "CurrentWorkingDir + "CurrentDate_phenopype")
        root directory of the project
    name: str (default: "CurrentDate_phenopype")
        name of your project
    """
    
    def __init__(self, root=os.getcwd(), name="phenopype_project", **kwargs):
        
        root_dir = os.path.join(root, name)
        
        ## kwargs
        flag_overwrite = kwargs.get("overwrite", False)
        flag_query = kwargs.get("query", True)

        ## feedback
        print("\n")
        print("--------------------------------------------")
        print("phenopype will create a new project named \"" + name + "\". " +
              "The full path of the project's root directory will be:\n")
        print(root_dir)

        ## decision tree if directory exists
        while True:
            if flag_query == False:
                create = "y"
            else:
                create = input("Proceed? (y/n)\n")
            if create=="y" or create == "yes":
                if os.path.isdir(root_dir):
                    if flag_overwrite == True:
                        shutil.rmtree(root_dir, ignore_errors=True, onerror=_del_rw) 
                        print("\n\"" + root_dir + "\" created (overwritten)")
                        pass
                    else:
                        overwrite = input("Warning - project root_dir already exists - overwrite? (y/n)")
                        if overwrite == "y" or overwrite == "yes":
                            shutil.rmtree(root_dir, ignore_errors=True, onerror=_del_rw) 
                            print("\n\"" + root_dir + "\" created (overwritten)")
                            pass
                        else:
                            print("\n\"" + root_dir + "\" not created!")
                            print("--------------------------------------------")    
                            break
                else:
                    pass
            else:
                print("\n\"" + root_dir + "\" not created!")
                break
            
            self.root_dir = root_dir
            os.makedirs(self.root_dir)
            self.data_dir = os.path.join(self.root_dir, "data")
            os.mkdir(self.data_dir)
            self.dirpath_list = []
            self.attributes_dict = {}
            self.name = name
            
            ## global project attributes
            project_data = {
                "name": name,
                "date_created": datetime.datetime.today().strftime('%Y%m%d_%H%M%S'),
                "date_changed": datetime.datetime.today().strftime('%Y%m%d_%H%M%S')}
            project_io = {
                "root_dir": self.root_dir,
                "data_dir": self.data_dir}
            project_attributes = ordereddict([('information', 
                    [ordereddict([('project_data', project_data)]), 
                     ordereddict([('project_io', project_io)])
                     ])])
            save_yaml(project_attributes, os.path.join(self.root_dir, "attributes.yaml"))

            print("\nproject attributes written to " + os.path.join(self.root_dir, "attributes.yaml"))
            print("--------------------------------------------")
            break



    def add_files(self, image_dir, **kwargs):
        """Add files to your project from a directory, can look recursively. 
        Optional: specify a search string for filenames or file extensions. 
    
        Parameters
        ----------
    
        image_dir: str 
            path to directory with images                             
        search_mode: str (default: "dir")
            "dir" searches current directory for valid files; "recursive" walks through all subdirectories
        filetypes: list 
            single or multiple string patterns to target files with certain endings
        include: list 
            single or multiple string patterns to target certain files to include - can be used together with exclude
        exclude: list 
            single or multiple string patterns to target certain files to include - can be used together with include
        """
        
        ## kwargs
        flag_overwrite = kwargs.get("overwrite",False)
        search_mode = kwargs.get("search_mode","dir")
        file_endings = kwargs.get("filetypes", [])
        exclude_args = kwargs.get("exclude", [])
        include_args = kwargs.get("include", [])
        unique_by = kwargs.get("unique_by", "filepaths")
        flag_raw = kwargs.get("raw_mode", "copy")

        ## dummy filepaths for refinement
        filepaths1, filepaths2, filepaths3, filepaths4 = [],[],[],[]
        original_filepaths, filepaths_not_added = [], []
        ## find files 
        if search_mode == "recursive":
            for root, dirs, files in os.walk(image_dir):
                for file in os.listdir(root):
                    filepath = os.path.join(root,file)
                    if os.path.isfile(filepath):
                        filepaths1.append(filepath)
        elif search_mode == "dir":
            for file in os.listdir(image_dir):
                filepath = os.path.join(image_dir,file)
                if os.path.isfile(filepath):   
                    filepaths1.append(filepath)
                    
        ## file endings
        if len(file_endings)>0:
            for filepath in filepaths1:
                if filepath.endswith(tuple(file_endings)):
                    filepaths2.append(filepath)
        elif len(file_endings)==0:
            filepaths2 = filepaths1
            
        ## include
        if len(include_args)>0:
            for filepath in filepaths2:   
                if any(inc in os.path.basename(filepath) for inc in include_args):
                    filepaths3.append(filepath)
        else:
            filepaths3 = filepaths2
            
        ## exclude
        if len(exclude_args)>0:
            for filepath in filepaths3:   
                if not any(exc in os.path.basename(filepath) for exc in exclude_args):
                    filepaths4.append(filepath)
        else:
            filepaths4 = filepaths3
        
        ## save to object
        filepaths = filepaths4
        filenames = []
        for filepath in filepaths:
            filenames.append(os.path.basename(filepath))
        
        ## allow unique filenames filepath or by filename only
        if unique_by=="filepaths":
            for filename, filepath in zip(filenames, filepaths):
                if not filepath in original_filepaths:
                    original_filepaths.append(filepath)
                else:
                    filepaths_not_added.append(filepath)
        elif unique_by=="filenames":
            for filename, filepath in zip(filenames, filepaths):
                if not filename in filenames:
                    original_filepaths.append(filepath)
                else:
                    filepaths_not_added.append(filepath)

        ## loop through files
        for original_filepath in original_filepaths:
            original_filename = os.path.basename(original_filepath)
            original_filetype = os.path.splitext(original_filename)[1]
        
            ## flatten folder structure
            relpath = os.path.relpath(original_filepath,image_dir)
            depth = relpath.count("\\")
            relpath_flat = os.path.dirname(relpath).replace("\\","__")
            if depth > 0:
                subfolder_prefix = str(depth) + "__" + relpath_flat + "__"
            else:
                subfolder_prefix = str(depth) + "__" 
                
            ## image paths
            phenopype_dirname = subfolder_prefix + os.path.splitext(original_filename)[0]
            phenopype_dirpath = os.path.join(self.root_dir,"data",phenopype_dirname)

            ## make image-specific directories
            if os.path.isdir(phenopype_dirpath) and flag_overwrite==False:
                print(phenopype_dirname + " already exists (overwrite=False)")
                continue
            if os.path.isdir(phenopype_dirpath) and flag_overwrite==True:
                shutil.rmtree(phenopype_dirpath, ignore_errors=True, onerror=_del_rw)
                print("phenopype-project folder " + phenopype_dirname + " created (overwritten)")
                pass
            else:
                print("phenopype-project folder " + phenopype_dirname + " created")
                pass
            os.mkdir(phenopype_dirpath)
            phenopype_filepath_raw = os.path.join(phenopype_dirpath,"raw" + original_filetype)

            flag_resize = False
            if flag_raw == "copy":
                copyfile(original_filepath, phenopype_filepath_raw)
            elif flag_raw.__class__.__name__ == "float" or flag_raw.__class__.__name__ == "int":
                flag_resize = True
                raw = cv2.imread(original_filepath)
                raw_resized = cv2.resize(raw, (0,0), fx=1*flag_raw, fy=1*flag_raw) 
                cv2.imwrite(phenopype_filepath_raw, raw_resized)            
            elif flag_raw == "link":
                phenopype_filepath_raw = original_filepath
                
                
            original_io = {
                "filename": original_filename,
                "filepath": original_filepath,
                "filetype": original_filetype}

            phenopype_io = {
                "project": self.name,
                "dirname": phenopype_dirname,
                "dirpath": phenopype_dirpath,
                "filepath_raw": phenopype_filepath_raw,
                "raw_mode": flag_raw,
                "resize": flag_resize} 

            attributes = {'information':
                          {'meta_data': exif_data(original_filepath),
                           'original_io': original_io,
                           'phenopype_io': phenopype_io}
                          }
                                       
            ## write attributes file
            attributes_path = os.path.join(phenopype_dirpath, "attributes.yaml")
            save_yaml(attributes, attributes_path)

            ## add to project object
            self.dirpath_list.append(phenopype_dirpath)
            self.attributes_dict[phenopype_dirname] = attributes


    def add_pype_preset(self, **kwargs):

        ## kwargs
        flag_overwrite = kwargs.get("overwrite", False)
        flag_interactive = kwargs.get("test_and_modify", None)
        pype_name = kwargs.get("name","pype1")
        preset_name = kwargs.get("preset","config1")

        ## modify preset 
        if flag_interactive:
            if flag_interactive.__class__.__name__ == "str":
                p = pype(self.attributes_dict[flag_interactive]["information"]["phenopype_io"]["filepath_raw"])
            if flag_interactive.__class__.__name__ == "bool":
                p = pype(self.attributes_dict[next(iter(self.attributes_dict))]["information"]["phenopype_io"]["filepath_raw"])

            test_path = os.path.join(self.root_dir, "temp_pype.yaml")
            save_yaml(load_yaml(eval("pype_presets." + preset_name)), test_path)
            p.run(steps=["preprocessing", "segmentation"], pype_config=test_path)
            preset = p.pype_config
            os.remove(test_path)
            
        ## save pype-config file
        for directory in self.dirpath_list:
            
            ## get dir from local attributes file
            attr = load_yaml(os.path.join(directory, "attributes.yaml"))
            dirpath = attr["information"]["phenopype_io"]["dirpath"]
            dirname = attr["information"]["phenopype_io"]["dirname"]
            pype_path = os.path.join(dirpath, pype_name + ".yaml")

            pype_config = {"pype_info":
                           {"name": pype_name,
                            "preset": preset_name,
                            "date_created": datetime.datetime.today().strftime('%Y%m%d_%H%M%S'),
                            "date_modified": datetime.datetime.today().strftime('%Y%m%d_%H%M%S')},
                           "image_info":
                           {"filename": attr["information"]["original_io"]["filename"],
                            "project": attr["information"]["phenopype_io"]["project"],
                            "size_px_xy": attr["information"]["meta_data"]["size_xy_px"],
                            "exposure_time": attr["information"]["meta_data"]["exposure_time"],
                            "data_taken": attr["information"]["meta_data"]["date_taken"],
                            "date_phenopyped": None
                            }
                           }
                
            if not flag_interactive:
                preset = load_yaml(eval("pype_presets." + preset_name))
            pype_config.update(preset)

            if os.path.isfile(pype_path) and flag_overwrite==False:
                print(pype_name + ".yaml already exists in " + dirname +  " (overwrite=False)")
                continue
            elif os.path.isfile(pype_path) and flag_overwrite==True:
                print(pype_name + ".yaml created for " + dirname + " (overwritten)")
                pass
            else:
                print(pype_name + ".yaml created for " + dirname)
                pass
            save_yaml(pype_config, pype_path)
                
def save_project(project_file):
    output_str = os.path.join(project_file.root_dir, 'project.data')
    with open(output_str, 'wb') as output:
        pickle.dump(project_file, output, pickle.HIGHEST_PROTOCOL)
         
def load_project(path):
    with open(path, 'rb') as output:
        return pickle.load(output)

class pype:
    def __init__(self, image, **kwargs):
        
        ## kwargs
        resize = kwargs.get("resize", False)
        self.PC = pype_container(image, resize=resize)
            
    def run(self, **kwargs):
        
        ## kwargs
        print_settings = kwargs.get("print_settings",False)
        flag_return = kwargs.get("return_results",False)
        flag_show = kwargs.get("show",True)
        steps_exclude = kwargs.get("exclude",[]) 
        steps_include = kwargs.get("include",[]) 

        ## fetch pype configuration from file or preset
        pype_config = kwargs.get("pype_config", None)

        if isinstance(pype_config,  str):
            pype_config_locations = [os.path.join(self.PC.dirpath, pype_config + ".yaml"),
                       os.path.join(self.PC.dirpath, pype_config)]
            for loc in pype_config_locations:
                if os.path.isfile(loc):
                    self.pype_config = load_yaml(loc)
                    self.pype_config_file = loc
        else:
            self.pype_config = pype_config
            self.pype_config_file = self.dirname
            
        if not pype_config:
            print("not")
            loc = os.path.join(self.dirname, "pipeline1.yaml")
            save_yaml(_make_pype_template(), loc)
            self.pype_config = load_yaml(loc)
            self.pype_config_file = loc

        ## open config file with system viewer
        if flag_show:
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', self.pype_config_file))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(self.pype_config_file)
            else:                                   # linux variants
                subprocess.call(('xdg-open', self.pype_config_file))

        self.FM = yaml_file_monitor(self.pype_config_file, print_settings=print_settings)
        update = {}
        iv = None
        
        while True:
            
            ## reset pype container
            flag_vis = False
            self.PC.reset(components=["contour_list"])
            self.PC.df_result["date_phenopyped"] = datetime.datetime.today().strftime('%Y%m%d_%H%M%S') 
            self.PC.df_result["pype_name"] = pype_config
            
            ## get config file and assemble pype
            self.pype_config = self.FM.content
            if not steps_include:
                steps_pre = []
                for item in self.pype_config:
                    steps_pre.append(item)
                steps = [e for e in steps_pre if e not in steps_exclude]
            elif steps_include:
                steps = steps_include

            ## apply pype
            for step in steps:
                if step in ["pype_info", "image_info"]:
                    continue
                for item in self.pype_config[step]:
                    try:
                        ## construct method name and arguments
                        if isinstance(item, str):
                            method_name = item
                            method_args = {}
                        else:
                            method_name = list(item)[0]
                            method_args = dict(list(dict(item).values())[0])
                            
                        ## run method
                        method_loaded = eval(step + "." + method_name)
                        method_loaded(self.PC, **method_args)

                        ## check if visualization argument is given in config
                        if method_name == "show_image":
                            flag_vis = True
                    except Exception as ex:
                        location = step + "." + method_name + ": " + str(ex.__class__.__name__)
                        print(location + " - " + str(ex))

            ## show image and hold
            if flag_show:
                try:
                    if not flag_vis:
                        self.PC = visualization.show_image(self.PC)
                    iv = _image_viewer(self.PC.canvas, prev_attributes=update)
        
                    ## pass on settings for next call
                    update = iv.__dict__
    
                except Exception as ex:
                    print("visualisation: " + str(ex.__class__.__name__) + " - " + str(ex))
    
                ## close
                if iv:
                    if iv.done:
                        self.FM.stop()
                        break
            else:
                self.FM.stop()
                break

        if flag_return:
            return self.PC



class pype_container(object):
    def __init__(self, image, **kwargs):
        """ This object acts as a "sticky-ball" for all the operations bewteen one pype-iteration, and 
        contains the raw image to extract information, the modified image for processing, and all in-between
        steps (e.g. masks and detected contours). Depending on the input (phenopype directory (default), 
        path to an image, or array), more pr less complete meta-information will be passed on to the results file
        that will be stored in the same directory as the input-image (or custom directory [default: current working 
        directory] , in case of the array).
        
        Parameters
        ----------

        image: array
        """

        ## kwargs
        dirpath = kwargs.get("dirpath", None)
        resize = kwargs.get("resize", False)
        
        ## load image 
        self.flag_pp_proj = False
        if image.__class__.__name__ == "str":
            if os.path.isdir(image) and "attributes.yaml" in os.listdir(image):
                self.flag_pp_proj = True
                attr = load_yaml(os.path.join(image, "attributes.yaml"))
                image = cv2.imread(attr["information"]["phenopype_io"]["filepath_raw"])
                dirpath = attr["information"]["phenopype_io"]["dirpath"]
                df_dict = {"filename": attr["information"]["original_io"]["filename"],
                            "project": attr["information"]["phenopype_io"]["project"],
                            "size_px_xy": attr["information"]["meta_data"]["size_xy_px"],
                            "resize": resize,
                            "exposure_time": attr["information"]["meta_data"]["exposure_time"],
                            "data_taken": attr["information"]["meta_data"]["date_taken"]}

        ## set up meta info
        self.dirpath = dirpath
        self.df_result = pd.DataFrame([df_dict])
        self.df_result_copy = copy.deepcopy(self.df_result)

        ## set up images
        if resize:
            self.image = cv2.resize(image, (0,0), fx=1*resize, fy=1*resize) 
        else:
            self.image = image
        self.image_mod = copy.deepcopy(self.image)
        self.image_bin = None
        self.canvas = None
        
        ## set up containers
        self.mask_binder = {}
        self.contours = {}

    def reset(self, components=[]):
        
        self.image_mod = copy.deepcopy(self.image)
        self.image_bin = None
        self.canvas = None

        if "contour" in components or "contours" in components or "contour_list" in components:
            self.df_result = copy.deepcopy(self.df_result_copy)
            self.contours = {}
        if "mask" in components or "masks" in components:
            self.mask_binder = {}
            
            
        # def save(self):     
        #     with open(self.path + '.data', 'wb') as output:
        #         pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)
        # def load(self):
        #     with open(self.content + '.data', 'rb') as output:
        #         pickle.load(output)
                
                
        #     self.mask = {}
        # def show(self):
        #     pretty.pprint(self.__dict__)
        # def load_raw(self):
        #     img = cv2.imread(os.path.join(self.filepath_raw))
        #     return img
        # def show_raw(self):
        #     img = cv2.imread(os.path.join(self.filepath_raw))
        #     show_img(img)
            
        # def create_mask(self, **kwargs):
        #     name = kwargs.get("name", "mask1")
        #     self.mask[name] = mask.create_mask(self.filepath_raw)
        #     cv2.imwrite(name + ".jpg", self.mask[name].mask_bin)
        
            
# class image_container(object):    
#     def __init__(self, filename, filepath): 
#         self.filename = filename    
#         self.filetype = os.path.splitext(filename)[1]
#         self.filepath = filepath    
#         self.filepath_raw = os.path.join(filepath,"raw" + self.filetype)
#         self.filepath_config = os.path.join(filepath,"config.yaml")
        
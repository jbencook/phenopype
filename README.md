# phenopype

phenopype is a phenotyping pipeline for python. It is designed to extract phenotypic data from digital images or video material with minimal user input, and therefore aims at large datasets. It does not have a GUI, but instead is designed to be run from a python integrated development environment (IDE), like [spyder](https://www.spyder-ide.org/), [pycharm](https://www.jetbrains.com/pycharm/), or [VScode](https://code.visualstudio.com/), providing an "RStudio"-like feeling. phenopype is developed by [me](https://luerig.net) and builds on a collection of scripts ([iso_cv](https://github.com/mluerig/iso_cv), [iso_track](https://github.com/mluerig/iso_track)) that I wrote for my PhD at [Eawag](https://www.eawag.ch/en/department/eco/) and [ETH Zürich](http://www.adaptation.ethz.ch/).

phenopype is currently alpha, and still under heavy construction. A few core features like object detection or videotracking work ([see below](#features)), more are [planned](#development). If you are interested in using phenopype, check the installation guide and [contact me](https://www.eawag.ch/en/aboutus/portrait/organisation/staff/profile/moritz-luerig/show/) directly or raise [issues](https://github.com/mluerig/phenopype/issues) if you encounter problems. Some python knowledge is helpful, but not necessarily required if you know how to use R. Feel free to get in touch of you have requests or ideas for further use cases (e.g. for your own study system) that you think could be solved with phenopype. 

# features

|Object detection|Object tracking| Scale detection|
|:--:|:--:|:--:|
|<img src="assets/object_detection.gif" width="90%" />|<img src="assets/object_tracking.gif" width="80%" />| <img src="assets/scale_detection.gif" width="100%" />|
|Automatic object detection via multistep thresholding in a predefined area. Useful if your images have borders or irregular features. Accurracy can be increased with custom modules, e.g. for colour or shape|Automatic object tracking that uses foreground-background subtractor. High performance possible (shown example is close to real time with HD stream). Can be set to distinguish colour or shapes.|A scale that is once identified and measured can be found in all following pictures. Automatically corrects pixel-size ratios. Performance depends on image size| 
|<img src="assets/object_detection.JPG" width="80%" />|<img src="assets/object_tracking.png" width="80%" />| <img src="assets/scale_detection.png" width="100%" />|
|||| 

# dependencies 
- python (3.6)

- numpy 
- pandas 
- opencv (3.4.1)
- trackpy (0.4.x)
- exifread

# installation
1. install python (anaconda is highly recommended: https://www.anaconda.com/download/ - don't forget to add "conda" to your PATH).
2. open a terminal / shell and enter: 
```
conda update conda
conda install numpy pandas trackpy exifread
conda install -c conda-forge opencv 
conda install -c soft-matter trackpy
```
If you have trouble installing opencv: https://stackoverflow.com/questions/23119413/how-do-i-install-python-opencv-through-conda

To download phenopype from github, you need pip:

```
conda install pip
pip install git+https://github.com/mluerig/phenopype
```

All conda installations come with the spyder IDE. You can call spyder from the command line:

```
spyder
```

Open `example.py` to analyze some pictures - you are now all set to phenopype your organisms.

# quick start 

(coming soon)

# development (planned):

## hdf5-implementation

## shape detection

## landmark tool

## training dataset generation

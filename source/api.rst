
API reference
=============

Projects
--------

Phenopype projects are composed of a directory tree in which each folder contains the copy or a link to a single raw image file. Each raw 
should have only one folder, so that result or intermediate output from different iterations of processing and analysis are stored side 
by side. The project root folder should be separate from the raw data, e.g. as a folder inside of your project folder:

.. code-block:: python

	import phenopype as pp

	myproj = pp.project(root_dir="\my_project\phenopype")
	myproj.add_files(image_dir="\my_project\data_raw")
	myproj.add_config(name = "v1")
	pp.project.save(myproj)

	## after closing Python, the project can be accessed using the projects load function
	myproj = pp.project.load("\my_project\phenopype\project.data")

Above code creates a folder structure as follows:

.. code-block:: bash

	my_project\
	 data_raw 
	 phenopype\		# create phenopype project here with "pp.project"
	  data\ 		# created automatically
	   project.data		# created with "pp.project.save"
	   file1\		# add files to project using "pp.project.add_files"
	    raw.jpg			# created by "pp.project.add_files"
	    attributes.yaml	# created by "pp.project.add_files"
	    pype_config_v1.yaml	# added with "pp.project.add_config"
	    results_v1.csv
	   file2\
	    ...
	   ... 
	 data
	 scripts
	 manuscript
	 figures

.. important::

	Currently the only useful information contained in the project object (:code:`myproj`) is a list of all directories inside the
	project's directory tree. It is important to save `both` the project AND all results in the data directories using the appropriate 
	functions in (:ref:`Export`). Future release will expand the functionality of the project class and its associated methods. 

.. autoclass:: phenopype.main.project
	:members:
	:undoc-members:
	:show-inheritance:



pype (high throughput function)
-------------------------------

.. raw:: html

	Method used to process image datasets with high throughput and reproducibility. Should be used in 
	conjunction with image organized in a Phenopype directory structure. To get started with the high 
	througput workflow, see <a href="tutorial_2_phenopype_workflow.html">Tutorial 2</a> and 
	<a href="tutorial_3_managing_projects_1.html">Tutorial 3</a>.
	<br>

.. autoclass:: phenopype.main.pype
	:members:
	:undoc-members:
	:show-inheritance:


Utility functions
-----------------

Utility functions, e.g. to load and display images ,e.g. :func:`pp.utils.load_image` and :func:`pp.utils.show_image`. 
Any of these functions can be called directly after loading  phenopype without the need to add the :code:`utils` submodule:

.. code-block:: python

	import phenopype as pp
	
	image_path = "image_dir/my_image.jpg"
	
	image = pp.load_image(image_path) 	# instead of pp.utils.load_image
	pp.show_image(image) 			# instead of pp.utils.show_image
	dir(pp) 				# shows available classes and functions

.. automodule:: phenopype.utils
	:members:
	:undoc-members:
	:show-inheritance:
	:exclude-members: custom_formatwarning


Image analysis (core modules)
-----------------------------

Core image processing functions. Any function can be executed in prototyping, low throughput, and high 
throughput workflow. In general, the order in which the different steps are performed should always be 
the same:

**preprocessing > segmentation > measurement > visualization > export**

In general, any function can either take an array or a phenopype container. If an array is passed, additional 
input arguments may be required (e.g. to draw contours onto an image, but an array and a DataFrame containing the
contours must be supplied, whereas a container already includes both). 


Preprocessing
"""""""""""""

.. automodule:: phenopype.core.preprocessing
	:members:
	:undoc-members:
	:show-inheritance:



Segmentation
""""""""""""

.. automodule:: phenopype.core.segmentation
	:members:
	:undoc-members:
	:show-inheritance:



Measurement
"""""""""""

.. automodule:: phenopype.core.measurement
	:members:
	:undoc-members:
	:show-inheritance:



Visualization
"""""""""""""

.. automodule:: phenopype.core.visualization
	:members:
	:undoc-members:
	:show-inheritance:



Export
""""""

.. automodule:: phenopype.core.export
	:members:
	:undoc-members:
	:show-inheritance:	



Video analysis
--------------

.. raw:: html

	These classes provide basic motion tracking features via foreground-background subtraction - for more details see 
	<a href="https://docs.opencv.org/3.4/d1/dc5/tutorial_background_subtraction.html">the OpenCV docs 2</a> and 
	<a href="tutorial_6_video_analysis.html">Tutorial 6</a>.

Motion tracker
""""""""""""""

.. autoclass:: phenopype.tracking.motion_tracker
	:members:
	:undoc-members:
	:show-inheritance:	

Tracking methods
""""""""""""""""

.. autoclass:: phenopype.tracking.tracking_method
	:members:
	:undoc-members:
	:show-inheritance:	

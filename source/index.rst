Phenopype: a phenotyping pipeline for Python
============================================

.. raw:: html

	<hr>

.. image:: phenopype_logo.png




.. raw:: html

	<div align="justify">
	<br>
	<strong>Phenopype is a high throughput phenotyping pipeline for Python to support biologists in extracting high dimensional phenotypic data from digital images</strong>. The program provides intuitive, high level computer vision functions for image preprocessing, segmentation, and feature extraction. Users can assemble their own function-stacks that can be stored in the  human-readable `yaml`-format along with raw data and results, facilitating high throughput and full data reproducibility. Phenopype can be run from Python or from a Python Integrated Development Environment (IDE), like <i>Spyder</i>. Phenopype is designed to provide robust image analysis workflows that can be implemented with little or no Python experience.<br>
	<br>
	<strong>Getting started:</strong>
		<ol>
			<li><a href="installation.html">Install Phenopype </a> - via the <i>Python Package Index</i> (PYPI): <code>pip install phenopype</code></li> 
			<li><a href="tutorial_0.html">Run the Tutorials </a> - Tutorial 1 is for Python beginners, otherwise Tutorial 2 is a good starting point </li>
			<li><a href="#examples">Check the Examples</a> - Example 1 delineates a typical computer vision workflow </li>
		</ol>
	</div>
	<hr>

	<div class="container-fluid">
	<div class="row">
	<div class="col-md-6">
	<h2>Documentation</h2>

.. toctree::
	:maxdepth: 2

	installation
	api
	resources
	
.. raw:: html
	
	</div>
	<div class="col-md-6">
	<h2>Tutorials</h2>

.. toctree::
	:maxdepth: 1

	tutorial_0
	tutorial_1_python_intro
	tutorial_2_phenopype_workflow
	tutorial_3_managing_projects_1
	tutorial_4_managing_projects_2
	tutorial_5_gui_interactions
	tutorial_6_video_analysis

.. raw:: html

	</div>
	</div>
	<hr>

Examples
--------

.. raw:: html

	<div class="row">
	
		<div class="col-md-4">
			<div class="thumbnail">
			<a href="example_1_detect_objects_isopods.html">
			
.. image:: thumbs/ex1.jpg
			
.. raw:: html
			
			<b><p style="text-decoration: underline;">Detecting aquatic isopods</p></b>
			<b>Organism: </b>waterlouse (or sowbug)<br>
			<b>Species: </b><i>Asellus aquaticus</i> <br>
			<b>Traits: </b>size, pigmentation, body-shape <br>
			</a>
			</div>
		</div>

		<div class="col-md-4">
			<div class="thumbnail">
			<a href="example_2_landmarks_stickleback.html">
			
.. image:: thumbs/ex2.jpg
			
.. raw:: html
			
			<b><p style="text-decoration: underline;">Placing landmarks</p></b>
			<b>Organism: </b>threespine stickleback <br>
			<b>Species: </b><i>Gasterosteus aculeatus</i> <br>
			<b>Traits: </b>landmarks, geometric morphometrics <br>
			</a>
			</div>
		</div>

		<div class="col-md-4">
			<div class="thumbnail">
			<a href="example_3_phytoplankton.html">
			
.. image:: thumbs/ex3.jpg
			
.. raw:: html

			<b><p style="text-decoration: underline;">Detecting plankton cells</p></b>
			<b>Organism: </b>phytoplankton <br>
			<b>Species: </b><i>community</i> <br>
			<b>Traits: </b>pixel level intensity, shape-metrics <br>
			</a>
			</div>
		</div>

	</div>
	<div class="row">

		<div class="col-md-4">
			<div class="thumbnail">
			<a href="example_4_video_analysis_stickleback.html">
			
.. image:: thumbs/ex4.jpg
			
.. raw:: html

			<b><p style="text-decoration: underline;">Recording predator prey interactions</p></b>
			<b>Organism: </b>stickleback and isopods <br>
			<b>Species: </b><i>G. aculeatus, A. aquaticus</i> <br>
			<b>Traits: </b>movement, size <br>
			</a>
			</div>
		</div>
		
		<div class="col-md-4">
			<div class="thumbnail">
			<a href="example_5_shape_stickleback.html">
			
.. image:: thumbs/ex5.jpg
			
.. raw:: html

			<b><p style="text-decoration: underline;">Measuring armor plate area</p></b>
			<b>Organism: </b>threespine stickleback <br>
			<b>Species: </b><i>G. aculeatus</i> <br>
			<b>Traits: </b>counting armor plates; shape and size<br>
			</a>
			</div>
		</div>
		
		<div class="col-md-4">
			<div class="thumbnail">
			<a href="example_6_counting_snails.html">
			
.. image:: thumbs/ex6.jpg
			
.. raw:: html
			
			<b><p style="text-decoration: underline;">Counting snails</p></b>
			<b>Organism: </b>New Zealand mud snail <br>
			<b>Species: </b><i>Potamopyrgus antipodarum</i> <br>
			<b>Traits: </b>size (area), abundance<br>
			</a>
			</div>
		</div>
		

	</div>
	<div class="row">

		<div class="col-md-4">
			<div class="thumbnail">
			<a href="example_7_worm_length.html">
			
.. image:: thumbs/ex7.jpg
			
.. raw:: html

			<b><p style="text-decoration: underline;">Measuring length-width ratios in worms</p></b>
			<b>Organism: </b>California blackworm<br>
			<b>Species: </b><i>Lumbriculus variegatus</i> <br>
			<b>Traits: </b>length, width, area<br>
			</a>
			</div>
		</div>

	</div>


	</div>







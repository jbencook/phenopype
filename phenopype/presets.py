preset1 = """
segmentation:
- blur:
    kernel_size: 15
- threshold:
    method: otsu
- morphology:
    operation: close
    shape: ellipse
    kernel_size: 3
    iterations: 10
- find_contours:
    retrieval: ccomp
    min_diameter: 0
    min_area: 0
measurement:
- colour:
    channels: [gray, rgb]
visualization:
- select_canvas:
    canvas: image
- show_contours:
    line_thickness: 2
    text_thickness: 1
    text_size: 1
    fill: 0.3
- show_masks:
    colour: blue
    line_thickness: 5
"""

preset2 = """
preprocessing:
- create_mask:
    label: mask1
segmentation:
- blur:
    kernel_size: 15
- threshold:
    method: otsu
- morphology:
    operation: close
    shape: ellipse
    kernel_size: 3
    iterations: 10
- find_contours:
    retrieval: ccomp
    min_diameter: 0
    min_area: 0
measurement:
- colour:
    channels: [gray, rgb]
visualization:
- select_canvas:
    canvas: image
- show_contours:
    line_thickness: 2
    text_thickness: 1
    text_size: 1
    fill: 0.3
- show_masks:
    colour: blue
    line_thickness: 5
export:
- save_results:
    overwrite: true
- save_canvas:
    resize: 0.5
    overwrite: true
"""

preset3="""
preprocessing:
- create_mask:
    label: mask1
    tool: polygon
segmentation:
- blur:
    kernel_size: 15
- threshold:
    method: adaptive
    colourspace: red
    blocksize: 199
    constant: 1
- morphology:
    operation: close
    shape: ellipse
    kernel_size: 5
    iterations: 3
- find_contours:
    retrieval: ext
    min_diameter: 0
    min_area: 0
- watershed:
    iterclose: 3
    iteropen: 7
    kernelclose: 3
    kernelopen: 5
measurement:
- colour:
    channels: [gray, rgb]
visualization:
- select_canvas:
    canvas: image_mod
- show_contours:
    line_thickness: 2
    text_thickness: 1
    text_size: 1
    fill: 0
"""


landmarking1 = """
preprocessing:
- create_mask
measurement:
- landmarks
- polylines
visualization:
- show_landmarks:
    point_size: 25
    point_col: green
    label_size: 3
    label_width: 5
- show_masks:
    colour: blue
    line_thickness: 5
- show_polylines:
    colour: blue
    line_thickness: 5
export:
- save_landmarks
- save_masks
- save_polylines
"""


inverted1 = """
pype:
  name: v1
  preset: preset1
  date_created: '20200304_155635'
preprocessing:
- invert_image  
segmentation:
- blur:
    kernel_size: 5
- threshold:
    method: binary
    value: 180
    colourspace: blue
- morphology:
    operation: open
    shape: cross
    kernel_size: 5
    iterations: 3
- find_contours:
    retrieval: ccomp
    min_diameter: 0
    min_area: 500
visualization:
- show_contours:
    line_thickness: 2
    text_thickness: 1
    text_size: 1
    fill: 0.3
"""
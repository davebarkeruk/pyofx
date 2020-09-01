![pyofx](/docs/images/pyofx.jpg)

# pyofx
Command line based Python3 host for rendering images through OpenFX plugins.

Current features:
* Process a single frame through an OFX plugin.
* Display plugins inside an OFX bundle.
* Display a plugin's paramters.
* Use JSON file to control plugin parameters at render time.
* Use filter or general OFX contexts.

## Requirements

* Python3
* Numpy
* Python Image Library (PIL)
* OFX Bundle installed, for example BorisFX Sapphire

## Usage

### List Command
Display the plugins in an OFX bundle.
```
Usage:
  pyofx list dir bundle

Arguments:
  dir        Path to the ofx bundle directory.
  bundle     Name of the ofx bundle to load.
```

### Params Command
Display the parameters in a plugin, or save the parameters to a JSON formatted file. 
```
Usage:
  pyofx params [-j JSON] dir bundle plugin
  
Arguments:
  dir        Path to the ofx bundle directory.
  bundle     Name of the ofx bundle to load.
  plugin     Name of plugin to use.
  JSON       JSON filename.
```

### Filter Command
Render a plugin using the Filter context using default parameter values.
```
Usage:
  pyofx filter dir bundle plugin infile outfile
  
Arguments:
  dir        Path to the ofx bundle directory.
  bundle     Name of the ofx bundle to load.
  plugin     Name of plugin to use.
  infile     Filename of input image.
  outfile    Filename of output image.
```

### Render Command 
Render a plugin using a JSON file to control all aspects of render process. 
```
Usage:
  pyofx render dir json
  
Arguments:
  dir        Path to the ofx bundle directory.
  json       JSON file containing parameter settings.
```

How to render in General context:

1. Use the `params` command to create a JSON parameters file.
2. Edit the JSON file.
   - Add paths to image files. Note, optional paths can be left as null.
   - Make desired changes to plugin parameters.
   - Set frame_size, the pixel width and height of the render frame.
3. Use the editted JSON file as an input to the `render` command.

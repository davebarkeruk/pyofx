![pyofx](/docs/images/pyofx.jpg)

# pyofx
Command line based Python3 host for rendering images through OpenFX plugins.

A minimal number of OFX suites have been implemented.

Current version can process an image through a single plugin and save the output. The host is hardwired to use Filter context, so additional input clips is not supported.

The script can also list the plugins in an OFX bundle, and list the parameters of an individual plugin.

The plugin's default parameter values can be changed using an optional JSON formatted file.

## Requirements

* Python3
* Numpy
* Python Image Library (PIL)
* OFX Bundle installed, for example BorisFX Sapphire

## Usage

There are three commands, list, describe and render. List displays all the available plugins in an OFX bundle. Describe displays all the parameters in the selected plugin. Render takes an input image, processes it through the selected plugin and saves the output.

Command  | Details
-------- | --------
List     | pyofx list dir bundle
Describe | pyofx desc \[-j JSON\] dir bundle plugin
Render   | pyofx render \[-j JSON\] dir bundle plugin infile outfile

Argument | Description
-------- | -----------
dir      | Path to the ofx bundle directory.
bundle   | Name of the ofx bundle to load.
plugin   | Name of plugin to use.
infile   | Filename of input image.
outfile  | Filename of output image.
JSON     | Optional filename of JSON file used as parameter value input/output.

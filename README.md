![pyofx](/docs/images/pyofx.jpg)

# pyofx
Simple Python3 host for rendering images through OpenFX plugins.

Currently very bare bones opperation, with minimal number of OFX suites partially implemented. Will open an image file, process it through an OFX plugin using default parameter values, and output an image file. 

Tested on Ubuntu 18.04

## Requirements

* Python3
* Numpy
* Python Image Library (PIL)
* OFX Bundle installed, for example BorisFX Sapphire

## Usage

There are three commands, list, describe and render. List displays all the available plugins in an OFX bundle. Describe displays all the parameters in the selected plugin. Render takes an input image, processes it through the selected plugin and saves the output.

Command | Details
-- | --
List | pyofx list \<dir\> \<bundle\>
Describe | pyofx desc \<dir\> \<bundle\> \<plugin\>
Render | pyofx render \<dir\> \<bundle\> \<plugin\> \<infile\> \<outfile\>

Argument| Description
-- | --
\<dir\> | Path to the ofx bundle directory.
\<bundle\> | Name of the ofx bundle to load.
\<plugin\> | Name of plugin to use.
\<infile\> | Filename of input image.
\<outfile\> | Filename of output image.

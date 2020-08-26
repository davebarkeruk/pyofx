# pyofx
Simple Python3 host for rendering images through OpenFX plugins.

Currently very bare bones opperation, with minimal number of OFX suites partially implemented. Will open and image file, process it through an OFX plugin using default parameter values, and output an image file. 

Tested on Ubuntu 18.04

## Requirements

* Python3
* Numpy
* Python Image Library (PIL)

## Usage

List plugins inside an OFX bundle:  
`python3 pyofx list <OFX Bundle Directory> <Bundle Name>`

eg:  
`python3 pyofx list /usr/OFX/Plugins Sapphire`

Render image through OFX Plugin:  
`python3 pyofx render <OFX Bundle Directory> <Bundle Name> <Plugin Name> <Input Filename> <Output Filename\`

eg:  
`python3 pyofx render /usr/OFX/Plugins Sapphire com.genarts.sapphire.Stylize.S_HalfToneColor in.png out.jpg`

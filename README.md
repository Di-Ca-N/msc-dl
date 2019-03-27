# msc-dl

Command line interface to download only audio from Youtube videos. It gets (from a file) a list of search terms and downloads the audio of the first video retrieved by a youtube search. 


## Installation
1. Clone or download repository
1. Run <code> pip install requirements.txt</code>

Obs: For this software to work you'll need [Python3](https://www.python.org/) and [ffmpeg](https://www.ffmpeg.org/download.html) already installed

## How to use
1. Create a <code>_filename_.txt</code> file
1. List, one line each, the search terms
1. Run, by command line, the software, passing the file created on last step as argument

The files will be downloaded to "Songs/" folder, on the working directory

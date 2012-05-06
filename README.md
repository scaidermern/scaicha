# Overview

scaicha is a python script for pie chart generation. It generates a music
tag chart based on the top artists of an arbitrary last.fm user.

The Data is gathered with the help of the last.fm API and charts are drawn
using the python module pycha.


# Requirements
- python (>=2.5)
- pycha (shipped, also needs cairo)
- last.fm account with a sufficient number of submitted songs
- convert from imagemagick or graphicsmagick (could be omitted with the help of some small code changes)


# Usage

## standard mode
generate a pie chart using the default options:
$ python main.py -u username

there are several options to configure the behaviour of scaicha:
  -u <arg>, --user <arg>        last.fm user name (required)
  -p <arg>, --period <arg>      period of top artists (3, 6, 12; default: overall)
  -i <arg>, --ignores <arg>     comma separated list of tags to ignore, e.g. "hip hop,rap"
  -j <arg>, --join <arg>        combines a list of tag groups. groups are separated by commas, tags by colon
  -m <arg>, --minTagPerc <arg>  minimum tag percentage (default: 1.0), less occuring tags will be merged into other tags
  -c <arg>, --colorScheme <arg> color scheme to use (rainbow (default) or gradient)
  -b <arg>, --baseColor <arg>   base color to use (hex string or a HTML 4.0 color name)
  -l <arg>, --lighten <arg>     lighten base color by given factor (between 0.0 and 1.0)
  -r <arg>, --resize <arg>      resize image
  -s      , --score             draw score


some examples:

use only the top artists from the past three months:
$ python main.py -u KarlKartoffel -p 3

define some tags to ignore:
$ python main.py -u WilliamKidd -i "hip hop,french"

combine some tags, here: combine 'classic rock' and 'hard rock' into 'rock':
$ python main.py -u CaptainFarell -j "rock:classic rock:hard rock"
combine even more tags (note the usage of ':' and ','):
$ python main.py -u CaptainFarell -j "rock:classic rock:hard rock,metal:heavy metal:power metal"
you can even create new tags or rename existing ones if you like:
$ python main.py -u CaptainFarell -j "good stuff:rock:metal,bad stuff:hiphop:rap,worst crap ever:indie"

draw a color gradient instead of the default rainbow colors:
$ python main.py -u Pferdinand -c gradient

use another base color:
$ python main.py -u AverageJoe -b "#7d00ff"
$ python main.py -u JohnSmith -b maroon

lighten base color slightly:
$ python main.py -u AaronAronsen -l 0.3

note: all parameters can be combined


## CGI mode
- enable CGI at your webserver
- copy scaicha.py, main.py and settings.py in your CGI directory
- set CGI to True in settings.py
- make sure your webserver is able to create new files inside the CGI directory in order to use the cache
- place the cgi.html document in the webserver's html directory and adapt the location of main.py in the form
- open cgi.html in your browser

note: the CGI mode lacks proper testing, use at your own risk
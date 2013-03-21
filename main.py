#!/usr/bin/python
#
# main.py: configuring and executing scaicha
#
# Copyright (C) 2008-2009,2012 Alexander Heinlein <alexander.heinlein@web.de>
# Copyright (C) 2008-2009 Daemon Hell
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License  
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the  
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA
#

from scaicha import *
from settings import *
import getopt
import sys

if CGI:
    import cgitb
    cgitb.enable()
    import cgi


def usage(name):
    if CGI: return
    print 'usage:', name, '-u [OPTIONS]'
    print '  -u <arg>, --user <arg>        last.fm user name (required)'
    print '  -p <arg>, --period <arg>      period of top artists (3, 6, 12; default: overall)'
    print '  -i <arg>, --ignore <arg>      comma separated list of tags to ignore, e.g. "hip hop,rap"'
    print '  -j <arg>, --join <arg>        combines a list of tag groups. groups are separated by commas, tags by colon'
    print '  -m <arg>, --minTagPerc <arg>  minimum tag percentage (default: 1.0), less occuring tags will be merged into other tags'
    print '  -c <arg>, --colorScheme <arg> color scheme to use (rainbow (default) or gradient)'
    print '  -b <arg>, --baseColor <arg>   base color to use (hex string or a HTML 4.0 color name)'
    print '  -l <arg>, --lighten <arg>     lighten base color by given factor (between 0.0 and 1.0)'
    print '  -r <arg>, --resize <arg>      resize image'
    print '  -s      , --score             enable score drawing'
    print '  -d      , --dump              enable dumping tags to file'
    print '  -t,     , --tagSubstitution   disable substitution of misspelled tags'
    print '  -h      , --help              print this help and exit'
    print

def split_ignore_tags(tags):
    """ splits a comma separated string of tags to ignore """
    ignore_list = []
    for tag in tags.split(","):
        ignore_list.append(tag.strip().lower())
    ignore_list.sort()
    return ignore_list

def split_combine_tags(tags):
   """ splits a comma separated string of colon separated tags to combine """
   combine_list = []
   for list in tags.split(","):
       group_list = []
       for tag in list.split(":"):
           group_list.append(tag.strip().lower())
       combine_list.append(group_list)
   return combine_list

def run_standalone(s):
    print 'scaicha version', VER
     
    try:
        # get command line arguments
        opts, args = getopt.getopt(sys.argv[1:], 'u:p:i:j:m:c:b:l:r:sdth', ['user=', 'period=', 'ignore=', 'join=', 'minTagPerc=', 'colorScheme=', 'baseColor=', 'lighten=', 'resize=', 'score', 'dump', 'tagSubstitution', 'help'])
    except getopt.GetoptError:
        usage(sys.argv[0])
        raise RuntimeError, 'invalid argument specified'

    username = False    
    for opt, arg in opts:
        if opt in ('-u', '--user'):
            s.set_username(arg)
            username = True
        elif opt in ('-p', '--period'):
            s.set_period(arg)
        elif opt in ('-i', '--ignore'):
            s.set_ignore_tags(split_ignore_tags(arg))
        elif opt in ('-j', '--join'):
            s.set_combine_tags(split_combine_tags(arg))
        elif opt in ('-m', '--minTagPerc'):
            s.set_min_tag_perc(float(arg))
        elif opt in ('-c', '--colorScheme'):
            s.set_color_scheme(arg)
        elif opt in ('-b', '--baseColor'):
            s.set_base_color(arg)
        elif opt in ('-l', '--lighten'):
            s.set_color_lighten_fac(float(arg))
        elif opt in ('-r', '--resize'):
            if not arg.isdigit():
                raise RuntimeError, 'invalid number for size specified'
            else:
                s.set_size(arg)
        elif opt in ('-s', '--score'):
            s.set_score()
        elif opt in ('-d', '--dump'):
            s.set_dump_tags()
        elif opt in ('-t', '--tagSubstitution'):
            s.unset_tag_substitution()
        elif opt in ('-h', '--help'):
            usage(sys.argv[0])
            sys.exit(1)

    if not username:
        usage(sys.argv[0])
        raise RuntimeError, 'no username specified'
        sys.exit(1)

    if DEV \
       or os.path.exists(s.get_filename()) == False \
       or (time.time() - os.path.getmtime(s.get_filename())) > cache_time \
       or os.path.getsize(s.get_filename()) == 0:
        s.run()

def run_CGI(s):
    args = cgi.parse()
    
    username = args['name'][0]
    if not username:
        raise RuntimeError, 'no username specified'
    else:
        s.set_username(username)

    if 'period' in args:
        s.set_period(args['period'][0])
    
    if 'ignore' in args:
        s.set_ignore_tags(split_ignore_tags(args['ignore'][0]))

    if 'join' in args:
        s.set_combine_tags(split_combine_tags(args['join'][0]))
    
    if 'minTagPerc' in args:
        s.set_min_tag_perc(float(args['minTagPerc'][0]))
    
    if 'colorScheme' in args:
        s.set_color_scheme(args['colorScheme'][0])
    
    if 'baseColor' in args:
        s.set_base_color(args['baseColor'][0])
    
    if 'lighten' in args:
        s.set_color_lighten_fac(float(args['lighten'][0]))

    if 'size' in args:
        s.set_size(args['size'][0])
    
    if 'score' in args:
        s.set_score()

    if DEV \
       or os.path.exists(s.get_filename()) == False \
       or (time.time() - os.path.getmtime(s.get_filename())) > cache_time \
       or os.path.getsize(s.get_filename()) == 0:
        s.run()

    image = open(s.get_filename(), 'r')
    print 'Content-Type: image/png\r\n'
    print image.read()
    image.close()

if __name__ == '__main__':
    s = scaicha()

    if not CGI:
        run_standalone(s)
    else:
        run_CGI(s)

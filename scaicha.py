# scaicha.py: last.fm music tag pie chart generator
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

VER = '0.5'
from settings import *
# xml reading:
import urllib
# newer python?
#from lxml import etree
# python 2.5:
import xml.etree.cElementTree as etree

# pycha:
import sys
import cairo
import pycha.pie
import pycha.bar

import os
import time
import math
from operator import itemgetter

basicColors = dict(
    yellow='#ffff00',
    fuchsia='#ff00ff',
    red='#ff0000',
    silver='#c0c0c0',
    gray='#808080',
    olive='#808000',
    purple='#800080',
    maroon='#800000',
    aqua='#00ffff',
    lime='#00ff00',
    teal='#008080',
    green='#008000',
    blue='#0000ff',
    navy='#000080',
    black='#000000')

class scaicha:
    """ scaicha main class """
    
    def __init__(self):
        self.username = ''
        self.period   = 'overall'
        self.min_tag_perc = 1.0
        self.color_scheme = 'rainbow'
        self.base_color   = '#c80000'
        self.color_lighten_fac = 0.0
        self.ignored_tags  = []
        self.combined_tags = []
        self.draw_score = False
        self.do_substitute_tags = True
        self.do_dump_tags = False
        self.filename = ''
        self.size = 0
        self.tag_count  = 0.0
        self.total_play_count = 0
        self.other_tags = 0 # in percent
        
        # create cache directory if set and not existing
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)
    
    def set_username(self, name):
        self.username = name

    def set_period(self, period):
        if period in ('3', '6', '12'):
            self.period = period + 'month'
        elif period == 'overall':
            self.period = 'overall'
        else:
            raise RuntimeError, 'invalid period specified'
    
    def set_ignore_tags(self, tags):
        self.ignored_tags = tags
    
    def set_combine_tags(self, tags):
        self.combined_tags = tags
    
    def set_min_tag_perc(self, perc):
        if perc >= 0.0 and perc < 100.0:
            self.min_tag_perc = perc
        else:
            raise RuntimeError, "minimum tag percentage must be >=0.0 and <100.0"
    
    def set_color_scheme(self, scheme):
        if scheme in ('rainbow', 'gradient'):
            self.color_scheme = scheme
        else:
            raise RuntimeError, 'invalid color scheme specified'
    
    def set_base_color(self, color):
        if color[0] == "#": # hex color given
            self.base_color = color
        elif color.lower() in basicColors: # no hex color, check for known name
            self.base_color = basicColors[color.lower()]
        else:
            raise RuntimeError, 'unknown color specified'
    
    def set_color_lighten_fac(self, fac):
        if fac >= 0.0 and fac <= 1.0:
            self.color_lighten_fac = fac
        else:
            raise RuntimeError, 'color lighten factor must be >= 0.0 and <=1.0'

    def set_size(self, size):
        self.size = size
        
    def set_score(self):
        self.draw_score = True
    
    def set_dump_tags(self):
        self.do_dump_tags = True
    
    def unset_substitute_tags(self):
        self.do_substitute_tags = False
    
    def get_filename(self):
        if not self.filename:
            self.filename       = '%s_%s_pie.png' % (self.username, self.period)
            self.filename_score = '%s_%s_score.png' % (self.username, self.period)
        return self.filename
    
    def get_tags_filename(self):
        return '%s_%s_tags.txt' % (self.username, self.period)

    def get_artists(self):
        # file name of user cache, no slashes allowed
        cache_file = ('%s%s_%s.user.cache' % (cache_dir, self.username.replace('/', '_').encode("utf-8"), self.period))
        if os.path.exists(cache_file) == False \
        or time.time() - os.path.getmtime(cache_file ) > cache_time \
        or os.path.getsize(cache_file) == 0:
            if not CGI: print "downloading top artists for", self.username
            tree = etree.parse(urllib.urlopen(ART_URL % (self.username, self.period)))
            cache = open (cache_file,'w')
            for st in urllib.urlopen(ART_URL % (self.username,self.period)):
                cache.write(st)
            cache.close()
        elif not CGI: print 'using top artists from cache'
        cache = open(cache_file,'r')
        tree = etree.parse(cache)
        cache.close()
        
        artists = list()
        iter = tree.getiterator()
        for element in iter:
            if (element.tag == 'name'):
                name = element.text
            if (element.tag == 'playcount'):
                artists.append((name, element.text))
                self.total_play_count += int(element.text)
        return artists

    def get_tags(self, artists):
        tags = dict()

        for entry in artists:
            # get artist name and play count
            art_name = entry[0].replace(' ', '+').replace('/','+')
            art_play_count = int(entry[1])
            
            # file name of artist cache, no slashes allowed
            cache_file = ('%s%s.artist.cache' % (cache_dir, art_name.encode("utf-8")))
            if os.path.exists(cache_file) == False \
            or time.time() - os.path.getmtime(cache_file) > cache_time \
            or os.path.getsize(cache_file) == 0:
                if not CGI: print "downloading tag data for", entry[0].encode("utf-8")
                cache = open (cache_file,'w')
                # get artist xml document
                for st in urllib.urlopen((TAG_URL % art_name).encode("utf-8")):
                    cache.write(st)
                cache.close()
            elif not CGI: print 'using tag data for', entry[0].encode("utf-8"), 'from cache'
            cache = open (cache_file,'r')
            tree = etree.parse(cache)
            cache.close()
            
            # as the tag numbers from last.fm are a rather stupid value (neither an absolute value nor a real ratio)
            # we need to sum up all tag values per artist first in order to calculate the tag percentage
            iter = tree.getiterator()
            total_tag_values = 0
            for element in iter:
                if ((element.tag == 'count') and (element.text != '0')):
                    total_tag_values += int(element.text)
            
            # now calculate the tag percentage and generate the tag list
            tag_name = None
            for element in iter:
                if (element.tag == 'name'):
                    tag_name = element.text.lower()
                    for bad_char in "-/": # remove some bad chars, reduces number of differently spelled tags with same meaning
                        tag_name = tag_name.replace(bad_char, "")#
                    while "  " in tag_name: # replace duplicated whitespaces
                        tag_name = tag_name.replace("  ", " ")
                if ((element.tag == 'count') and (element.text != '0')):
                    art_tag_perc  = int(element.text) / float(total_tag_values) * 100.0
                    art_play_perc = (art_play_count / float(self.total_play_count)) * 100.0
                    tag_value = art_tag_perc * float(art_play_perc) / 100.0
                    if tag_name in tags:
                        tags[tag_name] += tag_value
                    else:
                        tags[tag_name] = tag_value

                    self.tag_count += tag_value
                    tag_name = None

        return tags

    def draw_pie_chart(self, tags):
        if not CGI: print 'drawing chart'
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 440, 1500)

        # sort tags by their count
        tagList = sorted(tags.iteritems(), key = itemgetter(1))
        # reverse to draw most occuring tag first
        tagList.reverse()
        
        dataSet = [("{0} ({1:03.1f}%)".format(tag, count), [[0, count]]) for tag, count in tagList if tag != "other tags"]
        # insert 'other tags' at the end
        dataSet.append(("{0} ({1:03.1f}%)".format('other tags', self.other_tags), [[0, self.other_tags]]))
        
        # lighten base color if requested
        init_color = self.base_color
        if self.color_lighten_fac != 0.0:
            r, g, b = pycha.color.hex2rgb(self.base_color)
            init_color = pycha.color.lighten(r, g, b, self.color_lighten_fac)

        options = {
            'axis': {
                'x': {
                    'ticks': [dict(v=i, label=d[0]) for i, d in enumerate(tagList)],
                    'hide' : True,
                },
                'y': {
                    'hide' : True,
                },
            },
            'background': {'hide': True},
            'padding': { 
                'left': 0,
                'right': 0,
                'top': 0,
                'bottom': 1000,
            },
            'colorScheme': {
                'name': self.color_scheme,
                'args': {
                    'initialColor': init_color,
                },
            },
            'legend': {
                'hide': False,
                'opacity' : 0.5,
                'borderColor' : '#ffffff',
                'position': {
                    'top': 390,
                    'left' : 140
                }
            },
        }

        chart = pycha.pie.PieChart(surface, options)

        chart.addDataset(dataSet)
        chart.render()
        
        surface.write_to_png(self.get_filename())
        if not CGI: print 'chart written to', self.get_filename()

    def calculate_score(self, tags):
        prescore1 = 0
        words = dict()
        
        for tag in tags.keys():
            prescore1 += tags[tag]**2
            for word in tag.split(' '):
                if word in words:
                     words[word] += 1
                else: 
                    words[word] = 1
                    
        prescore1 = math.sqrt(prescore1) / (sum(tags.values()))
        prescore = math.sqrt(sum(words.values()) / float(len(words)))
        return 150 * math.exp(-3 * (prescore * prescore1)**2)

    def draw_score(self, score):
        if not CGI: print 'drawing score'
        score = int(score)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 50)
        ctx = cairo.Context(surface)
        ctx.set_source_rgb(0, 0, 0)

        for x in range(200):
            ctx.rectangle(0.25 + x, 0.25, 1, 10)
            ctx.set_source_rgb(x * 0.005, x * 0.005, x * 0.005)
            ctx.fill()

        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(27, 30)
        ctx.set_font_size(15)
        ctx.show_text('your scaicha score is')
        ctx.set_source_rgb(1, 0, 0)

        if score > 99:
            ctx.move_to(88, 45)
        else:
            ctx.move_to(95, 45)

        ctx.show_text(str(score))
        ctx.set_source_rgb(1, 0, 0)
        ctx.rectangle(0.25 + score * 1.33, 0.25, 2, 15)
        ctx.fill()

        surface.write_to_png(self.filename_score)

    # substitutes misspelled tags, if enabled
    def substitute_tags(self, tags):
        # dictionary of tag substitions
        # note: this dict will have the opposite format of the file,
        #       the keys will get replaced by their values
        substitutions = {}
        
        # parse substitution file
        fileName = "tag_substitutions.txt"
        file = open(fileName, "r")
        lineNum = 0
        for line in file:
            lineNum += 1
            line = line.rstrip("\n")
            
            if len(line) == 0 or line.startswith("#"): continue # skip empty lines and comments
            
            separator = line.find(":") # separator between main tag and substitution list
            if separator == -1:
                if not CGI: print "error: %s:%s has invalid format" % (fileName, lineNum)
                continue
            
            mainTag = line[:separator]
            tagSubsList = line[separator + 1:]
            for tagSubs in tagSubsList.split(","): # separator between tags in substitution list
                tagSubs = tagSubs.lstrip(" ").rstrip(" ")
                if tagSubs == mainTag:
                    if not CGI: print "warning: %s:%s contains main tag '%s' in substitution list" % (fileName, lineNum, mainTag)
                else:
                    substitutions[tagSubs] = mainTag
        file.close()
        
        # substitute tags
        tagDelList = []
        tagAddDict = {}
        for tag in tags:
            if tag in substitutions:
                mainTag = substitutions[tag]
                
                # substitute tag by adding its score to the
                # main tag and deleting the substituted tag
                subsScore = tags[tag]
                if mainTag in tags:
                    tags[mainTag] += subsScore
                else:
                    tagAddDict[mainTag] = subsScore
                tagDelList.append(tag)
        
        # delete substituted tags
        for tag in tagDelList:
            del tags[tag]
        # add tag substitutions previously not present
        tags.update(tagAddDict)
        
        return tags
    
    # dumps tags to file, if enabled
    def dump(self, tags):
        # sort tags by their count
        tagList = sorted(tags.iteritems(), key = itemgetter(1))
        # reverse to dump most occuring tag first
        tagList.reverse()
        
        with open(self.get_tags_filename(), "w") as file:
            for tag, count in tagList:
                file.write("%s\t%s\n" % (count, tag.encode("utf-8")))
        if not CGI: print 'tag statistic written to', self.get_tags_filename()
    
    def combine_tags(self, tags):
        for combination in self.combined_tags:
            group = combination[0]
            for tag in combination[1:]:
                if tag not in tags: continue
                if group in tags:
                    tags[group] += tags[tag]
                else:
                    tags[group] = tags[tag]
                del tags[tag]
        return tags

    def trim_tags(self, tags):
        """ removes tags to be ignored and adds tags
        with less than min_tag_perc to other tags """
        for tag in tags.keys():
            if tag in self.ignored_tags:
                self.tag_count -= tags[tag]
                del tags[tag]

        for tag in tags.keys():
            if tags[tag] < self.min_tag_perc:
                self.other_tags += tags[tag]
                del tags[tag]
        return tags

    def run(self):
        if not self.username:
            raise RuntimeError, 'no username specified'

        arts = self.get_artists()
        if len(arts) == 0:
            if not CGI: print "error: no artists found"
            return
        
        tags = self.get_tags(arts)
        if self.do_substitute_tags:
            tags = self.substitute_tags(tags)
        tags = self.combine_tags(tags)
        if self.do_dump_tags:
            self.dump(tags)
        tags = self.trim_tags(tags)
        
        filename = self.get_filename()
        
        self.draw_pie_chart(tags)
        # crop image border
        os.popen('convert -trim -page +0+0 ./%s ./%s' % (filename, filename))
        # draw username and date to image
        os.popen('DATE=$(date "+%%F"); convert -pointsize 11 -rotate 90 -draw "gravity SouthWest text 0,0 \\"%s %s $DATE by scaicha\\"" -rotate -90 ./%s ./%s' % (self.username, self.period, filename, filename))
        
        if self.draw_score:
            score = self.calculate_score(tags)
            self.draw_score(score)
            os.popen('montage -tile 1x -background none -geometry +0+0 ./%s ./%s ./%s' % (self.filename_score, filename, filename))
        
        if self.size > 0:
            os.popen('convert -resize %s ./%s ./%s' %(self.size, filename, filename))

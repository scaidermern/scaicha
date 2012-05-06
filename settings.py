# settings.py: scaicha configuration

DEV = True # always rebuild chart
CGI = False # run as CGI or standalone version?
API_KEY = 'db6646a55074b09f8be725bcda9088e8'
ART_URL = 'http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=%s&period=%s&api_key=%s' % ("%s","%s", API_KEY)
TAG_URL = 'http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&artist=%s&api_key=%s' % ("%s", API_KEY)

cache_time   = 86400
cache_dir    = 'scaicha_cache/'

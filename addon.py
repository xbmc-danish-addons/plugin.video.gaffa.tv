#
#      Copyright (C) 2013 Tommy Winther
#      http://tommy.winther.nu
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
import os
import sys
import urlparse
import re
import urllib2
import xbmcgui
import xbmcplugin
import xbmcaddon

import buggalo

BASE_URL = 'http://gaffa.dk/tv/archive/'
VIDEO_URL = 'http://videobackup.gaffa.dk/videos/%s.mov'


def showOverview():
    u = urllib2.urlopen(BASE_URL)
    html = u.read()
    u.close()

    for m in re.finditer("<option[ ]+value='([0-9]+)'>([^<]+)</option>", html):
        category_id = m.group(1)
        title = m.group(2)

        item = xbmcgui.ListItem(title, iconImage=ICON)
        item.setProperty('Fanart_Image', FANART)
        item.setInfo(type='video', infoLabels={
            'title': title
        })

        url = PATH + '?id=' + category_id + '&page=1'
        xbmcplugin.addDirectoryItem(HANDLE, url, item, isFolder=True)

    xbmcplugin.endOfDirectory(HANDLE)


def showCategory(category_id, page=1):
    url = BASE_URL + str(category_id)
    if page > 1:
        url += '/page:%s' % page
    print url

    u = urllib2.urlopen(url)
    html = u.read()
    u.close()

    for m in re.finditer('<a href="/tv/clip/([0-9]+)" title="(.*?)"><img src=\'([^\']+)\'.*?<p>(.*?)</p>', html,
                         re.DOTALL):
        title = m.group(2)[9:]
        icon = m.group(3).replace('_193.jpg', '_640.jpg')
        description = m.group(4)

        m = re.search('splash/(.*?)_193', m.group(3))
        if m:
            url = VIDEO_URL % m.group(1)

        item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
        item.setProperty('Fanart_Image', icon)
        item.setInfo(type='video', infoLabels={
            'title': title,
            'plot': description,
            'studio': ADDON.getAddonInfo('name')
        })

        xbmcplugin.addDirectoryItem(HANDLE, url, item)

    if re.search('class="next"', html) is not None:
        item = xbmcgui.ListItem(ADDON.getLocalizedString(30000), iconImage=ICON)
        item.setProperty('Fanart_Image', FANART)
        url = PATH + '?id=' + category_id + '&page=' + str(page + 1)
        xbmcplugin.addDirectoryItem(HANDLE, url, item, True)

    xbmcplugin.endOfDirectory(HANDLE)


if __name__ == '__main__':
    ADDON = xbmcaddon.Addon()
    PATH = sys.argv[0]
    HANDLE = int(sys.argv[1])
    PARAMS = urlparse.parse_qs(sys.argv[2][1:])

    ICON = os.path.join(ADDON.getAddonInfo('path'), 'icon.png')
    FANART = os.path.join(ADDON.getAddonInfo('path'), 'fanart.jpg')

    buggalo.SUBMIT_URL = 'http://tommy.winther.nu/exception/submit.php'
    try:
        if 'id' in PARAMS and 'page' in PARAMS:
            showCategory(PARAMS['id'][0], int(PARAMS['page'][0]))
        elif 'id' in PARAMS:
            showCategory(PARAMS['id'])
        else:
            showOverview()
    except:
        buggalo.onExceptionRaised()
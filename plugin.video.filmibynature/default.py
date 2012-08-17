import urllib, urllib2, re, sys, xbmcplugin, xbmcgui
import cookielib, os, string, cookielib, StringIO
import os, time, base64, logging, calendar, binascii
import xbmcaddon
from xml.dom.minidom import parse, parseString
from datetime import datetime

try:
    import json
except ImportError:
    import simplejson as json
    

#Filmi by nature
fbn = xbmcaddon.Addon(id=re.compile("plugin://(.+?)/").findall(sys.argv[0])[0])

addonPath = fbn.getAddonInfo('path')
artPath = addonPath + '/resources/art'
resourcePath = addonPath + '/resources'
defaultIconImg = os.path.join(xbmc.translatePath(addonPath), "icon.png")
addonDataPath = fbn.getAddonInfo('profile')
movieImgUrlJsonFile = 'MovieImgUrl_V2.json'
octoshapeChannelsFile = 'Octoshape-Channels.json'
yeahChannelsFile = 'Yeah-Channels.json'
cachedImgUrlJsonObj = {}
maxLinksPerPageOption = [15, 25, 50]

oldMovieImgUrlJsonFile = ['MovieImgUrl.json', 'MovieImgUrl_V1.json']

      
      
def TV():
        #addDir('TV SHOWS','http://www.filmitown.com/forums/forumdisplay.php?f=18',1,os.path.join(xbmc.translatePath( artPath ), "TV_Shows_V1.png"))
        addDir('MOVIES', 'http://www.sominaltvtheater.com/', 20, os.path.join(xbmc.translatePath(artPath), "Movies_V1.png"))
        addDir('MUSIC VIDEOS', 'http://www.sominaltvtheater.com/', 40, os.path.join(xbmc.translatePath(artPath), "Music_V1.png"))
        addDir('YouTube CHANNELS', 'http://www.youtube.com/', 60, os.path.join(xbmc.translatePath(artPath), "YouTube_V1.png"))
        #addDir('LIVE TV','LIVE',80,os.path.join(xbmc.translatePath( artPath ), "Live_V1.png"))
        #addDir('NEW ADD-ON :: [B]VEOH[/B] [I]beta[/I]', 'http://code.google.com/p/apple-tv2-xbmc/', 50, os.path.join(xbmc.translatePath( artPath ), "AJ_V1.png"))
        

def WHAT_IS_COMING(url):
        d = xbmcgui.Dialog()
        d.ok('Do you like this add-on and AJ work?', '', 'DONATE today: \n[B]http://code.google.com/p/apple-tv2-xbmc/[/B]')
                

def CHANNELS(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        web = ''.join(link.splitlines())
        match = re.compile('<td><img src="(.+?)" alt="" border="0" /></td>		<td class="alt1Active" align="left" id="(.+?)" style="border-left-width: 0;">			<div>				<a href="(.+?)" class="forum-link"><strong>(.+?)</strong></a>').findall(web)
        for thumbnail, id, url, name in match:
                addDir(unescape(name), 'http://www.filmitown.com/forums/' + unescape(url), 2, 'http://www.filmitown.com/forums/' + thumbnail)
                    
              
def SHOWS(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        web = ''.join(link.splitlines())
        match = re.compile('<div>				<a href="(.+?)" class="forum-link"><strong>(?!<font color="blue">)(.+?)</strong></a>							</div>').findall(web)
        for url, name in match:
                newName = unescape(name).replace('<img src="http://www.filmitown.com/forums/forums/images/mainlogo/hot.jpg" border="0">', ' @@HOT@@')
                newName = newName.replace('<img src="http://www.filmitown.com/forums/forums/images/mainlogo/hot.jpg" border="0"', ' @@HOT@@')
                newName = newName.replace('<img src="http://www.filmitown.com/forums/forums/images/mainlogo/hot.jpg" border=', ' @@HOT@@')
                newName = newName.replace('<img src="/forums/images/mainlogo/hot.jpg" border="0">', ' @@HOT@@')
                newName = newName.replace('<img src="/forums/images/mainlogo/hot.jpg" border="0"', ' @@HOT@@')
                newName = newName.replace('<img src="/forums/images/mainlogo/hot.jpg" border=', ' @@HOT@@')
                newName = newName.replace('<img src="http://www.filmitown.com/forums/forums/images/mainlogo/new.gif" border="0">', ' **NEW**')
                newName = newName.replace('<img src="http://www.filmitown.com/forums/forums/images/mainlogo/new.gif" border="0"', ' **NEW**')
                newName = newName.replace('<img src="http://www.filmitown.com/forums/forums/images/mainlogo/new.gif" border=', ' **NEW**')
                newName = newName.replace('<img src="/forums/images/mainlogo/new.jpg" border="0">', ' **NEW**')
                newName = newName.replace('<img src="/forums/images/mainlogo/new.gif" border="0">', ' **NEW**')
                addDir(newName, 'http://www.filmitown.com/forums/' + unescape(url), 3, '')
        match = re.compile('<div>				<a href="(.+?)" class="forum-link"><strong><font color="blue">(.+?)</font></strong></a>							</div>').findall(web)
        if(len(match) != 0):
                splitted = match[0][0].split('<a href="')
                if(len(splitted) != 0):
                        archivedLink = splitted[len(splitted) - 1]
                addDir('**>>**' + match[0][1] + '**>>**', 'http://www.filmitown.com/forums/' + unescape(archivedLink), 2, '')
    

def EPISODES(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        web = ''.join(link.splitlines())
        match = re.compile('<div>							(.+?)									<a href="(.+?)" id="thread_title_(.+?)">(.+?)</a>').findall(web)
        for extraChars, url, id, name in match:
                addDir(unescape(name), 'http://www.filmitown.com/forums/' + unescape(url), 4, '')
        
        #SUPPORT FOR PAGES 
        web = web.replace('\t', '').split('<td class="tcat" width="100%">Threads in Forum<span class="normal">');
        match = re.compile('<td class="alt2"><span class="smallfont" title="Showing results (.+?)"><strong>(.+?)</strong></span></td>').findall(web[0])
        if(len(match) != 0):
                currentPage = int(match[0][1])
                match = re.compile('<td class="alt1" nowrap="nowrap"><a rel="start" class="smallfont" href="(.+?)" title="First Page - Results (.+?)"><strong>&laquo;</strong> First</a></td>').findall(web[0])
                if(len(match) != 0):
                        addDir('<<<< FIRST PAGE <<', 'http://www.filmitown.com/forums/' + unescape(match[0][0]), 3, os.path.join(xbmc.translatePath(artPath), "first-icon.png"))
                match = re.compile('<td class="alt1"><a class="smallfont" href="(.+?)" title="Show results (.+?)">(.+?)</a>').findall(web[0])
                for url, title, page in match:
                        thisPage = 0
                        try:
                                thisPage = int(page)
                        except:
                                continue
                        if(thisPage < currentPage):
                                addDir('<<<< PREVIOUS PAGE - ' + page + ' <<', 'http://www.filmitown.com/forums/' + unescape(url), 3, os.path.join(xbmc.translatePath(artPath), "prev-icon.png"))
                        elif(thisPage > currentPage):
                                addDir('>> NEXT PAGE - ' + page + ' >>>>', 'http://www.filmitown.com/forums/' + unescape(url), 3, os.path.join(xbmc.translatePath(artPath), "next-icon.png"))
                match = re.compile('<td class="alt1" nowrap="nowrap"><a class="smallfont" href="(.+?)" title="Last Page - Results (.+?)">Last <strong>&raquo;</strong></a></td>').findall(web[0])
                if(len(match) != 0):
                        addDir('>> LAST PAGE >>>>', 'http://www.filmitown.com/forums/' + unescape(match[0][0]), 3, os.path.join(xbmc.translatePath(artPath), "last-icon.png"))
                        

def PARTS(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        web = ''.join(link.splitlines())
        web = web.replace('</div><br />', '</div><br /><br />')
        web = web.replace('color="red"', 'color="Red"')
        web = web.replace('*DVD Quality* (DailyMotion)</b>', 'DailyMotion *DVD Quality*:-</b>')
        web = web.replace('<font color="Red"><b>', '<b><font color="Red">')
        web = web.replace('</b></font>', '</font></b>')
        web = web.replace('<br />Watch Online', '<b>Watch Online')
        web = web.replace('Online/Download', 'Online')
        match = re.compile('<b>Watch Online (.+?):(.+?)</b><br />(.+?)<br /><br />').findall(web)
        if(len(match) != 0):
                arr = web.split(match[len(match) - 1][2])
                extraMatch = re.compile('<b>Watch Online (.+?):(.+?)</b><br />(.+?)</div>').findall(arr[1])
                match.extend(extraMatch)
        else:
                extraMatch = re.compile('<b>Watch Online (.+?):(.+?)</b><br />(.+?)<br /></div>').findall(web)
                match.extend(extraMatch)
        extraMatch = re.compile('<b><font color="Red">Watch Online (.+?)</font>(.+?)<br /><br />(.+?)<br /><br />').findall(web)
        match.extend(extraMatch)
        
        for name, extraChars, links in match:
                #print match
                matching = re.compile('Part (.+?) : <a href="(.+?)" target="_blank">Watch</a>').findall(links)
                playList = ''
                i = 1
                matchCount = len(matching)
                for part, url in matching:
                        addPlayableLink(unescape(name) + ' - Part: ' + part, unescape(url), 13, '')
                        playList = playList + unescape(url)
                        if(i < matchCount):
                                playList = playList + ':;'
                        i = i + 1
                if(i > matchCount and matchCount > 0):
                        addPlayListLink('[B]Direct PLAY - ' + unescape(name) + '[/B] [I]Playlist of above ' + str(matchCount) + ' videos[/I]', playList, 6, '')
                if(matchCount == 0):
                        extraMatch = re.compile('<a href="http://www.hostingcup.com/(.+?)" target="_blank">(.+?)</a>').findall(links)
                        matchCount = len(extraMatch)
                        if(matchCount == 1):
                                addPlayableLink(unescape(name), unescape(extraMatch[0][1]), 13, '')
                if(matchCount == 0):
                        extraMatch = re.compile('<a href="http://hostingbulk.com/(.+?)" target="_blank">(.+?)</a>').findall(links)
                        matchCount = len(extraMatch)
                        if(matchCount == 1):
                                addPlayableLink(unescape(name), unescape(extraMatch[0][1]), 13, '')


def PLAYLIST_VIDEOLINKS(url, name):
        #xbmc.executebuiltin("XBMC.Notification(PLease Wait!,Loading video links into XBMC Media Player,5000)")
        ok = True
        playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playList.clear()
        #time.sleep(2)
        links = url.split(':;')
        
        pDialog = xbmcgui.DialogProgress()
        ret = pDialog.create('Loading playlist...')
        totalLinks = len(links)
        loadedLinks = 0
        remaining_display = 'Videos loaded :: [B]' + str(loadedLinks) + ' / ' + str(totalLinks) + '[/B] into XBMC player playlist.'
        pDialog.update(0, 'Please wait for the process to retrieve video link.', remaining_display)
        for videoLink in links:
                loadVideos(videoLink, name, True, True)
                
                loadedLinks = loadedLinks + 1
                percent = (loadedLinks * 100) / totalLinks
                #print percent
                remaining_display = 'Videos loaded :: [B]' + str(loadedLinks) + ' / ' + str(totalLinks) + '[/B] into XBMC player playlist.'
                pDialog.update(percent, 'Please wait for the process to retrieve video link.', remaining_display)
                if (pDialog.iscanceled()):
                        return False
                        
        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play(playList)
        if not xbmcPlayer.isPlayingVideo():
                d = xbmcgui.Dialog()
                d.ok('INVALID VIDEO PLAYLIST', 'The playlist videos were removed due to copyright issue.', 'Check other links.')
        return ok


def LOAD_AND_PLAY_VIDEO(url, name):
        ok = True
        print url
        videoUrl = loadVideos(url, name, True, False)
        if videoUrl == None:
                d = xbmcgui.Dialog()
                d.ok('NO VIDEO FOUND', 'This video was removed due to copyright issue.', 'Check other links.')
                return False
        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play(videoUrl)
        return ok


def VIDEOLINKS(url, name):
        loadVideos(url, name, False, False)


def loadVideos(url, name, isRequestForURL, isRequestForPlaylist):
        LinkFill = True
        print url
        #DAILYMOTION
        try:
                p = re.compile('/daily.php\?url\=(.+?)&AJ;')
                match = p.findall(url + '&AJ;')
                link = 'http://www.dailymotion.com/video/' + str(match[0])
                req = urllib2.Request(link)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                sequence = re.compile('"sequence":"(.+?)"').findall(link)
                newseqeunce = urllib.unquote(sequence[0]).decode('utf8').replace('\\/', '/')
                imgSrc = re.compile('og:image" content="(.+?)"').findall(link)
                if(len(imgSrc) == 0):
                	imgSrc = re.compile('/jpeg" href="(.+?)"').findall(link)
                dm_low = re.compile('"sdURL":"(.+?)"').findall(newseqeunce)
                dm_high = re.compile('"hqURL":"(.+?)"').findall(newseqeunce)
                if(isRequestForURL):
                        videoUrl = ''
                        if(len(dm_high) == 0):
                                videoUrl = dm_low[0]
                        else:
                                videoUrl = dm_high[0]
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem('EPISODE', thumbnailImage=imgSrc[0])
                                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                                playlist.add(url=videoUrl, listitem=liz)
                                return videoUrl
                        else:
                                return videoUrl
                                
                else:
                        if(len(dm_low) > 0):
                                addLink ('PLAY Standard Quality ', dm_low[0], imgSrc[0])
                        if(len(dm_high) > 0):
                                addLink ('PLAY High Quality ', dm_high[0], imgSrc[0])
        except: pass
        
        #YOUTUBE
        try:
                p = re.compile('/yt.php\?url\=(.+?)&AJ;')
                match = p.findall(url + '&AJ;')
                print match
                code = match[0]
                linkImage = 'http://i.ytimg.com/vi/' + code + '/default.jpg'
                req = urllib2.Request('http://www.youtube.com/watch?v=' + code + '&fmt=18')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                
                if len(re.compile('shortlink" href="http://youtu.be/(.+?)"').findall(link)) == 0:
                        if len(re.compile('\'VIDEO_ID\': "(.+?)"').findall(link)) == 0:
                                req = urllib2.Request('http://www.youtube.com/get_video_info?video_id=' + code + '&asv=3&el=detailpage&hl=en_US')
                                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                                response = urllib2.urlopen(req)
                                link = response.read()
                                response.close()
                map = None
                link = link.replace('\\u0026', '&')
                match = re.compile('url_encoded_fmt_stream_map=(.+?)&').findall(link)
                if len(match) == 0:
                        map = (re.compile('url_encoded_fmt_stream_map": "(.+?)"').findall(link)[0]).replace('\\/', '/').split('url=')
                else:
                        map = urllib.unquote(match[0]).decode('utf8').split('url=')
                if re.search('status=fail', link):
                        return
                if map == None:
                        return
                #print map
                highResoVid = ''
                youtubeVideoQual = fbn.getSetting('videoQual')
                for attr in map:
                        if attr == '':
                                continue
                        parts = attr.split('&qual')
                        url = urllib.unquote(parts[0]).decode('utf8')
                        print url
                        qual = re.compile('&itag=(\d*)').findall(url)[0]
                        print qual
                        if(qual == '13'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY 3GP Low Quality - 176x144', url, linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        if(qual == '17'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY 3GP Medium Quality - 176x144', url, linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        if(qual == '36'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY 3GP High Quality - 320x240', url, linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        if(qual == '5'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY FLV Low Quality - 400\\327226', url, linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        if(qual == '34'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY FLV Medium Quality - 480x360', url, linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        if(qual == '6'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY FLV Medium Quality - 640\\327360', url, linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        if(qual == '35'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY FLV High Quality - 854\\327480', url, linkImage)
                                else:
                                        highResoVid = url
                        if(qual == '18'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY MP4 High Quality - 480x360', url, linkImage)
                                else:
                                        highResoVid = url
                                        
                        if(qual == '22'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY MP4 High Quality - 1280x720', url, linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '1' or youtubeVideoQual == '2':
                                                break
                        if(qual == '37'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY MP4 High-2 Quality - 1920x1080', url, linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '2':
                                                break
                        if(qual == '38'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY MP4 Epic Quality - 4096\\3272304', url, linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '2':
                                                break
                        if(qual == '43'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY WEBM Medium Quality - 4096\\3272304', url, linkImage)
                                else:
                                        highResoVid = url
                        if(qual == '44'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY WEBM High Quality - 4096\\3272304', url, linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '1' or youtubeVideoQual == '2':
                                                break
                        if(qual == '45'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY WEBM High-2 Quality - 4096\\3272304', url, linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '2':
                                                break
                print highResoVid
                if(isRequestForURL):
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem('VIDEO PART', thumbnailImage=linkImage)
                                xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(url=highResoVid, listitem=liz)
                                return highResoVid
                        else:
                                return highResoVid

        except: pass
        
        #Z-SHARE
        try:
                
                p = re.compile('/watch.php\?url\=(.+?)/')
                match = p.findall(url)
                url = 'http://www.zshare.net/video/' + match[0]
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                match = re.compile('iframe src\="http://www.zshare.net/videoplayer(.+?)"').findall(link)
                req = urllib2.Request('http://www.zshare.net/videoplayer' + match[0].replace(' ', '%20'))
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                videoUrl = re.compile('file: "(.+?)"').findall(link)[0]
                videoUrl = videoUrl.replace(' ', '%20') + '|User-Agent=' + urllib.quote_plus('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_1) AppleWebKit/534.48.3 (KHTML, like Gecko) Version/5.1 Safari/534.48.3' + '&Accept=' + urllib.quote_plus('text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8') + '&Accept_Encoding=' + urllib.quote_plus('gzip, deflate'))
                
                if(isRequestForURL):
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem('EPISODE', thumbnailImage='')
                                xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(url=videoUrl, listitem=liz)
                                return videoUrl
                        else:
                                return videoUrl
                else:
                        addLink ('PLAY High Quality Video', videoUrl, '')
        except: pass

        #HOSTING CUP
        try:
                chkUrl = url + '&AJ;'
                id = re.compile('http://www.hostingcup.com/(.+?)&AJ;').findall(chkUrl)[0]
                url = 'http://www.hostingcup.com/' + id
                webLink = ''.join(link.splitlines()).replace('\t', '')
                #Trying to find out easy way out :)
                paramSet = re.compile("return p\}\(\'(.+?)\',36,(.+?),\'(.+?)\'").findall(webLink)
                
                result = parseValue(paramSet[0][0], 36, int(paramSet[0][1]), paramSet[0][2].split('|'))
                result = result.replace('\\', '').replace('"', '\'')
                print result

                imgUrl = re.compile("s1.addVariable\(\'image\',\'(.+?)\'\);").findall(result)[0]
                videoUrl = re.compile("s1.addVariable\(\'file\',\'(.+?)\'\);").findall(result)[0]
                
                print 'HOSTING CUP url = ' + videoUrl
                if(isRequestForURL):
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem(name, thumbnailImage=imgUrl)
                                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                                playlist.add(url=videoUrl, listitem=liz)
                                return videoUrl
                        else:
                                return videoUrl
                else:
                        addLink ('[B]PLAY VIDEO[/B]: ' + name, videoUrl, imgUrl)
        except: pass

        #HOSTING BULK
        try:
                chkUrl = url + '&AJ;'
                id = re.compile('http://hostingbulk.com/(.+?)&AJ;').findall(chkUrl)[0]
                url = 'http://hostingbulk.com/' + id
                webLink = ''.join(link.splitlines()).replace('\t', '')
                #Trying to find out easy way out :)
                paramSet = re.compile("return p\}\(\'(.+?)\',36,(.+?),\'(.+?)\'").findall(webLink)
                
                result = parseValue(paramSet[0][0], 36, int(paramSet[0][1]), paramSet[0][2].split('|'))
                result = result.replace('\\', '').replace('"', '\'')
                print result

                imgUrl = re.compile("s1.addVariable\(\'image\',\'(.+?)\'\);").findall(result)[0]
                videoUrl = re.compile("s1.addVariable\(\'file\',\'(.+?)\'\);").findall(result)[0]
                
                print 'HOSTING BULK url = ' + videoUrl
                if(isRequestForURL):
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem(name, thumbnailImage=imgUrl)
                                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                                playlist.add(url=videoUrl, listitem=liz)
                                return videoUrl
                        else:
                                return videoUrl
                else:
                        addLink ('[B]PLAY VIDEO[/B]: ' + name, videoUrl, imgUrl)
        except: pass



#MOVIES

def MOVIES_MENU(url, name):
        addDir('*[B]High Definition[/B]* Collection', 'http://www.sominaltvtheater.com/2010/11/bluray-movies-collection.html', 21, os.path.join(xbmc.translatePath(artPath), "HD_Movies_V1.png"))
        addDir('[B]HINDI[/B] MOVIES', 'http://www.sominaltvtheater.com/2010/11/hindi-movies.html', 23, os.path.join(xbmc.translatePath(artPath), "Hindi_Movies_V1.png"))
        addDir('[B]TELUGU[/B] MOVIES', 'http://www.sominaltvtheater.com/2010/11/telugu-movies.html', 24, os.path.join(xbmc.translatePath(artPath), "Telugu_Movies_V1.png"))
        addDir('[B]TAMIL[/B] MOVIES', 'http://www.sominaltvtheater.com/2010/11/tamil-movies.html', 25, os.path.join(xbmc.translatePath(artPath), "Tamil_Movies_V1.png"))
        
#        addDir('[B]HINDI[/B] MOVIES','hindi',22,os.path.join(xbmc.translatePath( artPath ), "Hindi_Movies_V1.png"))
#        addDir('[B]TELUGU[/B] MOVIES','telugu',22,os.path.join(xbmc.translatePath( artPath ), "Telugu_Movies_V1.png"))
#        addDir('[B]TAMIL[/B] MOVIES','tamil',22,os.path.join(xbmc.translatePath( artPath ), "Tamil_Movies_V1.png"))
#        addDir('[B]MALAYALAM[/B] MOVIES','malayalam',22,os.path.join(xbmc.translatePath( artPath ), "Malayalam_Movies_V1.png"))
#        addDir('[B]KANNADA[/B] MOVIES','kannada',22,os.path.join(xbmc.translatePath( artPath ), "Kannada_Movies_V1.png"))
#        addDir('[B]BENGALI[/B] MOVIES','bengali',22,os.path.join(xbmc.translatePath( artPath ), "Bengali_Movies_V1.png"))
#        addDir('[B]MARATHI[/B] MOVIES','marathi',22,os.path.join(xbmc.translatePath( artPath ), "Marathi_Movies_V1.png"))
        


#BharatMovies
def BM_MOVIES_BY_LANG(lang, name):
        url = 'http://www.bharatmovies.com/' + lang + '/watch/movies.htm'
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        link = ''.join(link.splitlines()).replace('\t', '').replace('ilactive', 'ila')
        index = re.compile('<a id=ila href=(.+?)>(.+?)</a>').findall(link)
        indexCount = len(index)
        if indexCount > 0:
                indexURL = ''
                i = 0
                for indexLink, indexChar in index:
                        print indexChar + ' <--> ' + indexLink
                        indexURL = indexURL + indexChar + '<-->' + 'http://www.bharatmovies.com/' + lang + '/watch/' + indexLink
                        i = i + 1
                        if i < indexCount:
                                indexURL = indexURL + '&AJ;'
                addDir('A-Z DIRECTORIES', indexURL, 26, os.path.join(xbmc.translatePath(artPath), "AZ_Dir_V1.png"))
                
                if re.search('Movie Index By Release Year', link):
                        addDir('Browse by RELEASE DECADES', lang, 27, os.path.join(xbmc.translatePath(artPath), "Release_Decades_V1.png"))
                
                if lang == 'hindi':
                        addDir('Browse MORE [B]HINDI[/B] MOVIES', 'http://www.sominaltvtheater.com/2010/11/hindi-movies.html', 23, os.path.join(xbmc.translatePath(artPath), "Hindi_Movies_V1.png"))
                elif lang == 'telugu':
                        addDir('Browse MORE [B]TELUGU[/B] MOVIES', 'http://www.sominaltvtheater.com/2010/11/telugu-movies.html', 24, os.path.join(xbmc.translatePath(artPath), "Telugu_Movies_V1.png"))
                elif lang == 'tamil':
                        addDir('Browse MORE [B]TAMIL[/B] MOVIES', 'http://www.sominaltvtheater.com/2010/11/tamil-movies.html', 25, os.path.join(xbmc.translatePath(artPath), "Tamil_Movies_V1.png"))
                        
        else:
                xbmc.executebuiltin("XBMC.Notification(PLease Wait!,Loading ALL MOVIES in this category,5000)")
                BM_LIST(url, name)


def BM_MOVIES_A_Z_DIR(indexMap, name):
        indexNameList = []
        indexUrlList = []
        indexEntries = indexMap.split('&AJ;')
        for indexEntry in indexEntries:
                index = indexEntry.split('<-->')
                #imgUrl = os.path.join(xbmc.translatePath( artPath ), "alpha/red-"+index[0]+".png")
                indexNameList.append('[B]' + index[0] + '[/B]')
                indexUrlList.append(index[1])
                #if index[0] == '#':
                #        imgUrl = os.path.join(xbmc.translatePath( artPath ), "alpha/red-hash.png")
                #addDir(index[0], index[1], 28, imgUrl)
        d = xbmcgui.Dialog()
        indexSelect = d.select('A-Z Directories:', indexNameList)
        if indexSelect == -1:
                indexSelect = 0
        url = indexUrlList[indexSelect]
        name = indexNameList[indexSelect]
        BM_LIST(url, name)

        
def BM_MOVIES_BY_DECADES(lang, name):
        indexNameList = []
        indexUrlList = []
        url = 'http://www.bharatmovies.com/' + lang + '/watch/' + lang + '-movies-new.htm'
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        link = ''.join(link.splitlines()).replace('\t', '').replace('ilactive', 'ila')
        index = re.compile('<a id=ila href=(.+?)>(.+?)</a>').findall(link)
        for indexLink, indexChar in index:
                print indexChar + ' <--> ' + indexLink
                indexUrl = 'http://www.bharatmovies.com/' + lang + '/watch/' + indexLink
                indexNameList.append('[B]' + indexChar + '[/B]')
                indexUrlList.append(indexUrl)
                #addDir(indexChar, indexUrl, 28, '')
        d = xbmcgui.Dialog()
        indexSelect = d.select('Decades:', indexNameList)
        if indexSelect == -1:
                indexSelect = 0
        url = indexUrlList[indexSelect]
        name = indexNameList[indexSelect]
        BM_LIST(url, name)
                

def BM_LIST(url, name):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        link = ''.join(link.splitlines()).replace('\t', '').replace('ilactive', 'ila').replace('<i>', '').replace('</i>', '')
        movies = re.compile('<div id=L[1,2]><a href=(.+?)>(.+?)</a><span>(.+?)</span></div>').findall(link)
        if len(movies) > 0 and fbn.getSetting('load_image_from_tmdb') == 'true':
                xbmc.executebuiltin("XBMC.Notification(PLease Wait!,Loading MOVIE image from themoviedb.org, Check add-on settings for more information, 5000)")
                
        for movieLink, movieName, movieCast in movies:
        
                movieNameParts = re.compile('(.+?)<font color=red>(.+?)</font>').findall(movieName)
                if len(movieNameParts) > 0:
                        movieName = movieNameParts[0][0] + ' ' + movieNameParts[0][1]
                
                #print movieName + ' --> '+movieLink + ' -->CASTING--> '+movieCast
                movieLink = url[0 : url.rindex('/') + 1] + movieLink
                addDirAndLoadImg(movieName, movieLink, 29)
        
        
def BM_VIDEO_SOURCES(url, name):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        link = ''.join(link.splitlines()).replace('\t', '')
        sourceNames = re.compile('<br> Source: [2,3,4,5,6,7,8,9,10] <br>').findall(link)
        sourceNames.append('<br> Source: 1 <br>')
        sourceVideoLinks = link.split('<br> Source:')
        
        partHeading = 'Part'
        if re.search('/songs/', url):
                partHeading = 'Song'
        
        index = 0
        sourceNbr = 1
        for sourceName in sourceNames:
                try:
                        sourceName = re.compile('<div id=source>Source: (.+?)</div>').findall(sourceVideoLinks[index])[0]
                except:
                        index = index + 1
                        continue
                print sourceName
                if sourceName == 'YouKu' or sourceName == 'Rajshri':
                        index = index + 1
                        xbmc.executebuiltin("XBMC.Notification(Skipped Source: YouKu,Not yet supported,5000)")
                        continue
                sourceVideos = re.compile('<embed(.+?)>').findall(sourceVideoLinks[index])
                matchCount = len(sourceVideos)
                if matchCount == 1:
                        try:
                                if re.search('http://www.youtube.com/p/', sourceVideos[0]):
                                        videoLink = sourceVideos[0] + '&'
                                        playlistID = re.compile('http://www.youtube.com/p/(.+?)&').findall(videoLink)[0]
                                        print 'retreiveYouTubePlayList ' + playlistID
                                        retreiveYouTubePlayList(playlistID, '', 'Source #' + str(sourceNbr) + ' ' + sourceName, 'Part')
                                        sourceNbr = sourceNbr + 1
                                        index = index + 1
                                        continue
                        
                                elif re.search('http://www.youtube.com/view_play_list', videoLink):
                                        videoLink = sourceVideos[0] + '&'
                                        playlistID = re.compile('http://www.youtube.com/view_play_list\?p=(.+?)&').findall(videoLink)[0]
                                        print 'retreiveYouTubePlayList ' + playlistID
                                        retreiveYouTubePlayList(playlistID, '', 'Source #' + str(sourceNbr) + ' ' + sourceName, 'Part')
                                        sourceNbr = sourceNbr + 1
                                        index = index + 1
                                        continue
                        except: pass
                        
                if matchCount > 1:
                        playList = ''
                        i = 1
                        for sourceVideo in sourceVideos:
                                sourceVideo = re.compile(' src=(.+?) ').findall(' ' + sourceVideo + ' ')[0].replace('\'', '').replace('"', '')
                                addPlayableMovieLink('Source #' + str(sourceNbr) + ' ' + sourceName + ' - ' + partHeading + ': ' + str(i), unescape(sourceVideo), 31, '')
                                playList = playList + unescape(sourceVideo)
                                if(i < matchCount):
                        		        playList = playList + ':;'
                                i = i + 1
                        if(i > matchCount and matchCount > 0):
                                addPlayListLink('[B]Direct PLAY - ' + sourceName + '[/B] [I]Playlist of above ' + str(matchCount) + ' videos[/I]', playList, 32, '')
                else:
                        sourceVideo = re.compile(' src=(.+?) ').findall(' ' + sourceVideos[0] + ' ')[0].replace('\'', '').replace('"', '')
                        addPlayableMovieLink('[B]SINGLE LINK[/B] Source #' + str(sourceNbr) + ' ' + sourceName, unescape(sourceVideo), 31, '')
                sourceNbr = sourceNbr + 1
                index = index + 1
        

#SominalTVTheater

def MORE_MOVIES_HINDI(url, name):
        MoviesList(url, 30)
        

def MORE_MOVIES_TELUGU(url, name):
        MoviesList(url, 30)
        

def MORE_MOVIES_TAMIL(url, name):
        MoviesList(url, 30)


def MOVIES_BLURAY(url, name):
        BlurayMoviesList(url)


def BlurayMoviesList(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        link = ''.join(link.splitlines()).replace('\t', '').replace('\'', '"').replace('&nbsp;', '')
        moviesContentArray = re.compile('<div class="cover"><div class="entry">(.+?)<div style="clear:both;"></div><div class="clear"></div>').findall(link)
        moviesArray = re.compile('<a href="(.+?)"><img alt="" class="ethumb" src="(.+?)" style="cursor: move;" /></a>').findall(moviesContentArray[0])
        movieIndex = 1
        for movieLink, movieImg in moviesArray:
                #movieTitle = 'MOVIE #' + str(movieIndex)
                movieTitle = movieLink[movieLink.rindex('/') + 1 : movieLink.rindex('.')]
                
                addDir(unescape(movieTitle), movieLink, 30, movieImg)
                movieIndex = movieIndex + 1


def MoviesList(url, mode):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        link = ''.join(link.splitlines()).replace('\t', '').replace('\'', '"').replace('&nbsp;', '')
        moviesContentArray = re.compile('<br /><br />(.+?)<div class="clear"></div>').findall(link)
        if(len(moviesContentArray) == 0):
                moviesContentArray = re.compile('</div><br /><div style="text-align: center;">(.+?)<div style="clear:both;"></div>').findall(link)
        
        moviesContent = moviesContentArray[0]
        
        moviesContent = moviesContent.replace('<a href="http://adf.ly/377117/http://www.sominaltvtheater.com/2010/11/bluray-movies-collection.html"><b>(Hindi, Telugu, &amp; Tamil)</b></a>', '')
        moviesContent = moviesContent.replace('<span class="Apple-style-span" style="font-size: xx-small;"></span>', '')
        moviesContent = moviesContent.replace('<a href="http://www.sominaltvtheater.com/2010/11/apaharan-2005-bluray.html"></a>', '')
        moviesContent = moviesContent.replace('</a><a href="http://www.sominaltvtheater.com/2011/04/teen-thay-bhai-2011-dvdscr.html">', '')
        moviesContent = moviesContent.replace('</a><span class="Apple-style-span" style="color: blue; font-size: xx-small;">*BluRay*</span>', ' *BluRay*</a>')
        moviesContent = moviesContent.replace('</a><b><span class="Apple-style-span" style="color: blue; font-size: xx-small;">*BluRay*</span></b>', ' *BluRay*</a>')
        moviesContent = moviesContent.replace('</a><b><span class="Apple-style-span" style="color: blue; font-size: xx-small;">*HD*</span></b>', ' *HD*</a>')
        
        moviesContent = moviesContent.replace('</a><span class="Apple-style-span" style="font-size: xx-small;">DVD</span>', ' ~DVD~</a>')
        moviesContent = moviesContent.replace('</a><span class="Apple-style-span" style="font-size: xx-small;">DVDSCR</span>', ' --DVDSCR--</a>')
        moviesContent = moviesContent.replace('</a><span class="Apple-style-span" style="font-size: xx-small;">TS</span>', ' --TS--</a>')
        moviesContent = moviesContent.replace('</a><span class="Apple-style-span" style="font-size: xx-small;">TC</span>', ' --TC--</a>')
        moviesContent = moviesContent.replace('</a><span class="Apple-style-span" style="font-size: xx-small;">DVD <span class="Apple-style-span" style="color: blue;"><b>*HD*</b></span></span>', ' *HD*</a>')
        
        moviesContent = moviesContent.replace('</a><b><span class="Apple-style-span" style="color: blue; font-size: xx-small;">Telugu</span></b>', ' (Telugu)</a>')
        moviesContent = moviesContent.replace('</a><b><span class="Apple-style-span" style="color: blue; font-size: xx-small;">Tamil</span></b>', ' (Tamil)</a>')
        moviesContent = moviesContent.replace('</a><a href="http://www.sominaltvtheater.com/2011/05/laaga-chunari-mein-daag-2007-dvd.html">', '')
        moviesContent = moviesContent.replace('></a>', '>SKIP ME</a>')
        movies = re.compile('<a href="(.+?)">(.+?)</a>').findall(moviesContent)
        i = 0
        
        for movieLink, movieTitle in movies:
                if movieTitle == 'SKIP ME':
                        continue
                if re.search('Hindi, Telugu, & Tamil', unescape(movieTitle)) or re.search('<b>\(Click Here\)</b>', unescape(movieTitle)):
                        continue
                if movieTitle == '*HD*' or movieTitle == '(Click Here)':
                        continue
                i = i + 1
                #print str(i) + ': ' + movieTitle + ' LINK = ' + movieLink.replace('" target="_blank','')
                addDirAndLoadImg(unescape(movieTitle), movieLink.replace('" target="_blank', ''), mode)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='movies')



def MOVIE_VIDEO_PARTS(url, name):
        
        if re.search('http://www.youtube.com/', url):
                url = url.replace('?&amp;', '?').replace('?f&amp;', '?').replace('?f&', '?').replace('?&', '?') + '&'
                playlistID = re.compile('http://www.youtube.com/view_play_list\?p=(.+?)&').findall(url)[0]
                print ' ALREADY GOT DIRECT URL retreiveYouTubePlayList ' + playlistID
                retreiveYouTubePlayList(playlistID, '', name, 'Part')
                return
        print url
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        link = ''.join(link.splitlines()).replace('\t', '').replace('\'', '"').replace('<b><b>', '<b>').replace('</b></b>', '</b>').replace(' font-weight: normal;', '')
        imgUrl = ''
        videoContentLink = re.compile('<div class="cover"><div class="entry">(.+?)<div style="clear:both;"></div><div class="clear"></div>').findall(link)
        try:
                imgUrl = re.compile('src="(.+?)"').findall(videoContentLink[0])[0]
                print imgUrl
        except: pass
        videoLinkSources = re.compile('<a href="(.+?)">(.+?)</a>').findall(videoContentLink[0])
        
        moreVideoLinks = re.compile('<iframe(.+?)src="(.+?)"(.+?)>').findall(videoContentLink[0])
        for temp1, videoLink, temp2 in moreVideoLinks:
                videoLinkSources.append([videoLink, 'Full Movie'])
        
        moreVideoLinks = re.compile('<param name="movie" value="(.+?)">').findall(videoContentLink[0])
        for videoLink in moreVideoLinks:
                videoLinkSources.append([videoLink, 'Full Movie'])
        
        
        sourcePart = 1
        for videoLink, videoName in videoLinkSources:
                videoName = videoName.replace('(Click Here)', '')
                if re.search('<img', videoName) or videoLink == 'http://www.youtube.com/user/SominalTvTheaters' or re.search('Click Here', videoName):
                        print "SKIP IMG or unwanted URL"
                        continue
                if re.search('DOWNLOAD', videoName):
                        videoName = 'Full Movie '
                videoLink = videoLink.replace('" target="_blank', '')
                sourceName = videoName + ' :: SOURCE# ' + str(sourcePart)
                sourcePart = sourcePart + 1
                if re.search('http://adf\.ly/', videoLink):
                        videoLink = videoLink + '&AJ;'
                        videoLink = re.compile('http://adf.ly/(.+?)/(.+?)&AJ;').findall(videoLink)[0][1]
                if not re.search('http://', videoLink):
                        videoLink = 'http://' + videoLink
                if re.search('http://sominaltvmovies', videoLink):
                        req = urllib2.Request(videoLink)
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                        response = urllib2.urlopen(req)
                        link = response.read()
                        response.close()
                        link = ''.join(link.splitlines()).replace('\t', '').replace('\'', '"')
                        videoContent = re.compile('<div class="post-body entry-content">(.+?)<div style="clear: both;"></div>').findall(link)
                        if(len(videoContent) == 1):
                        		videoParts = re.compile('src="(.+?)"').findall(videoContent[0])
                        		
                        		if(len(videoParts) > 1):
                        		        i = 1
                        		        playList = ''
                        		        matchCount = len(videoParts)
                        		        for videoPartLink in videoParts:
                        		                addPlayableMovieLink(sourceName + ' - Part: ' + str(i), unescape(videoPartLink), 31, imgUrl)
                        		                playList = playList + unescape(videoPartLink)
                        		                if(i < matchCount):
                        		                        playList = playList + ':;'
                        		                i = i + 1
                        		        if(i > matchCount and matchCount > 0):
                        		                addPlayListLink('[B]Direct PLAY - ' + sourceName + '[/B] [I]Playlist of above ' + str(matchCount) + ' videos[/I]', playList, 32, imgUrl)
                        						
                        		elif(len(videoParts) == 1):
                        		        videoPartLink = videoParts[0]
                        		        if re.search('http://www.dailymotion.com/widget/jukebox', videoPartLink):
                        		                matching = re.compile('\%2Fplaylist\%2F(.+?)&').findall(videoPartLink)
                        		                if len(matching) == 0:
                        		                        continue
                        		                playlistID = matching[0]
                        		                print 'retreiveDailyMotionPlayList ' + playlistID
                        		                retreiveDailyMotionPlayList(playlistID, imgUrl, sourceName, 'Part')
                        		                
                        		        elif re.search('http://www.youtube.com/p/', videoPartLink):
                        		                matching = re.compile('http://www.youtube.com/p/(.+?)\?').findall(videoPartLink)
                        		                if len(matching) == 0:
                        		                        continue
                        		                playlistID = matching[0]
                        		                print 'retreiveYouTubePlayList ' + playlistID
                        		                retreiveYouTubePlayList(playlistID, imgUrl, sourceName, 'Part')
                        		                
                        		        else:
                        		                addPlayableMovieLink('[B]SINGLE LINK [/B]' + sourceName, unescape(videoPartLink), 31, imgUrl)
                else:
                        if re.search('http://www.dailymotion.com/widget/jukebox', videoLink):
                                
                                matching = re.compile('\%2Fplaylist\%2F(.+?)&').findall(videoLink)
                                if len(matching) == 0:
                                        continue
                                playlistID = matching[0]
                                print 'retreiveDailyMotionPlayList ' + playlistID
                                retreiveDailyMotionPlayList(playlistID, imgUrl, sourceName, 'Part')
                        		                
                        elif re.search('http://www.dailymotion.com/playlist/', videoLink):
                                videoLink = videoLink + '&AJ;'
                                matching = re.compile('http://www.dailymotion.com/playlist/(.+?)&').findall(videoLink)
                                if len(matching) == 0:
                                        continue
                                playlistID = matching[0]
                                print 'retreiveDailyMotionPlayList ' + playlistID
                                retreiveDailyMotionPlayList(playlistID, imgUrl, sourceName, 'Part')
                        		                
                        elif re.search('http://www.youtube.com/p/', videoLink):
                                matching = re.compile('http://www.youtube.com/p/(.+?)\?').findall(videoLink)
                                if len(matching) == 0:
                                        continue
                                playlistID = matching[0]
                                print 'retreiveYouTubePlayList ' + playlistID
                                retreiveYouTubePlayList(playlistID, imgUrl, sourceName, 'Part')
                        
                        elif re.search('http://www.youtube.com/view_play_list', videoLink):
                                videoLink = videoLink + '&'
                                matching = re.compile('http://www.youtube.com/view_play_list\?p=(.+?)&').findall(videoLink)
                                if len(matching) == 0:
                                        continue
                                playlistID = matching[0]
                                print 'retreiveYouTubePlayList ' + playlistID
                                retreiveYouTubePlayList(playlistID, imgUrl, sourceName, 'Part')
                        
                        else:
                                addPlayableMovieLink('[B]SINGLE LINK [/B]' + sourceName, unescape(videoLink), 31, imgUrl)
                
            
                        		
#YOUTUBE        
def getVideoTitle(video):
        return getText(video.getElementsByTagName("title")[0].childNodes)
        
def getVideoID(video):
        return getText(video.getElementsByTagName("yt:videoid")[0].childNodes)
                
def getText(nodelist):
        rc = []
        for node in nodelist:
                if node.nodeType == node.TEXT_NODE:
                        rc.append(node.data)
        return ''.join(rc)


#VIMEO
def vimeo_getReqSignature(video):
        return getText(video.getElementsByTagName("request_signature")[0].childNodes)

def vimeo_getVidThumb(video):
        return getText(video.getElementsByTagName("thumbnail")[0].childNodes)
        
def vimeo_getQuality(video):
        quality = 'sd'
        try:
                if(getText(video.getElementsByTagName("isHD")[0].childNodes) == '1'):
                        quality = 'hd'
        except: pass
        return quality
        
def vimeo_getReqSignatureExpires(video):
        return getText(video.getElementsByTagName("request_signature_expires")[0].childNodes)
       
       
def vimeo_getVideoUrl(videoId, reqSig, reqSigExp, qual):
        video_url = "http://player.vimeo.com/play_redirect?clip_id=%s&sig=%s&time=%s&quality=%s&codecs=H264,VP8,VP6&type=moogaloop_local&embed_location=" % (videoId, reqSig, reqSigExp, qual)
        req = urllib2.Request(video_url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        video_url = response.geturl()
        response.close()
        return video_url      

def MOVIE_PLAYLIST_VIDEOLINKS(url, name):
        #xbmc.executebuiltin("XBMC.Notification(PLease Wait!,Loading video links into XBMC Media Player,5000)")
        ok = True
        playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playList.clear()
        #time.sleep(2)
        links = url.split(':;')
        
        pDialog = xbmcgui.DialogProgress()
        ret = pDialog.create('Loading playlist...')
        totalLinks = len(links)
        loadedLinks = 0
        remaining_display = 'Videos loaded :: [B]' + str(loadedLinks) + ' / ' + str(totalLinks) + '[/B] into XBMC player playlist.'
        pDialog.update(0, 'Please wait for the process to retrieve video link.', remaining_display)
                
        for videoLink in links:
                Movie_loadVideos(videoLink, name, True, True)
                
                loadedLinks = loadedLinks + 1
                percent = (loadedLinks * 100) / totalLinks
                #print percent
                remaining_display = 'Videos loaded :: [B]' + str(loadedLinks) + ' / ' + str(totalLinks) + '[/B] into XBMC player playlist.'
                pDialog.update(percent, 'Please wait for the process to retrieve video link.', remaining_display)
                if (pDialog.iscanceled()):
                        return False
        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play(playList)
        if not xbmcPlayer.isPlayingVideo():
                d = xbmcgui.Dialog()
                d.ok('INVALID VIDEO PLAYLIST', 'The playlist videos were removed due to copyright issue.', 'Check other links.')
        return ok


def MOVIE_LOAD_AND_PLAY_VIDEO(url, name):
        ok = True
        print url
        xbmc.executebuiltin("XBMC.Notification(PLease Wait!,Loading video link into XBMC Media Player,5000)")
        videoUrl = Movie_loadVideos(url, name, True, False)
        if videoUrl == None:
                d = xbmcgui.Dialog()
                d.ok('NO VIDEO FOUND', 'This video was removed due to copyright issue.', 'Check other links.')
                return False
        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play(videoUrl)
        return ok


def MOVIE_VIDEOLINKS(url, name):
        Movie_loadVideos(url, name, False, False)


def Movie_loadVideos(url, name, isRequestForURL, isRequestForPlaylist):
        url = url + '&AJ;'
        print 'VIDEO URL = ' + url
        
        #YOUTUBE
        try:
                match = re.compile('http://www.youtube.com/v/(.+?)&').findall(url)
                code = match[0]
                
                linkImage = 'http://i.ytimg.com/vi/' + code + '/default.jpg'
                req = urllib2.Request('http://www.youtube.com/watch?v=' + code + '&fmt=18')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                if len(re.compile('shortlink" href="http://youtu.be/(.+?)"').findall(link)) == 0:
                        if len(re.compile('\'VIDEO_ID\': "(.+?)"').findall(link)) == 0:
                                req = urllib2.Request('http://www.youtube.com/get_video_info?video_id=' + code + '&asv=3&el=detailpage&hl=en_US')
                                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                                response = urllib2.urlopen(req)
                                link = response.read()
                                response.close()
                map = None
                link = link.replace('\\u0026', '&')
                match = re.compile('url_encoded_fmt_stream_map=(.+?)&').findall(link)
                if len(match) == 0:
                        map = (re.compile('url_encoded_fmt_stream_map": "(.+?)"').findall(link)[0]).replace('\\/', '/').split('url=')
                else:
                        map = urllib.unquote(match[0]).decode('utf8').split('url=')
                if re.search('status=fail', link):
                        return
                if map == None:
                        return
                #print map
                highResoVid = ''
                youtubeVideoQual = fbn.getSetting('videoQual')
                for attr in map:
                        if attr == '':
                                continue
                        parts = attr.split('&qual')
                        url = urllib.unquote(parts[0]).decode('utf8')
                        print url
                        qual = re.compile('&itag=(\d*)').findall(url)[0]
                        print qual
                        if(qual == '13'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY 3GP Low Quality - 176x144', url, linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        if(qual == '17'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY 3GP Medium Quality - 176x144', url, linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        if(qual == '36'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY 3GP High Quality - 320x240', url, linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        if(qual == '5'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY FLV Low Quality - 400\\327226', url, linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        if(qual == '34'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY FLV Medium Quality - 480x360', url, linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        if(qual == '6'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY FLV Medium Quality - 640\\327360', url, linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        if(qual == '35'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY FLV High Quality - 854\\327480', url, linkImage)
                                else:
                                        highResoVid = url
                        if(qual == '18'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY MP4 High Quality - 480x360', url, linkImage)
                                else:
                                        highResoVid = url
                                        
                        if(qual == '22'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY MP4 High Quality - 1280x720', url, linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '1' or youtubeVideoQual == '2':
                                                break
                        if(qual == '37'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY MP4 High-2 Quality - 1920x1080', url, linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '2':
                                                break
                        if(qual == '38'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY MP4 Epic Quality - 4096\\3272304', url, linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '2':
                                                break
                        if(qual == '43'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY WEBM Medium Quality - 4096\\3272304', url, linkImage)
                                else:
                                        highResoVid = url
                        if(qual == '44'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY WEBM High Quality - 4096\\3272304', url, linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '1' or youtubeVideoQual == '2':
                                                break
                        if(qual == '45'):
                                if(not(isRequestForURL)):
                                        addLink ('PLAY WEBM High-2 Quality - 4096\\3272304', url, linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '2':
                                                break
                print highResoVid
                if(isRequestForURL):
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem('VIDEO PART', thumbnailImage=linkImage)
                                xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(url=highResoVid, listitem=liz)
                                return highResoVid
                        else:
                                return highResoVid

        except: pass
        
        #DAILYMOTION
        try:
                match = re.compile('http://www.dailymotion.com/(.+?)&').findall(url)
                if(len(match) > 0):
                        newUrl = url.replace('?', '&')
                        match = re.compile('video/(.+?)&').findall(newUrl)
                        if len(match) == 0:
                                match = re.compile('swf/(.+?)&').findall(newUrl)
                                print match
                link = 'http://www.dailymotion.com/video/' + str(match[0])
                print link
                req = urllib2.Request(link)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                sequence = re.compile('"sequence":"(.+?)"').findall(link)
                newseqeunce = urllib.unquote(sequence[0]).decode('utf8').replace('\\/', '/')
                imgSrc = re.compile('og:image" content="(.+?)"').findall(link)
                if(len(imgSrc) == 0):
                	imgSrc = re.compile('/jpeg" href="(.+?)"').findall(link)
                dm_low = re.compile('"sdURL":"(.+?)"').findall(newseqeunce)
                dm_high = re.compile('"hqURL":"(.+?)"').findall(newseqeunce)
                if(isRequestForURL):
                        videoUrl = ''
                        if(len(dm_high) == 0):
                                videoUrl = dm_low[0]
                        else:
                                videoUrl = dm_high[0]
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem('EPISODE', thumbnailImage=imgSrc[0])
                                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                                playlist.add(url=videoUrl, listitem=liz)
                                return videoUrl
                        else:
                                return videoUrl
                                
                else:
                        if(len(dm_low) > 0):
                                addLink ('PLAY Standard Quality ', dm_low[0], imgSrc[0])
                        if(len(dm_high) > 0):
                                addLink ('PLAY High Quality ', dm_high[0], imgSrc[0])
        except: pass
        
        
        #VIMEO
        try:
                if not re.search('vimeo.com', url):
                        raise
                id = re.compile('clip_id=(.+?)&').findall(url)
                videoID = str(id[0])
                link = 'http://www.vimeo.com/moogaloop/load/clip:' + videoID
                req = urllib2.Request(link)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                domObj = parseString(link)
                rs = vimeo_getReqSignature(domObj)
                rse = vimeo_getReqSignatureExpires(domObj)
                qual = vimeo_getQuality(domObj)
                videoUrl = vimeo_getVideoUrl(videoID, rs, rse, qual)
                
                print videoUrl
                imgUrl = vimeo_getVidThumb(domObj)
                print imgUrl
                
                if(isRequestForURL):
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem('EPISODE', thumbnailImage=imgUrl)
                                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                                playlist.add(url=videoUrl, listitem=liz)
                                return videoUrl
                        else:
                                return videoUrl
                                
                else:
                        addLink ('[B]PLAY VIDEO[/B]: ' + name, videoUrl, imgUrl)
        except: pass
        
        #HOSTING CUP
        try:
                id = re.compile('http://www.hostingcup.com/(.+?)&AJ;').findall(url)[0]
                hostingUrl = 'http://www.hostingcup.com/' + id
                req = urllib2.Request(hostingUrl)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                webLink = ''.join(link.splitlines()).replace('\t', '')
                #Trying to find out easy way out :)
                paramSet = re.compile("return p\}\(\'(.+?)\',36,(.+?),\'(.+?)\'").findall(webLink)
                
                result = parseValue(paramSet[0][0], 36, int(paramSet[0][1]), paramSet[0][2].split('|'))
                result = result.replace('\\', '').replace('"', '\'')
                print result

                imgUrl = re.compile("s1.addVariable\(\'image\',\'(.+?)\'\);").findall(result)[0]
                videoUrl = re.compile("s1.addVariable\(\'file\',\'(.+?)\'\);").findall(result)[0]
                
                print 'HOSTING CUP url = ' + videoUrl
                if(isRequestForURL):
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem(name, thumbnailImage=imgUrl)
                                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                                playlist.add(url=videoUrl, listitem=liz)
                                return videoUrl
                        else:
                                return videoUrl
                else:
                        addLink ('[B]PLAY VIDEO[/B]: ' + name, videoUrl, imgUrl)
        except: pass

        #HOSTING BULK
        try:
                id = re.compile('http://hostingbulk.com/(.+?)&AJ;').findall(url)[0]
                if re.search('embed', id):
                        id = re.compile('embed\-(.+?)\-').findall(id)[0] + '.html'
                hostingUrl = 'http://hostingbulk.com/' + id
                req = urllib2.Request(hostingUrl)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                webLink = ''.join(link.splitlines()).replace('\t', '')
                #Trying to find out easy way out :)
                paramSet = re.compile("return p\}\(\'(.+?)\',36,(.+?),\'(.+?)\'").findall(webLink)
                
                result = parseValue(paramSet[0][0], 36, int(paramSet[0][1]), paramSet[0][2].split('|'))
                result = result.replace('\\', '').replace('"', '\'')
                print result

                imgUrl = re.compile("s1.addVariable\(\'image\',\'(.+?)\'\);").findall(result)[0]
                videoUrl = re.compile("s1.addVariable\(\'file\',\'(.+?)\'\);").findall(result)[0]
                
                print 'HOSTING BULK url = ' + videoUrl
                if(isRequestForURL):
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem(name, thumbnailImage=imgUrl)
                                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                                playlist.add(url=videoUrl, listitem=liz)
                                return videoUrl
                        else:
                                return videoUrl
                else:
                        addLink ('[B]PLAY VIDEO[/B]: ' + name, videoUrl, imgUrl)
        except: pass
        
        #NOVAMOV
        try:
                p = re.compile('http://www.novamov.com/video/(.+?)&AJ;')
                match = p.findall(url)
                link = 'http://www.novamov.com/video/' + match[0]
                req = urllib2.Request(link)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                link = ''.join(link.splitlines()).replace('\'', '"')
                match = re.compile('flashvars.file="(.+?)";').findall(link)
                imgUrl = ''
                videoUrl = match[0]
                videoTitle = name
                if(isRequestForURL):
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem(videoTitle, thumbnailImage=imgUrl)
                                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                                playlist.add(url=videoUrl, listitem=liz)
                                return videoUrl
                        else:
                                return videoUrl
                else:
                        addLink ('[B]PLAY VIDEO[/B]: ' + videoTitle, videoUrl, imgUrl)
        except: pass
        
        
        #MOVSHARE
        try:
                match = re.compile('http://www.movshare.net/video/(.+?)&AJ;').findall(url)
                if(len(match) == 0):
                        match = re.compile('http://www.movshare.net/embed/(.+?)/').findall(url)
                movUrl = 'http://www.movshare.net/video/' + match[0]
                req = urllib2.Request(movUrl)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                link = ''.join(link.splitlines()).replace('\t', '').replace('\'', '"')
                if re.search('Video hosting is expensive. We need you to prove you"re human.', link):
                        values = {'wm': '1'}
                        headers = { 'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3' }
                        data = urllib.urlencode(values)
                        req = urllib2.Request(movUrl, data, headers)
                        response = urllib2.urlopen(req)
                        link = response.read()
                        response.close()
                        link = ''.join(link.splitlines()).replace('\t', '').replace('\'', '"')
                
                match = re.compile('<param name="src" value="(.+?)" />').findall(link)
                if(len(match) == 0):
                        match = re.compile('flashvars.file="(.+?)"').findall(link)
                imgUrl = ''
                videoUrl = match[0]
                videoTitle = name
                if(isRequestForURL):
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem(videoTitle, thumbnailImage=imgUrl)
                                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                                playlist.add(url=videoUrl, listitem=liz)
                                return videoUrl
                        else:
                                return videoUrl
                else:
                        addLink ('[B]PLAY VIDEO[/B]: ' + videoTitle, videoUrl, imgUrl)
        except: pass


        #MEGAVIDEO
        try:
                if not re.search('megavideo.com', url):
                        raise
                id = re.compile('http://www.megavideo.com/v/(.+?)&').findall(url)
                if len(id) > 0:
                        url = get_redirected_url('http://www.megavideo.com/v/' + id[0], None) + '&AJ;'
                id = re.compile('v=(.+?)&').findall(url)
                video_id = id[0]
                req = urllib2.Request('http://www.megavideo.com/xml/videolink.php?v=' + video_id)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                link = ''.join(link.splitlines()).replace('\t', '').replace('\'', '"')
        
                un = re.compile(' un="(.+?)"').findall(link)
                k1 = re.compile(' k1="(.+?)"').findall(link)
                k2 = re.compile(' k2="(.+?)"').findall(link)
                hashresult = decrypt(un[0], k1[0], k2[0])
                
                s = re.compile(' s="(.+?)"').findall(link)
                
                title = re.compile(' title="(.+?)"').findall(link)
                videoTitle = urllib.unquote_plus(title[0].replace('+', ' ').replace('.', ' '))
                
                imgUrl = ''
                videoUrl = "http://www" + s[0] + ".megavideo.com/files/" + hashresult + "/" + videoTitle.replace('www.apnajoy.com', '') + ".flv";
                print 'MEGA VIDEO url = ' + videoUrl
                if(isRequestForURL): 
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem(videoTitle, thumbnailImage=imgUrl)
                                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                                playlist.add(url=videoUrl, listitem=liz)
                                return videoUrl
                        else:
                                return videoUrl
                else:
                        addLink ('[B]PLAY VIDEO[/B]: ' + videoTitle, videoUrl, imgUrl)
        except: pass


        #VIDEOBB
        try:
                p = re.compile('videobb.com/e/(.+?)&AJ;')
                video_id = p.findall(url)[0]
                
                video_info_link = 'http://www.videobb.com/player_control/settings.php?v=' + video_id + '&fv=v1.2.72'
                jsonObj = json.load(urllib.urlopen(video_info_link))
                        
                key1 = jsonObj["settings"]["config"]["rkts"]
                key2 = jsonObj["settings"]["login_status"]["pepper"]
                key3 = jsonObj["settings"]["banner"]["lightbox2"]["time"]
                
                values = binascii.unhexlify(videobb_decrypt(jsonObj["settings"]["login_status"]["spen"], jsonObj["settings"]["login_status"]["salt"], 950569)).split(';')
                print values
                spn = getUrlParams(values[0])
                outk = getUrlParams(values[1])
                ikey = videobb_getikey(int(outk["ik"]))
                
                urlKey = ''
                for spnkey in spn:
                        spnval = spn[spnkey]
                        if spnval == '1':
                                cypher = jsonObj["settings"]["video_details"]["sece2"]
                                urlKey = urlKey + spnkey + '=' + videobb_decrypt(cypher, key1, ikey, ln=256) + '&'
                        if spnval == '2':
                                cypher = jsonObj["settings"]["banner"]["g_ads"]["url"]
                                urlKey = urlKey + spnkey + '=' + videobb_decrypt(cypher, key1, ikey) + '&'
                        if spnval == '3':
                                cypher = jsonObj["settings"]["banner"]["g_ads"]["type"]
                                urlKey = urlKey + spnkey + '=' + videobb_decrypt(cypher, key1, ikey, 26, 25431, 56989, 93, 32589, 784152) + '&'
                        if spnval == '4':
                                cypher = jsonObj["settings"]["banner"]["g_ads"]["time"]
                                urlKey = urlKey + spnkey + '=' + videobb_decrypt(cypher, key1, ikey, 82, 84669, 48779, 32, 65598, 115498) + '&'
                        if spnval == '5':
                                cypher = jsonObj["settings"]["login_status"]["euno"]
                                urlKey = urlKey + spnkey + '=' + videobb_decrypt(cypher, key2, ikey, 10, 12254, 95369, 39, 21544, 545555) + '&'
                        if spnval == '6':
                                cypher = jsonObj["settings"]["login_status"]["sugar"]
                                urlKey = urlKey + spnkey + '=' + videobb_decrypt(cypher, key3, ikey, 22, 66595, 17447, 52, 66852, 400595) + '&'
                    
                urlKey = urlKey + "start=0"
                
                video_link = ""
                for videoStrm in jsonObj["settings"]["res"]:
                        if videoStrm["d"]:
                                video_link = str(base64.b64decode(videoStrm["u"]))
                if video_link == "":
                        raise Exception("VIDEO_STOPPED")
                video_link = video_link + '&' + urlKey
                
                imgUrl = str(jsonObj["settings"]["config"]["thumbnail"])
                videoUrl = video_link
                videoTitle = jsonObj["settings"]["video_details"]["video"]["title"]
                if(isRequestForURL):
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem(videoTitle, thumbnailImage=imgUrl)
                                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                                playlist.add(url=videoUrl, listitem=liz)
                                return videoUrl
                        else:
                                return videoUrl
                else:
                        addLink ('[B]PLAY VIDEO[/B]: ' + videoTitle, videoUrl, imgUrl)
        except:
                pass
        


        #VEEVR
        try:
                p = re.compile('veevr.com/embed/(.+?)&AJ;')
                match = p.findall(url)
                referer = 'http://veevr.com/embed/' + match[0]
                
                req = urllib2.Request('http://menial.veevr.com/count.js')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                req.add_header('Referer', referer)
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                keyStr = re.compile('var keyStr = "(.+?)"').findall(link)[0]
                input = re.compile('eval\(decode64\(\'(.+?)\'\)\)').findall(link)[0]
                
                output = ''
                i = 0
                #input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "")
                input = re.sub('[^A-Za-z0-9\+\/\=]', "", input)
                while (i < len(input)) :
                        enc1 = string.find(keyStr, input[i])
                        i = i + 1
                        enc2 = string.find(keyStr, input[i])
                        i = i + 1
                        enc3 = string.find(keyStr, input[i])
                        i = i + 1
                        enc4 = string.find(keyStr, input[i])
                        i = i + 1
                        chr1 = (enc1 << 2) | (enc2 >> 4)
                        chr2 = ((enc2 & 15) << 4) | (enc3 >> 2)
                        chr3 = ((enc3 & 3) << 6) | enc4
                        output = output + unichr(chr1)
                        if (enc3 != 64) :
                                output = output + unichr(chr2)
                        if (enc4 != 64) :
                                output = output + unichr(chr3)
                output = output.replace('\'', '"')
                #print output
                videoInfoUrl = re.compile('clip:{(.+?),url:"(.+?)"').findall(output)[0][1].replace('%3F', '?').replace('%26', '&')
                req = urllib2.Request(videoInfoUrl)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                domObj = parseString(link)
                #print domObj.toprettyxml()
                videoUrl = domObj.getElementsByTagName("meta")[0].getAttribute('base') + ' playpath=' + domObj.getElementsByTagName("video")[0].getAttribute('src')
                imgUrl = ''
                videoTitle = name
                if(isRequestForURL):
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem(videoTitle, thumbnailImage=imgUrl)
                                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                                playlist.add(url=videoUrl, listitem=liz)
                                return videoUrl
                        else:
                                return videoUrl
                else:
                        addLink ('[B]PLAY VIDEO[/B]: ' + videoTitle, videoUrl, imgUrl)
        except: pass
        
        #VEOH
        try:
                if not re.search('veoh.com', url):
                        raise
                id = re.compile('permalinkId=v(.+?)&').findall(url)
                if len(id) == 0:
                        id = re.compile('http://www.veoh.com/v(.+?)&').findall(url)
                
                url = 'http://www.veoh.com/rest/v2/execute.xml?method=veoh.video.findByPermalink&permalink=v' + id[0] + '&apiKey=E97FCECD-875D-D5EB-035C-8EF241F184E2'
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                domObj = parseString(link)
                #print domObj.toprettyxml()
                if len(domObj.getElementsByTagName("error")) > 0:
                        print domObj.getElementsByTagName("error")[0].getAttribute('errorMessage')
                        return
                videoUrl = get_redirected_url(domObj.getElementsByTagName("video")[0].getAttribute('ipodUrl'), None)
                imgUrl = domObj.getElementsByTagName("video")[0].getAttribute('fullHighResImagePath')
                videoTitle = name
                if(isRequestForURL):
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem(videoTitle, thumbnailImage=imgUrl)
                                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                                playlist.add(url=videoUrl, listitem=liz)
                                return videoUrl
                        else:
                                return videoUrl
                else:
                        addLink ('[B]PLAY VIDEO[/B]: ' + videoTitle, videoUrl, imgUrl)
        except: pass
        
        

#MUSIC

def MUSIC_MENU(url, name):
        addDir('Good [B]MUSIC[/B] Collection', 'http://www.sominaltvtheater.com/2010/11/music-videos.html', 41, os.path.join(xbmc.translatePath(artPath), "More_Music_V1.png"))
        addDir('[B]HINDI[/B] MUSIC VIDEOS', 'hindi', 43, os.path.join(xbmc.translatePath(artPath), "Hindi_Music_V1.png"))
        addDir('[B]TELUGU[/B] MUSIC VIDEOS', 'telugu', 43, os.path.join(xbmc.translatePath(artPath), "Telugu_Music_V1.png"))
        addDir('[B]TAMIL[/B] MUSIC VIDEOS', 'tamil', 43, os.path.join(xbmc.translatePath(artPath), "Tamil_Music_V1.png"))
        addDir('[B]MALAYALAM[/B] MUSIC VIDEOS', 'malayalam', 43, os.path.join(xbmc.translatePath(artPath), "Malayalam_Music_V1.png"))
        addDir('[B]KANNADA[/B] MUSIC VIDEOS', 'kannada', 43, os.path.join(xbmc.translatePath(artPath), "Kannada_Music_V1.png"))

def MUSIC_VIDEOS(url, name):
        MoviesList(url, 42)

def MUSIC_VIDEO_PARTS(url, name):
        if re.search('http://www.youtube.com/', url):
                url = url.replace('?&amp;', '?').replace('?f&amp;', '?').replace('?f&', '?').replace('?&', '?') + '&'
                playlistID = re.compile('http://www.youtube.com/view_play_list\?p=(.+?)&').findall(url)[0]
                print ' ALREADY GOT DIRECT URL retreiveYouTubePlayList ' + playlistID
                retreiveYouTubePlayList(playlistID, '', name, 'Song')
                return
        
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        link = ''.join(link.splitlines()).replace('\t', '').replace('\'', '"').replace('<b><b>', '<b>').replace('</b></b>', '</b>').replace(' font-weight: normal;', '')
        imgUrl = ''
        videoContentLink = re.compile('<div class="cover"><div class="entry">(.+?)<div style="clear:both;"></div><div class="clear"></div>').findall(link)
        try:
                imgUrl = re.compile('src="(.+?)"').findall(videoContentLink[0])[0]
                print imgUrl
        except: pass
        
        if re.search('http://www.youtube.com/', videoContentLink[0]):
                urlContent = videoContentLink[0].replace('?&amp;', '?').replace('?f&amp;', '?').replace('?f&', '?').replace('?&', '?')
                playlistIDFound = re.compile('http://www.youtube.com/view_play_list\?p=(.+?)"').findall(urlContent)
                if len(playlistIDFound) == 0:
                        playlistIDFound = re.compile('http://www.youtube.com/playlist\?p=(.+?)"').findall(urlContent)
                
                if len(playlistIDFound) == 0:
                        playlistID = re.compile('http://www.youtube.com/user/(.+?)grid/user/(.+?)"').findall(urlContent)[0][1]
                else:
                        playlistID = playlistIDFound[0]
                if playlistID[0:2] == 'PL':
                        playlistID = playlistID[2:len(playlistID)]
                retreiveYouTubePlayList(playlistID, imgUrl, name, 'Song')
                

def BM_MUSIC_BY_LANG(lang, name):
        url = 'http://www.bharatmovies.com/' + lang + '/songs/' + lang + '-video-songs.htm'
        if lang == 'hindi':
                url = 'http://www.bharatmovies.com/' + lang + '/songs/bollywood-video-songs.htm'
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        link = ''.join(link.splitlines()).replace('\t', '').replace('ilactive', 'ila')
        index = re.compile('<a id=ila href=(.+?)>(.+?)</a>').findall(link)
        indexCount = len(index)
        if indexCount > 0:
                indexURL = ''
                i = 0
                for indexLink, indexChar in index:
                        print indexChar + ' <--> ' + indexLink
                        indexURL = indexURL + indexChar + '<-->' + 'http://www.bharatmovies.com/' + lang + '/songs/' + indexLink
                        i = i + 1
                        if i < indexCount:
                                indexURL = indexURL + '&AJ;'
                
                if re.search('Movie Index By Release Year', link):
                        addDir('A-Z DIRECTORIES', indexURL, 26, os.path.join(xbmc.translatePath(artPath), "AZ_Dir_V1.png"))
                        addDir('Browse by RELEASE DECADES', lang, 27, os.path.join(xbmc.translatePath(artPath), "Release_Decades_V1.png"))
                else:
                        BM_MUSIC_A_Z_DIR(indexURL, 'A-Z DIRECTORIES')
                                        
        else:
                xbmc.executebuiltin("XBMC.Notification(PLease Wait!,Loading ALL MOVIE MUSIC in this category,5000)")
                BM_LIST(url, name)


def BM_MUSIC_A_Z_DIR(indexMap, name):
        indexEntries = indexMap.split('&AJ;')
        indexNameList = []
        indexUrlList = []
        for indexEntry in indexEntries:
                index = indexEntry.split('<-->')
                #imgUrl = os.path.join(xbmc.translatePath( artPath ), "alpha/blue-"+index[0]+".png")
                #if index[0] == '#':
                #        imgUrl = os.path.join(xbmc.translatePath( artPath ), "alpha/blue-hash.png")
                indexNameList.append(index[0])
                indexUrlList.append(index[1])
                #addDir(index[0], index[1], 28, imgUrl)
        d = xbmcgui.Dialog()
        indexSelect = d.select('A-Z Directories:', indexNameList)
        if indexSelect == -1:
                indexSelect = 0
        url = indexUrlList[indexSelect]
        name = indexNameList[indexSelect]
        BM_LIST(url, name)

def getUrlParams(url):
    params = {}
    if url is None:
        return params
    paramstring = url
    if len(paramstring) >= 2:
        paramstring = paramstring.replace('?', '')
        if (paramstring[len(paramstring) - 1] == '/'):
            paramstring = paramstring[0:len(paramstring) - 2]
        pairsofparams = paramstring.split('&')
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                params[splitparams[0]] = urllib.unquote_plus(splitparams[1])
    return params

#Videobb
def videobb_getikey(i):
    if i == 1:
        return 226593
    elif i == 2:
        return 441252
    elif i == 3:
        return 301517
    elif i == 4:
        return 596338
    elif i == 5:
        return 852084
    else:
        return -1


def videobb_hex2bin(hexStr):
    binaryStr = ''
    for c in hexStr:
        binaryStr = binaryStr + bin(int(c, 16))[2:].zfill(4)
    return binaryStr


def videobb_bin2hex(binStr):
    hexStr = ''
    for i in range(len(binStr) - 4, -1, -4):
        oneBinStr = binStr[i:i + 4]
        hexStr = hexStr + hex(int(oneBinStr.zfill(4), 2))[2:]
    hexStr = hexStr[::-1]
    return hexStr


def videobb_decrypt(cypher, key1, key2, keySetA_1=11, keySetA_2=77213, keySetA_3=81371, keySetB_1=17, keySetB_2=92717, keySetB_3=192811, ln=None):
    
    C = list(videobb_hex2bin(cypher))
    if ln is None:
        ln = len(C) * 2
    B = int(ln * 1.5) * [None]
    
    for i in range(0, int(ln * 1.5)):
        key1 = (key1 * keySetA_1 + keySetA_2) % keySetA_3
        key2 = (key2 * keySetB_1 + keySetB_2) % keySetB_3
        B[i] = (key1 + key2) % int(ln * 0.5)

    x = y = z = 0
    
    for i in range(ln, -1 , -1):
        x = B[i]
        y = i % int(ln * 0.5)
        z = C[x]
        C[x] = C[y]
        C[y] = z

    for i in range(0, int(ln * 0.5), 1):
        C[i] = str(int(C[i]) ^ int(B[i + ln]) & 1)

    binStr = ''.join(C)
    return videobb_bin2hex(binStr)


#YouTube
def YouTube_CHANNELS(url, name):
        addDir('Add-on CHANNELS', 'http://www.youtube.com/', 65, os.path.join(xbmc.translatePath(artPath), "Addon_YouTube_V1.png"))
        addDir('MY CHANNELS', 'http://www.youtube.com/', 66, os.path.join(xbmc.translatePath(artPath), "MY_YouTube_V1.png"))
        addDir('Add new CHANNEL', 'http://www.youtube.com/', 67, os.path.join(xbmc.translatePath(artPath), "Add_New_YouTube_V1.png"))


def YouTube_MY_CHANNELS(url, name):
        myChannelsFilePath = os.path.join(xbmc.translatePath(addonDataPath), "MyChannels.json")
        if not os.path.exists(myChannelsFilePath):
                d = xbmcgui.Dialog()
                if d.yesno('NO channels added yet!', 'Would you like to add YouTube channel right now?', 'Get username from YouTube URL.'):
                        isAdded = YouTube_ADD_NEW_CHANNEL(url, name)
                        if not isAdded:
                                return
        
        if os.path.exists(myChannelsFilePath):
                try:
                        fc = open(myChannelsFilePath, 'r')
                        myChannelsJsonObj = json.load(fc, encoding='utf-8')
                        fc.close()
                        print 'CHANNELS JSON LOADED'
                        if len(myChannelsJsonObj) == 0:
                                d = xbmcgui.Dialog()
                                if d.yesno('NO channels added yet!', 'Would you like to add YouTube channel right now?', 'Get username from YouTube URL.'):
                                        isAdded = YouTube_ADD_NEW_CHANNEL(url, name)
                                        if not isAdded:
                                                return
                                        else:
                                                fc = open(myChannelsFilePath, 'r')
                                                myChannelsJsonObj = json.load(fc, encoding='utf-8')
                                                fc.close()

                        for myChannelUsername in myChannelsJsonObj:
                                userInfo = myChannelsJsonObj[myChannelUsername]
                                addDirWith_YT_Options(str(userInfo['title']), myChannelUsername, 63, userInfo['thumbnail'])
                        
                except ValueError:
                        os.remove(myChannelsFilePath)
                        print 'MY CHANNELS CORRUPT FILE DELETED = ' + myChannelsFilePath
        

def YouTube_REMOVE_CHANNEL(url, name):
        d = xbmcgui.Dialog()
        if not d.yesno('Remove Channel : [B]' + name + '[/B]', 'Do you want to continue?', 'Note: This action will not delete channel from YouTube.'):
                return
        myChannelsFilePath = os.path.join(xbmc.translatePath(addonDataPath), "MyChannels.json")
        if os.path.exists(myChannelsFilePath):
                try:
                        fc = open(myChannelsFilePath, 'r')
                        myChannelsJsonObj = json.load(fc, encoding='utf-8')
                        fc.close()
                        print 'CHANNELS JSON LOADED'
                        try:
                                del myChannelsJsonObj[url]
                                print 'CHANNEL DELETED = ' + url
                                fc = open(myChannelsFilePath, 'w')
                                print json.dump(myChannelsJsonObj, fc, encoding='utf-8')
                                fc.close()
                                d = xbmcgui.Dialog()
                                d.ok('Channel removed SUCCESSFULLY', 'You can add this channel again using same way.', 'ENJOY!')
                                xbmc.executebuiltin("Container.Refresh()")
                        except KeyError:
                                d = xbmcgui.Dialog()
                                d.ok('FAILED to remove channel', 'Please try again.')
                        
                except ValueError:
                        os.remove(myChannelsFilePath)
                        print 'MY CHANNELS CORRUPT FILE DELETED = ' + myChannelsFilePath
        else:
                d = xbmcgui.Dialog()
                d.ok('NO channels added yet', 'Add new channel using YouTube username.', 'Get username from YouTube URL.')


def YouTube_ADD_NEW_CHANNEL(url, name):
        keyb = xbmc.Keyboard('', 'Enter [B]YouTube[/B] username')
        keyb.doModal()
        if (keyb.isConfirmed()):
                username = keyb.getText()
                if username == None or username == '':
                        d = xbmcgui.Dialog()
                        d.ok('Username not entered', 'Please enter the YouTube username correctly.', 'Get username from YouTube URL.')
                else:
                        try:
                                myChannelsJsonObj = {}
                                myChannelsFilePath = os.path.join(xbmc.translatePath(addonDataPath), "MyChannels.json")
                                
                                if os.path.exists(myChannelsFilePath):
                                        try:
                                                fc = open(myChannelsFilePath, 'r')
                                                myChannelsJsonObj = json.load(fc, encoding='utf-8')
                                                fc.close()
                                                print 'CHANNELS JSON LOADED'
                                        except ValueError:
                                                os.remove(myChannelsFilePath)
                                                print 'CORRUPT FILE DELETED = ' + myChannelsFilePath
                                                
                                try:
                                        if myChannelsJsonObj[username] != None:
                                                d = xbmcgui.Dialog()
                                                d.ok('Channel already exists', 'Please enter the YouTube username correctly.', 'Get username from YouTube URL.')
                                                return False
                                except KeyError:
                                        print 'Search for YouTube username now = ' + username
                                        
                                userInfo = retrieve_YT_UserInfo(username)
                                if userInfo != None:
                                        myChannelsJsonObj[username] = userInfo
                                        fc = open(myChannelsFilePath, 'w')
                                        print json.dump(myChannelsJsonObj, fc, encoding='utf-8')
                                        fc.close()
                                        d = xbmcgui.Dialog()
                                        d.ok('Channel added SUCCESSFULLY', 'Brouse MY CHANNELS link to check your channels.', 'ENJOY!')
                                        return True
                        except urllib2.HTTPError:
                                d = xbmcgui.Dialog()
                                d.ok('Username doesn\'t exist', 'Please enter the YouTube username correctly.', 'Get username from YouTube URL.')
        return False
        

def YouTube_AJ_CHANNELS(url, name):
        addDir('Sominal TV Theatres', 'SominalTvTheaters', 70, 'http://i4.ytimg.com/i/cbiwrUudPQG185pXpeeiDw/1.jpg')
        addDirWithLastPageNbr('Sominal TV TAMIL Theatre', 'TAMILatSominalTv', 61, 'http://i4.ytimg.com/i/OL2eHmE4JJZUfaZWNkpxOw/1.jpg', 0)
        addDirWithLastPageNbr('Sominal TV TELUGU Theatre', 'TeluguTvTheater&AJ;&JA;(\*Telugu Movies\*)', 61, 'http://i4.ytimg.com/i/OjgUGhSsdRA9Hv6TG7BTFg/1.jpg', 0)
        addDirWithLastPageNbr('Sominal TV HD Music', 'SominalTvHDMusic', 61, 'http://i4.ytimg.com/i/sooA3IS6T6JYIJv_8nxlhQ/1.jpg', 0)
        addDirWithLastPageNbr('Sominal TV Hindi Music', 'SominalTvHindiMusic&AJ;&JA;(\*BluRay\* Hindi Music Videos)', 61, 'http://i4.ytimg.com/i/OL2eHmE4JJZUfaZWNkpxOw/1.jpg', 0)
        addDirWithLastPageNbr('Sominal TV Hindi Movie Trailers', 'HindiTrailersTv', 63, '', 0)
        addDirWithLastPageNbr('Sominal TV Telugu Tamil Music', 'TeluguTamilMUSIC', 61, 'http://i4.ytimg.com/i/OjgUGhSsdRA9Hv6TG7BTFg/1.jpg', 0)
        addDirWithLastPageNbr('Kamal TV Main Channel', 'KamalTheaterTv', 63, 'http://i3.ytimg.com/i/jpCN34S9eiH3vMwj7qxmWA/1.jpg', 0)
        addDirWithLastPageNbr('Kamal TV Hindi Music Videos', 'KamalTvHindiMusic', 63, 'http://i2.ytimg.com/i/EbCus8ovEyqM5ckC3csXlg/1.jpg', 0)
        addDirWithLastPageNbr('Kamal TV Music Channel', 'ThenhnepalMusicvideo', 63, 'http://i2.ytimg.com/i/i558g25fvoaryCOeB9qj8w/1.jpg', 0)
        addDirWithLastPageNbr('Kamal TV Movie Updates', 'KamalTvMoviesUpdated', 63, 'http://i4.ytimg.com/i/Ol5ZBa9Velmyn8aAMReiXA/1.jpg', 0)
        addDirWithLastPageNbr('Kamal TV Movie Trailers', 'HindiTvTrailers', 63, 'http://i3.ytimg.com/i/r14s-DAlJZZPVAHx7eNh2A/1.jpg', 0)
        addDirWithLastPageNbr('Kamal TV Telugu Movies', 'TeleguMovieAtKamalTv', 63, 'http://i3.ytimg.com/i/jRMuXwzzI1ApTYlhuoe7Tg/1.jpg', 0)
        addDir('EROS Entertainment', 'erosentertainment', 63, 'http://i1.ytimg.com/i/X52tYZiEh_mHoFja3Veciw/1.jpg')
        addDir('UTV Motion Picture', 'UTVMotionPictures', 63, 'http://i2.ytimg.com/i/yvOJDBxhi1yqW97hXw3BDw/1.jpg')
        addDir('Saavn', 'Saavn', 63, 'http://i2.ytimg.com/i/qi93fwjyr32JA3JeULeNkA/1.jpg')
        addDir('Bollywood Full HD Songs', 'KhanBluRaySongs', 63, 'http://i3.ytimg.com/i/2RYCzGc0sGBzijN6a6LqAw/1.jpg')
        addDir('Yash Raj Films', 'yrf', 63, 'http://i3.ytimg.com/i/bTLwN10NoCU4WDzLf1JMOA/1.jpg')
        addDir('Yash Raj Films Songs', 'YRFsongs', 63, 'http://i3.ytimg.com/i/jeD2I8jwXg2l_nvXb_6Hzw/1.jpg')
        addDir('Yash Raj Films TV', 'yrfTV', 63, 'http://i3.ytimg.com/i/VoK4m-6IAyWl5nasVQNsEA/1.jpg')
        addDir('Yash Raj Films Trailers', 'YRFTrailers', 63, 'http://i4.ytimg.com/i/kmsZoa20iZG5S_5HcwLOOQ/1.jpg')
        addDir('Yash Raj Films Movies', 'YRFMovies', 63, 'http://i2.ytimg.com/i/U8LF98Njvux51LYGLgXiaw/1.jpg')
        addDir('Rajshri Films', 'rajshri', 63, 'http://i2.ytimg.com/i/EKWXRsfUHkan-D_ljU8Asw/1.jpg')
        addDir('Reliance BIG Cinemas', 'RelianceBigCinemas', 63, 'http://i2.ytimg.com/i/mTalEEpaHhGE-uZUx9VECg/1.jpg')
        addDir('Venus Movies', 'VenusMovies', 63, 'http://i1.ytimg.com/i/pcsv3Ow-8IhoUGDEfPetsQ/1.jpg?v=9b2d44')
        addDir('Zoom Dekho', 'zoomdekho', 63, 'http://i4.ytimg.com/i/otI-SqRXnkAZX4bMqlRNjw/1.jpg')
        addDir('Hungama', 'hungama', 63, 'http://i3.ytimg.com/i/zR7770PbrKcG9OYGzBep9w/1.jpg')
        addDir('Bollywood Backstage', 'bollywoodbackstage', 63, 'http://i4.ytimg.com/i/Gkk5lH1ODiE1ep4P533SJQ/1.jpg')
        addDir('Lehren TV', 'lehrentv', 63, 'http://i1.ytimg.com/i/xcriVvVwJQ81AHoRwfcd-Q/1.jpg?v=a57716')
        
        
        
def YouTube_CHANNEL_PLAYLISTS(url, name, lastPageNbr):
        urlContent = url.split('&AJ;')
        playListId = urlContent[0]
        
        ifTitleContains = ''
        ifTitleNotContains = ''
        if(len(urlContent) > 1):
                searchCriterias = urlContent[1].split('&JA;')
                ifTitleContains = searchCriterias[0]
                ifTitleNotContains = searchCriterias[1]
        #linksPerPage = maxLinksPerPageOption[int(fbn.getSetting('linksPerPage'))]
        #startIndex = 1
        #if lastPageNbr > 0:
        #        startIndex = (lastPageNbr * linksPerPage) + 1
        #retrieve_YT_UserPlaylists(playListId, name, startIndex, linksPerPage, lastPageNbr+1, ifTitleContains, ifTitleNotContains)
        retrieve_YT_UserPlaylists(playListId, name, 1, 50, 1, ifTitleContains, ifTitleNotContains)

def YouTube_CHANNEL_PLAYLIST_VIDEOS(url, name):
        retrieve_YT_PlaylistVideoLinks(url, name)

def YouTube_CHANNEL_UPLOADS(url, name, lastPageNbr):
        linksPerPage = maxLinksPerPageOption[int(fbn.getSetting('linksPerPage'))]
        startIndex = 1
        if lastPageNbr > 0:
                startIndex = (lastPageNbr * linksPerPage) + 1
        retrieve_YT_UserUploads(url, name, startIndex, linksPerPage, lastPageNbr + 1)

def YouTube_CHANNEL_CONTENT(url, name):
        d = xbmcgui.Dialog()
        index = d.select('Select Category:', ['Uploads', 'Playlists'])
        if index == -1:
                YouTube_CHANNEL_UPLOADS(url, 'Uploads', 0)
        elif index == 0:
                YouTube_CHANNEL_UPLOADS(url, 'Uploads', 0)
        elif index == 1:
                YouTube_CHANNEL_PLAYLISTS(url, 'PLaylists', 0)
        

def YouTube_CHANNEL_SominalTVTheatres(url, name):
        addDirWithLastPageNbr('Sominal TV MUSIC VIDEOS', 'SominalTvTheaters&AJ;Music Videos&JA;\(HD\) Music Videos', 61, 'http://i4.ytimg.com/i/cbiwrUudPQG185pXpeeiDw/1.jpg', 0)
        addDirWithLastPageNbr('Sominal TV MOVIES', 'SominalTvTheaters&AJ;&JA;(Music Videos)|(\*Hindi Movies\*)|(\*SominalTv Movies\*)|(\*Telugu/Tamil\* Movies)', 61, 'http://i4.ytimg.com/i/cbiwrUudPQG185pXpeeiDw/1.jpg', 0)


#######LIVE####################
def Live(url, name):
        indexNameList = ['[B]DesiTv[/B]Streams.com', '[B]Movies[/B]n[B]TV[/B].com', '[B]ROSHAN TV[/B] [I]absolutely[/I] free', '[B]Music[/B]', '[B]News & MTA[/B]']
        octoChannels = getOctoshapeChannels()
        if octoChannels != None:
                indexNameList.append('[B]Octoshape[/B]')
                
        yeahChannels = getYeahChannels()
        if yeahChannels != None:
                indexNameList.append('[B]YEAH TV[/B]')
                
        d = xbmcgui.Dialog()
        indexSelect = d.select('LIVE REMOTE', indexNameList)
        if indexSelect == -1:
                return
        if indexSelect == 0:
                indiaTV = 'http://www.cyberviewtv.org/ind/'
                pakTV = 'http://www.cyberviewtv.org/pak/'
                sportsTV = 'http://www.cyberviewtv.org/sport/'
                liveUrl = indiaTV
                isCyberViewTV = 'True'
                channelSelect = d.select('Select LIVE TV package:', ['Indian Channels', 'Pakistan Channels', 'Sports Channels'])
                if channelSelect == 0:
                        liveUrl = indiaTV
                        isCyberViewTV = 'True'
                elif channelSelect == 1:
                        liveUrl = pakTV
                        isCyberViewTV = 'True'
                elif channelSelect == 2:
                        liveUrl = sportsTV
                        isCyberViewTV = 'False'
                        
                web = loginCyberLive(liveUrl + 'player.php', isCyberViewTV)
                
                if web != None:
                        #print web
                        channels = re.compile('<tr><tdwidth="80"height="50"valign="middle">(.+?)</td><tdwidth="31"></td><tdwidth="122"valign="middle"><imgwidth=50height=40src="(.+?)">').findall(web)
                        for chId, chLogo in channels:
                                print chId + ' :: ' + chLogo
                                if isCyberViewTV == 'True':
                                	addPlayableLiveLinkWithOption('Channel ID: ' + chId, liveUrl + 'MediaPlayer.php?chid=' + chId, 83, chLogo, isCyberViewTV)
                                else:
                                	addPlayableLiveLinkWithOption('Channel ID: ' + chId, liveUrl + 'Flashplayer.php?stream=2&chid=' + chId, 83, chLogo, isCyberViewTV)
                                
                return
        
        if indexSelect == 1:
                indiaTV = 'http://moviesntv.com/hindi/'
                pakTV = 'http://moviesntv.com/pak/'
                sportsTV = 'http://moviesntv.com/sport/'
                liveUrl = indiaTV
                isTV = 'True'
                channelSelect = d.select('Select LIVE TV package:', ['Indian Channels', 'Pakistan Channels'])
                if channelSelect == 0:
                        liveUrl = indiaTV
                        isTV = 'True'
                elif channelSelect == 1:
                        liveUrl = pakTV
                        isTV = 'True'
                        
                web = loginMoviesnTV(liveUrl + 'player.php', isTV)
                
                if web != None:
                        #print web
                        channels = re.compile('<tr><tdwidth="80"height="50"valign="middle">(.+?)</td><tdwidth="31"></td><tdwidth="122"valign="middle"><imgwidth=50height=40src="(.+?)">').findall(web)
                        for chId, chLogo in channels:
                                print chId + ' :: ' + chLogo
                                addPlayableLiveLinkWithOption('Channel ID: ' + chId, liveUrl + 'MediaPlayer.php?chid=' + chId, 84, chLogo, isTV)
                return
        
        
        elif indexSelect == 2:
                addLiveLink ('STAR ONE', 'rtmpe://208.77.20.52/dm/ app=dm playpath=starone swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/ss/star_one.jpg')
                addLiveLink ('SAHARA ONE', 'rtmpe://208.77.20.52/dm/ app=dm playpath=saharaone swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/ss/sahara_one.jpg')
                addLiveLink ('STAR PLUS', 'rtmpe://208.77.20.52/dm/ app=dm playpath=starplus swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/ss/star_plus.jpg')
                addLiveLink ('SONY TV', 'rtmpe://208.77.20.52/streams/ app=streams playpath=sonytv swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/ss/set_asia.jpg')
                addLiveLink ('COLORS TV', 'rtmp://122.248.252.56/live/ app=live playpath=nokia40col150.sdp swfUrl=http://telugutv.net/player.swf swfVfy=true live=true', 'http://www.lyngsat-logo.com/logo/tv/cc/colors_in.jpg')
                addLiveLink ('AAPKA COLORS', 'rtmpe://208.77.20.52/dm/ app=dm playpath=apclr swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/aa/aapka_colors.jpg')
                addLiveLink ('SET MAX', 'rtmpe://208.77.20.52/dm/ app=dm playpath=setmax swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/ss/sony_max_tv_asia.jpg')
                addLiveLink ('ZEE TV', 'rtmpe://208.77.20.52/dm/ app=dm playpath=zeetv swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/zz/zee_tv.jpg')
                addLiveLink ('NDTV IMAGINE', 'rtmpe://208.77.20.52/streams/ app=streams playpath=ndtvimagine swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/ii/imagine_tv_in.jpg')
                addLiveLink ('STAR GOLD', 'rtmpe://208.77.20.52/streams/ app=streams playpath=stargold swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/ss/star_gold.jpg')
                addLiveLink ('SAHARA FILMY', 'rtmpe://208.77.20.52/streams/ app=streams playpath=saharafilmy swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/ss/sahara_filmy.jpg')
                addLiveLink ('UTV MOVIES', 'rtmpe://208.77.20.52/streams/ app=streams playpath=utvmovies swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/uu/utv_movies.jpg')
                addLiveLink ('MTV INDIA', 'rtmpe://208.77.20.52/dm/ app=dm playpath=mtv swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/mm/mtv_india.jpg')
                addLiveLink ('SAB TV', 'rtmpe://208.77.20.52/dm/ app=dm playpath=sab swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/ss/sony_sab_tv.jpg')
                #addLiveLink ('ETC PUNJABI', 'rtmpe://208.77.20.52/dm/ app=dm playpath=aetcpunjab swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf','http://www.lyngsat-logo.com/logo/tv/ee/etc_punjabi.jpg')
                addLiveLink ('NDTV 24X7', 'rtmpe://208.77.20.52/streams/ app=streams playpath=ndtv swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/aa/atn_ndtv_24x7.jpg')
                addLiveLink ('NDTV PROFIT', 'rtmpe://208.77.20.52/streams/ app=streams playpath=ndtvprofit swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/nn/ndtv_profit.jpg')
                #addLiveLink ('NEWS 9', 'rtmpe://208.77.20.50/s1/ app=s1 playpath=news9 swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf','http://www.lyngsat-logo.com/logo/tv/nn/news_9_in.jpg')
                #addLiveLink ('STAR NEWS', 'rtmpe://208.77.20.52/dm/ app=dm playpath=starnews swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf','http://www.lyngsat-logo.com/logo/tv/ss/star_news_india.jpg')
                addLiveLink ('NDTV GOOD TIMES', 'rtmpe://208.77.20.52/streams/ app=streams playpath=ndtvgoodtimes swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/nn/ndtv_good_times.jpg')
                #addLiveLink ('B4U MOVIES', 'rtmpe://208.77.20.52/dm/ app=dm playpath=b4umovies swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf','http://www.lyngsat-logo.com/logo/tv/aa/atn_b4u_movies.jpg')
                #addLiveLink ('CHANNEL UFX', 'rtmpe://208.77.20.50/s1/ app=s1 playpath=ufx swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf','http://www.lyngsat-logo.com/logo/tv/cc/channel_ufx.jpg')
                addLiveLink ('9XM', 'rtmp://122.248.252.56/live/ app=live playpath=nokia409xm150.sdp swfUrl=http://telugutv.net/player.swf swfVfy=true live=true', 'http://www.lyngsat-logo.com/logo/tv/num/9x_music.jpg')
                addLiveLink ('9X Jhakaas', 'rtmp://122.248.252.56/live/ app=live playpath=nokia40jhakaas150.sdp swfUrl=http://telugutv.net/player.swf swfVfy=true live=true', 'http://www.lyngsat-logo.com/logo/tv/num/9x_jhakaas.jpg')
                addLiveLink ('9X Tashan', 'rtmp://122.248.252.56/live/ app=live playpath=nokia40tashan150.sdp swfUrl=http://telugutv.net/player.swf swfVfy=true live=true', 'http://www.lyngsat-logo.com/logo/tv/num/9x_tashan.jpg')
                addLiveLink ('DESI 4U HITS', 'rtmpe://208.77.20.46/streams/ app=streams playpath=dhits swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://watchsuntv.com/images/desi4uhits.png')
                addLiveLink ('DESI 4U CINEMA', 'rtmpe://208.77.20.46/streams/ app=streams playpath=dcinema swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://watchsuntv.com/images/desicinema.png')
                addLiveLink ('DESI 4U CLASSIC', 'rtmpe://208.77.20.46/streams/ app=streams playpath=dclassic swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://watchsuntv.com/images/desiclassic.png')
                addLiveLink ('DESI 4U MOVIES', 'rtmpe://208.77.20.46/streams/ app=streams playpath=dmovies swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://watchsuntv.com/images/desimovies.png')
                #addLiveLink ('ENTERR 10 MOVIES', 'rtmpe://208.77.20.50/s1/ app=s1 playpath=enter10 swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf','http://watchsuntv.com/images/enterr_10_movies.jpg')
                addLiveLink ('NEO CRICKET', 'rtmpe://208.77.20.50/dm/ app=dm playpath=tvasia swfUrl=http://www.watchsuntv.com/play/flash/player.swf swfVfy=true live=true pageUrl=http://www.watchsuntv.com/play/flash/player.swf', 'http://www.lyngsat-logo.com/logo/tv/nn/neo_cricket_asia.jpg')
                
                return

        elif indexSelect == 3:
                addLiveLink ('ZOOM TV', 'rtmp://cdn.rtmp1.yupptv.tv/nwk app=nwk playpath=zoomtv swfUrl=http://www.yupptv.com/yupptvhdflvplayer/hdplayer.swf swfVfy=true live=true pageUrl=http://www.yupptv.com/account/FlashPlayerFrame.aspx?ChanId=15', 'http://www.lyngsat-logo.com/logo/tv/zz/zoom_tv.jpg')
                addLiveLink ('[B]9XM[/B]', 'rtmp://210.210.27.37:1935/live/livestream3 swfUrl=http://www.9xm.in/livetv/liveStreamPlayer.swf swfVfy=true live=true', 'http://www.lyngsat-logo.com/logo/tv/num/9xm_in.jpg')
                return
        
        elif indexSelect == 4:
                addDir('NDTV Channels', 'http://www.ndtv.com/', 81, 'http://www.ndtv.com/common/header/images/ndtv_logo_black.gif')
                addLiveLink ('TIMES NOW', 'rtmp://cdn.rtmp1.yupptv.tv/nwk app=nwk playpath=timesnow swfUrl=http://www.yupptv.com/yupptvhdflvplayer/hdplayer.swf swfVfy=true live=true pageUrl=http://www.yupptv.com/account/FlashPlayerFrame.aspx?ChanId=118', 'http://www.lyngsat-logo.com/logo/tv/tt/times_now.jpg')
                addLiveLink ('Dunya News', 'rtmp://173.245.68.50/live/cam.flv swfUrl=http://www.dunyanews.tv/newsite/live_stream/player.swf swfVfy=true pageUrl=http://www.dunyanews.tv/newsite/live_stream/new1_live_tv.php live=true ', 'http://www.dunyanews.tv/images/logo.png')
                addLiveLink ('Dunya News *HD*', 'rtmp://72.13.93.132/live playpath=mp4:livestream_1.f4v swfUrl=http://www.dunyanews.tv/livehd/swfs/videoPlayer.swf swfVfy=true pageUrl=http://www.dunyanews.tv/livehd/index.php live=true ', 'http://www.dunyanews.tv/images/logo.png')
                addLiveLink ('PTV News', 'rtmp://live.server4sale.com/live/PTVnews swfUrl=http://www.pakistanvision.com/swfs/videoPlayer.swf swfVfy=true pageUrl=http://www.ptv.com.pk/livetvnews.asp live=true ', 'http://academy.ptv.com.pk/images/ptv-news.jpg')
                addLiveLink ('Geo News', 'rtmp://live.dmasti.pk/news playpath=livestream swfUrl=http://www.f4funda.com/player.swf?title=DunyaNews&allowscriptaccess=always&file=livestream.flv&bufferlength=2&volume=100&bitrate=150&duration=99999999999999999&streamer=rtmp://live.dmasti.pk/news&allowscriptaccess=always%20bgcolor=white&full%20screen=true&autostart=true swfVfy=true pageUrl=http://www.f4funda.com/player.swf?title=DunyaNews&allowscriptaccess=always&file=livestream.flv&bufferlength=2&volume=100&bitrate=150&duration=99999999999999999&streamer=rtmp://live.dmasti.pk/news&allowscriptaccess=always%20bgcolor=white&full%20screen=true&autostart=true live=true ', 'http://www.satlogo.com/logo/hires/gg/geo_news_e.png')
                addLiveLink ('Al Jazeera', 'rtmp://media2.lsops.net/live/ playpath=aljazeer_en_high.sdp swfUrl="http://www.livestation.com/flash/player/5.4/player.swf" pageUrl="http://www.livestation.com/channels/3-al-jazeera-english-english" swfVfy=true live=true', 'http://1.bp.blogspot.com/_n7RltmTdk-g/TSz0E1u7_xI/AAAAAAAAZRc/LWD4MRQ2Tc4/s1600/Al-Jazeera%2BLogo.jpg')
                addLiveLink ('CNN', 'rtmp://media2.lsops.net/live/ playpath=cnn_en_high.sdp swfUrl="http://www.livestation.com/flash/player/5.4/player.swf" pageUrl="http://www.livestation.com/channels/66-cnn-international" swfVfy=true live=true', 'http://i.cdn.turner.com/cnn/.element/img/3.0/global/header/hdr-main.gif')
                addLiveLink ('BBC World', 'rtmp://media2.lsops.net/live/ playpath=bbcworld1_en_high.sdp swfUrl="http://www.livestation.com/flash/player/5.4/player.swf" pageUrl="http://www.livestation.com/channels/10-bbc-world-news-english" swfVfy=true live=true', 'http://www.bbcworldnews.com/Pages/Images/Assets/9ee0304f-37db-40d1-8e11-26b7d46ce1df.jpg')
                #MTA links
                addLiveLink ('MTA [Urdu]', 'http://ms.mta.tv/Urdu300k', 'http://www.alislam.org/images/MTA-logo.gif')
                addLiveLink ('MTA [English]', 'rtsp://ms.mta.tv/English300k', 'http://www.alislam.org/images/MTA-logo.gif')
                addLiveLink ('MTA3', 'rtsp://ms.mta.tv/MTA3_300K', 'http://www.alislam.org/images/MTA-logo.gif')
                return
        
        
        
        elif indexSelect == 5 and octoChannels != None:
                hostname = '127.0.0.1'
                port = fbn.getSetting('octoshapePort')
                millis = int(round(time.time() * 1000))
                channels = octoChannels
                if channels != None:
                        catNameList = ['Education', 'Devotional', 'News', 'Sports', 'Hindi', 'Kannada', 'Malayalam', 'Tamil', 'Telugu']
                        d = xbmcgui.Dialog()
                        catSelect = d.select('SELECT Category', catNameList)
                        if catSelect == -1:
                                return
                        category = catNameList[catSelect]
                        for channelUrl in channels:
                                #print channels[channelUrl]['category']
                                try:
                                        if category == channels[channelUrl]['category']:
                                                parsed = re.compile('octoshape:////(.+?)/(.+?)&AJ;').findall(channelUrl + '&AJ;')[0]
                                                millis = millis + 1
                                                url = 'http://' + hostname + ':' + port + '/ms2/' + str(millis) + '/0MediaPlayer+0+/octoshape+hVVVV+' + parsed[0] + '+V+' + parsed[1] + '/' + parsed[1].replace('.', '')
                                                url = url + '?ticketUrl=' + urllib.quote('http://www.yupptv.com/ticket1.aspx')
                                                print url
                                                addLiveLink(channels[channelUrl]['channel'], url, channels[channelUrl]['thumb'])
                
                                except: pass
                                #print channels[channelUrl]['channel']
                                #print channels[channelUrl]['thumb']
                return
                
        elif indexSelect == 6 or octoChannels == None:
                channels = yeahChannels
                if channels != None:
                        catNameList = ['Education', 'Devotional', 'News', 'Sports', 'Hindi', 'Kannada', 'Malayalam', 'Tamil', 'Telugu']
                        d = xbmcgui.Dialog()
                        catSelect = d.select('SELECT Category', catNameList)
                        if catSelect == -1:
                                return
                        category = catNameList[catSelect]
                        for channelUrl in channels:
                                #print channels[channelUrl]['category']
                                try:
                                        if category == channels[channelUrl]['category']:
                                                addLiveLink(channels[channelUrl]['channel'], channelUrl, channels[channelUrl]['thumb'])
                
                                except: pass
                return
                        

def getOctoshapeChannels():
        channelsFilePath = os.path.join(xbmc.translatePath(addonDataPath), octoshapeChannelsFile)
        channelsJsonObj = None
        if os.path.exists(channelsFilePath):
                try:
                        fc = open(channelsFilePath, 'r')
                        channelsJsonObj = json.load(fc, encoding='utf-8')
                        fc.close()
                        print 'METADATA FILE LOADED'
                except ValueError:
                        print 'FAILED to read JSON file'
        return channelsJsonObj
        
def getYeahChannels():
        channelsFilePath = os.path.join(xbmc.translatePath(addonDataPath), yeahChannelsFile)
        channelsJsonObj = None
        if os.path.exists(channelsFilePath):
                try:
                        fc = open(channelsFilePath, 'r')
                        channelsJsonObj = json.load(fc, encoding='utf-8')
                        fc.close()
                        print 'METADATA FILE LOADED'
                except ValueError:
                        print 'FAILED to read JSON file'
        return channelsJsonObj

def Live_iTvDesiLink(name, url, thumb):
        try:
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                link = ''.join(link.splitlines())
                streamUrl = re.compile('param name="URL" value="(.+?)"').findall(link)[0]
                addLiveLink (name , streamUrl, thumb)
        except: pass
        
        
def Live_desiTvStreamsLink(name, url, thumb):
        try:
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                link = ''.join(link.splitlines())
                streamUrl = re.compile('src="mms(.+?)"').findall(link)[0]
                addLiveLink (name , 'mms' + streamUrl, thumb)
        except: pass
        
        
def Live_NDTV(url, name):
        #NDTV CHANNEL LINKS
        addLiveLink ('NDTV 24x7', 'http://bglive-a.bitgravity.com/ndtv/247lo/live/native', 'http://www.lyngsat-logo.com/logo/tv/nn/ndtv_24x7.jpg')
        addLiveLink ('NDTV PROFIT', 'http://bglive-a.bitgravity.com/ndtv/prolo/live/native', 'http://www.lyngsat-logo.com/logo/tv/nn/ndtv_profit.jpg')
        addLiveLink ('NDTV INDIA', 'http://bglive-a.bitgravity.com/ndtv/indlo/live/native', 'http://www.lyngsat-logo.com/logo/tv/nn/ndtv_india.jpg')
        addLiveLink ('NDTV HINDU', 'http://bglive-a.bitgravity.com/ndtv/indhi/live/native', 'http://www.lyngsat-logo.com/logo/tv/nn/ndtv_hindu.jpg')
        addLiveLink ('NDTV GOOD TIMES', 'http://bglive-a.bitgravity.com/ndtv/prohi/live/native', 'http://www.lyngsat-logo.com/logo/tv/nn/ndtv_good_times.jpg')


def loginCyberLive(url, isCyberViewTV):
        try:
                print 'isCyberViewTV = ' + isCyberViewTV
                cookiejar = cookielib.LWPCookieJar()
                cookiejar = urllib2.HTTPCookieProcessor(cookiejar) 
                opener = urllib2.build_opener(cookiejar)
                urllib2.install_opener(opener)
                
                user = fbn.getSetting('cybertv_user')
                pwd = fbn.getSetting('cybertv_pass')
                if isCyberViewTV == 'False':
                        user = fbn.getSetting('cybercriket_user')
                        pwd = fbn.getSetting('cybercriket_pass')
                
                if user == '' or pwd == '':
                        d = xbmcgui.Dialog()
                        d.ok('Login Details MISSING', 'Please provide login details for DesiTvStreams.com', 'Buy packages at DesiTvStreams.com to get access.')
                        fbn.openSettings(sys.argv[ 0 ])
                user = fbn.getSetting('cybertv_user')
                pwd = fbn.getSetting('cybertv_pass')
                if isCyberViewTV == 'False':
                        user = fbn.getSetting('cybercriket_user')
                        pwd = fbn.getSetting('cybercriket_pass')
                millis = str(int(round(time.time())))
                values = {'amember_login': user, 'amember_pass': pwd, 'login_attempt_id': millis}
                headers = { 'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3' }
                data = urllib.urlencode(values)
                req = urllib2.Request(url, data, headers)
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                #print link
                
                if re.search('Username or password incorrect', link):
                        d = xbmcgui.Dialog()
                        d.ok('Login Failed', 'Error: Your email or password is incorrect.', 'Please verify your login details.')
                        return
                else:
                        return ''.join(link.splitlines()).replace('\t', '').replace('\'', '"').replace(' ', '').replace('&nbsp;', '')
        except:
                d = xbmcgui.Dialog()
                d.ok('LOGIN Failed', 'Its not your fault. BREAK TIME!', 'Please check if desitvstreams.com website is alive.')
                return



def Live_CyberViewTv_Play(url, name, isCyberViewTV):
        d = xbmcgui.Dialog()
        #indexSelect = d.select('Select streaming server:', ['USA','Europe','Canada',])
        indexSelect = int(fbn.getSetting('cybertv_server'))
        server = '1'
        if indexSelect == 0:
                server = '3'
        elif indexSelect == 1:
                server = '2'
        web = loginCyberLive(url + '&server=' + server, isCyberViewTV)
        protocolType = ['mms', 'rtsp']
        
        xbmcPlayer = xbmc.Player()
        if web != None:
                streamUrl = re.compile('<embedsrc="(.+?)"').findall(web)[0]
                xbmcPlayer.play(streamUrl.replace('mms', protocolType[int(fbn.getSetting('cybertv_stream_type'))]))
        if not xbmcPlayer.isPlayingVideo():
                d = xbmcgui.Dialog()
                d.ok('FAILED to PLAY STREAM', 'Please check if the streaming is working at desitvstream.com', 'Check other streaming servers.')
        
def loginMoviesnTV(url, isTV):
        try:
                print 'isTV = ' + isTV
                cookiejar = cookielib.LWPCookieJar()
                cookiejar = urllib2.HTTPCookieProcessor(cookiejar) 
                opener = urllib2.build_opener(cookiejar)
                urllib2.install_opener(opener)
                user = fbn.getSetting('moviesntv_user')
                pwd = fbn.getSetting('moviesntv_pass')
                if isTV == 'False':
                        user = fbn.getSetting('moviesntvcriket_user')
                        pwd = fbn.getSetting('moviesntvcriket_pass')
                
                if user == '' or pwd == '':
                        d = xbmcgui.Dialog()
                        d.ok('Login Details MISSING', 'Please provide login details for moviesntv.com', 'Buy packages at moviesntv.com to get access.')
                        fbn.openSettings(sys.argv[ 0 ])
                user = fbn.getSetting('moviesntv_user')
                pwd = fbn.getSetting('moviesntv_pass')
                if isTV == 'False':
                        user = fbn.getSetting('moviesntvcriket_user')
                        pwd = fbn.getSetting('moviesntvcriket_pass')
                print url
                millis = str(int(round(time.time() * 1000)))
                values = {'amember_login': user, 'amember_pass': pwd, 'login_attempt_id': millis}
                headers = { 'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3' }
                data = urllib.urlencode(values)
                req = urllib2.Request(url, data, headers)
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()
                
                if re.search('Username or password incorrect', link):
                        d = xbmcgui.Dialog()
                        d.ok('Login Failed', 'Error: Your email or password is incorrect.', 'Please verify your login details.')
                        return
                else:
                        return ''.join(link.splitlines()).replace('\t', '').replace('\'', '"').replace(' ', '').replace('&nbsp;', '')
        except:
                d = xbmcgui.Dialog()
                d.ok('LOGIN Failed', 'Its not your fault. BREAK TIME!', 'Please check if moviesntv.com website is alive.')
                return



def Live_MoviesnTV_Play(url, name, isTV):
        d = xbmcgui.Dialog()
        #indexSelect = d.select('Select streaming server:', ['USA','Europe','Canada',])
        indexSelect = int(fbn.getSetting('moviesntv_server'))
        server = '1'
        if indexSelect == 0:
                server = '3'
        elif indexSelect == 1:
                server = '2'
        web = loginMoviesnTV(url + '&server=' + server, isTV)
        protocolType = ['mms', 'rtsp']
        
        xbmcPlayer = xbmc.Player()
        if web != None:
                streamUrl = re.compile('<embedsrc="(.+?)"').findall(web)[0]
                xbmcPlayer.play(streamUrl.replace('mms', protocolType[int(fbn.getSetting('moviesntv_stream_type'))]))
        if not xbmcPlayer.isPlayingVideo():
                d = xbmcgui.Dialog()
                d.ok('FAILED to PLAY STREAM', 'Please check if the streaming is working at moviesntv.com', 'Check other streaming servers.')
        

def Live_MastTv_Play(streamName, name):
        req = urllib2.Request('http://www.mast.tv/channel.php?stream=' + streamName + '&location=nederland')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        videoUrl = re.compile('<param name="initParams" value="m=(.+?),').findall(link)
        xbmcPlayer = xbmc.Player()
        if len(videoUrl) != 0:
                xbmcPlayer.play(videoUrl[0].replace(' ', '%20'))#.replace('s1.mast.tv','50.7.240.170:911'))
        if not xbmcPlayer.isPlayingVideo():
                d = xbmcgui.Dialog()
                d.ok('FAILED to PLAY STREAM', 'Please check if the streaming is working at mast.tv')
        


        
#######YOUTUBE APIs############

def retrieve_YT_UserInfo(YouTubeUserId):
        url = 'http://gdata.youtube.com/feeds/api/users/' + YouTubeUserId
        #url='http://gdata.youtube.com/feeds/api/videos/yrvUcOiPb1g'
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        domObj = parseString(link)
        #print domObj.toprettyxml()
        entry = domObj.getElementsByTagName("entry")[0]
        
        userInfo = {}
        userInfo['title'] = getText(entry.getElementsByTagName("title")[0].childNodes)
        userInfo['thumbnail'] = entry.getElementsByTagName("media:thumbnail")[0].getAttribute('url')
        return userInfo
        

def retrieve_YT_UserUploads(YouTubeUserId, name='', startIndex=1, maxCount=50, pageNbr=0):
        url = 'http://gdata.youtube.com/feeds/api/users/' + YouTubeUserId + '/uploads?v=2&max-results=' + str(maxCount) + '&start-index=' + str(startIndex)
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        domObj = parseString(link)
        #print domObj.toprettyxml()
        videos = domObj.getElementsByTagName("entry")

        imgUrl = 'http://i.ytimg.com/vi/' + YouTubeUserId + '/default.jpg'
        matchCount = len(videos)
        if(matchCount == 1):
                videoID = getText(videos[0].getElementsByTagName("yt:videoid")[0].childNodes)
                videoLink = 'http://www.youtube.com/v/' + videoID
                try:
                        addPlayableMovieLink(getText(videos[0].getElementsByTagName("title")[0].childNodes), videoLink, 31, 'http://i.ytimg.com/vi/' + videoID + '/default.jpg')
                except KeyError: pass
        elif(matchCount > 1):
                for video in videos:
                        videoTitle = getText(video.getElementsByTagName("title")[0].childNodes)
                        videoID = getText(video.getElementsByTagName("yt:videoid")[0].childNodes)
                        videoLink = 'http://www.youtube.com/v/' + videoID
                        try:
                                addPlayableMovieLink(videoTitle, videoLink, 31, 'http://i.ytimg.com/vi/' + videoID + '/default.jpg')
                        except KeyError: pass
                        
        currCountOfVideo = len(videos)
        if(currCountOfVideo == maxCount):
                addDirWithLastPageNbr('[B]NEXT PAGE >>[/B]', YouTubeUserId, 64, os.path.join(xbmc.translatePath(artPath), "next-icon.png"), pageNbr)
        if(pageNbr > 1):
                addDirWithLastPageNbr('[B]<< PREVIOUS PAGE[/B]', YouTubeUserId, 64, os.path.join(xbmc.translatePath(artPath), "prev-icon.png"), pageNbr - 2)


def retrieve_YT_PlaylistVideoLinks(playlistID, playlistTitle='', startIndex=1, maxCount=50, playList='', playListLinksCount=0):
        url = 'http://gdata.youtube.com/feeds/api/playlists/' + playlistID + '?v=2&max-results=' + str(maxCount) + '&start-index=' + str(startIndex)
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        domObj = parseString(link)
        #print domObj.toprettyxml()
        videos = domObj.getElementsByTagName("entry")

        imgUrl = 'http://i.ytimg.com/vi/' + playlistID + '/default.jpg'
        i = 1
        matchCount = len(videos)
        if playListLinksCount == 0:
                playListLinksCount = matchCount
        else:
                playListLinksCount = playListLinksCount + matchCount
        
        if(matchCount == 1):
                videoID = getText(videos[0].getElementsByTagName("yt:videoid")[0].childNodes)
                videoLink = 'http://www.youtube.com/v/' + videoID
                addPlayableMovieLink(getText(videos[0].getElementsByTagName("title")[0].childNodes), videoLink, 31, 'http://i.ytimg.com/vi/' + videoID + '/default.jpg')
        elif(matchCount > 1):
                for video in videos:
                        videoTitle = getText(video.getElementsByTagName("title")[0].childNodes)
                        videoID = getText(video.getElementsByTagName("yt:videoid")[0].childNodes)
                        videoLink = 'http://www.youtube.com/v/' + videoID
                        addPlayableMovieLink(videoTitle, videoLink, 31, 'http://i.ytimg.com/vi/' + videoID + '/default.jpg')
                        playList = playList + videoLink
                        if(i < matchCount or matchCount == maxCount):
                                playList = playList + ':;'
                        i = i + 1
        if(matchCount == maxCount):
                retrieve_YT_PlaylistVideoLinks(playlistID, playlistTitle, startIndex + maxCount, maxCount, playList, playListLinksCount)
        elif(playListLinksCount > 0):
                addPlayListLink('[B]Direct PLAY - ' + playlistTitle + '[/B] [I]Playlist of above ' + str(playListLinksCount) + ' videos[/I]', playList, 32, imgUrl)
        


def retrieve_YT_UserPlaylists(YouTubeUserId, name='', startIndex=1, maxCount=50, pageNbr=0, ifTitleContains='', ifTitleNotContains=''):
        
        url = 'http://gdata.youtube.com/feeds/api/users/' + YouTubeUserId + '/playlists?v=2&max-results=' + str(maxCount) + '&start-index=' + str(startIndex)
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        domObj = parseString(link)
        #print domObj.toprettyxml()
        playlists = domObj.getElementsByTagName("entry")
        for playlist in playlists:
                playListTitle = unicode(getText(playlist.getElementsByTagName("title")[0].childNodes)).encode("utf-8")
                playlistID = getText(playlist.getElementsByTagName("yt:playlistId")[0].childNodes)
                print playListTitle
                if ifTitleContains != '' and not re.search(ifTitleContains, playListTitle):
                        continue
                elif ifTitleNotContains != '' and re.search(ifTitleNotContains, playListTitle):
                        continue
                if re.search('Sominal', YouTubeUserId):
                        addDirAndLoadImg(playListTitle, playlistID, 62)
                else:
                        addDir(playListTitle, playlistID, 62, '')
                
        print len(playlists)
        currCountOfPlayList = len(playlists)
        print maxCount
        if(currCountOfPlayList == maxCount):
                retrieve_YT_UserPlaylists(YouTubeUserId, name, startIndex + maxCount, maxCount, pageNbr, ifTitleContains, ifTitleNotContains)
        #        addDirWithLastPageNbr('[B]NEXT PAGE >>[/B]',YouTubeUserId+'&AJ;'+ifTitleContains+'&AJ;'+ifTitleNotContains,61,os.path.join(xbmc.translatePath( artPath ), "next-icon.png"), pageNbr)
        #if(pageNbr > 1):
        #        addDirWithLastPageNbr('[B]<< PREVIOUS PAGE[/B]',YouTubeUserId+'&AJ;'+ifTitleContains+'&AJ;'+ifTitleNotContains,61,os.path.join(xbmc.translatePath( artPath ), "prev-icon.png"), pageNbr-2)
        

def retreiveYouTubePlayList(playlistID, imgUrl, sourceName, videoType='Part'):
        url = 'http://gdata.youtube.com/feeds/api/playlists/' + playlistID + '?v=2'
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        domObj = parseString(link)
        #print domObj.toprettyxml()
        videos = domObj.getElementsByTagName("entry")
        i = 1
        playList = ''
        matchCount = len(videos)
        if(matchCount == 1):
                videoLink = 'http://www.youtube.com/v/' + getVideoID(videos[0])
                addPlayableMovieLink('[B]SINGLE LINK [/B]' + sourceName, videoLink, 31, imgUrl)
        elif(matchCount > 1):
                for video in videos:
                        videoID = getVideoID(video)
                        videoTitle = getVideoTitle(video)
                        print '\tvideoID = ' + videoID
                        videoLink = 'http://www.youtube.com/v/' + videoID
                        if videoType == 'Song':
                                addPlayableMovieLink(sourceName + ' - ' + videoTitle, videoLink, 31, imgUrl)
                        else:
                                addPlayableMovieLink(sourceName + ' - ' + videoType + ': ' + str(i), videoLink, 31, imgUrl)
                        playList = playList + videoLink
                        if(i < matchCount):
                                playList = playList + ':;'
                        i = i + 1
                if(i > matchCount and matchCount > 0):
                        addPlayListLink('[B]Direct PLAY - ' + sourceName + '[/B] [I]Playlist of above ' + str(matchCount) + ' videos[/I]', playList, 32, imgUrl)



####################################################################################################################
# MegaVideo Routine
####################################################################################################################
        
#Python Video Decryption and resolving routines.
#Courtesy of Voinage, Coolblaze.
#Megavideo - Coolblaze # Part 1 put this below VIDEOLINKS function.

def ajoin(arr):
        strtest = ''
        for num in range(len(arr)):
                strtest = strtest + str(arr[num])
        return strtest

def asplit(mystring):
        arr = []
        for num in range(len(mystring)):
                arr.append(mystring[num])
        return arr
                
def decrypt(str1, key1, key2):

        __reg1 = []
        __reg3 = 0
        while (__reg3 < len(str1)):
                __reg0 = str1[__reg3]
                holder = __reg0
                if (holder == "0"):
                        __reg1.append("0000")
                else:
                        if (__reg0 == "1"):
                                __reg1.append("0001")
                        else:
                                if (__reg0 == "2"): 
                                        __reg1.append("0010")
                                else: 
                                        if (__reg0 == "3"):
                                                __reg1.append("0011")
                                        else: 
                                                if (__reg0 == "4"):
                                                        __reg1.append("0100")
                                                else: 
                                                        if (__reg0 == "5"):
                                                                __reg1.append("0101")
                                                        else: 
                                                                if (__reg0 == "6"):
                                                                        __reg1.append("0110")
                                                                else: 
                                                                        if (__reg0 == "7"):
                                                                                __reg1.append("0111")
                                                                        else: 
                                                                                if (__reg0 == "8"):
                                                                                        __reg1.append("1000")
                                                                                else: 
                                                                                        if (__reg0 == "9"):
                                                                                                __reg1.append("1001")
                                                                                        else: 
                                                                                                if (__reg0 == "a"):
                                                                                                        __reg1.append("1010")
                                                                                                else: 
                                                                                                        if (__reg0 == "b"):
                                                                                                                __reg1.append("1011")
                                                                                                        else: 
                                                                                                                if (__reg0 == "c"):
                                                                                                                        __reg1.append("1100")
                                                                                                                else: 
                                                                                                                        if (__reg0 == "d"):
                                                                                                                                __reg1.append("1101")
                                                                                                                        else: 
                                                                                                                                if (__reg0 == "e"):
                                                                                                                                        __reg1.append("1110")
                                                                                                                                else: 
                                                                                                                                        if (__reg0 == "f"):
                                                                                                                                                __reg1.append("1111")

                __reg3 = __reg3 + 1

        mtstr = ajoin(__reg1)
        __reg1 = asplit(mtstr)
        __reg6 = []
        __reg3 = 0
        while (__reg3 < 384):
        
                key1 = (int(key1) * 11 + 77213) % 81371
                key2 = (int(key2) * 17 + 92717) % 192811
                __reg6.append((int(key1) + int(key2)) % 128)
                __reg3 = __reg3 + 1
        
        __reg3 = 256
        while (__reg3 >= 0):

                __reg5 = __reg6[__reg3]
                __reg4 = __reg3 % 128
                __reg8 = __reg1[__reg5]
                __reg1[__reg5] = __reg1[__reg4]
                __reg1[__reg4] = __reg8
                __reg3 = __reg3 - 1
        
        __reg3 = 0
        while (__reg3 < 128):
        
                __reg1[__reg3] = int(__reg1[__reg3]) ^ int(__reg6[__reg3 + 256]) & 1
                __reg3 = __reg3 + 1

        __reg12 = ajoin(__reg1)
        __reg7 = []
        __reg3 = 0
        while (__reg3 < len(__reg12)):

                __reg9 = __reg12[__reg3:__reg3 + 4]
                __reg7.append(__reg9)
                __reg3 = __reg3 + 4
                
        
        __reg2 = []
        __reg3 = 0
        while (__reg3 < len(__reg7)):
                __reg0 = __reg7[__reg3]
                holder2 = __reg0
        
                if (holder2 == "0000"):
                        __reg2.append("0")
                else: 
                        if (__reg0 == "0001"):
                                __reg2.append("1")
                        else: 
                                if (__reg0 == "0010"):
                                        __reg2.append("2")
                                else: 
                                        if (__reg0 == "0011"):
                                                __reg2.append("3")
                                        else: 
                                                if (__reg0 == "0100"):
                                                        __reg2.append("4")
                                                else: 
                                                        if (__reg0 == "0101"): 
                                                                __reg2.append("5")
                                                        else: 
                                                                if (__reg0 == "0110"): 
                                                                        __reg2.append("6")
                                                                else: 
                                                                        if (__reg0 == "0111"): 
                                                                                __reg2.append("7")
                                                                        else: 
                                                                                if (__reg0 == "1000"): 
                                                                                        __reg2.append("8")
                                                                                else: 
                                                                                        if (__reg0 == "1001"): 
                                                                                                __reg2.append("9")
                                                                                        else: 
                                                                                                if (__reg0 == "1010"): 
                                                                                                        __reg2.append("a")
                                                                                                else: 
                                                                                                        if (__reg0 == "1011"): 
                                                                                                                __reg2.append("b")
                                                                                                        else: 
                                                                                                                if (__reg0 == "1100"): 
                                                                                                                        __reg2.append("c")
                                                                                                                else: 
                                                                                                                        if (__reg0 == "1101"): 
                                                                                                                                __reg2.append("d")
                                                                                                                        else: 
                                                                                                                                if (__reg0 == "1110"): 
                                                                                                                                        __reg2.append("e")
                                                                                                                                else: 
                                                                                                                                        if (__reg0 == "1111"): 
                                                                                                                                                __reg2.append("f")
                                                                                                                                        
                __reg3 = __reg3 + 1

        endstr = ajoin(__reg2)
        return endstr




########DAILYMOTION########          
def retreiveDailyMotionPlayList(playlistID, imgUrl, sourceName, videoType):
        url = 'http://www.dailymotion.com/playlist/' + playlistID
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        link = ''.join(link.splitlines()).replace('\t', '')
        videoList = re.compile('<a dm:context="/playlist/' + playlistID + '" title="(.+?)" href="(.+?)"').findall(link)
        i = 1
        playList = ''
        matchCount = len(videoList)
        if(matchCount == 1):
                videoLink = 'http://www.dailymotion.com' + videoList[0][1]
                addPlayableMovieLink('[B]SINGLE LINK [/B]' + sourceName, unescape(videoLink), 31, imgUrl)
        elif(matchCount > 1):
                for title, videoLink in videoList:
                        videoLink = 'http://www.dailymotion.com' + videoLink
                        print title + ' LINK = ' + videoLink
                        addPlayableMovieLink(sourceName + ' - ' + videoType + ': ' + str(i), unescape(videoLink), 31, imgUrl)
                        playList = playList + unescape(videoLink)
                        if(i < matchCount):
                                playList = playList + ':;'
                        i = i + 1
                if(i > matchCount and matchCount > 0):
                        addPlayListLink('[B]Direct PLAY - ' + sourceName + '[/B] [I]Playlist of above ' + str(matchCount) + ' videos[/I]', playList, 32, imgUrl)


          

#######################################
####display wait to user in dialog box
#######################################
def display_wait(time_to_wait, title, text):
        print 'waiting ' + str(time_to_wait) + ' secs'    

        pDialog = xbmcgui.DialogProgress()
        ret = pDialog.create(' ' + title)

        secs = 0
        percent = 0
        increment = int(100 / time_to_wait)

        cancelled = False
        while secs < time_to_wait:
                secs = secs + 1
                percent = increment * secs
                secs_left = str((time_to_wait - secs))
                remaining_display = ' Wait ' + secs_left + ' seconds for the video link to activate...'
                pDialog.update(percent, ' ' + text, remaining_display)
                xbmc.sleep(1000)
                if (pDialog.iscanceled()):
                        cancelled = True
                        break
        if cancelled == True:     
                print 'Request cancelled'
                return False
        else:
                print 'Wait completed. Lets rock'
                return True


def QUEUE_VIDEO(url, name):
        if re.search('AJLBDAJ', name):
                name.replace('AJLBDAJ', '')
                url = loadVideos(url, name, True, True)
                if url == None:
                        d = xbmcgui.Dialog()
                        d.ok('NO VIDEO FOUND', 'This video was removed due to copyright issue.', 'This video is not queued, check other links.')
                        return False
        elif re.search('AJMOVLBDAJ', name):
                name.replace('AJMOVLBDAJ', '')
                url = Movie_loadVideos(url, name, True, True)
                if url == None:
                        d = xbmcgui.Dialog()
                        d.ok('NO VIDEO FOUND', 'This video was removed due to copyright issue.', 'This video is not queued, check other links.')
                        return False
        d = xbmcgui.Dialog()
        d.ok('VIDEO QUEUED', 'The video is added to player queue successfully.', 'Use the same option to queue more videos.')
        
        
def CLEAR_QUEUE(url, name):
        playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playList.clear()
        d = xbmcgui.Dialog()
        d.ok('VIDEO QUEUE CLEARED', 'The XBMC player playlist is cleared successfully.')
                        

def PLAY_QUEUE(url, name):
        playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play(playList)
        if not xbmcPlayer.isPlayingVideo():
                d = xbmcgui.Dialog()
                d.ok('VIDEO QUEUE EMPTY', 'The XBMC video queue is empty.', 'Add more links to video queue.')
        
        
def DOWNLOAD_WITH_JDOWNLOADER(url, name):
        if re.search('AJLBDAJ', name):
                name.replace('AJLBDAJ', '')
                url = loadVideos(url, name, True, False)
                if url == None:
                        d = xbmcgui.Dialog()
                        d.ok('NO VIDEO FOUND', 'This video was removed due to copyright issue.', 'Check other links.')
                        return False
        elif re.search('AJMOVLBDAJ', name):
                name.replace('AJMOVLBDAJ', '')
                url = Movie_loadVideos(url, name, True, False)
                if url == None:
                        d = xbmcgui.Dialog()
                        d.ok('NO VIDEO FOUND', 'This video was removed due to copyright issue.', 'Check other links.')
                        return False
        print 'DOWNLOAD URL = ' + url
        xbmc.executebuiltin('XBMC.RunPlugin(plugin://plugin.program.jdownloader/?action=addlink&url=%s)' % (urllib.quote_plus(url)))
        


def DOWNLOAD_VIDEO(url, name):
        if re.search('AJLBDAJ', name):
                name.replace('AJLBDAJ', '')
                url = loadVideos(url, name, True, False)
                if url == None:
                        d = xbmcgui.Dialog()
                        d.ok('NO VIDEO FOUND', 'This video was removed due to copyright issue.', 'Check other links.')
                        return False
        elif re.search('AJMOVLBDAJ', name):
                name.replace('AJMOVLBDAJ', '')
                url = Movie_loadVideos(url, name, True, False)
                if url == None:
                        d = xbmcgui.Dialog()
                        d.ok('NO VIDEO FOUND', 'This video was removed due to copyright issue.', 'Check other links.')
                        return False
        download_video_file(url, name, False, False)


def DOWNLOAD_QUIETLY(url, name):
        if re.search('AJLBDAJ', name):
                name.replace('AJLBDAJ', '')
                url = loadVideos(url, name, True, False)
                if url == None:
                        d = xbmcgui.Dialog()
                        d.ok('NO VIDEO FOUND', 'This video was removed due to copyright issue.', 'Check other links.')
                        return False
        elif re.search('AJMOVLBDAJ', name):
                name.replace('AJMOVLBDAJ', '')
                url = Movie_loadVideos(url, name, True, False)
                if url == None:
                        d = xbmcgui.Dialog()
                        d.ok('NO VIDEO FOUND', 'This video was removed due to copyright issue.', 'Check other links.')
                        return False
        download_video_file(url, name, True, False)
        
        
def DOWNLOAD_AND_PLAY_VIDEO(url, name):
        if re.search('AJLBDAJ', name):
                name.replace('AJLBDAJ', '')
                url = loadVideos(url, name, True, False)
                if url == None:
                        d = xbmcgui.Dialog()
                        d.ok('NO VIDEO FOUND', 'This video was removed due to copyright issue.', 'Check other links.')
                        return False
        elif re.search('AJMOVLBDAJ', name):
                name.replace('AJMOVLBDAJ', '')
                url = Movie_loadVideos(url, name, True, False)
                if url == None:
                        d = xbmcgui.Dialog()
                        d.ok('NO VIDEO FOUND', 'This video was removed due to copyright issue.', 'Check other links.')
                        return False
        download_video_file(url, name, False, False)
                                
                                
                                
def download_video_file(url, name, isDownloadQuietly=False, playVideo=False):

        downloadFolder = fbn.getSetting('download_folder')

        print 'MYPATH: ' + downloadFolder
        if downloadFolder is '':
                d = xbmcgui.Dialog()
                d.ok('Download Error', 'You have not set the download folder.\n Please set the addon settings and try again.', '', '')
                fbn.openSettings(sys.argv[ 0 ])
        else:
                if not os.path.exists(downloadFolder):
                        print 'Download Folder Doesnt exist. Trying to create it.'
                        os.makedirs(downloadFolder)
                extn = '.flv'
                last = url.rfind(extn)
                if last == -1:
                        extn = '.avi'
                        last = url.rfind(extn)
                        if last == -1:
                                extn = '.mp4'
                                last = url.rfind(extn)
                                if last == -1:
                                        extn = '.flv'
                if last != -1:
                        first = url.rfind('/')
                        newName = url[(first + 1):last]
                        if(newName != ''):
                                name = newName
                
                askFilename = fbn.getSetting('ask_filename')
                if askFilename == 'true':
                        keyb = xbmc.Keyboard('', 'Enter filename')
                        keyb.doModal()
                        if (keyb.isConfirmed()):
                                filenameInput = urllib.quote_plus(keyb.getText())
                                if filenameInput != '':
                                        name = filenameInput
                                else:
                                        name = name[0:25] + ' ' + datetime.utcnow().strftime("%Y-%m-%d %H%M")
                        else:
                                name = name[0:25] + ' ' + datetime.utcnow().strftime("%Y-%m-%d %H%M")
                else:
                        name = name[0:25] + ' ' + datetime.utcnow().strftime("%Y-%m-%d %H%M")
                name = name.replace('\\', '-')
                mypath = os.path.join(downloadFolder, name + extn)
                if os.path.isfile(mypath) is True:
                        d = xbmcgui.Dialog()
                        d.ok('Download Error', 'The video you are trying to download already exists!', '', '')
                else:              
                        print 'About to download file using url = ' + url
                        try:
                                if isDownloadQuietly == False:
                                        downloadSuccess = Download(url, mypath, name)
                                        if downloadSuccess == True and playVideo == True:
                                                xbmcPlayer = xbmc.Player()
                                                xbmcPlayer.play(mypath)
                                                return True
                                else:
                                        Download_Quietly(url, mypath, name)
                        except:
                                print 'download failed'
                                raise


class StopDownloading(Exception): 
        def __init__(self, value): 
                self.value = value 
        def __str__(self): 
                return repr(self.value)
            

def Download(url, dest, displayname=False):
        #get settings
        ok = True
        if displayname == False:
                displayname = url
        deleteIncomplete = fbn.getSetting('del_incomplete_dwnld')
        dp = xbmcgui.DialogProgress()
        dp.create('Downloading', '', displayname)
        print 'downloading will start now and will be saved at = ' + dest
        start_time = time.time() 
        try: 
                urllib.urlretrieve(url, dest, lambda nb, bs, fs: dwnld_percent_hook(nb, bs, fs, dp, start_time, displayname))
        except:
                if deleteIncomplete == 'true':
                #delete partially downloaded file if setting says to.
                        while os.path.exists(dest): 
                                try: 
                                        os.remove(dest) 
                                        break 
                                except: 
                                        pass 
        #only handle StopDownloading (from cancel), ContentTooShort (from urlretrieve), and OS (from the race condition); let other exceptions bubble 
                if sys.exc_info()[0] in (urllib.ContentTooShortError, StopDownloading, OSError): 
                        ok = False
        return ok


def dwnld_percent_hook(numblocks, blocksize, filesize, dp, start_time, filename):
        try: 
                percent = min(numblocks * blocksize * 100 / filesize, 100) 
                currently_downloaded = float(numblocks) * blocksize / (1024 * 1024) 
                kbps_speed = numblocks * blocksize / (time.time() - start_time) 
                if kbps_speed > 0: 
                        eta = (filesize - numblocks * blocksize) / kbps_speed 
                else: 
                        eta = 0 
                kbps_speed = kbps_speed / 1024 
                total = float(filesize) / (1024 * 1024) 
                mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total) 
                e = 'Speed: %.02f Kb/s ' % kbps_speed 
                e += 'ETA: %02d:%02d' % divmod(eta, 60)
                file = 'File: ' + filename
                dp.update(percent, file, mbs, e)
        except: 
                percent = 100 
                dp.update(percent) 
        if dp.iscanceled(): 
                dp.close() 
                raise StopDownloading('Stopped Downloading')


def Download_Quietly(url, dest, displayname=False):
        #get settings
        ok = True
        deleteIncomplete = fbn.getSetting('del_incomplete_dwnld')
        if displayname == False:
                displayname = url
        print 'downloading QUIELTY will start now and will be saved at = ' + dest
        start_time = time.time() 
        try:
                xbmc.executebuiltin("XBMC.Notification(Download started!," + displayname.replace(',', '') + ",5000,http://www.multiglow.com/images/download_icon_small.png)")
                urllib.urlretrieve(url, dest, lambda nb, bs, fs: dwnld_percent_notify(nb, bs, fs, start_time, displayname))
        except:
                if deleteIncomplete == 'true':
                #delete partially downloaded file if setting says to.
                        while os.path.exists(dest): 
                                try: 
                                        os.remove(dest) 
                                        break 
                                except: 
                                        pass 
        #only handle StopDownloading (from cancel), ContentTooShort (from urlretrieve), and OS (from the race condition); let other exceptions bubble 
                xbmc.executebuiltin("XBMC.Notification(Download failed!," + displayname.replace(',', '') + ",1000,http://www.multiglow.com/images/download_icon_small.png)")
                if sys.exc_info()[0] in (urllib.ContentTooShortError, StopDownloading, OSError): 
                        ok = False 
                else: 
                        raise
        if(ok == True):
                xbmc.executebuiltin("XBMC.Notification(Download completed!," + displayname.replace(',', '') + ",5000,http://www.multiglow.com/images/download_icon_small.png)")
        return ok


def dwnld_percent_notify(numblocks, blocksize, filesize, start_time, filename):
        try: 
                percent = min(numblocks * blocksize * 100 / filesize, 100) 
                currently_downloaded = float(numblocks) * blocksize / (1024 * 1024) 
                kbps_speed = numblocks * blocksize / (time.time() - start_time) 
                if kbps_speed > 0: 
                        eta = (filesize - numblocks * blocksize) / kbps_speed 
                else: 
                        eta = 0 
                kbps_speed = kbps_speed / 1024 
                total = float(filesize) / (1024 * 1024) 
                mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total) 
                e = 'Speed: %.02f Kb/s ' % kbps_speed 
                e += 'ETA: %02d:%02d' % divmod(eta, 60)
                file = 'File: ' + filename
                #try:
                #        if [10,20,30,40,50,60,70,80,90].index(percent) > -1:
                #                xbmc.executebuiltin("XBMC.Notification(Dwnld... "+str(percent)+"% :: "+mbs+","+file+",1,http://www.multiglow.com/images/download_icon_small.png)")
                #except IndexError: pass
                #except: raise
        except: 
                percent = 100
         


def addLiveLink(name, url, iconimage):
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={ "Title": name })
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz)
        return ok
        
def addPlayableLiveLink(channelTitle, channelId, mode, channelThumb):
        u = sys.argv[0] + "?url=" + urllib.quote_plus(channelId) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(channelTitle)
        ok = True
        liz = xbmcgui.ListItem(channelTitle, iconImage="DefaultVideo.png", thumbnailImage=channelThumb)
        liz.setInfo(type="Video", infoLabels={ "Title": channelTitle })
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
        return ok

def addPlayableLiveLinkWithOption(channelTitle, channelId, mode, channelThumb, option):
        u = sys.argv[0] + "?url=" + urllib.quote_plus(channelId) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(channelTitle) + "&option=" + urllib.quote_plus(str(option))
        ok = True
        liz = xbmcgui.ListItem(channelTitle, iconImage="DefaultVideo.png", thumbnailImage=channelThumb)
        liz.setInfo(type="Video", infoLabels={ "Title": channelTitle })
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
        return ok
        
def addPlayableLink(name, url, mode, iconimage):
        u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={ "Title": name })
        # adding context menus
        #new name LOAD BEFORE DOWNLOAD AJ
        loadName = name + 'AJLBDAJ'
        contextMenuItems = []
        contextMenuItems.append(('Download', 'XBMC.RunPlugin(%s?mode=10&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(loadName), urllib.quote_plus(url))))
        contextMenuItems.append(('Download and Play', 'XBMC.RunPlugin(%s?mode=12&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(loadName), urllib.quote_plus(url))))
        contextMenuItems.append(('Download Quietly', 'XBMC.RunPlugin(%s?mode=11&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(loadName), urllib.quote_plus(url))))
        #contextMenuItems.append(('Download with JDownloader', 'XBMC.RunPlugin(%s?mode=17&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(loadName), urllib.quote_plus(url))))
        contextMenuItems.append(('Queue Video', 'XBMC.RunPlugin(%s?mode=14&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(loadName), urllib.quote_plus(url))))
        contextMenuItems.append(('Play Video Queue', 'XBMC.RunPlugin(%s?mode=15&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(loadName), urllib.quote_plus(url))))
        contextMenuItems.append(('Clear Video Queue', 'XBMC.RunPlugin(%s?mode=16&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(loadName), urllib.quote_plus(url))))
        
        liz.addContextMenuItems(contextMenuItems, replaceItems=True)
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
        return ok
        

def addPlayableMovieLink(name, url, mode, iconimage):
        u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={ "Title": name })
        # adding context menus
        #new name LOAD BEFORE DOWNLOAD AJ
        loadName = name + 'AJMOVLBDAJ'
        contextMenuItems = []
        contextMenuItems.append(('Download', 'XBMC.RunPlugin(%s?mode=10&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(loadName), urllib.quote_plus(url))))
        contextMenuItems.append(('Download and Play', 'XBMC.RunPlugin(%s?mode=12&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(loadName), urllib.quote_plus(url))))
        contextMenuItems.append(('Download Quietly', 'XBMC.RunPlugin(%s?mode=11&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(loadName), urllib.quote_plus(url))))
        #contextMenuItems.append(('Download  with JDownloader', 'XBMC.RunPlugin(%s?mode=17&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(loadName), urllib.quote_plus(url))))
        contextMenuItems.append(('Queue Video', 'XBMC.RunPlugin(%s?mode=14&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(loadName), urllib.quote_plus(url))))
        contextMenuItems.append(('Play Video Queue', 'XBMC.RunPlugin(%s?mode=15&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(loadName), urllib.quote_plus(url))))
        contextMenuItems.append(('Clear Video Queue', 'XBMC.RunPlugin(%s?mode=16&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(loadName), urllib.quote_plus(url))))
        
        liz.addContextMenuItems(contextMenuItems, replaceItems=True)
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
        return ok
        

def addPlayListLink(name, url, mode, iconimage):
        u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={ "Title": name })
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
        return ok
        

def addDir(name, url, mode, iconimage):
        u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={ "Title": name })
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
        return ok
        
        
def addDirWithLastPageNbr(name, url, mode, iconimage, lastPageNbr):
        u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&lastPageNbr=" + str(lastPageNbr)
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={ "Title": name })
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
        return ok


def addDirWith_YT_Options(name, url, mode, iconimage):
        u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={ "Title": name })
        
        contextMenuItems = []
        contextMenuItems.append(('Remove Channel', 'XBMC.RunPlugin(%s?mode=68&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(name), urllib.quote_plus(url))))
        liz.addContextMenuItems(contextMenuItems, replaceItems=True)
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
        return ok

def saveImgUrlJsonObj():
        global cachedImgUrlJsonObj
        if cachedImgUrlJsonObj != None and len(cachedImgUrlJsonObj) > 0 :
                print 'Saving METADATA JSON obj...'
                if not os.path.exists(xbmc.translatePath(addonDataPath)):
                        print 'Data dir to be created now.'
                        os.makedirs(xbmc.translatePath(addonDataPath))
                cachedFilePath = os.path.join(xbmc.translatePath(addonDataPath), movieImgUrlJsonFile)
                fc = open(cachedFilePath, 'w')
                print json.dump(cachedImgUrlJsonObj, fc, encoding='utf-8')
                fc.close()

def loadImgUrlJsonObj():
        global cachedImgUrlJsonObj
        if cachedImgUrlJsonObj == None or len(cachedImgUrlJsonObj) == 0:
                cachedFilePath = os.path.join(xbmc.translatePath(addonDataPath), movieImgUrlJsonFile)
                if not os.path.exists(cachedFilePath):
                        for oldFileName in oldMovieImgUrlJsonFile:
                                oldFilePath = os.path.join(xbmc.translatePath(addonDataPath), oldFileName)
                                if os.path.exists(oldFilePath):
                                        os.remove(oldFilePath)
                                        print 'OLD METADATA FILE DELETED = ' + oldFilePath
                        cachedFilePath = os.path.join(xbmc.translatePath(addonPath + '/resources'), movieImgUrlJsonFile)
                        if not os.path.exists(cachedFilePath):
                                return None
                        print 'METADATA FILE with add-on will be loaded for the first time.'
                try:
                        fc = open(cachedFilePath, 'r')
                        cachedImgUrlJsonObj = json.load(fc, encoding='utf-8')
                        fc.close()
                        print 'METADATA FILE LOADED'
                except ValueError:
                        os.remove(cachedFilePath)
                        print 'CORRUPTED METADATA FILE DELETED = ' + cachedFilePath
        return cachedImgUrlJsonObj
loadImgUrlJsonObj()

def addDirAndLoadImg(name, url, mode):
        u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
        ok = True
        global cachedImgUrlJsonObj
        
        movieName = ''
        movieYear = ''
        findex = name.find('(')
        if findex != -1:
                movieName = name[0: findex].replace('*BluRay*', '').replace('*HD*', '').replace('DVD', '').replace('HQ', '').strip()
                rindex = name.find(')')
                if(rindex > findex):
                        movieYear = name[findex + 1: rindex].strip()
        elif re.search('2011 - ', name):
                movieYear = '2011'
                movieName = name.replace('2011 - ', '').replace('*BluRay*', '').replace('*HD*', '').replace('DVD', '').replace('HQ', '').strip()
        else:
                movieName = name.replace('2011 - ', '').replace('*BluRay*', '').replace('*HD*', '').replace('DVD', '').replace('HQ', '').strip()
        fanart = ''
        icon = ''
        try:
                movieKey = movieName + '+' + movieYear
                imgInfo = None
                if cachedImgUrlJsonObj != None and len(cachedImgUrlJsonObj) > 0:
                        try:
                                imgInfo = cachedImgUrlJsonObj[movieKey]
                        except KeyError:
                                imgInfo = None
                        
                if imgInfo == None:
                        try:
                                imgInfo = retrieveMovieInfo(movieName, movieYear)
                                if imgInfo != None:
                                        cachedImgUrlJsonObj[movieKey] = imgInfo
                        except:
                                imgInfo = None
                        
                if imgInfo == None or imgInfo['icon'] == None or imgInfo['icon'] == '' or imgInfo['icon'] == 'None':
                        try:
                                imgInfo = retrieveImageSrcFromSominal(url)
                                if imgInfo != None:
                                        cachedImgUrlJsonObj[movieKey] = imgInfo
                        except:
                                imgInfo = None
        
                if not (imgInfo == None or imgInfo['fanart'] == None or imgInfo['fanart'] == '' or imgInfo['fanart'] == 'None'):
                        fanart = imgInfo['fanart']
                if not (imgInfo == None or imgInfo['icon'] == None or imgInfo['icon'] == '' or imgInfo['icon'] == 'None'):
                        icon = imgInfo['icon']
        except: raise
        
        liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=icon)
        liz.setInfo(type="Video", infoLabels={ "Title": name })
        liz.setProperty('fanart_image', fanart)
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
        return ok
    

def retrieveImageSrcFromSominal(url):
        if not re.search('www.sominaltvtheater.com', url):
                return None
        
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        link = ''.join(link.splitlines()).replace('\t', '').replace('\'', '"').replace('<b><b>', '<b>').replace('</b></b>', '</b>').replace(' font-weight: normal;', '')
        imgUrl = re.compile('<div class="cover"><div class="entry">(.+?)</div>').findall(link)
        imgUrl = re.compile('src="(.+?)"').findall(imgUrl[0])[0]
        if(len(imgUrl) > 999):
                return None
        
        imgInfo = {}
        imgInfo['icon'] = imgUrl
        imgInfo['fanart'] = ''
        print 'IMAGE INFO retrieved from Sominal'
        return imgInfo
        
        
#theMovieDb.org API
def retrieveMovieInfo(movieName, movieYear):
        if fbn.getSetting('load_image_from_tmdb') == 'false':
                return
        
        url = 'http://api.themoviedb.org/2.1/Movie.search/en/json/57983e31fb435df4df77afb854740ea9/' + urllib.quote(movieName) + '+' + movieYear
        metaObj = json.load(urllib.urlopen(url))[0]
        #print metaObj
        backdrops = metaObj['backdrops']
        fanart = getImageUrl(backdrops)
        posters = metaObj['posters']
        icon = getImageUrl(posters)
        imgInfo = {}
        imgInfo['icon'] = str(icon)
        imgInfo['fanart'] = str(fanart)
        #print imgInfo
        print 'IMAGE INFO retrieved for movie = ' + movieName
        return imgInfo
        
        
def getImageUrl(images):
        for image in images:
                imageInfo = image['image']
                size = imageInfo['size']
                if size == 'original':
                        return imageInfo['url']
        

# Parse p,a,c,k,e,d string for video URL
def parseValue(p, a, c, k):
        while(c >= 1):
                c = c - 1
                if(k[c]):
                        #p=p.replace(new RegExp('\\b'+c.toString(a)+'\\b','g'),k[c]);
                        base36Str = base36encode(c)
                        p = re.sub('\\b' + base36Str + '\\b', k[c], p)
                        #print k[c] + 'BASE ' + base36Str + 'CONTENT ' + p
        return p


def base36encode(number):
        if not isinstance(number, (int, long)):
                raise TypeError('number must be an integer')
        if number < 0:
                raise ValueError('number must be positive')

        alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'

        base36 = ''
        while number:
                number, i = divmod(number, 36)
                base36 = alphabet[i] + base36

        return base36 or alphabet[0]

def base36decode(number):
        return int(number, 36)


def unescape(url):
        htmlCodes = [
                ['&', '&amp;'],
                ['<', '&lt;'],
                ['>', '&gt;'],
                ['"', '&quot;'],
        ]
        for code in htmlCodes:
                url = url.replace(code[1], code[0])
        return url

def get_redirected_url(url, data):
        opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
        if data == None:
                return opener.open(url).url
        else:
                return opener.open(url, data).url
        

def get_params():
        param = []
        paramstring = sys.argv[2]
        if len(paramstring) >= 2:
                params = sys.argv[2]
                cleanedparams = params.replace('?', '')
                if (params[len(params) - 1] == '/'):
                        params = params[0:len(params) - 2]
                pairsofparams = cleanedparams.split('&')
                param = {}
                for i in range(len(pairsofparams)):
                        splitparams = {}
                        splitparams = pairsofparams[i].split('=')
                        if (len(splitparams)) == 2:
                                param[splitparams[0]] = splitparams[1]
                                
        return param    

params = get_params()
url = None
name = None
mode = None
lastPageNbr = None
option = None

try:
        url = urllib.unquote_plus(params["url"])
except:
        pass
try:
        name = urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode = int(params["mode"])
except:
        pass
try:
        lastPageNbr = int(params["lastPageNbr"])
except:
        pass
try:
        option = urllib.unquote_plus(params["option"])
except:
        pass
                

if mode == None or url == None or len(url) < 1:
        TV()
       
elif mode == 1:
        CHANNELS(url)

elif mode == 2:
        SHOWS(url)

elif mode == 3:
        EPISODES(url)

elif mode == 4:
        PARTS(url) 

elif mode == 5:
        VIDEOLINKS(url, name)
        
elif mode == 6:
        PLAYLIST_VIDEOLINKS(url, name)
        
elif mode == 10:
        DOWNLOAD_VIDEO(url, name)
        
elif mode == 11:
        DOWNLOAD_QUIETLY(url, name)
        
elif mode == 12:
        DOWNLOAD_AND_PLAY_VIDEO(url, name)
        
elif mode == 13:
        LOAD_AND_PLAY_VIDEO(url, name)
        
elif mode == 14:
        QUEUE_VIDEO(url, name)

elif mode == 15:
        PLAY_QUEUE(url, name)

elif mode == 16:
        CLEAR_QUEUE(url, name)
        
elif mode == 17:
        DOWNLOAD_WITH_JDOWNLOADER(url, name)

elif mode == 20:
        MOVIES_MENU(url, name)
        
elif mode == 21:
        MOVIES_BLURAY(url, name)
        
elif mode == 22:
        BM_MOVIES_BY_LANG(url, name)
        
elif mode == 23:
        MORE_MOVIES_HINDI(url, name)

elif mode == 24:
        MORE_MOVIES_TELUGU(url, name)

elif mode == 25:
        MORE_MOVIES_TAMIL(url, name)
        
elif mode == 26:
        BM_MOVIES_A_Z_DIR(url, name)
        
elif mode == 27:
        BM_MOVIES_BY_DECADES(url, name)
        
elif mode == 28:
        BM_LIST(url, name)
        
elif mode == 29:
        BM_VIDEO_SOURCES(url, name)
        
elif mode == 30:
        MOVIE_VIDEO_PARTS(url, name)
        
elif mode == 31:
        MOVIE_LOAD_AND_PLAY_VIDEO(url, name)
        
elif mode == 32:
        MOVIE_PLAYLIST_VIDEOLINKS(url, name)
        
elif mode == 33:
        MOVIE_VIDEOLINKS(url, name)
  
elif mode == 40:
        MUSIC_MENU(url, name)

elif mode == 41:
        MUSIC_VIDEOS(url, name)
        
elif mode == 42:
        MUSIC_VIDEO_PARTS(url, name)
        
elif mode == 43:
        BM_MUSIC_BY_LANG(url, name)
        
elif mode == 44:
        BM_MUSIC_A_Z_DIR(url, name)
        
elif mode == 50:
        WHAT_IS_COMING(url)
        
elif mode == 60:
        YouTube_CHANNELS(url, name)

elif mode == 61:
        YouTube_CHANNEL_PLAYLISTS(url, name, lastPageNbr)

elif mode == 62:
        YouTube_CHANNEL_PLAYLIST_VIDEOS(url, name)
        
elif mode == 63:
        YouTube_CHANNEL_CONTENT(url, name)

elif mode == 64:
        YouTube_CHANNEL_UPLOADS(url, name, lastPageNbr)

elif mode == 65:
        YouTube_AJ_CHANNELS(url, name)
        
elif mode == 66:
        YouTube_MY_CHANNELS(url, name)
        
elif mode == 67:
        YouTube_ADD_NEW_CHANNEL(url, name)
        
elif mode == 68:
        YouTube_REMOVE_CHANNEL(url, name)
        
elif mode == 70:
        YouTube_CHANNEL_SominalTVTheatres(url, name)
        
elif mode == 80:
        Live(url, name)
        
elif mode == 81:
        Live_NDTV(url, name)

elif mode == 82:
        Live_MastTv_Play(url, name)

elif mode == 83:
        Live_CyberViewTv_Play(url, name, option)
        
elif mode == 84:
        Live_MoviesnTV_Play(url, name, option)
        
print '-----------------------------'
for argu in sys.argv:
        print argu
print fbn.getAddonInfo('profile')
saveImgUrlJsonObj()
xbmcplugin.endOfDirectory(int(sys.argv[1]))

                
"""
        elif indexSelect == 2:
                
                channelSelect = d.select('Select LIVE TV package:', ['Indian Channels', 'Pakistan Channels', 'Sports Channels', 'MTA TV'])
                if channelSelect == 0:
                        addPlayableLiveLink ('Star Plus','starplus',82,'http://www.mast.tv/images/starplus.jpg')
                        addPlayableLiveLink ('Zee TV','zeetv',82,'http://www.mast.tv/images/zeetv.jpg')
                        addPlayableLiveLink ('Sony TV','sony',82,'http://www.mast.tv/images/sony.jpg')
                        addPlayableLiveLink ('Zee Cinema','zeecinema',82,'http://www.mast.tv/images/zeecinema.jpg')
                        addPlayableLiveLink ('Colors','colors',82,'http://www.mast.tv/images/colors.jpg')
                        addPlayableLiveLink ('Star Gold','stargold',82,'http://www.mast.tv/images/stargold.jpg')
                        addPlayableLiveLink ('Set Max','setmax',82,'http://www.mast.tv/images/setmax.jpg')
                        addPlayableLiveLink ('NDTV Imagine','ndtvimagen',82,'http://www.mast.tv/images/ndtvimagen.jpg')
                        addPlayableLiveLink ('Sab TV','sabtv',82,'http://www.mast.tv/images/sabtv.jpg')
                        addPlayableLiveLink ('Filmy','filmy',82,'http://www.mast.tv/images/filmy.jpg')
                        addPlayableLiveLink ('ZOOM','zoom',82,'http://www.mast.tv/images/zoom.jpg')
                        addPlayableLiveLink ('9XM','9xm',82,'http://www.mast.tv/images/9xm.jpg')
                        addPlayableLiveLink ('Zing','zing',82,'http://www.mast.tv/images/zing.jpg')
                        addPlayableLiveLink ('Zee Punjabi','zeep',82,'http://www.mast.tv/images/zeep.jpg')
                        addPlayableLiveLink ('mh1','mh1',82,'http://www.mast.tv/images/mh1.jpg')
                        addPlayableLiveLink ('NDTV 24X7','ndtvnews',82,'http://www.mast.tv/images/ndtvnews.jpg')
                        addPlayableLiveLink ('EXPRESS 24X7','expresseng',82,'http://www.mast.tv/images/expresseng.jpg')
                        addPlayableLiveLink ('Peace TV','peace',82,'http://www.mast.tv/images/peace.jpg')
                        
                        #addLiveLink ('HIGH TV','rtmp://94.75.250.212/liverepeater212o1/_definst_/doConnect=3dft4e7rt/ app=liverepeater212o1/_definst_/doConnect=3dft4e7rt/ playpath=78760_OAI6B447LCQ pageurl=http://freedocast.com/forms/watchstream.aspx?sc=5307428231E3214310A0','http://www.letssync.com/_gallery/_freedocast/channellogos/8565/1032581536965.jpg')
                        #addLiveLink ('SVBC', 'rtmp://94.75.250.197/paidrepeater197/ app=paidrepeater197/ playpath=915_IW75622K1P pageurl=http://express.freedocast.com/forms/Fcwatchstream.aspx?sc=31DD213510A2','http://www.lyngsat-logo.com/hires/ss/svbc_in.png')
                        #addLiveLink ('ASIANET', 'rtmp://94.75.250.52/paidrepeater52/1176_UOQ3092FTL swfUrl=http://cdn.freedocast.com/player-octo/playerv2/swfs/broadkastplayer-yupp.swf pageUrl=http://express.freedocast.com/forms/Fcwatchstream.aspx?sc=428231E32135109A','http://images-mediawiki-sites.thefullwiki.org/01/2/5/6/69996214224260213.png')
                
                elif channelSelect == 1:
                        addPlayableLiveLink ('Samaa TV','samatv',82,'http://www.mast.tv/images/samatv.jpg')
                        addPlayableLiveLink ('PTV Home','ptvhome',82,'http://www.mast.tv/images/ptvhome.jpg')
                        addLiveLink ('PTV Home #2','rtmp://live.server4sale.com/live/PTVhome swfUrl=http://www.pakistanvision.com/swfs/videoPlayer.swf swfVfy=true pageUrl=http://ptv.com.pk/PTVHOME-live.asp live=true ','http://www.idesitv.com/images/ptv.png')
                        addPlayableLiveLink ('GEO TV','geotv',82,'http://www.mast.tv/images/geotv.jpg')
                        addPlayableLiveLink ('ARY Digital','arydigital',82,'http://www.mast.tv/images/arydigital.jpg')
                        addPlayableLiveLink ('MASALA','masala',82,'http://www.mast.tv/images/masala.jpg')
                        
                        addPlayableLiveLink ('DAWN News','dawnews',82,'http://www.mast.tv/images/dawnews.jpg')
                        addPlayableLiveLink ('GEO News','geonews',82,'http://www.mast.tv/images/geonews.jpg')
                        addPlayableLiveLink ('Al jajeera','ajjnews',82,'http://www.mast.tv/images/ajjnews.jpg')
                        addPlayableLiveLink ('DUNYA News','dunyanews',82,'http://www.mast.tv/images/dunyanews.jpg')
                        addPlayableLiveLink ('INDUS VISION','indus',82,'http://www.mast.tv/images/indus.jpg')
                        addPlayableLiveLink ('ARY NEWS','arynews',82,'http://www.mast.tv/images/arynews.jpg')
                        addPlayableLiveLink ('HUM TV','humtv',82,'http://www.mast.tv/images/humtv.jpg')
                        addPlayableLiveLink ('INDUS M','indusm',82,'http://www.mast.tv/images/indusm.jpg')
                        addPlayableLiveLink ('NOOR','noor',82,'http://www.mast.tv/images/noor.jpg')
                        addPlayableLiveLink ('ATV','atv',82,'http://www.mast.tv/images/atv.jpg')
                        
                
                elif channelSelect == 2:
                        addPlayableLiveLink ('STAR CRICKET','live-Cric1',82,'http://www.mast.tv/images/live-cric1.jpg')
                        addPlayableLiveLink ('LIVE CRICKET','live-Cric2',82,'http://www.mast.tv/images/live-cric2.jpg')
                        addPlayableLiveLink ('TEN ACTION','live-Cric3',82,'http://www.mast.tv/images/live-cric3.jpg')
                        addPlayableLiveLink ('TEN CRICKET','live-Cric4',82,'http://www.mast.tv/images/live-cric4.jpg')
                        addPlayableLiveLink ('SUPER','live-Cric5',82,'http://www.mast.tv/images/live-cric5.jpg')
                        addPlayableLiveLink ('NEO SPORTS','live-Cric6',82,'http://www.mast.tv/images/live-cric6.jpg')
                        
                elif channelSelect == 3:
                        addLiveLink ('MTA [Urdu]', 'http://ms.mta.tv/mobile.wmv', 'http://www.alislam.org/images/MTA-logo.gif')
                        addLiveLink ('MTA [English]', 'rtsp://ms.mta.tv/English300k', 'http://www.alislam.org/images/MTA-logo.gif')
                        addLiveLink ('MTA3', 'rtsp://62.128.58.133/MTA_High', 'http://www.alislam.org/images/MTA-logo.gif')
                
                return
"""


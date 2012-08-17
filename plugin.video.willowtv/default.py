import urllib,urllib2,urlparse,re,sys,xbmcplugin,xbmcgui
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging,calendar
import xbmcaddon
from xml.dom.minidom import parse, parseString
#Willow TV
wtv=xbmcaddon.Addon(id='plugin.video.willowtv')

addonPath=wtv.getAddonInfo('path')
artPath=addonPath+'/resources/art'
defaultIconImg=os.path.join(xbmc.translatePath( artPath ), "cricket-icon.png")

login = 'https://www.willow.tv/EventMgmt/UserMgmt/Login.asp'
backup_login = 'https://live.willow.tv/EventMgmt/Login.asp'

hostname='http://www.willow.tv'
backup_hostname='http://live.willow.tv'

youtubeChannel='willow'

maxLinksPerPageOption = [15,25,50]

def loginWillowTV(url):
        try:
                print url
                cookiejar = cookielib.LWPCookieJar()
                cookiejar = urllib2.HTTPCookieProcessor(cookiejar) 
                opener = urllib2.build_opener(cookiejar)
                urllib2.install_opener(opener)
                email = wtv.getSetting('email')
                pwd = wtv.getSetting('password')
                values = {'Email': email,'Password': pwd, 'KeepSigned': 'true', 'LoginFormSubmit': 'true'}
                headers = { 'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3' }
                data = urllib.urlencode(values)
                req = urllib2.Request(url, data, headers)
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                web = ''.join(link.splitlines()).replace('\t','').replace('\'','"')
                match=re.compile('Error: Your email or password is incorrect').findall(web)
                if(len(match)>0):
                        d = xbmcgui.Dialog()
                        d.ok('Login Failed', 'Error: Your email or password is incorrect.','Please verify your login details.')
                        return False
                else:
                        return True
        except:
                d = xbmcgui.Dialog()
                d.ok('LOGIN Failed', 'Its not your fault. BREAK TIME!','Please go out of Willow TV and try again.')
                return False


def HOME():
        addDir('My Packages','willow.tv',6,'http://i3.ytimg.com/i/2V_LHwvaNS2XWZ5l8x3jLQ/1.jpg?v=c12daa','')
        addDir('YouTube Channel','willow',20,'http://i3.ytimg.com/i/2V_LHwvaNS2XWZ5l8x3jLQ/1.jpg?v=c12daa','')
        

def MYPACKAGES(url, name):

        try:
                loginCheck = loginWillowTV(login)
                if(loginCheck == False):
                        return False
                xbmc.executebuiltin("XBMC.Notification(Willow TV,Account Login Sucessful,5000,)")
                #LOGIN SUCCESS. Show My Packages. 
                url = 'http://www.willow.tv/EventMgmt/UserMgmt/MyPackages.asp'
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                web = ''.join(link.splitlines()).replace('\t','').replace('\'','"')
                match=re.compile('<table cellspacing=0 cellpadding=0 width="100%"><tr><td><table class="matchListBgClr fontSize80" width=100% cellspacing=1 cellpadding=5><tr><td (.+?)="20%">Event</td><td>(.+?)</td></tr><tr class=MainRow><td>Package</td><td>(.+?)</td></tr><tr class=MainRow><td>Purchase Date</td><td class=MainRow>(.+?)</td></tr><tr><td colspan=2><div id=ShowHideMsg(.+?) align=right><a class=TableLink href=(.+?)><strong>Click here</strong></a> to see Matches included in this Package</div><DIV style="display:none" id=MatchList(.+?)></div></td></tr></table></td></tr><tr><td align=right>Click here to <a class=TableLink href="..(.+?)"><strong>WATCH</strong></a> this event.<br><br></td></tr></table>').findall(web)
                for tmp,event,package,purchaseDate,extra1,extra2,extra3,urlParam in match:
                        iconImg = ''
                        fanart = ''
                        if(event=='ICC World Cup 2011'):
                                fanart=os.path.join(xbmc.translatePath( artPath ), "worldCup2011_fanart1.jpg")
                        addDirWithOption(package,'http://www.willow.tv/EventMgmt'+urlParam,'FALSE',1,iconImg,fanart)
                xbmc.executebuiltin("XBMC.Notification(Willow TV,Account Packages Loaded,5000,)")
        except:
                raise
                xbmc.executebuiltin("XBMC.Notification(Willow TV is DOWN,Please use WILLOW TV [BACKUP PLAN],5000,)")
        fanart=os.path.join(xbmc.translatePath( addonPath ), "fanart.jpg")
        #addDirWithOption('Willow TV [BACKUP PLAN. Use this if failed to see other your Packages]','http://live.willow.tv/EventMgmt/UserMgmt/MatchList.asp','TRUE',1,iconImg,fanart)


def MATCHES(url,name, isBackupPlan):
        if(isBackupPlan == 'TRUE'):
                loginCheck = loginWillowTV(backup_login)
                if(loginCheck == False):
                        return
                xbmc.executebuiltin("XBMC.Notification(BACKTUP Willow TV,Account Login Sucessful,5000,)")
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        web = ''.join(link.splitlines()).replace('\t','').replace('\'','"').replace('style="display:none;"','')
        match=re.compile('<tr class="SeriesMatchRow_(.+?)" ><td class="matchListDataBgClr"><SCRIPT>CXWriteLocalDateTime(.+?);</SCRIPT></td><td class="matchListDataBgClr">(.+?)</td><td class="matchListDataBgClr">(.+?)</tr>').findall(web)
        if len(match) > 0:
                for id, matchDate, matchName, matchURL in match:
                        datetime_obj = time.strptime(matchDate, '("%m/%d/%Y %H:%M:%S %Z")')
                        localMatchDate = time.strftime('(%a, %b %d %Y %I:%M %p)', time.localtime(calendar.timegm(datetime_obj)))
                        addDirWithOption(localMatchDate + ' - [B]' + matchName + '[/B]',matchURL,isBackupPlan,2,'','')
        else:
                
                UPCOMING_MATCH_LIST('http://www.willow.tv/EventMgmt/UserMgmt/FixtureArchiveHelper.asp?eid=160&target=upcoming')
                ARCHIVE_MATCH_LIST('http://www.willow.tv/EventMgmt/UserMgmt/FixtureArchiveHelper.asp?eid=160&target=concluded')

        #xbmc.executebuiltin("XBMC.Notification("+name+",Match List Loaded,5000,)")

def UPCOMING_MATCH_LIST(url,name='', isBackupPlan='FALSE'):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        web = ''.join(link.splitlines()).replace('\t','').replace('\'','"')
        print web
        match=re.compile('<tr toggler="yes" (.+?)CXGetLocalDateTime(.+?);</SCRIPT></a><td class="matchListDataBgClr">(.+?)</td><td class="matchListDataBgClr">(.+?)</td>').findall(web)
        for temp, matchDate, matchName, matchCategories in match:
                datetime_obj = time.strptime(matchDate, '("%m/%d/%Y %H:%M:%S %Z")')
                localMatchDate = time.strftime('(%a, %b %d %Y %I:%M %p)', time.localtime(calendar.timegm(datetime_obj)))
                addDirWithOption(localMatchDate + ' - [B] UPCOMING or LIVE :: ' + matchName + '[/B]',matchCategories,isBackupPlan,13,'','')  
                
                
def UPCOMING_SECTIONS(url,name,isBackupPlan='FALSE'):
        newMatch = re.compile('<a class="TableLink" href="(.+?)">(.+?)</a>').findall(url)
        for videoURL,videoDesc in newMatch:
                if not re.search('scorecard',videoDesc,re.I):
                        videoLabel = ''
                        if re.search('live',videoDesc,re.I):
                                videoLabel = 'LIVE'
                        elif re.search('highlight',videoDesc,re.I):
                                videoLabel = 'Highlights'
                        elif re.search('replay',videoDesc,re.I):
                                videoLabel = 'Replay'
                        if(isBackupPlan == 'TRUE'):
                                addDirWithOption(videoLabel,backup_hostname+unescape(videoURL.replace(backup_hostname,'')),isBackupPlan,3,'','')
                        else:
                                addDirWithOption(videoLabel,hostname+unescape(videoURL.replace(hostname,'')),isBackupPlan,3,'','')
  
                         

def ARCHIVE_MATCH_LIST(url,name='', isBackupPlan='FALSE'):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        print 'MATCHES link == '+url
        web = ''.join(link.splitlines()).replace('\t','').replace('\'','"')
        match=re.compile('<tr class="(.+?)"><td style="text-align:left!important;" id="concludedDateField_(.+?)"><script type="text/javascript">document.getElementById\("concludedDateField_(.+?)"\).innerHTML = CXGetLocalDateTime(.+?);</script></td><td style="text-align:left!important;">(.+?)</td><td style="text-align: right">(.+?)</td></tr>').findall(web)
        for className, id, id2, matchDate, matchName, matchURL in match:
                datetime_obj = time.strptime(matchDate, '("%d %b %Y %H:%M %Z")')
                localMatchDate = time.strftime('(%a, %b %d %Y %I:%M %p)', time.localtime(calendar.timegm(datetime_obj)))
                addDirWithOption(localMatchDate + ' - [B]' + matchName + '[/B]',matchURL,isBackupPlan,12,'','')


def ARCHIVE_SECTIONS(url,name, isBackupPlan):
        newMatch = re.compile('<a href="(.+?)" style="(.+?)"><img src="(.+?)" alt="(.+?)" title="(.+?)" />').findall(url)
        for videoURL,videoStyle,videoImg,videoAlt,videoType in newMatch:
                if(videoAlt != 'Video Scorecard'):
                        if(isBackupPlan == 'TRUE'):
                                addDirWithOption(videoAlt,backup_hostname+unescape(videoURL.replace(backup_hostname,'')),isBackupPlan,3,'','')
                        else:
                                addDirWithOption(videoAlt,hostname+unescape(videoURL.replace(hostname,'')),isBackupPlan,3,'','')


def SECTIONS(url,name, isBackupPlan):
        newMatch = re.compile('<a class="TableLink" href="(.+?)">(.+?)</a>').findall(url)
        for videoURL,videoType in newMatch:
                if(videoType != '(Video Scorecard)'):
                        if(isBackupPlan == 'TRUE'):
                                addDirWithOption(videoType,backup_hostname+unescape(videoURL.replace(backup_hostname,'')),isBackupPlan,3,'','')
                        else:
                                addDirWithOption(videoType,hostname+unescape(videoURL.replace(hostname,'')),isBackupPlan,3,'','')
             
             

def STREAMS(url, name, isBackupPlan):
        loginCheck = False
        if(isBackupPlan == 'TRUE'):
                loginCheck = loginWillowTV(backup_login)
        else:
                loginCheck = loginWillowTV(login)
        if(loginCheck == False):
                return
        #xbmc.executebuiltin("XBMC.Notification(LOADING..,Retreiving available video streams,5000,)")
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        web = ''.join(link.splitlines()).replace('\t','').replace('\'','"')
        match = re.compile('var playlistLength = (.+?);').findall(web)
        option = 1
        if(len(match)==0):
                #addDirWithOption('STREAM VIDEO LINK',url,str(option),4,'','')
                VIDEOLINKS(url,'VIDEO STREAM LINK',str(option), 1)
        else:
                days = re.compile('document.getElementById\("StreamingTitleIndex"\).value=').findall(web)
                totalOptions=int(match[0])
                day = 1
                if len(days) == 0:
                        LOAD_VIDEOLINKS(url, option, totalOptions, web, 1)
                else:
                        totalDays = len(days)
                        while day <= totalDays:
                                addDirWithOption('Match DAY - '+str(day), url, str(option)+'&AJ;'+str(totalOptions)+'&AJ;'+web+'&AJ;'+str(day), 5, '', '')
                                day = day + 1
                        



def DAY_VIDEOLINKS(url, option, totalOptions, web, day, isBackupPlan='FALSE'):
        loginCheck = False
        if(isBackupPlan == 'TRUE'):
                loginCheck = loginWillowTV(backup_login)
        else:
                loginCheck = loginWillowTV(login)
        if(loginCheck == False):
                return
        #xbmc.executebuiltin("XBMC.Notification(LOADING..,Retreiving available video streams,5000,)")
        LOAD_VIDEOLINKS(url, option, totalOptions, web, day)
        
        
def LOAD_VIDEOLINKS(url, option, totalOptions, web, day):
        print 'Total Streaming Options = '+str(totalOptions)
        web = web.replace('"','')
        match = re.compile('<button onclick=document.getElementById\(StreamingServer\).value=(.+?);document.URLOptionsForm.submit\(\); id=(.+?) name=(.+?) class=buttonEnabled type=button>(.+?)</button>').findall(web)
        if(totalOptions == len(match)):
                for streamOption, temp1, temp2, streamName  in match:
                        iconImg=os.path.join(xbmc.translatePath( artPath ), "stream_icon.png")
                        VIDEOLINKS(url,'VIDEO STREAM LINK - '+streamOption+' ['+streamName+']',streamOption, day)
        else:
                while(option <= totalOptions):
                        iconImg=os.path.join(xbmc.translatePath( artPath ), "stream_icon.png")
                        VIDEOLINKS(url,'VIDEO PART - '+str(option),option, day)
                        option = option+1

def VIDEOLINKS(url,name, option, day):
        print url
        link = ''
        try:
                values = {'StreamingServer': option, 'StreamingTitleIndex': day}
                headers = { 'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3' }
                data = urllib.urlencode(values)
                req = urllib2.Request(url, data, headers)
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                #print link
                web = ''.join(link.splitlines()).replace('\t','').replace('\'','"')
                iconImg=os.path.join(xbmc.translatePath( artPath ), "playnow_icon.png")
                #playVideo('PLAY NOW', url, web, iconImg)
                #xbmc.executebuiltin("XBMC.Notification("+name+",Select PLAY NOW to watch video,5000,)")
                playVideo(name, url, web, iconImg)
        except:
                if re.search('YouTube', link):
                        xbmc.executebuiltin("XBMC.Notification(REDIRECTING to YouTube,Using your YouTube user details,2000,)")
                        YouTube_CHANNEL_CONTENT('willow','willow')
                else:
                        xbmc.executebuiltin("XBMC.Notification(STREAM LINK FAILED,Fail to load stream link. Try other links,2000,)")
                
                return False
       
        
        
def playVideo(name, url, web, iconimage):
        ok=True
        flashvarsMatch=re.compile('var flashvars = {};(.+?)var params = {};').findall(web)
        if(len(flashvarsMatch) == 0):
                rtmp_path=re.compile('src: "(.+?)"').findall(web)[0].replace('%26','&')
                print rtmp_path
                #SWFObject=re.compile('plugin_llnwStreamingPlugin: "(.+?)"').findall(web)[0]
                SWFObject = 'http://willow.tv/EventMgmt/scripts/StrobeMediaPlayback.swf'
                print SWFObject
                
                streamURL = rtmp_path + " swfUrl="+SWFObject + " swfVfy=true" + " live=true"
                if(rtmp_path != ''):
                        addLink(name, streamURL, iconimage, '')
                else:
                        d = xbmcgui.Dialog()
                        d.ok('PLAYBACK Failed', 'Connection URL not found.','Please try again later or check logs.')
                
        else:
                flashvars=re.compile('flashvars.(.+?) = "(.+?)";').findall(flashvarsMatch[0])
                flashvarsComment=re.compile('//flashvars.(.+?) = "(.+?)";').findall(flashvarsMatch[0])
                streamURL = ''
                for fname,fvalue in flashvars:
                        for fnameC, fvalueC in flashvarsComment:
                                if(fname != fnameC):
                                        print fname +'='+ fvalue
                                        if(fname == 'File'):
                                                streamURL=fvalue.replace('%26','&')
                                        break
                if(streamURL != ''):
                        addLink(name, streamURL, iconimage, '')
                else:
                        d = xbmcgui.Dialog()
                        d.ok('PLAYBACK Failed', 'Connection URL not found.','Please try again later or check logs.')
                
#YouTube Channel
def YouTube_CHANNEL_PLAYLISTS(url, name):
        urlContent = url.split('&AJ;')
        playListId = urlContent[0]
        
        ifTitleContains=''
        ifTitleNotContains=''
        if(len(urlContent) > 1):
                searchCriterias = urlContent[1].split('&JA;')
                ifTitleContains = searchCriterias[0]
                ifTitleNotContains = searchCriterias[1]
        retrieve_YT_UserPlaylists(playListId, name, 1, 50, 1, ifTitleContains, ifTitleNotContains)

def YouTube_CHANNEL_PLAYLIST_VIDEOS(url, name):
        retrieve_YT_PlaylistVideoLinks(url, name)

def YouTube_CHANNEL_UPLOADS(url, name, lastPageNbr):
        linksPerPage = maxLinksPerPageOption[int(wtv.getSetting('linksPerPage'))]
        startIndex = 1
        if lastPageNbr > 0:
                startIndex = (lastPageNbr * linksPerPage) + 1
        retrieve_YT_UserUploads(url, name, startIndex, linksPerPage, lastPageNbr+1)
        

def YouTube_CHANNEL_LIVE(url, name):
        try:
                req = urllib2.Request('http://www.youtube.com/'+url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                web = ''.join(link.splitlines()).replace('\t','').replace('\'','"')
                #print web
                activeEventsCount = int(re.compile('<div class="title">Active Events \((.+?)\)</div>').findall(web)[0])
                eventCount = 1
                print activeEventsCount
                events = re.compile('id="playnav-event-title-play-live_streaming-0-(.+?)"><span dir="ltr" class="yt-www-ls-event-title">(.+?)</span>').findall(web)
                for id, title in events:
                        videoUrl = 'http://www.youtube.com/watch?v='+id
                        imgUrl = 'http://i2.ytimg.com/vi/'+id+'/default.jpg'
                        print title
                        #print eventCount
                        addYTPlayableMovieLink(title,videoUrl,33,imgUrl)
                        eventCount = eventCount + 1
                        if(eventCount > activeEventsCount):
                                break
        except:
                d = xbmcgui.Dialog()
                d.ok('No ACTIVE live events', 'There are no active LIVE events','Try schedule and check again.')
                return False
        
        

def YouTube_CHANNEL_CONTENT(url, name):
        d = xbmcgui.Dialog()
        index = d.select('Select Category:', ['Uploads','Playlists','LIVE'])
        if index == 0:
                YouTube_CHANNEL_UPLOADS(url, 'Uploads', 0)
        elif index == 1:
                YouTube_CHANNEL_PLAYLISTS(url, 'Playlists')
        elif index == 2:
                YouTube_CHANNEL_LIVE(url, 'LIVE')
                
#######YOUTUBE APIs############

def retrieve_YT_UserInfo(YouTubeUserId):
        url='http://gdata.youtube.com/feeds/api/users/'+YouTubeUserId
        #url='http://gdata.youtube.com/feeds/api/videos/yrvUcOiPb1g'
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        domObj = parseString(link)
        #print domObj.toprettyxml()
        entry = domObj.getElementsByTagName("entry")[0]
        
        userInfo = {}
        userInfo['title'] = getText(entry.getElementsByTagName("title")[0].childNodes)
        userInfo['thumbnail'] = entry.getElementsByTagName("media:thumbnail")[0].getAttribute('url')
        return userInfo
        

def retrieve_YT_UserUploads(YouTubeUserId, name='', startIndex=1, maxCount=50, pageNbr=0):
        url='http://gdata.youtube.com/feeds/api/users/'+YouTubeUserId+'/uploads?v=2&max-results='+str(maxCount) + '&start-index='+str(startIndex)
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        domObj = parseString(link)
        #print domObj.toprettyxml()
        videos=domObj.getElementsByTagName("entry")

        imgUrl = 'http://i.ytimg.com/vi/'+YouTubeUserId+'/default.jpg'
        matchCount = len(videos)
        if(matchCount == 1):
                videoID=getText(videos[0].getElementsByTagName("yt:videoid")[0].childNodes)
                try:
                        addYTPlayableMovieLink(getText(videos[0].getElementsByTagName("title")[0].childNodes),videoID,31,'http://i.ytimg.com/vi/'+videoID+'/default.jpg')
                except KeyError: pass
        elif(matchCount > 1):
                for video in videos:
                        videoTitle = getText(video.getElementsByTagName("title")[0].childNodes)
                        videoID = getText(video.getElementsByTagName("yt:videoid")[0].childNodes)
                        try:
                                addYTPlayableMovieLink(videoTitle,videoID,31,'http://i.ytimg.com/vi/'+videoID+'/default.jpg')
                        except KeyError: pass
                        
        currCountOfVideo = len(videos)
        if(currCountOfVideo == maxCount):
                addYTDirWithLastPageNbr('[B]NEXT PAGE >>[/B]',YouTubeUserId,22,os.path.join(xbmc.translatePath( artPath ), "next-icon.png"), pageNbr)
        if(pageNbr > 1):
                addYTDirWithLastPageNbr('[B]<< PREVIOUS PAGE[/B]',YouTubeUserId,22,os.path.join(xbmc.translatePath( artPath ), "prev-icon.png"), pageNbr-2)


def retrieve_YT_PlaylistVideoLinks(playlistID, playlistTitle='', startIndex=1, maxCount=50, playList='',playListLinksCount=0):
        url='http://gdata.youtube.com/feeds/api/playlists/'+playlistID+'?v=2&max-results='+str(maxCount) + '&start-index='+str(startIndex)
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        domObj = parseString(link)
        #print domObj.toprettyxml()
        videos=domObj.getElementsByTagName("entry")

        imgUrl = 'http://i.ytimg.com/vi/'+playlistID+'/default.jpg'
        i = 1
        matchCount = len(videos)
        if playListLinksCount == 0:
                playListLinksCount = matchCount
        else:
                playListLinksCount = playListLinksCount + matchCount
        
        if(matchCount == 1):
                videoID=getText(videos[0].getElementsByTagName("yt:videoid")[0].childNodes)
                addYTPlayableMovieLink(getText(videos[0].getElementsByTagName("title")[0].childNodes),videoID,31,'http://i.ytimg.com/vi/'+videoID+'/default.jpg')
        elif(matchCount > 1):
                for video in videos:
                        videoTitle = getText(video.getElementsByTagName("title")[0].childNodes)
                        videoID = getText(video.getElementsByTagName("yt:videoid")[0].childNodes)
                        addYTPlayableMovieLink(videoTitle,videoID,31,'http://i.ytimg.com/vi/'+videoID+'/default.jpg')
                        playList = playList + videoID
                        if(i < matchCount or matchCount == maxCount):
                                playList = playList + ':;'
                        i = i + 1
        if(matchCount == maxCount):
                retrieve_YT_PlaylistVideoLinks(playlistID, playlistTitle, startIndex+maxCount, maxCount, playList, playListLinksCount)
        elif(playListLinksCount > 0):
                addYTPlayListLink('[B]Direct PLAY - ' + playlistTitle + '[/B] [I]Playlist of above ' + str(playListLinksCount) + ' videos[/I]',playList,32,imgUrl)
        

def retrieve_YT_UserPlaylists(YouTubeUserId, name='', startIndex=1, maxCount=50, pageNbr=0, ifTitleContains='', ifTitleNotContains=''):
        
        url='http://gdata.youtube.com/feeds/api/users/'+YouTubeUserId+'/playlists?v=2&max-results='+str(maxCount) + '&start-index='+str(startIndex)
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        domObj = parseString(link)
        #print domObj.toprettyxml()
        playlists=domObj.getElementsByTagName("entry")
        for playlist in playlists:
                playListTitle = unicode(getText(playlist.getElementsByTagName("title")[0].childNodes)).encode("utf-8")
                playlistID = getText(playlist.getElementsByTagName("yt:playlistId")[0].childNodes)
                print playListTitle
                if ifTitleContains != '' and not re.search(ifTitleContains, playListTitle):
                        continue
                elif ifTitleNotContains != '' and re.search(ifTitleNotContains, playListTitle):
                        continue
                addDir(playListTitle, playlistID,21,'','')
                
        print len(playlists)
        currCountOfPlayList = len(playlists)
        print maxCount
        if(currCountOfPlayList == maxCount):
                retrieve_YT_UserPlaylists(YouTubeUserId, name, startIndex+maxCount, maxCount, pageNbr, ifTitleContains, ifTitleNotContains)
        #        addYTDirWithLastPageNbr('[B]NEXT PAGE >>[/B]',YouTubeUserId+'&AJ;'+ifTitleContains+'&AJ;'+ifTitleNotContains,61,os.path.join(xbmc.translatePath( artPath ), "next-icon.png"), pageNbr)
        #if(pageNbr > 1):
        #        addYTDirWithLastPageNbr('[B]<< PREVIOUS PAGE[/B]',YouTubeUserId+'&AJ;'+ifTitleContains+'&AJ;'+ifTitleNotContains,61,os.path.join(xbmc.translatePath( artPath ), "prev-icon.png"), pageNbr-2)



def retrieve_YT_UserLiveEvents(YouTubeUserId):
        
        url='http://gdata.youtube.com/feeds/api/users/'+YouTubeUserId+'/live/events?v=2'
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        domObj = parseString(link)
        #print domObj.toprettyxml()
        playlists=domObj.getElementsByTagName("entry")
        for playlist in playlists:
                title = unicode(getText(playlist.getElementsByTagName("title")[0].childNodes)).encode("utf-8")
                videoID = getText(playlist.getElementsByTagName("yt:videoid")[0].childNodes)
                status = getText(playlist.getElementsByTagName("yt:status")[0].childNodes)
                imgUrl = 'http://i.ytimg.com/vi/'+videoID+'/default.jpg'
                if status == 'active':
                        title = '[B]ACTIVE[/B] '+title
                elif status == 'pending':
                        title = '[B]UPCOMING[/B] '+title
                else:
                        continue
                addYTPlayableMovieLink(title,'http://www.youtube.com/watch?v='+videoID,33,imgUrl)
                
        
        
def YouTube_PLAY_PLAYLIST(url,name):
        #xbmc.executebuiltin("XBMC.Notification(PLease Wait!,Loading video links into XBMC Media Player,5000)")
        ok=True
        playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playList.clear()
        #time.sleep(2)
        links = url.split(':;')
        
        pDialog = xbmcgui.DialogProgress()
        ret = pDialog.create('Loading playlist...')
        totalLinks = len(links)
        loadedLinks = 0
        remaining_display = 'Videos loaded :: [B]'+str(loadedLinks)+' / '+str(totalLinks)+'[/B] into XBMC player playlist.'
        pDialog.update(0,'Please wait for the process to retrieve video link.',remaining_display)
                
        for videoLink in links:
                load_YT_Video(videoLink,name,True,True)
                
                loadedLinks = loadedLinks + 1
                percent = (loadedLinks * 100)/totalLinks
                #print percent
                remaining_display = 'Videos loaded :: [B]'+str(loadedLinks)+' / '+str(totalLinks)+'[/B] into XBMC player playlist.'
                pDialog.update(percent,'Please wait for the process to retrieve video link.',remaining_display)
                if (pDialog.iscanceled()):
                        return False
        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play(playList)
        if not xbmcPlayer.isPlayingVideo():
                d = xbmcgui.Dialog()
                d.ok('INVALID VIDEO PLAYLIST', 'The playlist videos were removed due to copyright issue.','Check other links.')
        return ok
        
        
def YouTube_PLAY_VIDEO(url,name):
        ok=True
        print url
        videoUrl = load_YT_Video(url,name,True,False)
        if videoUrl == None:
                d = xbmcgui.Dialog()
                d.ok('VIDEO UNAVAILABLE', 'This video is not available to view through this add-on.','Try to access link directly.')
                return False
        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play(videoUrl)
        return ok


def YouTube_PLAY_LIVE_VIDEO(url, name):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        #print link
        #videoUrl = load_YT_Video(url,name,True,False)
        loginUrl = re.compile('href="https://accounts.google.com/ServiceLogin(.+?)">Sign In</a>').findall(link)[0]
        loginCookie = loginYouTube('https://accounts.google.com/ServiceLogin'+loginUrl.replace('&amp;','&'))
        videoUrl = None
        videoUrl_sec = None
        if loginCookie != None:
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                link = link.replace('\\u0026','&')
                #print link
                if re.search('url_encoded_fmt_stream_map', link):
                        map = None
                        match=re.compile('url_encoded_fmt_stream_map=(.+?)&').findall(link)
                        if len(match) == 0:
                                map=(re.compile('url_encoded_fmt_stream_map": "(.+?)"').findall(link)[0]).replace('\\/', '/').split('url=')
                        else:
                                map=urllib.unquote(match[0]).decode('utf8').split('url=')
                        videoUrl = resolve_YT_Video(map, name, True, False,'',True)
                        
                else:
                        map = None
                        match=re.compile('fmt_stream_map=(.+?)&').findall(link)
                        if len(match) == 0:
                                map=(re.compile('fmt_stream_map": "(.+?)"').findall(link)[0]).replace('\\/', '/').split('url=')
                        else:
                                map=urllib.unquote(match[0]).decode('utf8').split('url=')
                        
                        videoUrl = resolve_YT_Video(map, name, True, False,'',True)
                
                #print videoUrl
                
                if videoUrl == None and videoUrl_sec == None:
                        d = xbmcgui.Dialog()
                        d.ok('VIDEO UNAVAILABLE', 'This video is not available to view through this add-on.','Try to access link directly.')
                        return False
                cookies = ''
                for cookie in loginCookie:
                        #print cookie.name
                        #print cookie.value
                        cookies = cookies + cookie.name + '=' + cookie.value + '; '
                #print 'FINAL COOKIE' + cookies
                xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
                xbmcPlayer.play(videoUrl+'|User-Agent='+urllib.quote_plus('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')+'&Referer='+urllib.quote_plus(url)+'&Cookie='+urllib.quote_plus(cookies))
                

def loginYouTube(url):
        try:
                email = wtv.getSetting('yt_email')
                pwd = wtv.getSetting('yt_password')
                if (not email or email == '') or (not pwd or pwd == ''):
                        d = xbmcgui.Dialog()
                        d.ok('Provide YouTube account details', 'To watch LIVE CRICKET on your favorite Willow TV,','please provide your login details for YouTube account linked to Willow TV.')
                        wtv.openSettings(sys.argv[ 0 ]) 
                        email = wtv.getSetting('yt_email')
                        pwd = wtv.getSetting('yt_password')
                from mechanize import ParseResponse
                
                cookiejar = cookielib.LWPCookieJar()
                http_cookiejar = urllib2.HTTPCookieProcessor(cookiejar) 
                opener = urllib2.build_opener(http_cookiejar)
                urllib2.install_opener(opener)
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                urllib2.HTTPSHandler(debuglevel=1)
                response = urllib2.urlopen(req)
                forms = ParseResponse(response, backwards_compat=False)
                response.close()
                form = forms[0]
                form['Passwd'] = pwd
                form['Email'] = email
                req = form.click()
                response = urllib2.urlopen(req)
                web = response.read()
                if re.search('Enter the verification code',web,re.I):
                    response = urllib2.urlopen(req)
                    forms = ParseResponse(response, backwards_compat=False)
                    response.close()
                    form = forms[0]
                    keyb = xbmc.Keyboard()
                    keyb.setHeading('Please provide 2-step verification PIN:')
                    keyb.doModal()
                    code = None
                    if (keyb.isConfirmed()):
                            code = keyb.getText()
                    if code is None:
                            d = xbmcgui.Dialog()
                            d.ok('YouTube login failed', 'Cannot proceed without verification code.','Process has been cancelled by user.')
                            return None
                    form["smsUserPin"] = code
                    req = form.click()
                    response = urllib2.urlopen(req)
                    forms = ParseResponse(response, backwards_compat=False)
                    response.close()
                    form = forms[0]
                    req = form.click()
                    response = urllib2.urlopen(req)
                    web = response.read()
                while re.search('<title>Redirecting</title>', web):
                
                        redirect_re = re.compile('<meta http-equiv="refresh" content="0; url=\&\#39;(.+?)\&\#39;"')
                        # check for redirect meta tag
                        match = redirect_re.search(web)
                        if match:
                                url = redirect_re.findall(web)[0].replace('&amp;','&')
                        else:
                                url = None
                                break
                        req = urllib2.Request(url)
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                        response = urllib2.urlopen(req)
                        web=response.read()
                        response.close()
                
                return cookiejar
        except:
                raise
                d = xbmcgui.Dialog()
                d.ok('YouTube login failed', 'Please opt for 2-step authentication method of google','You should check if you have provided correct username and password')
                return None



def load_YT_Video(code,name,isRequestForURL,isRequestForPlaylist):
        print 'YT VIDEO ID = '+ code
        
        #YOUTUBE
        try:
                linkImage = 'http://i.ytimg.com/vi/'+code+'/default.jpg'
                req = urllib2.Request('http://www.youtube.com/watch?v='+code+'&fmt=18')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                
                if len(re.compile('shortlink" href="http://youtu.be/(.+?)"').findall(link)) == 0:
                        if len(re.compile('\'VIDEO_ID\': "(.+?)"').findall(link)) == 0:
                                req = urllib2.Request('http://www.youtube.com/get_video_info?video_id='+code+'&asv=3&el=detailpage&hl=en_US')
                                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                                response = urllib2.urlopen(req)
                                link=response.read()
                                response.close()
                map = None
                link = link.replace('\\u0026','&')
                match=re.compile('url_encoded_fmt_stream_map=(.+?)&').findall(link)
                if len(match) == 0:
                        map=(re.compile('url_encoded_fmt_stream_map": "(.+?)"').findall(link)[0]).replace('\\/', '/').split('url=')
                else:
                        map=urllib.unquote(match[0]).decode('utf8').split('url=')
                if re.search('status=fail', link):
                        return
                if map == None:
                        return
                #print map
                return resolve_YT_Video(map, name,isRequestForURL,isRequestForPlaylist,linkImage)

        except: pass
        

def resolve_YT_Video(map, name,isRequestForURL,isRequestForPlaylist,linkImage,selectVideoQual=False):
        try:
                
                highResoVid = ''
                youtubeVideoQual = wtv.getSetting('videoQual')
                #print map
                videoQuals = []
                videoLinks = []
                for attr in map:
                        if attr == '':
                                continue
                        parts = attr.split('&qual')
                        url = urllib.unquote(parts[0]).decode('utf8')
                        qual = re.compile('&itag=(\d*)').findall(url)[0]
                        print qual
                        
                                
                        if(qual == '13'):
                                if(selectVideoQual):
                                        videoQuals.append('LOW 3GP')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY 3GP Low Quality - 176x144',url,linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        elif(qual == '17'):
                                if(selectVideoQual):
                                        videoQuals.append('SD 3GP')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY 3GP Medium Quality - 176x144',url,linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        elif(qual == '36'):
                                if(selectVideoQual):
                                        videoQuals.append('HD 3GP')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY 3GP High Quality - 320x240',url,linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        elif(qual == '5'):
                                if(selectVideoQual):
                                        videoQuals.append('LOW FLV')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY FLV Low Quality - 400\\327226',url,linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        elif(qual == '34'):
                                if(selectVideoQual):
                                        videoQuals.append('SD 480p FLV')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY FLV Medium Quality - 480x360',url,linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        elif(qual == '6'):
                                if(selectVideoQual):
                                        videoQuals.append('SD 640p FLV')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY FLV Medium Quality - 640\\327360',url,linkImage)
                                elif(highResoVid == ''):
                                        highResoVid = url
                        elif(qual == '35'):
                                if(selectVideoQual):
                                        videoQuals.append('SD FLV')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY FLV High Quality - 854\\327480',url,linkImage)
                                else:
                                        highResoVid = url
                        elif(qual == '18'):
                                if(selectVideoQual):
                                        videoQuals.append('SD 480p MP4')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY MP4 High Quality - 480x360',url,linkImage)
                                else:
                                        highResoVid = url
                                        
                        elif(qual == '22'):
                                if(selectVideoQual):
                                        videoQuals.append('HD 720p MP4')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY MP4 High Quality - 1280x720',url,linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '1' or youtubeVideoQual == '2':
                                                break
                        elif(qual == '37'):
                                if(selectVideoQual):
                                        videoQuals.append('HD 1080p MP4')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY MP4 High-2 Quality - 1920x1080',url,linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '2':
                                                break
                        elif(qual == '38'):
                                if(selectVideoQual):
                                        videoQuals.append('HD 4096p WEBM')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY MP4 Epic Quality - 4096\\3272304',url,linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '2':
                                                break
                        elif(qual == '43'):
                                if(selectVideoQual):
                                        videoQuals.append('HD 4096p WEBM')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY WEBM Medium Quality - 4096\\3272304',url,linkImage)
                                else:
                                        highResoVid = url
                        elif(qual == '44'):
                                if(selectVideoQual):
                                        videoQuals.append('HD 4096p WEBM')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY WEBM High Quality - 4096\\3272304',url,linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '1' or youtubeVideoQual == '2':
                                                break
                        elif(qual == '45'):
                                if(selectVideoQual):
                                        videoQuals.append('HD 4096p WEBM')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY WEBM High-2 Quality - 4096\\3272304',url,linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '2':
                                                break
                        elif(qual == '120'):
                                if(selectVideoQual):
                                        videoQuals.append('HD 720p Fast')
                                        videoLinks.append(url)
                                elif(not(isRequestForURL)):
                                        addLink ('PLAY HD Video Quality',url,linkImage)
                                else:
                                        highResoVid = url
                                        if youtubeVideoQual == '1' or youtubeVideoQual == '2':
                                                break
                
                if(selectVideoQual):
                        d = xbmcgui.Dialog()
                        index = d.select('Select video quality:', videoQuals)
                        if index == -1:
                                return None
                        highResoVid = videoLinks[index]
                if(isRequestForURL):
                        if(isRequestForPlaylist):
                                liz = xbmcgui.ListItem('VIDEO PART', thumbnailImage=linkImage)
                                xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(url = highResoVid, listitem=liz)
                                return highResoVid
                        else:
                                return highResoVid

        except: pass
                        		
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


def addLink(name,url,iconimage,fanart=''):
        if(iconimage == ''):
                iconimage = defaultIconImg
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        if(fanart==''):
                fanart=os.path.join(xbmc.translatePath( artPath ), "worldCup2011_fanart2.jpg")
        liz.setProperty('fanart_image',fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


def addDir(name,url,mode,iconimage,fanart):
        if(iconimage == ''):
                iconimage = defaultIconImg
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        if(fanart==''):
                fanart=os.path.join(xbmc.translatePath( artPath ), "worldCup2011_fanart2.jpg")
        liz.setProperty('fanart_image',fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok


def addDirWithOption(name,url,option,mode,iconimage,fanart):
        if(iconimage == ''):
                iconimage = defaultIconImg
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&option="+urllib.quote_plus(option)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        if(fanart==''):
                fanart=os.path.join(xbmc.translatePath( artPath ), "worldCup2011_fanart2.jpg")
        liz.setProperty('fanart_image',fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        
def addYTDirWithLastPageNbr(name,url,mode, iconimage, lastPageNbr):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&lastPageNbr="+str(lastPageNbr)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        

def addYTPlayableMovieLink(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        print 'u = ' + u
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok
        

def addYTPlayListLink(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

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

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param


def check_settings():
        email = wtv.getSetting('email')
        pwd   = wtv.getSetting('password')
        if (not email or email == '') or (not pwd or pwd == ''):
                d = xbmcgui.Dialog()
                d.ok('Welcome to Willow TV', 'To watch LIVE CRICKET on your favorite Willow TV,','please provide your login details for both Willow TV and YouTube.')
                wtv.openSettings(sys.argv[ 0 ]) 

params=get_params()
url=None
name=None
option=None
mode=None
lastPageNbr=None

check_settings()
email = wtv.getSetting('email')
pwd = wtv.getSetting('password')

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        option=params["option"]
except:
        pass
try:
        lastPageNbr=int(params["lastPageNbr"])
except:
        pass

if mode==None or url==None or len(url)<1:
        HOME()

elif mode==1:
        MATCHES(url,name,option)

elif mode==2:
        SECTIONS(url,name,option)

elif mode==3:
        STREAMS(url,name,option)

elif mode==4:
        VIDEOLINKS(url,name,option)
        
elif mode==5:
        options = option.split('%26AJ%3B')
        DAY_VIDEOLINKS(url, int(options[0]), int(options[1]), options[2], int(options[3]))

elif mode==6:
        MYPACKAGES(url,name)
        
elif mode==11:
        ARCHIVE_MATCH_LIST(url,name,option)

elif mode==12:
        ARCHIVE_SECTIONS(url,name,option)
        
elif mode==13:
        UPCOMING_SECTIONS(url,name,option)
        
elif mode==20:
        YouTube_CHANNEL_CONTENT(url, name)

elif mode==21:
        YouTube_CHANNEL_PLAYLIST_VIDEOS(url, name)

elif mode==22:
        YouTube_CHANNEL_UPLOADS(url, name, lastPageNbr)

elif mode==31:
        YouTube_PLAY_VIDEO(url, name)
        
elif mode==32:
        YouTube_PLAY_PLAYLIST(url, name)
        
elif mode==33:
        YouTube_PLAY_LIVE_VIDEO(url, name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))

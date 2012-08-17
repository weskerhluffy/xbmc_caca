import urllib,urllib2,re,sys,xbmcplugin,xbmcgui
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging,calendar
import xbmcaddon
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json

#stageVU
svu=xbmcaddon.Addon(id='plugin.video.stagevu')

addonPath=os.getcwd()
artPath=addonPath+'/resources/art'
defaultIconImg=os.path.join(xbmc.translatePath( addonPath ), "icon_white.png")
addonSettings = xbmcaddon.Addon(id='plugin.video.stagevu')
categories = ["Any","Animation","Art","Blogs","Comedy","Educational","Games","Music","News and Politics","Mature","Sports","Others"]
languages = ["Any","English","Arabic","Chinese (Mandarin)","Chinese (Cantonese)","French","German","Hindi","Japanese","Russian","Spanish","Amharic","Arabic","Assamese","Azerbaijani","Bengali","Bhojpuri","Burmese","Cebuano","Chinese (Cantonese)","Chinese (Mandarin)","Czech","Dutch","English","Filipino","French","Fula","Gan","German","Greek","Gujarati","Hakka","Hausa","Hindi","Hungarian","Igbo","Indonesian","Italian","Japanese","Javanese","Kannada","Khmer","Korean","Kurdish","Language","Lao","Madurese","Maithili","Malagasy","Malay","Malayalam","Marathi","Nepali","Oriya","Oromo","Pashto","Persian","Polish","Portuguese","Punjabi","Romanian","Russian","Serbo-Croatian","Shona","Sindhi","Sinhalese","Somali","Spanish","Sundanese","Tamazight","Tamil","Telugu","Thai","Turkish","Ukrainian","Uzbek","Vietnamese","Other/None"]
videoLength = ["Any","3","15","30","45","60","90","120"]

def LOGIN():
        urlogin = 'http://stagevu.com/ajax/login.php'
        cookiejar = cookielib.LWPCookieJar()
        cookiejar = urllib2.HTTPCookieProcessor(cookiejar) 
        opener = urllib2.build_opener(cookiejar)
        urllib2.install_opener(opener)
        email = wtv.getSetting('email')
        pwd = wtv.getSetting('password')
        values = {'Email': email,'Password': pwd, 'KeepSigned': 'true', 'LoginFormSubmit': 'true'}
        headers = { 'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3' }
        data = urllib.urlencode(values)
        req = urllib2.Request(urlogin, data, headers)
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


def HOME():
        #loginCheck = LOGIN()
        #if(loginCheck == False):
        #        return False
        #xbmc.executebuiltin("XBMC.Notification(Stage VU,Account Login Sucessful,5000,)")
        #LOGIN SUCCESS. Show My Packages.
        categoryIcon = os.path.join(xbmc.translatePath( artPath ), 'categories-icon.png')
        addDir('CATEGORIES','http://stagevu.com/index',6,categoryIcon,'')
        searchIcon = os.path.join(xbmc.translatePath( artPath ), 'search-icon.png')
        addDir('SEARCH [By Videos]','http://stagevu.com/search?x=0&y=0&in=Videos',1,searchIcon,'')
        #addDir('* SEARCH [CHANNELS]','http://stagevu.com/chansearch?x=0&y=0&in=Channels',1,searchIcon,'')
        addDir('SEARCH [By Tags]','http://stagevu.com/search?x=0&y=0&in=Tags',1,searchIcon,'')
        addDir('ADVANCED SEARCH','http://stagevu.com/search?minsec=&maxmin=&maxsec=&maxrating=&width=&height=',2,searchIcon,'')
        
        
def SEARCH(url,name):
        keyb = xbmc.Keyboard('', '[B]Search[/B]')
        keyb.doModal()
        if (keyb.isConfirmed()):
                search = urllib.quote_plus(keyb.getText())
                url = url + '&for='+search
                parseVideoResults(url)
        

def ADVANCEDSEARCH(url,name):
        xbmc.executebuiltin("XBMC.Notification(ADVANCED Search Settings ,For better results set default values in Add-on Settings,5000)")
        keywords = ''
        if(svu.getSetting('enable_keywords') == '0'):
                keyb = xbmc.Keyboard('', 'enter [B]Keywords[/B]')
                keyb.doModal()
                if (keyb.isConfirmed()):
                        keywords = urllib.quote_plus(keyb.getText())
        elif(svu.getSetting('enable_keywords') != '2'):
                keywords = svu.getSetting('keywords')
        url = url + '&keywords='+keywords
        print url
        
        tags = ''
        if(svu.getSetting('enable_tags') == '0'):
                keyb = xbmc.Keyboard('', 'enter [B]Tags[/B] [I]separated by commas(,)[/I]')
                keyb.doModal()
                if (keyb.isConfirmed()):
                        tags = urllib.quote_plus(keyb.getText())
        elif(svu.getSetting('enable_tags') != '2'):
                tags = svu.getSetting('tags')
        url = url + '&tags='+tags
        print url
        
        submitter = ''
        if(svu.getSetting('enable_submitter') == '0'):
                keyb = xbmc.Keyboard('', 'enter [B]Submitted By[/B]')
                keyb.doModal()
                if (keyb.isConfirmed()):
                        submitter = urllib.quote_plus(keyb.getText())
        elif(svu.getSetting('enable_submitter') != '2'):
                submitter = svu.getSetting('submitter')
        url = url + '&submitter='+submitter
        print url
        
        category = categories[int(svu.getSetting('category'))]
        if(category == 'Any'):
                category = ''
        url = url + '&category='+category
        print url
        
        minmin = videoLength[int(svu.getSetting('minmin'))]
        if(minmin == 'Any'):
                minmin = ''
        url = url + '&minmin='+minmin
        print url
        
        
        minrating = svu.getSetting('minrating')
        if(minrating == '0'):
                minrating = ''
        url = url + '&minrating='+minrating
        print url
        
        language = languages[int(svu.getSetting('language'))]
        if(language == 'Any'):
                language = ''
        url = url + '&language='+language
        print url
        
        xbmc.executebuiltin("XBMC.Notification(Using Advanced Search settings, For better and quick results set default values in Addon Settings,5000)")
        
        #d = xbmcgui.Dialog()
        #d.ok('Advanced Search', 'Some pre-defined search criteria values',  'are picked from Addon Settings.')
        parseVideoResults(url)
        

def CATEGORIES(url,name):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        web = ''.join(link.splitlines()).replace('\t','').replace('\'','"')
        match=re.compile('<li><a href="http://stagevu.com/videos/(.+?)">(.+?)</a></li>').findall(web)
        for urlParam,categoryName in match:
                addDir(categoryName,'http://stagevu.com/videos/'+urlParam,3,'','')

def CATEGORY(url,name):
       parseVideoResults(url)
       
       
def parseVideoResults(url):
       req = urllib2.Request(url)
       req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
       response = urllib2.urlopen(req)
       link=response.read()
       response.close()
       parseVideoLinks(link, '')
       
       
def parseVideoLinks(data, jsonObj):
       web = ''.join(data.splitlines()).replace('\t','').replace('\'','"').replace('v[1]["page"]','')
       match=re.compile('<div class="resultcont">(.+?)</div></div>').findall(web)
       xbmc.executebuiltin("XBMC.Notification(LOADING...,Retrieving video links from stagevu,5000)")
       if(len(match) == 0):
              d = xbmcgui.Dialog()
              d.ok('No results found', 'Modify your search criteria or update','Advanced Search in Add-on Setting')
              
       for searchResult in match:
              videoLink = re.compile('<h2><a href="http://stagevu.com/video/(.+?)">(.+?)</a>').findall(searchResult)
              info=re.compile('<span class="bold">(.+?)</span>(.+?);').findall(searchResult)
              videoInfo = '['
              for infoParamName, infoParamVal in info:
                     videoInfo = videoInfo + '('+infoParamName+infoParamVal+')'
              rating = re.compile('<span class="bold">Rating:</span> <img src="(.+?)" alt="(.+?)" />').findall(searchResult)
              name = videoLink[0][1][0:25] + '... ' + videoInfo + '(Rating :' +rating[0][1]+ ')]'
              #addDir(name,'http://stagevu.com/video/'+videoLink[0][0],4,'http://stagevu.com/img/thumbnail/'+videoLink[0][0]+'big.jpg','')
              try:
                     VIDEOLINK('http://stagevu.com/video/'+videoLink[0][0],name)
              except:
                     pass
              
       match=re.compile('<a class="newest" href="#" onclick=" = (.+?);').findall(web)
       firstPage = 0
       if(len(match) > 0):
              firstPage = int(match[0])
       print 'First Page = '+str(firstPage)

       match=re.compile('<a class="oldest" href="#" onclick=" = (.+?);').findall(web)
       lastPage = 0
       if(len(match) > 0):
              lastPage = int(match[0])
       print 'Last Page = '+str(lastPage)
       
       if(lastPage == 0 and firstPage == 0):
              return

       if(jsonObj == ''):
              jsonObj = parseJsonObj(web)
       currentPage = int(jsonObj['page'])
       print 'Current Page = '+str(currentPage)
       
       
       if(firstPage > 0):
              firstIcon = os.path.join(xbmc.translatePath( artPath ), 'first-icon.png')
              addPageLink("<<<FIRST PAGE<", jsonObj, firstPage, firstIcon)
       if(currentPage - firstPage > 1):
              prevIcon = os.path.join(xbmc.translatePath( artPath ), 'prev-icon.png')
              addPageLink("<<PREVIOUS PAGE: "+str(currentPage-1)+"<", jsonObj, currentPage-1, prevIcon)
       if(lastPage - currentPage > 1):
              nextIcon = os.path.join(xbmc.translatePath( artPath ), 'next-icon.png')
              addPageLink(">NEXT PAGE: "+str(currentPage+1)+">>", jsonObj, currentPage+1, nextIcon)
       if(lastPage > 0):
              lastIcon = os.path.join(xbmc.translatePath( artPath ), 'last-icon.png')
              addPageLink(">LAST PAGE: "+str(lastPage)+">>>", jsonObj, lastPage, lastIcon)
              
       #xbmc.executebuiltin("Container.SetViewMode(500)")


def addPageLink(name, jsonObj, page, icon):
       jsonObj['page']=str(page)
       searchData64 = base64.b64encode(json.dumps(jsonObj))
       addDir(name,searchData64,5,icon,'')


def parseJsonObj(web):
       match=re.compile('scriptid: (.+?),').findall(web)
       
       scriptId = ''
       if len(match) > 0:
              scriptId = match[0]
       print scriptId

       classVar = ''
       match=re.compile('"class": "(.+?)",').findall(web)
       if len(match) > 0:
              classVar = match[0]
       print classVar

       template = ''
       match=re.compile('template: "(.+?)",').findall(web)
       if len(match) > 0:
              template = match[0]
       print template

       descriptionlen = ''
       match=re.compile('descriptionlen: (.+?),').findall(web)
       if len(match) > 0:
              descriptionlen = match[0]
       print descriptionlen

       boxwidth = ''
       match=re.compile('boxwidth: (.+?),').findall(web)
       if len(match) > 0:
              boxwidth = match[0]
       print boxwidth

       serialized = ''
       match=re.compile('serialized: "(.+?)",').findall(web)
       if len(match) > 0:
              serialized = match[0]
       print serialized

       perpage = ''
       match=re.compile('perpage: (.+?),').findall(web)
       if len(match) > 0:
              perpage = match[0]
       print perpage

       page = ''
       match=re.compile(',page: (.+?)').findall(web)
       if len(match) > 0:
              page = match[0]
       print page


       data={'scriptid': '%s'%scriptId,
              'class': '%s'%classVar,
              'template': '%s'%template,
              'descriptionlen': '%s'%descriptionlen,
              'boxwidth': '%s'%boxwidth,
              'serialized': '%s'%serialized,
              'perpage': '%s'%perpage,
              'page': '%s'%page}

       return json.loads(json.dumps(data))


def GOTOPAGE(url,name):
       searchData=base64.b64decode(url)
       params= 'settings='+searchData
       url='http://stagevu.com/ajax/getgenericsearch.php'
       req = urllib2.Request(url,params)
       req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
       response = urllib2.urlopen(req)
       link=response.read()
       response.close()
       obj=json.loads(json.loads(json.dumps(link)))
       link=obj['display']
       parseVideoLinks(link, json.loads(searchData))


def VIDEOLINK(url,name):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        web = ''.join(link.splitlines()).replace('\t','').replace('\'','"')
        match=re.compile('<param name="src" value="(.+?)"(.+?)<param name="movieTitle" value="(.+?)"(.+?)<param name="previewImage" value="(.+?)"').findall(web)
        #addLink('*PLAY* - ' + match[0][2],match[0][0],match[0][4],'')
        addLink(unescape(name),match[0][0],match[0][4],'')
        
        
def DOWNLOAD_VIDEO(url,name):
        download_video_file(url,name, False, False)

def DOWNLOAD_QUIETLY(url,name):
        download_video_file(url,name, True, False)
        
def DOWNLOAD_AND_PLAY_VIDEO(url,name):
        download_video_file(url,name, False, True)
                                
                                
def download_video_file(url,name, isDownloadQuietly = False, playVideo = False):

        downloadFolder = svu.getSetting('download_folder')

        print 'MYPATH: '+downloadFolder
        if downloadFolder is '':
                d = xbmcgui.Dialog()
                d.ok('Download Error','You have not set the download folder.\n Please set the addon settings and try again.','','')
                svu.openSettings(sys.argv[ 0 ])
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
                        newName = url[(first+1):last]
                        if(newName != ''):
                                name = newName
                
                askFilename=svu.getSetting('ask_filename')
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
                name = name.replace('\\','-')
                mypath=os.path.join(downloadFolder,name + extn)
                if os.path.isfile(mypath) is True:
                        d = xbmcgui.Dialog()
                        d.ok('Download Error','The video you are trying to download already exists!','','')
                else:              
                        print 'About to download file using url = '+url
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
                displayname=url
        deleteIncomplete=svu.getSetting('del_incomplete_dwnld')
        dp = xbmcgui.DialogProgress()
        dp.create('Downloading', '', displayname)
        print 'downloading will start now and will be saved at = '+dest
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
                        ok=False
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
                file = 'File: '+filename
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
        deleteIncomplete=svu.getSetting('del_incomplete_dwnld')
        if displayname == False:
                displayname=url
        print 'downloading QUIELTY will start now and will be saved at = '+dest
        start_time = time.time() 
        try:
                xbmc.executebuiltin("XBMC.Notification(Download started!,"+displayname+",5000)")
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
                xbmc.executebuiltin("XBMC.Notification(Download failed!,"+displayname+",5000)")
                if sys.exc_info()[0] in (urllib.ContentTooShortError, StopDownloading, OSError): 
                        ok=False 
                else: 
                        raise
        if(ok == True):
                xbmc.executebuiltin("XBMC.Notification(Download complete!,"+displayname+",5000)")
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
                file = 'File: '+filename
                #xbmc.executebuiltin("XBMC.Notification(Downloading "+percent+"%,"+displayname+",2000)")
        except: 
                percent = 100
                

def addLink(name,url,iconimage,fanart):
        if(iconimage == ''):
                iconimage = defaultIconImg
        ok=True
        playIcon = os.path.join(xbmc.translatePath( artPath ), 'play.png')
        liz=xbmcgui.ListItem(name, iconImage=playIcon, thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty( "Video", "true" )
        liz.setProperty( "IsPlayable", "true");
        if(fanart==''):
                fanart=os.path.join(xbmc.translatePath( addonPath ), "fanart.jpg")
        liz.setProperty('fanart_image',fanart)
        
        # adding context menus
        contextMenuItems = []
        contextMenuItems.append(('Download', 'XBMC.RunPlugin(%s?mode=10&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(name), urllib.quote_plus(url))))
        contextMenuItems.append(('Download and Play', 'XBMC.RunPlugin(%s?mode=12&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(name), urllib.quote_plus(url))))
        contextMenuItems.append(('Download Quietly', 'XBMC.RunPlugin(%s?mode=11&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(name), urllib.quote_plus(url))))
        contextMenuItems.append(('Download with jDownloader', 'XBMC.RunPlugin(plugin://plugin.program.jdownloader/?action=addlink&url=%s)' % (urllib.quote_plus(url))))
        
        liz.addContextMenuItems(contextMenuItems, replaceItems=True)
        
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


def addDir(name,url,mode,iconimage,fanart):
        if(iconimage == ''):
                iconimage = defaultIconImg
        ok=True
        u = ''
        try:
                u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        except KeyError:
                xbmc.executebuiltin("XBMC.Notification(VIDEO LINK SKIPPED,ERROR while loading a link,5000)")
                return ok
        liz=xbmcgui.ListItem(name, iconImage="icon_white.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        if(fanart==''):
                fanart=os.path.join(xbmc.translatePath( addonPath ), "fanart.jpg")
        liz.setProperty('fanart_image',fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok



def unescape(string):
        htmlCodes = [
                ['&', '&amp;'],
                ['<', '&lt;'],
                ['>', '&gt;'],
                ['"', '&quot;'],
        ]
        for code in htmlCodes:
                string = string.replace(code[1], code[0])
        return string

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
                d.ok('Welcome to stageVU add-on', 'To watch your subscribed channels and videos,','please provide your login details.')
                wtv.openSettings(sys.argv[ 0 ]) 

params=get_params()
url=None
name=None
mode=None

#check_settings()
#email = wtv.getSetting('email')
#pwd = wtv.getSetting('password')

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

if mode==None or url==None or len(url)<1:
        HOME()

elif mode==1:
        SEARCH(url,name)
        
elif mode==2:
        ADVANCEDSEARCH(url,name)

elif mode==3:
        CATEGORY(url,name)

elif mode==4:
        VIDEOLINK(url,name)
        
elif mode==5:
        GOTOPAGE(url,name)
        
elif mode==6:
        CATEGORIES(url,name)
        
elif mode==10:
        DOWNLOAD_VIDEO(url,name)
        
elif mode==11:
        DOWNLOAD_QUIETLY(url,name)
        
elif mode==12:
        DOWNLOAD_AND_PLAY_VIDEO(url,name)
        
xbmcplugin.endOfDirectory(int(sys.argv[1]))

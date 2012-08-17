'''
Created on Dec 4, 2011

@author: ajju
'''
from TurtleContainer import AddonContext
from common import AddonUtils, XBMCInterfaceUtils, HttpUtils, ExceptionHandler
from common.DataObjects import ListItem
from common.HttpUtils import HttpClient
import BeautifulSoup
import re
import sys
import time
import xbmcgui, xbmcplugin #@UnresolvedImport
from moves import SnapVideo
import base64


'''
Creating a JSON object in following format:
{
    channelName:
    {
        iconimage: imgURL,
        channelType: IND|PAK,
        running_tvshows_url: running_tvshowUrl,
        finished_tvshows_url: finished_tvshowUrl,
        running_tvshows: [ {name: tvshowName, url: tvshowUrl}, {name: tvshowName2, url: tvshowUrl2} ]
        finished_tvshows: [ {name: tvshowName, url: tvshowUrl}, {name: tvshowName2, url: tvshowUrl2} ]
    }
}
'''

CHANNELS_JSON_FILE = 'DR_Channels_v2.json'
OLD_CHANNELS_JSON_FILE = 'DR_Channels_v1.json'
CHANNEL_TYPE_IND = 'IND'
CHANNEL_TYPE_PAK = 'PAK'
BASE_WSITE_URL = base64.b64decode('aHR0cDovL3d3dy5kZXNpcnVsZXoubmV0')

def __retrieveTVShows__(tvShowsUrl):
    tvShows = []
    if tvShowsUrl is None:
        return tvShows
    tvShowsUrl = BASE_WSITE_URL + tvShowsUrl
    contentDiv = BeautifulSoup.SoupStrainer('div', {'id':'forumbits', 'class':'forumbits'})
    soup = HttpClient().getBeautifulSoup(url=tvShowsUrl, parseOnlyThese=contentDiv)
    for tvShowTitleTag in soup.findAll('h2', {'class':'forumtitle'}):
        aTag = tvShowTitleTag.find('a')
        tvshowUrl = str(aTag['href'])
        if tvshowUrl[0:4] != "http":
            tvshowUrl = BASE_WSITE_URL + '/' + tvshowUrl
        tvshowName = aTag.getText()
        if not re.search('Past Shows', tvshowName, re.IGNORECASE):
            tvShows.append({"name":HttpUtils.unescape(tvshowName), "url":tvshowUrl})
    return tvShows
    
    
def __retrieveChannelTVShows__(tvChannelObj):
    running_tvshows = []
    finished_tvshows = []
    try:
        running_tvshows = __retrieveTVShows__(tvChannelObj["running_tvshows_url"])
    except:
        print 'Failed to load a channel... Continue retrieval of next tv show'
    try:
        finished_tvshows = __retrieveTVShows__(tvChannelObj["finished_tvshows_url"])
    except:
        print 'Failed to load a channel... Continue retrieval of next tv show'
    tvChannelObj["running_tvshows"] = running_tvshows
    tvChannelObj["finished_tvshows"] = finished_tvshows
        

def retrieveTVShowsAndSave(request_obj, response_obj):
    oldfilepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=OLD_CHANNELS_JSON_FILE, makeDirs=True)
    AddonUtils.deleteFile(oldfilepath)
    
    filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=CHANNELS_JSON_FILE, makeDirs=True)
    refresh = AddonContext().addon.getSetting('drForceRefresh')
    if refresh == None or refresh != 'true':
        lastModifiedTime = AddonUtils.getFileLastModifiedTime(filepath)
        if lastModifiedTime is not None:
            diff = long((time.time() - lastModifiedTime) / 3600)
            if diff < 720:
                return
            else:
                print CHANNELS_JSON_FILE + ' was last created 30 days ago, refreshing data.'
    else:
        print CHANNELS_JSON_FILE + ' request to force refresh data. '
    tvChannels = {"UTV Stars":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/uu/utv_stars.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/utv-stars/",
                   "finished_tvshows_url": None},
                  "Star Plus":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/star_plus.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/star-plus/",
                   "finished_tvshows_url": "/star-plus-past-shows/"},
                  "Zee TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/zz/zee_tv.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/zee-tv/",
                   "finished_tvshows_url": "/zee-tv-past-shows/"},
                  "Sony TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/set_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/sony-tv/",
                   "finished_tvshows_url": "/sony-tv-past-shows/"},
                  "Star One":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/star_one.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/star-one/",
                   "finished_tvshows_url": "/star-one-past-shows/"},
                  "Life OK":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ll/life_ok_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/life-ok/",
                   "finished_tvshows_url": None},
                  "Star Jalsha":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/star_jalsha.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/star-jalsha/",
                   "finished_tvshows_url": "/star-jalsha-past-shows/"},
                  "Sahara One":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/sahara_one.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/sahara-one/",
                   "finished_tvshows_url": "/sahara-one-past-shows/"},
                  "Colors":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/cc/colors_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/colors-channel/",
                   "finished_tvshows_url": "/colors-past-shows/"},
                  "NDTV Imagine":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ii/imagine_tv_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/ndtv-imagine/",
                   "finished_tvshows_url": "/ndtv-past-shows/"},
                  "Sab TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/sony_sab_tv.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/sab-tv/",
                   "finished_tvshows_url": "/sab-tv-past-shows/"},
                  "MTV (India/Pakistan)":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/mm/mtv_india.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/mtv-india-pakistan/",
                   "finished_tvshows_url": "/mtv-india-pakistan-past-shows/"},
                  "Bindass TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/uu/utv_bindass.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/bindass-tv/",
                   "finished_tvshows_url": "/bindass-tv-past-shows/"},
                  "Channel [V]":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/cc/channel_v_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/channel-v/",
                   "finished_tvshows_url": "/channel-v-past-shows/"},
                  "DD National":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/dd/dd_national.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/dd-national/",
                   "finished_tvshows_url": "/dd-national-others-past-shows/"},
                  "Ary Digital":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/aa/atn_ary_digital.jpg",
                   "channelType": "PAK",
                   "running_tvshows_url": "/ary-digital/",
                   "finished_tvshows_url": "/ary-past-shows/"},
                  "GEO TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/gg/geo_tv.jpg",
                   "channelType": "PAK",
                   "running_tvshows_url": "/geo-tv/",
                   "finished_tvshows_url": "/geo-tv-past-shows/"},
                  "HUM TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/hh/hum_tv.jpg",
                   "channelType": "PAK",
                   "running_tvshows_url": "/hum-tv/",
                   "finished_tvshows_url": "/hum-tv-past-shows/"},
                  "A PLUS":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/aa/a_plus.jpg",
                   "channelType": "PAK",
                   "running_tvshows_url": "/plus/",
                   "finished_tvshows_url": "/plus-past-shows/"},
                  "POGO":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/pp/pogo.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/pogo/",
                   "finished_tvshows_url": None},
                  "Nickelodeon":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/nn/nickelodeon_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/nick/",
                   "finished_tvshows_url": None},
                  "Disney Channel":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/dd/disney_channel_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/disney-channel/",
                   "finished_tvshows_url": None},
                  "Hungama TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/hh/hungama.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/hungama-tv/",
                   "finished_tvshows_url": None},
                  "Cartoon Network":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/cc/cartoon_network_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/cartoon-network/",
                   "finished_tvshows_url": None},
                  "Star Pravah":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/star_pravah.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/star-pravah/",
                   "finished_tvshows_url": None},
                  "Zee Marathi":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/zz/zee_marathi.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/zee-marathi/",
                   "finished_tvshows_url": None},
                  "Star Utsav":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/ss/star_utsav.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/star-utsav/",
                   "finished_tvshows_url": None},
                  "9X":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/num/9x_in.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/9x/",
                   "finished_tvshows_url": "/9x-past-shows/"},
                  "ZEE Bangla":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/zz/zee_bangla.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/zee-bangla/",
                   "finished_tvshows_url": "/zee-bangla-past-shows/"},
                  "Mahuaa TV":
                  {"iconimage":"http://www.lyngsat-logo.com/logo/tv/mm/mahuaa_bangla.jpg",
                   "channelType": "IND",
                   "running_tvshows_url": "/mahuaa-tv/",
                   "finished_tvshows_url": "/mahuaa-tv-past-shows/"}
                }
    
    XBMCInterfaceUtils.callBackDialogProgressBar(getattr(sys.modules[__name__], '__retrieveChannelTVShows__'), tvChannels.values(), 'Retrieving channel TV Shows', 'Failed to retrieve video information, please try again later', line1='Takes about 5 minutes first time', line3='Refreshes data every month or on force refresh or on new add-on version')
    #save tvChannels in moving data
    request_obj.get_data()['tvChannels'] = tvChannels
    status = AddonUtils.saveObjToJsonFile(filepath, tvChannels)
    if status is not None:
        print 'Saved status = ' + str(status)
    AddonContext().addon.setSetting('drForceRefresh', 'false')


def displayTVChannels(request_obj, response_obj):
    channelsList = None
    if request_obj.get_data().has_key('tvChannels'):
        channelsList = request_obj.get_data()['tvChannels']
    else:
        filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=CHANNELS_JSON_FILE)
        channelsList = AddonUtils.getJsonFileObj(filepath)
    if channelsList is None:
        raise Exception(ExceptionHandler.TV_CHANNELS_NOT_LOADED, 'Please delete data folder from add-on user data folder.')
    displayChannelType = int(AddonContext().addon.getSetting('drChannelType'))
    for channelName in channelsList:
        channelObj = channelsList[channelName]
        if ((displayChannelType == 1 and channelObj['channelType'] == CHANNEL_TYPE_IND) 
            or (displayChannelType == 2 and channelObj['channelType'] == CHANNEL_TYPE_PAK) 
            or (displayChannelType == 0)):
            item = ListItem()
            item.add_request_data('channelName', channelName)
            item.add_request_data('channelType', channelObj['channelType'])
            item.set_next_action_name('TV_Shows')
            xbmcListItem = xbmcgui.ListItem(label=channelName, iconImage=channelObj['iconimage'], thumbnailImage=channelObj['iconimage'])
            item.set_xbmc_list_item_obj(xbmcListItem)
            response_obj.addListItem(item)
            
    response_obj.set_xbmc_sort_method(xbmcplugin.SORT_METHOD_LABEL)
        

def displayTVShows(request_obj, response_obj):
    filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=CHANNELS_JSON_FILE)
    channelsList = AddonUtils.getJsonFileObj(filepath)
    channelObj = channelsList[request_obj.get_data()['channelName']]
    channelType = request_obj.get_data()['channelType']
    if channelObj.has_key('running_tvshows'):
        items = __displayTVShows__(channelObj['running_tvshows'], channelType)
        response_obj.extendItemList(items)
    if channelObj.has_key('finished_tvshows'):
        items = __displayTVShows__(channelObj['finished_tvshows'], channelType, True)
        response_obj.extendItemList(items)
        
            
def __displayTVShows__(tvShowsList, channelType, finished=False):
    items = []
    for tvShow in tvShowsList:
        tvShowName = tvShow['name']
        if finished:
            tvShowName = tvShowName + ' [' + AddonUtils.getBoldString('finished') + '] '
        item = ListItem()
        item.add_request_data('channelType', channelType)
        item.add_request_data('tvShowName', tvShowName)
        item.add_request_data('tvShowUrl', tvShow['url'])
        item.set_next_action_name('Show_Episodes')
        xbmcListItem = xbmcgui.ListItem(label=tvShowName)
        item.set_xbmc_list_item_obj(xbmcListItem)
        items.append(item)
    return items


def __retrieveTVShowEpisodes__(threads, response_obj):
    if threads is None:
        return
    for aTag in threads.findAll('a', {'class':re.compile(r'\btitle\b')}):
        episodeName = aTag.getText()
        if not re.search(r'\b(Watch|Episode|Video|Promo)\b', episodeName, re.IGNORECASE):
            pass
        else:
            item = ListItem()
            item.add_request_data('episodeName', HttpUtils.unescape(episodeName))
            episodeUrl = str(aTag['href'])
            if not episodeUrl.lower().startswith(BASE_WSITE_URL):
                if episodeUrl[0] != '/':
                    episodeUrl = '/' + episodeUrl
                episodeUrl = BASE_WSITE_URL + episodeUrl
            item.add_request_data('episodeUrl', episodeUrl)
            item.set_next_action_name('Episode_VLinks')
            xbmcListItem = xbmcgui.ListItem(label=episodeName)
            item.set_xbmc_list_item_obj(xbmcListItem)
            response_obj.addListItem(item)

def retrieveTVShowEpisodes(request_obj, response_obj):
    url = request_obj.get_data()['tvShowUrl']
    if request_obj.get_data().has_key('page'):
        url = url[0:len(url) - 1] + '-' + request_obj.get_data()['page'] + '.html'
    contentDiv = BeautifulSoup.SoupStrainer('div', {'id':'contentBody'})
    soup = HttpClient().getBeautifulSoup(url=url, parseOnlyThese=contentDiv)
    
    if not request_obj.get_data().has_key('page'):
        threads = soup.find('ol', {'class':'stickies', 'id':'stickies'})
        __retrieveTVShowEpisodes__(threads, response_obj)
    
    threads = soup.find('ol', {'class':'threads', 'id':'threads'})
    __retrieveTVShowEpisodes__(threads, response_obj)
            
    pagesDiv = soup.find('div', {'class':'threadpagenav'})
    if pagesDiv is not None:
        pagesInfoTag = pagesDiv.find('a', {'class':re.compile(r'\bpopupctrl\b')})
        if pagesInfoTag is not None:
            pageInfo = re.compile('Page (.+?) of (.+?) ').findall(pagesInfoTag.getText() + ' ')
            currentPage = int(pageInfo[0][0])
            totalPages = int(pageInfo[0][1])
            for page in range(1, totalPages + 1):
                if page != currentPage:
                    item = ListItem()
                    item.add_request_data('tvShowName', request_obj.get_data()['tvShowName'])
                    item.add_request_data('tvShowUrl', request_obj.get_data()['tvShowUrl'])
                    if page != 1:
                        item.add_request_data('page', str(page))
                    pageName = ''
                    if page < currentPage:
                        pageName = AddonUtils.getBoldString('              <-              Page #' + str(page))
                    else:
                        pageName = AddonUtils.getBoldString('              ->              Page #' + str(page))
                        
                    item.set_next_action_name('Show_Episodes_Next_Page')
                    xbmcListItem = xbmcgui.ListItem(label=pageName)
                    item.set_xbmc_list_item_obj(xbmcListItem)
                    response_obj.addListItem(item)


def retrieveVideoLinks(request_obj, response_obj):
    video_source_id = 1
    video_source_img = None
    video_part_index = 0
    video_playlist_items = []
    ignoreAllLinks = False
    
    content = BeautifulSoup.SoupStrainer('blockquote', {'class':re.compile(r'\bpostcontent\b')})
    soup = HttpClient().getBeautifulSoup(url=request_obj.get_data()['episodeUrl'], parseOnlyThese=content)
    if soup.has_key('div'):
        soup = soup.findChild('div', recursive=False)
    prevChild = ''
    for child in soup.findChildren():
        if child.name == 'img' or child.name == 'font'or child.name == 'b' :
            if child.name == 'b' and prevChild == 'a':
                continue
            else:
                if len(video_playlist_items) > 0:
                    response_obj.addListItem(__preparePlayListItem__(video_source_id, video_source_img, video_playlist_items))
                if video_source_img is not None:
                    video_source_id = video_source_id + 1
                    video_source_img = None
                    video_part_index = 0
                    video_playlist_items = []
                ignoreAllLinks = False
        elif not ignoreAllLinks and child.name == 'a' and not re.search('multi', str(child['href']), re.IGNORECASE):
            video_part_index = video_part_index + 1
            video_link = {}
            video_link['videoTitle'] = 'Source #' + str(video_source_id) + ' | ' + 'Part #' + str(video_part_index) + ' | ' + child.getText()
            video_link['videoLink'] = str(child['href'])
            try:
                __prepareVideoLink__(video_link)
                
                video_playlist_items.append(video_link)
                video_source_img = video_link['videoSourceImg']
                
                item = ListItem()
                item.add_request_data('videoLink', video_link['videoLink'])
                item.add_request_data('videoTitle', video_link['videoTitle'])
                item.set_next_action_name('SnapAndPlayVideo')
                xbmcListItem = xbmcgui.ListItem(label='Source #' + str(video_source_id) + ' | ' + 'Part #' + str(video_part_index) , iconImage=video_source_img, thumbnailImage=video_source_img)
                item.set_xbmc_list_item_obj(xbmcListItem)
                response_obj.addListItem(item)
            except:
                print 'Unable to recognize a source = ' + video_link['videoLink']
                video_source_img = None
                video_part_index = 0
                video_playlist_items = []
                ignoreAllLinks = True
        prevChild = child.name
    if len(video_playlist_items) > 0:
        response_obj.addListItem(__preparePlayListItem__(video_source_id, video_source_img, video_playlist_items))


def __preparePlayListItem__(video_source_id, video_source_img, video_playlist_items):
    item = ListItem()
    item.add_request_data('videoPlayListItems', video_playlist_items)
    item.set_next_action_name('SnapAndDirectPlayList')
    xbmcListItem = xbmcgui.ListItem(label=AddonUtils.getBoldString('DirectPlay') + ' | ' + 'Source #' + str(video_source_id) + ' | ' + 'Parts = ' + str(len(video_playlist_items)) , iconImage=video_source_img, thumbnailImage=video_source_img)
    item.set_xbmc_list_item_obj(xbmcListItem)
    return item


def __prepareVideoLink__(video_link):
    video_url = video_link['videoLink']
    new_video_url = None
    video_id = re.compile('(id|url)=(.+?)/').findall(video_url + '/')[0][1]
    if re.search('dm(\d*).php', video_url, flags=re.I):
        new_video_url = 'http://www.dailymotion.com/video/' + video_id + '_'
    elif re.search('flash.php', video_url, flags=re.I):
        new_video_url = 'http://www.zshare.net/video/' + video_id + '&'
    elif re.search('(youtube|u)(\d*).php', video_url, flags=re.I):
        new_video_url = 'http://www.youtube.com/watch?v=' + video_id + '&'
    elif re.search('megavideo', video_url, flags=re.I):
        new_video_url = 'http://www.megavideo.com/v/' + video_id + '&'
        
    video_hosting_info = SnapVideo.findVideoHostingInfo(new_video_url)
    video_link['videoLink'] = new_video_url
    video_link['videoSourceImg'] = video_hosting_info.get_video_hosting_image()

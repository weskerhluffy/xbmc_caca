'''
Created on Nov 25, 2011

@author: ajju
'''
from common.HttpUtils import HttpClient
import BeautifulSoup
import re
import string
from TurtleContainer import AddonContext
from common import AddonUtils, HttpUtils, XBMCInterfaceUtils, ExceptionHandler
import xbmcgui, xbmcplugin #@UnresolvedImport
import time
from common.DataObjects import ListItem
import sys
import base64


'''
Creating a JSON object in following format:
{
    channelName:
    {
        iconimage: imgURL,
        channelType: IND|PAK,
        running_tvshows|finished_tvshows: 
        [ {name: tvshowName, url: tvshowUrl}, {name: tvshowName2, url: tvshowUrl2} ]
    }
}
'''

OLD_CHANNELS_JSON_FILE = 'DT_Channels.json'
CHANNELS_JSON_FILE = 'DT_Channels_v1.json'
CHANNEL_TYPE_IND = 'IND'
CHANNEL_TYPE_PAK = 'PAK'
BASE_WSITE_URL = base64.b64decode('aHR0cDovL3d3dy5kZXNpLXRhc2hhbi5jb20=')

def __retrieveChannels__(tvChannels, dtUrl, channelType):
    contentDiv = BeautifulSoup.SoupStrainer('div', {'class':'copy fix'})
    soup = HttpClient().getBeautifulSoup(url=dtUrl, parseOnlyThese=contentDiv)
    for tvChannelTag in soup.findAll('tbody'):
        try:
            tvChannel = {}
            running_tvshows = []
            finished_tvshows = []
            tmp_tvshows_list = None
            firstRow = False
            for trTag in tvChannelTag.findAll('tr', recursive=False):
                if not firstRow:
                    channelImg = str(trTag.find('img')['src'])
                    channelName = re.compile(BASE_WSITE_URL + '/category/(tv-serials|pakistan-tvs)/(.+?)/').findall(str(trTag.find('a')['href']))[0][1]
                    channelName = string.upper(channelName.replace('-', ' '))
                    tvChannels[channelName] = tvChannel
                    tvChannel['iconimage'] = channelImg
                    tvChannel['channelType'] = channelType
                    firstRow = True
                else:
                    divTag = trTag.find('div')
                    if divTag != None:
                        txt = divTag.getText()
                        if re.search('running', txt, flags=re.IGNORECASE):
                            tmp_tvshows_list = running_tvshows
                            tvChannel['running_tvshows'] = running_tvshows
                        elif re.search('finished', txt, flags=re.IGNORECASE):
                            tmp_tvshows_list = finished_tvshows
                            tvChannel['finished_tvshows'] = finished_tvshows
                        else:
                            print 'UNKNOWN TV SHOW CATEGORY'
                    else:
                        for aTag in trTag.findAll('a'):
                            tvshowUrl = str(aTag['href'])
                            tvshowName = aTag.getText()
                            tmp_tvshows_list.append({'name':HttpUtils.unescape(tvshowName), 'url':tvshowUrl})
        except:
            print 'Failed to load a tv channel links.'

def retrieveTVShowsAndSave(request_obj, response_obj):
    oldfilepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=OLD_CHANNELS_JSON_FILE, makeDirs=True)
    AddonUtils.deleteFile(oldfilepath)
    
    filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=CHANNELS_JSON_FILE, makeDirs=True)
    refresh = AddonContext().addon.getSetting('dtForceRefresh')
    if refresh == None or refresh != 'true':
        lastModifiedTime = AddonUtils.getFileLastModifiedTime(filepath)
        if lastModifiedTime is not None:
            diff = long((time.time() - lastModifiedTime) / 3600)
            if diff < 720:
                return
            else:
                print CHANNELS_JSON_FILE + ' was last created 30 days ago, refreshing data.'
    else:
        print CHANNELS_JSON_FILE + ' request to forcely refresh data. '
    
    tvChannels = {}
    __retrieveChannels__(tvChannels, BASE_WSITE_URL + '/', CHANNEL_TYPE_IND)
    __retrieveChannels__(tvChannels, BASE_WSITE_URL + '/pakistan-tv/', CHANNEL_TYPE_PAK)
    #save tvChannels in moving data
    request_obj.get_data()['tvChannels'] = tvChannels
    
    status = AddonUtils.saveObjToJsonFile(filepath, tvChannels)
    if status is not None:
        print 'Saved status = ' + str(status)
    AddonContext().addon.setSetting('dtForceRefresh', 'false')
        
        
def displayTVChannels(request_obj, response_obj):
    channelsList = None
    if request_obj.get_data().has_key('tvChannels'):
        channelsList = request_obj.get_data()['tvChannels']
    else:
        filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=CHANNELS_JSON_FILE)
        channelsList = AddonUtils.getJsonFileObj(filepath)
    if channelsList is None:
        raise Exception(ExceptionHandler.TV_CHANNELS_NOT_LOADED, 'Please delete data folder from add-on user data folder.')
    displayChannelType = int(AddonContext().addon.getSetting('dtChannelType'))
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
        

def retrieveTVShowEpisodes(request_obj, response_obj):
    contentDiv = BeautifulSoup.SoupStrainer('div', {'id':'content'})
    url = request_obj.get_data()['tvShowUrl']
    channelType = request_obj.get_data()['channelType']
    if request_obj.get_data().has_key('page'):
        url = url + 'page/' + request_obj.get_data()['page']
    soup = HttpClient().getBeautifulSoup(url=url, parseOnlyThese=contentDiv)
    for aTag in soup.findAll('a', {'rel':'bookmark'}):
        episodeName = aTag.getText()
        try:
            time.strptime(episodeName, '%B %d, %Y')
            continue
        except:
            if re.search('Written Episode', episodeName):
                pass
            else:
                item = ListItem()
                item.add_request_data('episodeName', episodeName)
                item.add_request_data('episodeUrl', str(aTag['href']))
                item.set_next_action_name(channelType + '_Episode_VLinks')
                xbmcListItem = xbmcgui.ListItem(label=episodeName)
                item.set_xbmc_list_item_obj(xbmcListItem)
                response_obj.addListItem(item)
            
    pagesDiv = soup.find('div', {'class':'wp-pagenavi'})
    if pagesDiv is not None:
        pagesInfoTag = pagesDiv.find('span', {'class':'pages'}, recursive=False)
        if pagesInfoTag is not None:
            pageInfo = re.compile('Page (.+?) of (.+?) ').findall(pagesInfoTag.getText() + ' ')
            currentPage = int(pageInfo[0][0].replace(',',''))
            totalPages = int(pageInfo[0][1].replace(',',''))
            for page in range(1, totalPages + 1):
                if page == 1 or page == totalPages or page == currentPage - 1 or page == currentPage + 1:
                    if page != currentPage:
                        item = ListItem()
                        item.add_request_data('channelType', channelType)
                        item.add_request_data('tvShowName', request_obj.get_data()['tvShowName'])
                        item.add_request_data('tvShowUrl', request_obj.get_data()['tvShowUrl'])
                        if page != 1:
                            item.add_request_data('page', str(page))
                        pageName = AddonUtils.getBoldString('              ->              Page #' + str(page))
                            
                        item.set_next_action_name('Show_Episodes_Next_Page')
                        xbmcListItem = xbmcgui.ListItem(label=pageName)
                        item.set_xbmc_list_item_obj(xbmcListItem)
                        response_obj.addListItem(item)
            
                
def retrievePakVideoLinks(request_obj, response_obj):
    video_source_id = 0
    video_source_img = None
    video_part_index = 0
    video_playlist_items = []
    
    contentDiv = BeautifulSoup.SoupStrainer('div', {'id':'restricted-content', 'class':'post-content'})
    soup = HttpClient().getBeautifulSoup(url=request_obj.get_data()['episodeUrl'], parseOnlyThese=contentDiv)
    videoFrameTags = soup.findAll('iframe', {'class':re.compile('(youtube|dailymotion)-player')})
    for frameTag in videoFrameTags:
        videoLink = str(frameTag['src'])
        source_img = None
        if re.search('youtube', videoLink):
            source_img = 'http://www.automotivefinancingsystems.com/images/icons/socialmedia_youtube_256x256.png'
        elif re.search('dailymotion', videoLink):
            source_img = 'http://aux.iconpedia.net/uploads/1687271053.png'
            
        if video_source_img is None or video_source_img != source_img:
            if len(video_playlist_items) > 0:
                response_obj.addListItem(__preparePlayListItem__(video_source_id, video_source_img, video_playlist_items))
            video_source_id = video_source_id + 1
            video_source_img = source_img
            video_part_index = 0
            video_playlist_items = []
            
        video_part_index = video_part_index + 1
        video_link = {}
        video_link['videoTitle'] = 'Source #' + str(video_source_id) + ' | ' + 'Part #' + str(video_part_index)
        video_link['videoLink'] = videoLink
        video_playlist_items.append(video_link)
        
        item = ListItem()
        item.add_request_data('videoLink', video_link['videoLink'])
        item.add_request_data('videoTitle', video_link['videoTitle'])
        item.set_next_action_name('SnapAndPlayVideo')
        xbmcListItem = xbmcgui.ListItem(label='Source #' + str(video_source_id) + ' | ' + 'Part #' + str(video_part_index) , iconImage=video_source_img, thumbnailImage=video_source_img)
        item.set_xbmc_list_item_obj(xbmcListItem)
        response_obj.addListItem(item)
            
    if len(video_playlist_items) > 0:
        response_obj.addListItem(__preparePlayListItem__(video_source_id, video_source_img, video_playlist_items))
    


def retrieveIndVideoLinks(request_obj, response_obj):
    video_source_id = 0
    video_source_img = None
    video_part_index = 0
    video_playlist_items = []
    
    
    contentDiv = BeautifulSoup.SoupStrainer('p', {'style':re.compile(r'\bcenter\b')})
    soup = HttpClient().getBeautifulSoup(url=request_obj.get_data()['episodeUrl'], parseOnlyThese=contentDiv)
    for child in soup.findChildren():

        if child.name == 'img':
            if len(video_playlist_items) > 0:
                response_obj.addListItem(__preparePlayListItem__(video_source_id, video_source_img, video_playlist_items))
            video_source_id = video_source_id + 1
            video_source_img = child['src']
            video_part_index = 0
            video_playlist_items = []
        elif child.name == 'a':
            video_part_index = video_part_index + 1
            video_link = {}
            video_link['videoTitle'] = 'Source #' + str(video_source_id) + ' | ' + 'Part #' + str(video_part_index) + ' | ' + child.getText()
            video_link['videoLink'] = str(child['href'])
            video_playlist_items.append(video_link)
            
            item = ListItem()
            item.add_request_data('videoLink', video_link['videoLink'])
            item.add_request_data('videoTitle', video_link['videoTitle'])
            item.set_next_action_name('SnapAndPlayVideo')
            xbmcListItem = xbmcgui.ListItem(label='Source #' + str(video_source_id) + ' | ' + 'Part #' + str(video_part_index) , iconImage=video_source_img, thumbnailImage=video_source_img)
            item.set_xbmc_list_item_obj(xbmcListItem)
            response_obj.addListItem(item)
            
    if len(video_playlist_items) > 0:
        response_obj.addListItem(__preparePlayListItem__(video_source_id, video_source_img, video_playlist_items))
            

def __preparePlayListItem__(video_source_id, video_source_img, video_playlist_items):
    item = ListItem()
    item.add_request_data('videoPlayListItems', video_playlist_items)
    item.set_next_action_name('SnapAndDirectPlayList')
    xbmcListItem = xbmcgui.ListItem(label=AddonUtils.getBoldString('DirectPlay') + ' | ' + 'Source #' + str(video_source_id) + ' | ' + 'Parts = ' + str(len(video_playlist_items)) , iconImage=video_source_img, thumbnailImage=video_source_img)
    item.set_xbmc_list_item_obj(xbmcListItem)
    return item


def prepareVideoLink(request_obj, response_obj):
    items = response_obj.get_item_list()
    XBMCInterfaceUtils.callBackDialogProgressBar(getattr(sys.modules[__name__], '__prepareVideoLink__'), items, 'Preparing video link', 'Failed to retrieve video information, please try again later')


def __prepareVideoLink__(item):
    video_url = item.get_moving_data()['videoUrl']
    html = HttpClient().getHtmlContent(video_url)
    video_id = re.compile('http://www.youtube.com/embed/(.+?)\'').findall(html)[0]
    new_video_url = None
    if re.search('dailymotion', video_url, flags=re.I):
        new_video_url = 'http://www.dailymotion.com/video/' + video_id + '_'
    elif re.search('zshare', video_url, flags=re.I):
        new_video_url = 'http://www.zshare.net/video/' + video_id + '&'
    elif re.search('youtube', video_url, flags=re.I):
        new_video_url = 'http://www.youtube.com/watch?v=' + video_id + '&'
    elif re.search('megavideo', video_url, flags=re.I):
        new_video_url = 'http://www.megavideo.com/v/' + video_id + '&'
        
    if new_video_url is not None:
        item.add_moving_data('videoUrl', new_video_url)

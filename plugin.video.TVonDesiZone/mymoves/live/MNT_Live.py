'''
Created on Dec 10, 2011

@author: ajju
'''
from TurtleContainer import AddonContext
import time
from common.HttpUtils import HttpClient
import xbmcgui #@UnresolvedImport
import re
from common.DataObjects import ListItem
from common import ExceptionHandler


def selectChannelsCategory(request_obj, response_obj):
    d = xbmcgui.Dialog()
    channelSelect = d.select('Select LIVE TV package:', ['Indian Channels', 'Pakistan Channels'])
    liveUrl = None
    if channelSelect == 0:
        liveUrl = 'http://www.moviesntv.com/hindi/player.php'
    elif channelSelect == 1:
        liveUrl = 'http://www.moviesntv.com/pak/player.php'
    if liveUrl is None:
        raise Exception(ExceptionHandler.USER_PWD_NOT_PROVIDED, 'User and password is not provided to access desitvstreams.com')
    else:
        request_obj.set_data({'url': liveUrl})
        

def login(request_obj, response_obj):
    username = AddonContext().addon.getSetting('mnt_username')
    password = AddonContext().addon.getSetting('mnt_password')
    if username == '' or password == '':
        raise Exception(ExceptionHandler.USER_PWD_NOT_PROVIDED, 'User and password is not provided to access desitvstreams.com')
    millis = str(int(round(time.time())))
    params = {'amember_login': username, 'amember_pass': password, 'login_attempt_id': millis}
    #Enable HTML cookies
    HttpClient().enableCookies()
    htmlContent = HttpClient().getHtmlContent(request_obj.get_data()['url'], params)
    
    if re.search('Username or password incorrect', htmlContent):
        raise Exception(ExceptionHandler.USER_PWD_INCORRECT, 'User and password provided is not authorized to access desitvstreams.com')
    htmlContent = ''.join(htmlContent.splitlines()).replace('\t', '').replace('\'', '"').replace(' ', '').replace('&nbsp;', '')
    request_obj.get_data()['htmlContent'] = htmlContent


def displayChannels(request_obj, response_obj):
    server = int(AddonContext().addon.getSetting('mnt_server')) + 1
    
    channels = re.compile('<tr><tdwidth="80"height="50"valign="middle">(.+?)</td><tdwidth="31"></td><tdwidth="122"valign="middle"><imgwidth=50height=40src="(.+?)">(.+?)href="(.+?)"').findall(request_obj.get_data()['htmlContent'])
    for chId, chLogo, chtemp, chlink in channels: #@UnusedVariable
        item = ListItem()
        item.set_next_action_name('play_Live_Channel')
        item.add_request_data('channelLogo', chLogo)
        item.add_request_data('channelId', chId)
        channelUrl = ''
        channelName = chId
        if re.search('FlashPlayer', chlink, re.I):
            item.add_request_data('flash', True)
            channelUrl = request_obj.get_data()['url'].replace('player.php', 'FlashPlayer.php?stream=1&chid=' + chId + '&server=' + str(server))
            channelName = channelName + ' Flash HQ'
        else:
            item.add_request_data('flash', False)
            channelUrl = request_obj.get_data()['url'].replace('player.php', 'MediaPlayer.php?chid=' + chId + '&server=' + str(server))
        item.add_request_data('url', channelUrl)
        xbmcListItem = xbmcgui.ListItem(label=channelName, iconImage=chLogo, thumbnailImage=chLogo)
        item.set_xbmc_list_item_obj(xbmcListItem)
        response_obj.addListItem(item)
  

def retrieveLiveLink(request_obj, response_obj):
    videoStreamUrl = None
    channelName = request_obj.get_data()['channelId']
    if request_obj.get_data()['flash']:
        videoStreamUrl = retrieveFlashLiveLink(request_obj, response_obj)
        channelName = channelName + ' Flash HQ'
    else:
        videoStreamUrl = retrieveMMSLiveLink(request_obj, response_obj)
    
    
    item = ListItem()
    item.set_next_action_name('Play')
    item.add_moving_data('videoStreamUrl', videoStreamUrl)
    xbmcListItem = xbmcgui.ListItem(label=channelName, iconImage=request_obj.get_data()['channelLogo'], thumbnailImage=request_obj.get_data()['channelLogo'])
    item.set_xbmc_list_item_obj(xbmcListItem)
    response_obj.addListItem(item)
        

def retrieveFlashLiveLink(request_obj, response_obj):
    html = request_obj.get_data()['htmlContent']
    playpath = re.compile('clip:\{url\:"(.+?)"').findall(html)[0]
    swfUrl = 'http://www.moviesntv.com/hindi/' + re.compile('"rtmp_player"\,"(.+?)"').findall(html)[0]
    streamUrl = re.compile('netConnectionUrl:"(.+?)"').findall(html)[0]
    
    videoStreamUrl = streamUrl + ' playpath=' + playpath + ' swfUrl=' + swfUrl + ' swfVfy=true live=true pageUrl=' + request_obj.get_data()['url']
    return videoStreamUrl

def retrieveMMSLiveLink(request_obj, response_obj):
    html = request_obj.get_data()['htmlContent']
    videoStreamUrl = 'mms' + re.compile('src="mms(.+?)"').findall(html)[0]
    return videoStreamUrl

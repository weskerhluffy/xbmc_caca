'''
Created on Dec 10, 2011

@author: ajju
'''
from TurtleContainer import AddonContext
import time
from common.HttpUtils import HttpClient
import re
import BeautifulSoup
import sys
from common import XBMCInterfaceUtils, ExceptionHandler
from common.DataObjects import ListItem
import xbmcgui, xbmcplugin #@UnresolvedImport


def login(request_obj, response_obj):
    username = AddonContext().addon.getSetting('wst_username')
    password = AddonContext().addon.getSetting('wst_password')
    if username == '' or password == '':
        raise Exception(ExceptionHandler.USER_PWD_NOT_PROVIDED, 'User and password is not provided to access desitvstreams.com')
    millis = str(int(round(time.time())))
    params = {'amember_login': username, 'amember_pass': password, 'login_attempt_id': millis}
    #Enable HTML cookies
    HttpClient().enableCookies()
    htmlContent = HttpClient().getHtmlContent('http://www.watchsuntv.com/users/login.php', params)
    
    if re.search('Username or password incorrect', htmlContent):
        raise Exception(ExceptionHandler.USER_PWD_INCORRECT, 'User and password provided is not authorized to access desitvstreams.com')
    request_obj.get_data()['htmlContent'] = htmlContent

    
def displayChannels(request_obj, response_obj):
    content = BeautifulSoup.SoupStrainer('div', {'class':re.compile(r'\bchannels\b')})
    soup = HttpClient().getBeautifulSoup(url='http://www.watchsuntv.com/play', parseOnlyThese=content)
    channels = soup.findAll('li', {'class':'channel-info'})
    list_items = XBMCInterfaceUtils.callBackDialogProgressBar(getattr(sys.modules[__name__], '__displayChannels__'), channels, 'Preparing channel items', 'Failed to retrieve channel information, please try again later')
    response_obj.extendItemList(list_items)
    response_obj.set_xbmc_sort_method(xbmcplugin.SORT_METHOD_LABEL)
    
    
def __displayChannels__(channelInfoTag):
    imgTag = channelInfoTag.find('img')
    channelImg = str(imgTag['src'])
    
    aTag = channelInfoTag.find('a')
    channelName = aTag.getText()
    channelInfo = re.compile('server_playOn\((.+?),(.+?),"(.+?)"').findall(str(aTag['onclick']).replace(' ', '').replace('\'', '"'))[0]
    
    item = ListItem()
    item.set_next_action_name('play_Live_Channel')
    item.add_request_data('channelInfo', channelInfo)
    item.add_request_data('channelLogo', channelImg)
    item.add_request_data('channelName', channelName)
    xbmcListItem = xbmcgui.ListItem(label=channelName, iconImage=channelImg, thumbnailImage=channelImg)
    item.set_xbmc_list_item_obj(xbmcListItem)
    return item


def retrieveLiveLink(request_obj, response_obj):
    channelInfo = request_obj.get_data()['channelInfo']
    params = {'channel_id':channelInfo[0], 'server_type':channelInfo[1], 'timezone':channelInfo[2]}
    content = HttpClient().getHtmlContent(url='http://www.watchsuntv.com/play/pages/playOn/', params=params)
    streamUrl = re.compile('<param name="flashvars" value="streamer=(.+?)"').findall(content)[0]
    swfUrl = 'http://www.watchsuntv.com/play/' + re.compile('<param name="movie" value="(.+?)"').findall(content)[0]
    urlParams = streamUrl.split('&')
    videoStreamUrl = urlParams[0] + ' ' + urlParams[1].replace('file', 'playpath') + ' swfUrl=' + swfUrl + ' swfVfy=true live=true pageUrl=' + swfUrl
    
    item = ListItem()
    item.set_next_action_name('Play')
    item.add_moving_data('videoStreamUrl', videoStreamUrl)
    xbmcListItem = xbmcgui.ListItem(label=request_obj.get_data()['channelName'], iconImage=request_obj.get_data()['channelLogo'], thumbnailImage=request_obj.get_data()['channelLogo'])
    item.set_xbmc_list_item_obj(xbmcListItem)
    response_obj.addListItem(item)

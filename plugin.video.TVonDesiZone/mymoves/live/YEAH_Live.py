'''
Created on Dec 10, 2011

@author: ajju
'''
from TurtleContainer import AddonContext
from common import AddonUtils, ExceptionHandler
from common.DataObjects import ListItem
import xbmcgui, xbmcplugin #@UnresolvedImport


CHANNELS_JSON_FILE = 'Yeah-Channels.json'

def addYeahLiveItem(request_obj, response_obj):
    yeahfilepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=CHANNELS_JSON_FILE, makeDirs=False)
    if AddonUtils.doesFileExist(yeahfilepath):
        yeah_icon_filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonPath, extraDirPath=AddonUtils.ADDON_ART_FOLDER, filename='YEAH.png')
        item = ListItem()
        item.set_next_action_name('Yeah_TV')
        xbmcListItem = xbmcgui.ListItem(label='[B]YEAH[/B] STREAMS', iconImage=yeah_icon_filepath, thumbnailImage=yeah_icon_filepath)
        item.set_xbmc_list_item_obj(xbmcListItem)
        response_obj.addListItem(item)
    

def selectChannelsCategory(request_obj, response_obj):
    catNameList = ['Education', 'Devotional', 'News', 'Sports', 'Hindi', 'Kannada', 'Malayalam', 'Tamil', 'Telugu']
    d = xbmcgui.Dialog()
    catSelect = d.select('SELECT Category', catNameList)
    if catSelect == -1:
        raise Exception(ExceptionHandler.CATEGORY_NOT_SELECTED, 'Please select the category correctly')
    category = catNameList[catSelect]
    request_obj.set_data({'category': category})


def displayChannels(request_obj, response_obj):
    filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonProfile, extraDirPath=AddonUtils.ADDON_SRC_DATA_FOLDER, filename=CHANNELS_JSON_FILE)
    channelsList = AddonUtils.getJsonFileObj(filepath)
    for channelUrl in channelsList:
        if request_obj.get_data()['category'] == channelsList[channelUrl]['category']:
            channelName = channelsList[channelUrl]['channel']
            channelLogo = channelsList[channelUrl]['thumb']
            item = ListItem()
            item.set_next_action_name('play_Live_Channel')
            item.add_request_data('channelName', channelName)
            item.add_request_data('channelLogo', channelLogo)
            item.add_request_data('channelUrl', channelUrl)
            xbmcListItem = xbmcgui.ListItem(label=channelName, iconImage=channelLogo, thumbnailImage=channelLogo)
            item.set_xbmc_list_item_obj(xbmcListItem)
            response_obj.addListItem(item)
    response_obj.set_xbmc_sort_method(xbmcplugin.SORT_METHOD_LABEL)
    

def playChannel(request_obj, response_obj):
    item = ListItem()
    item.set_next_action_name('Play')
    item.add_moving_data('videoStreamUrl', request_obj.get_data()['channelUrl'])
    xbmcListItem = xbmcgui.ListItem(label=request_obj.get_data()['channelName'], iconImage=request_obj.get_data()['channelLogo'], thumbnailImage=request_obj.get_data()['channelLogo'])
    item.set_xbmc_list_item_obj(xbmcListItem)
    response_obj.addListItem(item)

'''
Created on Dec 5, 2011

@author: ajju
'''
from TurtleContainer import AddonContext
from common.DataObjects import ListItem
import xbmcgui #@UnresolvedImport
from common import AddonUtils


def displayMenuItems(request_obj, response_obj):
    # TV Shows item
    onDemand_icon_filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonPath, extraDirPath=AddonUtils.ADDON_ART_FOLDER, filename='onDemand.png')
    item = ListItem()
    item.set_next_action_name('On_Demand')
    xbmcListItem = xbmcgui.ListItem(label='TV ON DEMAND', iconImage=onDemand_icon_filepath, thumbnailImage=onDemand_icon_filepath)
    item.set_xbmc_list_item_obj(xbmcListItem)
    response_obj.addListItem(item)
    
    # LIVE TV item
    live_icon_filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonPath, extraDirPath=AddonUtils.ADDON_ART_FOLDER, filename='live.png')
    item = ListItem()
    item.set_next_action_name('Live')
    xbmcListItem = xbmcgui.ListItem(label='LIVE TV', iconImage=live_icon_filepath, thumbnailImage=live_icon_filepath)
    item.set_xbmc_list_item_obj(xbmcListItem)
    response_obj.addListItem(item)


def findTVShowsSource(request_obj, response_obj):
    sourceChosen = int(AddonContext().addon.getSetting('tvShowsSource'))
    if sourceChosen == 0:
        response_obj.set_redirect_action_name('DR_TV_Channels')
    elif sourceChosen == 1:
        response_obj.set_redirect_action_name('DT_TV_Channels')
        
        
def displayLiveTvSources(request_obj, response_obj):
    
    dts_icon_filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonPath, extraDirPath=AddonUtils.ADDON_ART_FOLDER, filename='DTS.png')
    item = ListItem()
    item.set_next_action_name('Desi_TV_Streams')
    xbmcListItem = xbmcgui.ListItem(label='[B]DESI TV[/B] STREAMS', iconImage=dts_icon_filepath, thumbnailImage=dts_icon_filepath)
    item.set_xbmc_list_item_obj(xbmcListItem)
    response_obj.addListItem(item)
    
    mnt_icon_filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonPath, extraDirPath=AddonUtils.ADDON_ART_FOLDER, filename='MNT.png')
    item = ListItem()
    item.set_next_action_name('Movies_n_TV')
    xbmcListItem = xbmcgui.ListItem(label='MOVIESnTV', iconImage=mnt_icon_filepath, thumbnailImage=mnt_icon_filepath)
    item.set_xbmc_list_item_obj(xbmcListItem)
    response_obj.addListItem(item)
    
    wst_icon_filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonPath, extraDirPath=AddonUtils.ADDON_ART_FOLDER, filename='WST.png')
    item = ListItem()
    item.set_next_action_name('Watch_Sun_TV')
    xbmcListItem = xbmcgui.ListItem(label='WATCH SUN TV', iconImage=wst_icon_filepath, thumbnailImage=wst_icon_filepath)
    item.set_xbmc_list_item_obj(xbmcListItem)
    #Hide WatchSunTV.com until it is not working.
    #response_obj.addListItem(item)

    free_icon_filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonPath, extraDirPath=AddonUtils.ADDON_ART_FOLDER, filename='FREE.png')
    item = ListItem()
    item.set_next_action_name('Free_TV')
    xbmcListItem = xbmcgui.ListItem(label='FREE TV', iconImage=free_icon_filepath, thumbnailImage=free_icon_filepath)
    item.set_xbmc_list_item_obj(xbmcListItem)
    response_obj.addListItem(item)

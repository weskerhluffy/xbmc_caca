'''
Created on Dec 25, 2011

@author: ajju
'''
from TurtleContainer import AddonContext
from common import AddonUtils, XBMCInterfaceUtils
from common.DataObjects import ListItem
from common.HttpUtils import HttpClient
import BeautifulSoup
import re
import xbmcgui #@UnresolvedImport
import sys
import urllib
from moves import SnapVideo


def displayMoviesMenu(request_obj, response_obj):
    # ALL Movies
    movies_icon_filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonPath, extraDirPath=AddonUtils.ADDON_ART_FOLDER, filename='movies.png')
    item = ListItem()
    item.set_next_action_name('Movies_List')
    item.add_request_data('movieCategoryUrl', 'http://www.pinoymovie.co/')
    xbmcListItem = xbmcgui.ListItem(label='All Movies', iconImage=movies_icon_filepath, thumbnailImage=movies_icon_filepath)
    item.set_xbmc_list_item_obj(xbmcListItem)
    response_obj.addListItem(item)
    # Recently Added
    item = ListItem()
    item.set_next_action_name('Recent_Movies_List')
    item.add_request_data('movieCategoryUrl', 'http://www.pinoymovie.co/')
    xbmcListItem = xbmcgui.ListItem(label='Recently Added', iconImage=movies_icon_filepath, thumbnailImage=movies_icon_filepath)
    item.set_xbmc_list_item_obj(xbmcListItem)
    #response_obj.addListItem(item)
    
    contentDiv = BeautifulSoup.SoupStrainer('div', {'id':'sidebar'})
    soup = HttpClient().getBeautifulSoup(url='http://www.pinoymovie.co/', parseOnlyThese=contentDiv)
    soup = soup.findChild('div', {'class':'right'})
    
    for liItemTag in soup.findChildren('li', {'class':re.compile(r'\bcat-item\b')}):
        aTag = liItemTag.findChild('a')
        categoryUrl = aTag['href']
        categoryName = aTag.getText()
        
        item = ListItem()
        item.set_next_action_name('Movies_List')
        item.add_request_data('movieCategoryUrl', categoryUrl)
        xbmcListItem = xbmcgui.ListItem(label=categoryName, iconImage=movies_icon_filepath, thumbnailImage=movies_icon_filepath)
        item.set_xbmc_list_item_obj(xbmcListItem)
        response_obj.addListItem(item)
    
    # Search TV
    search_icon_filepath = AddonUtils.getCompleteFilePath(baseDirPath=AddonContext().addonPath, extraDirPath=AddonUtils.ADDON_ART_FOLDER, filename='search.png')
    item = ListItem()
    item.set_next_action_name('Search_Movies_List')
    item.add_request_data('movieCategoryUrl', 'http://www.pinoymovie.co/?s=')
    xbmcListItem = xbmcgui.ListItem(label='Search Movies', iconImage=search_icon_filepath, thumbnailImage=search_icon_filepath)
    item.set_xbmc_list_item_obj(xbmcListItem)
    response_obj.addListItem(item)



def __retrieveAndCreateMovieItem__(movieTag):
    thumbTag = movieTag.findChild('div', {'class':'thumbnail'})
    imgUrl = ''
    if thumbTag is not None:    
        aTag = thumbTag.findChild('a')
        imgTag = aTag.findChild('img')
        imgUrl = imgTag['src']
    
    titleTag = movieTag.findChild('h2')
    aTag = titleTag.findChild('a')
    movieUrl = str(aTag['href'])
    title = unicode(titleTag.getText()).encode('utf8').replace('&#8217;', '\'').replace('&#038;', '&').replace('&#8230;', '...')
    
    descTag = movieTag.findChild('div', {'class':'entry'})
    desc = ''
    if descTag is not None:
        desc = unicode(descTag.getText()).encode('utf8').replace('&#8217;', '\'').replace('&#038;', '&').replace('&#8230;', '...')
    rating = 0.0
    ratingTag = movieTag.findChild('div', {'class':'post-ratings'})
    if ratingTag is not None:
        ratingInfo = ratingTag.getText()
        ratingFound = re.compile('average:(.+?)out of 5').findall(ratingInfo)
        if len(ratingFound) > 0:
            rating = float(ratingFound[0])
            rating = (rating / 5) * 10
    item = ListItem()
    item.set_next_action_name('Movie_VLinks')
    item.add_request_data('movieUrl', movieUrl)
    xbmcListItem = xbmcgui.ListItem(label=title, iconImage=imgUrl, thumbnailImage=imgUrl)
    xbmcListItem.setInfo('video', {'plot':desc, 'plotoutline':desc, 'title':title, 'originaltitle':title, 'rating':rating})
    item.set_xbmc_list_item_obj(xbmcListItem)
    return item
    

def displayMovies(request_obj, response_obj):
    url = request_obj.get_data()['movieCategoryUrl']
    if request_obj.get_data().has_key('page'):
        url_parts = url.split('?')
        
        url_part_A = ''
        url_part_B = ''
        if len(url_parts) == 2:
            url_part_A = url_parts[0]
            url_part_B = '?' + url_parts[1]
        else:
            url_part_A = url
        if url_part_A[len(url_part_A) - 1] != '/':
            url_part_A = url_part_A + '/'
        url = url_part_A + 'page/' + request_obj.get_data()['page'] + url_part_B
    contentDiv = BeautifulSoup.SoupStrainer('div', {'id':'content'})
    soup = HttpClient().getBeautifulSoup(url=url, parseOnlyThese=contentDiv)
    movieTags = soup.findChildren('div', {'class':'post'})
    for movieTag in movieTags:
        item = __retrieveAndCreateMovieItem__(movieTag)
        response_obj.addListItem(item)
    
    response_obj.set_xbmc_content_type('movies')
    
    pagesInfoTag = soup.findChild('div', {'class':'navigation'})
    print pagesInfoTag
    current_page = int(pagesInfoTag.find('span', {'class':'page current'}).getText())
    print current_page
    pages = pagesInfoTag.findChildren('a', {'class':'page'})
    print pages
    last_page = int(pages[len(pages) - 1].getText())
    
    if current_page < last_page:
        for page in range(current_page + 1, last_page + 1):
            createItem = False
            if page == last_page:
                pageName = AddonUtils.getBoldString('              ->              Last Page #' + str(page))
                createItem = True
            elif page <= current_page + 4:
                pageName = AddonUtils.getBoldString('              ->              Page #' + str(page))
                createItem = True
            if createItem:
                item = ListItem()
                item.add_request_data('movieCategoryUrl', request_obj.get_data()['movieCategoryUrl'])
                item.add_request_data('page', str(page))
                
                    
                item.set_next_action_name('Movies_List_Next_Page')
                xbmcListItem = xbmcgui.ListItem(label=pageName)
                item.set_xbmc_list_item_obj(xbmcListItem)
                response_obj.addListItem(item)
            
    
    
def __retrieveRecentMovies__(movieLinkTag):
    movieLink = movieLinkTag['href']
    contentDiv = BeautifulSoup.SoupStrainer('div', {'id':'content'})
    soup = HttpClient().getBeautifulSoup(url=movieLink, parseOnlyThese=contentDiv)
    movieTag = soup.findChild('div', {'class':'post'})
    return __retrieveAndCreateMovieItem__(movieTag)
    
    
def displayRecentMovies(request_obj, response_obj):
    contentDiv = BeautifulSoup.SoupStrainer('div', {'id':'sub-sidebar'})
    soup = HttpClient().getBeautifulSoup(url='http://www.pinoymovie.co/', parseOnlyThese=contentDiv)
    soup = soup.findChild('div', {'class':'right'})
    movieLinkTags = soup.findChildren('a')
    recentMoviesItems = XBMCInterfaceUtils.callBackDialogProgressBar(getattr(sys.modules[__name__], '__retrieveRecentMovies__'), movieLinkTags, 'Retrieving recent movies and its information', 'Failed to retrieve video information, please try again later', line1='Takes about 5 minutes')
    response_obj.extendItemList(recentMoviesItems)
    
    
def searchMovies(request_obj, response_obj):
    search_text = XBMCInterfaceUtils.getUserInput(heading='Enter search text')
    newtvChannelUrl = request_obj.get_data()['movieCategoryUrl'] + search_text
    request_obj.get_data()['movieCategoryUrl'] = newtvChannelUrl
    response_obj.set_redirect_action_name('Search_Movies')


def retrieveVideoLinks(request_obj, response_obj):

    url = request_obj.get_data()['movieUrl']
    contentDiv = BeautifulSoup.SoupStrainer('div', {'class':'video'})
    soup = HttpClient().getBeautifulSoup(url=url, parseOnlyThese=contentDiv)
    decodedSoup = urllib.unquote(str(soup))
    videoFrameLinks = re.compile('http://www.pinoymovie.c(o|a)/ajaxtabs/(.+?).htm').findall(decodedSoup)
    if len(videoFrameLinks) > 0:
        video_source_id = 1
        for ignoreIt, videoFrameLink in videoFrameLinks: #@UnusedVariable
            try:
                soup = HttpClient().getBeautifulSoup(url='http://www.pinoymovie.co/ajaxtabs/' + videoFrameLink + '.htm')
                video_url = str(soup.find('iframe')['src'])
                video_hosting_info = SnapVideo.findVideoHostingInfo(video_url)
                if video_hosting_info is None:
                    print 'UNKNOWN streaming link found: ' + video_url
                else:
                    video_source_img = video_hosting_info.get_video_hosting_image()
                    video_title = 'Source #' + str(video_source_id) + ' :: ' + video_hosting_info.get_video_hosting_name()
                    
                    item = ListItem()
                    item.add_request_data('videoLink', video_url)
                    item.add_request_data('videoTitle', video_title)
                    item.set_next_action_name('SnapAndPlayVideo')
                    xbmcListItem = xbmcgui.ListItem(label=video_title, iconImage=video_source_img, thumbnailImage=video_source_img)
                    item.set_xbmc_list_item_obj(xbmcListItem)
                    response_obj.addListItem(item)
                    video_source_id = video_source_id + 1
            except:
                print 'UNKNOWN streaming link found'
    else:
        videoLinks = re.compile('flashvars=(.+?)file=(.+?)&').findall(decodedSoup)
        
        moreLinks = re.compile('<iframe(.+?)src="(.+?)"', flags=re.I).findall(decodedSoup)
        if len(moreLinks) > 0:
            videoLinks.extend(moreLinks)
        
        moreLinks = re.compile('<a(.+?)href="(.+?)"', flags=re.I).findall(decodedSoup)
        if len(moreLinks) > 0:
            videoLinks.extend(moreLinks)
        
        if len(videoLinks) > 0:
            
            video_source_id = 1
            video_source_img = None
            video_part_index = 0
            video_playlist_items = []
            for ignoreIt, videoLink in videoLinks: #@UnusedVariable
                try:
                    if re.search('http://media.pinoymovie.ca/playlist/(.+?).xml', videoLink, re.I):
                        soupXml = HttpClient().getBeautifulSoup(url=videoLink)
                        
                        for media in soupXml.findChildren('track'):
                            video_url = media.findChild('location').getText()
                            video_hosting_info = SnapVideo.findVideoHostingInfo(video_url)
                            
                            if video_hosting_info is None:
                                print 'UNKNOWN streaming link found: ' + video_url
                            else:
                                
                                video_part_index = video_part_index + 1
                                video_link = {}
                                video_link['videoTitle'] = 'Source #' + str(video_source_id) + ' | ' + 'Part #' + str(video_part_index)
                                video_link['videoLink'] = video_url
                                video_link['videoSourceImg'] = video_hosting_info.get_video_hosting_image()
                                
                                video_playlist_items.append(video_link)
                                video_source_img = video_link['videoSourceImg']
                                
                                
                                item = ListItem()
                                item.add_request_data('videoLink', video_link['videoLink'])
                                item.add_request_data('videoTitle', video_link['videoTitle'])
                                item.set_next_action_name('SnapAndPlayVideo')
                                xbmcListItem = xbmcgui.ListItem(label=video_link['videoTitle'], iconImage=video_source_img, thumbnailImage=video_source_img)
                                item.set_xbmc_list_item_obj(xbmcListItem)
                                response_obj.addListItem(item)
                        
                        if len(video_playlist_items) > 0:
                            response_obj.addListItem(__preparePlayListItem__(video_source_id, video_source_img, video_playlist_items))
                            video_source_id = video_source_id + 1
                            video_source_img = None
                            video_part_index = 0
                            video_playlist_items = []
                    
                    else:
                        
                        if re.search('http://media.pinoymovie.ca/playlist/(.+?).htm', videoLink, re.I):
                            html = HttpClient().getHtmlContent(url=videoLink).replace('\'', '"')
                            videoLink = re.compile('<iframe(.+?)src="(.+?)"', flags=re.I).findall(html)[0][0]
                            
                        video_hosting_info = SnapVideo.findVideoHostingInfo(videoLink)
                        print videoLink
                        if video_hosting_info is None:
                            print 'UNKNOWN streaming link found: ' + videoLink
                            
                        else:
                            item = ListItem()
                            item.add_request_data('videoLink', videoLink)
                            item.add_request_data('videoTitle', 'Source #' + str(video_source_id))
                            item.set_next_action_name('SnapAndPlayVideo')
                            xbmcListItem = xbmcgui.ListItem(label='Source #' + str(video_source_id), iconImage=video_hosting_info.get_video_hosting_image(), thumbnailImage=video_hosting_info.get_video_hosting_image())
                            item.set_xbmc_list_item_obj(xbmcListItem)
                            response_obj.addListItem(item)
                            
                            video_source_id = video_source_id + 1
                except:
                    print 'UNKNOWN streaming link found'
                    video_source_img = None
                    video_part_index = 0
                    video_playlist_items = []
                    


def __preparePlayListItem__(video_source_id, video_source_img, video_playlist_items):
    item = ListItem()
    item.add_request_data('videoPlayListItems', video_playlist_items)
    item.set_next_action_name('SnapAndDirectPlayList')
    xbmcListItem = xbmcgui.ListItem(label=AddonUtils.getBoldString('DirectPlay') + ' | ' + 'Source #' + str(video_source_id) + ' | ' + 'Parts = ' + str(len(video_playlist_items)) , iconImage=video_source_img, thumbnailImage=video_source_img)
    item.set_xbmc_list_item_obj(xbmcListItem)
    return item


#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import xbmcplugin
import xbmcaddon
import xbmcgui
import urlresolver
import re
import sys
import mechanize

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

addon = xbmcaddon.Addon()
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addonId = addon.getAddonInfo('id')
translation = addon.getLocalizedString
xbox = xbmc.getCondVisibility("System.Platform.xbox")
baseUrl = "http://online-filmek.cc/"

def index():
  addDir('Filmek', '', 'filmopciok','')
  addDir('Sorozatok', '','sorozatopciok','')
  xbmcplugin.endOfDirectory(pluginhandle)

def listopciok(what):
  if what == 'film':
    cat = '/filmek/osszes/'
    func = 'filmlista'
  if what == 'sorozat':
    cat = '/sorozatok/'
    func = 'sorozatlista'

  addDir('Keresés', '', 'search','')
  if what == 'film':
    addDir('Kategóriák', '' , 'categories','')
  addDir('Legfrissebb',  baseUrl + cat + 'legfrissebb/1', func, '')
  addDir('Legnézettebb',  baseUrl + cat +'legnezettebb/1', func, '')
  xbmcplugin.endOfDirectory(pluginhandle)

def categories(url):
  addDir('Akció',  baseUrl + '/filmek/akcio/legfrissebb/1' , 'filmlista', '')
  addDir('Dráma',  baseUrl + '/filmek/drama/legfrissebb/1' , 'filmlista', '')
  addDir('Fantasztikus',  baseUrl + '/filmek/fantasztikus/legfrissebb/1' , 'filmlista', '')
  addDir('Horror',  baseUrl + '/filmek/horror/legfrissebb/1' , 'filmlista', '')
  addDir('Sci-fi',  baseUrl + '/filmek/scifi/legfrissebb/1' , 'filmlista', '')
  addDir('Thriller',  baseUrl + '/filmek/thriller/legfrissebb/1' , 'filmlista', '')
  addDir('Vígjáték',  baseUrl + '/filmek/vigjatek/legfrissebb/1' , 'filmlista', '')
  xbmcplugin.endOfDirectory(pluginhandle) 

def getUrl(url):
  req = urllib2.Request(url)
  req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:19.0) Gecko/20100101 Firefox/19.0')
  response = urllib2.urlopen(req)
  link = response.read()
  response.close()
  return link

def follow_redirect(url):
  req = urllib2.Request(url)
  req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:19.0) Gecko/20100101 Firefox/19.0')
  link = urllib2.urlopen(req).geturl()
  return link


def listvideos(urlFull,what='film'):
  content = getUrl(urlFull)
  soup = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES)

  currentPage = 0
  nextPage = 0
  maxpage = -1
  currentpage = urlFull.rsplit('/',1)
  nextpage = int(currentpage[1]) + 1

  filmek = soup.findAll('span', attrs={'class': 'tablazat'})
  for film_spans in filmek:
    link = film_spans.find('a', href=True)
    url = link['href']
    img = link.find('img',src=True)['src']
    title = link.find('img',src=True)['alt']
    if what == 'film':
      addDir(title, url, 'listproviders', img)
    if what == 'sorozat':
      addDir(title, url, 'listseries', img)
#  else:
#    filmek = soup.findAll('div', attrs={'class': 'box'})
#    for film_spans in filmek:
#      url = film_spans.find('a')['href']
#      title = film_spans.find('a').text
#      img = ''
#      print "LISTVIDEOS, SOROZAT: " + url
#      addDir(title, url, 'listproviders', img)

    # for the plot
#    print "ListVideos URL:" + url
#    content2 = getUrl(url)
#    soup2 = BeautifulSoup(content2,convertEntities=BeautifulSoup.HTML_ENTITIES)
#    plot = soup2.findAll('div', attrs={'class':'leiras'})[1].text
    #
  addDir('Következő -->', currentpage[0] + '/' + str(nextpage) ,'filmlista','')
  xbmcplugin.endOfDirectory(pluginhandle)

def listproviders(urlFull):
  content = getUrl(urlFull)
  soup = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES)
  print urlFull
  megoszto_link=soup.find('a', attrs={'id': 'megoszto_link'})['href']
  filmvilag=getUrl(megoszto_link)
  fsoup=BeautifulSoup(filmvilag,convertEntities=BeautifulSoup.HTML_ENTITIES)
  provtable = fsoup.find('table').findAll('tr')
  provtable.pop(0)
  for provider in provtable:
    td = provider.findAll('td')
    if td:
      minoseg = td[0].text
      prov = td[1].text
      if td[0].find('div')['class'] == 'kep-magyar_szinkron':
        nyelv = 'HUN'
      else:
        nyelv = 'SUB'
      url = td[3].find('a')['href']
      addDir('[' + minoseg + '] ' + prov + '  ' + nyelv , url, 'playvideo', '')
  xbmcplugin.endOfDirectory(pluginhandle)

def listseries(urlFull):
  content = getUrl(urlFull)
  soup = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES)
  filmek = soup.findAll('span', attrs={'class': 'tablazat'})
  for film_spans in filmek:
    url = film_spans.find('a')['href']
    fulltitle = film_spans.find('div',attrs={'class': 'box'}).text
    title = re.search('(\d+\. \xe9vad \d+\. r\xe9sz)', fulltitle)
    if title is not None:
      title = title.group(1)
    else:
      title = fulltitle[-30:]
    img = film_spans.find('a').find('img')['src'] 
    addDir(title, url, 'listproviders', img)
  xbmcplugin.endOfDirectory(pluginhandle)


def playvideo(url,title):
  link = follow_redirect(url)
  print "************ playvideo link: " + link

  content = getUrl(link)
  soup = BeautifulSoup(content,convertEntities=BeautifulSoup.HTML_ENTITIES)
  meta = soup.find('meta',attrs={"http-equiv":re.compile("^Refresh$", re.I)})
  if meta is not None:
    metalink = meta['content'].split(';')[1].split('=')[1]
    link = re.search('^http://adf.ly.*(http://.*)$',metalink).group(1)
    print "link a METABAN: " + link

  media_url = urlresolver.resolve(link)
  if media_url:
    xbmc.Player().play(media_url)
  else:
    print "urlresolver.resolve(" + link + ') failed, try to playing directly)'
    xbmc.Player().play(link)

def parameters_string_to_dict(parameters):
  paramDict = {}
  if parameters:
    paramPairs = parameters[1:].split("&")
    for paramsPair in paramPairs:
      paramSplits = paramsPair.split('=')
      if (len(paramSplits)) == 2:
        paramDict[paramSplits[0]] = paramSplits[1]
  return paramDict

def addDir(name, url, mode, iconimage,plot=''):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+"&fanart="+urllib.quote_plus(iconimage)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name,"plot": plot})
  liz.setProperty("fanart_image", iconimage)
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok

def search():
  keyboard = xbmc.Keyboard('', str(translation(30008)))
  keyboard.doModal()
  if keyboard.isConfirmed() and keyboard.getText():
    search_string = keyboard.getText()
    br = mechanize.Browser()
    br.addheaders = [('User-agent', 'Mozilla/5.0')]
    br.open(baseUrl)
    br.select_form(nr= 1)
    br.form['kereses'] = search_string
    data = br.submit()
    soup = BeautifulSoup(data.read(),convertEntities=BeautifulSoup.HTML_ENTITIES)
    filmek = soup.findAll('span', attrs={'class': 'tablazat'})
    for film in filmek:
      url = film.find('a')['href']
      img = film.find('a').find('img')['src']
      fulltitle = film.find('div',attrs={'class': 'box'}).text
      title = re.search('(\d+\. \xe9vad \d+\. r\xe9sz)', fulltitle)
      if title is not None:
        title = title.group(1)
      else:
        title = fulltitle[-30:]
      img = film.find('a').find('img')['src']
      m = re.match("^http://online-filmek.cc/(sorozat)/.*",url)
      if m:
        print "SEARCH, LISTSERIES->" + url
        addDir(title, url, 'listseries', img)
      else:
        addDir(title, url, 'listproviders', img)
  xbmcplugin.endOfDirectory(pluginhandle)


params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
title = urllib.unquote_plus(params.get('title', ''))
fanart = urllib.unquote_plus(params.get('fanart', ''))

if mode == "playvideo":
  print "Playvideo: name: " + name + "\turl:" + url
  playvideo(url,title)
elif mode == "filmlista":
  listvideos(url)
elif mode == 'sorozatlista':
  listvideos(url,'sorozat')
elif mode == "listproviders":
  listproviders(url)
elif mode == "categories":
  categories(url)
elif mode == "filmopciok":
  listopciok("film")
elif mode == "sorozatopciok":
  listopciok('sorozat')
elif mode == 'listseries':
  listseries(url)
elif mode == "search":
  search()
else:
  index()

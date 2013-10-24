#this work with Python 2.7.5
#next line tells QPython to run this in the console
#qpy:console
from urllib import URLopener
from HTMLParser import HTMLParser
from time import sleep
import os
from urllib import urlopen
from urllib import urlretrieve
# BS4 import for Nook and RPi
#from BeautifulSoup import BeautifulSoup
# BS4 import for Win7
from bs4 import BeautifulSoup
#import re
# Error on ap051028.html

# Variables
global bDoWork
global bVerified
bVerified = False

# Settings that control behaviour 
# Folder to store the APOD images
global strAPODPicturesFolder
#RPi
#strAPODPicturesFolder = '/home/pi/pishare/'
#Nook HD+ 
#strAPODPicturesFolder = '/mnt/ext_sdcard/Pictures/apod/'
#strAPODDataFolder = '/mnt/ext_sdcard/Pictures/apod/data/'
#Win7 Folder
strAPODPicturesFolder = "C:\\Users\\Dave\\Pictures\\apod\\"
strAPODDataFolder = "C:\\Users\\Dave\\Pictures\\apod\\data\\"
#Note2 Folder
#strAPODPicturesFolder = "/mnt/extSdCard/PhotoAlbums/apod/"
# Should we remove any extra images we may have downloaded during prior executions?
global bCleanExtras
bCleanExtras = False
# How long should we wait as a courtesy after doing work
global lWaitTime
lWaitTime = 0.9
# Do we only process recent files (up until finding a file previously downloaded)?
global bOnlyRecent
bOnlyRecent = False

def DownloadImageFromAPODPage(url):
    # Copy all of the content from the provided web page
    webpage = urlopen(url).read()
    print "-"
    print "URL: " + url
    global bDoWork
    global bCleanExtras
    global bVerified
    global strAPODPicturesFolder
    strAPODFileName = ""
    # Here I retrieve and print to screen the titles and links with just Beautiful Soup
    soup = BeautifulSoup(webpage)
    for url in soup.findAll("a"):
        imgurl = url.get('href')
        #print imgurl
        if not ('http://' in imgurl):
            imgurl = 'http://apod.nasa.gov/' + url.get('href')
            #sleep(lWaitTime)
            if imgurl[len(imgurl) - 3:len(imgurl)] == "jpg":
                print "IMG: " + imgurl
                strAPODFileName = imgurl.strip().split('/')[-1]
                print "strAPODFileName = " + strAPODFileName
                filename = strAPODPicturesFolder + strAPODFileName
                if bDoWork:
                    bDoWork = False
                    #filename = url.strip().split('/')[-1]
                    #print filename
                    if (not os.path.isfile(filename)) and ('apod.nasa.gov' in imgurl):
                        print "Downloading: " + filename
                        image = URLopener()
                        image.retrieve(imgurl,filename) 
                        sleep(lWaitTime)
                    elif (os.path.isfile(filename)):
                        print "Verified: " + filename
                        bVerified = True
                    if not bCleanExtras:
                        #if we are not cleaning extras we can break here
                        print "Not Seeking Extras"
                        break
                else:
                    if (os.path.isfile(filename)):
                        #this is the logic to clean extra downloads/duplicates                
                        print "Deleting " + filename
                        os.remove(filename)
    txtName = ""
    for bTag in soup.findAll("b"):
        if (txtName == ""):
            txtName = bTag.text
            txtName = txtName.strip()
            print txtName

    txtPName = ""
    for pTag in soup.findAll("p"):
        txtPName = pTag.text
        txtPName = txtPName.strip()
        if "Explanation:" in txtPName:
            iLoc = txtPName.find("Tomorrow's picture:")
            iLoc = iLoc - 1
            if iLoc > 0 and (strAPODFileName <> ""):
                txtPName = txtPName[0:iLoc].strip().replace('\n', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace('Explanation: ', '')
                if not (os.path.isfile(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Title.txt'))):
                    print "Title: " + txtName
                    print "FN: " + strAPODFileName.replace('.jpg', '_Title.txt')
                    f = open(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Title.txt'), 'w')
                    f.write(txtName.encode('utf8'))
                    f.close
                if not (os.path.isfile(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Info.txt'))):
                    print "Info Paragraph: " + txtPName
                    print "FN: " + strAPODFileName.replace('.jpg', '_Info.txt')
                    f = open(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Info.txt'), 'w')
                    f.write(txtPName.encode('utf8'))
                    f.close

# Grab image url
class GetIMGURLFromAPODPage(HTMLParser):
    def handle_starttag(self, tag, attrs):
        #tmpoutput = ""
        count = 0
        global bDoWork
        #self.output = ""
        # Only parse the 'anchor' tag.
        if tag == "a":
            # Check the list of defined attributes.
            for name, value in attrs:
                # If href is defined, print it.
                if name == "href":
                    if value[len(value) - 3:len(value)] == "jpg":
                        #print value
                        if not "http://" in value and bDoWork == True: 
                            bDoWork = False
                            tmpoutput = value
                            #print "Val: " + value
                            imgurl = 'http://apod.nasa.gov/apod/' + tmpoutput
                            #print "IMGURL: " + imgurl
                            filename = imgurl.split('/')[-1]
                            #print "FileName: " + filename

                            if (not os.path.isfile(filename)) and ('apod.nasa.gov' in imgurl):
                                print "Downloading: " + filename
                                image = URLopener()
                                image.retrieve(imgurl,filename) 
                                sleep(lWaitTime)
                            elif (os.path.isfile(filename)):
                                print "Verified: " + filename
                            break
                        #elif tmpoutput == "":
                        #    tmpoutput = value
                        #    print "Val: " + value
                        #    self.output = value
                            
def ProcessAPODPage(APODUrl):
    try:
        response = urlopen(APODUrl)
        html = response.read() 

        global bDoWork
        bDoWork = True
        try:
            parser = GetIMGURLFromAPODPage()
            parser.feed(html)
        except HTMLParseError:
            print "Parsing Error" 
        
        """
        try:
            imgurl = parser.output
        except ValueError:
            imgurl = ""

        print "IMGURL: " + imgurl
        filename = imgurl.split('/')[-1]
        print "FileName: " + filename

        if (not os.path.isfile(filename)) and ('apod.nasa.gov' in imgurl):
            image = URLopener()
            image.retrieve(imgurl,filename) 
        """

        #print os.getcwd()
        sleep(lWaitTime)
    except ValueError:
        print "Error processing page"


#'http://apod.nasa.gov/apod/astropix.html'
#The Following Line should get latest APOD
#ProcessAPODPage('http://apod.nasa.gov/apod/astropix.html')

class ProcessPagesInArchive(HTMLParser):
    def handle_starttag(self, tag, attrs):
        try:
            tmpoutput = ""
            count = 0
            global bVerified
            global bOnlyRecent
            # Only parse the 'anchor' tag.
            if tag == "a":
                # Check the list of defined attributes.
                for name, value in attrs:
                    # If href is defined, print it.
                    if name == "href" and not (bOnlyRecent and bVerified):
                        if (value != "astropix.html") and (value[len(value) - 5:len(value)] == ".html"):
                            #print value
                            if (not "http://" in value) and (not "/" in value): 
                                #print "Page: " + value
                                pageurl = 'http://apod.nasa.gov/apod/' + value
                                #print "URL: " + pageurl
                                #ProcessAPODPage(pageurl)
                                try:
                                    global bDoWork
                                    bDoWork = True
                                    DownloadImageFromAPODPage(pageurl)
                                    if (bDoWork):
                                        print "No JPG Found: " + pageurl
                                    sleep(lWaitTime)           
                                except TypeError:
                                    print "Type Error: " + pageurl
        except:
            print "Error Occured"

def ProcessAPODArchive():
    try:
        APODArchive = 'http://apod.nasa.gov/apod/archivepix.html'
        response = urlopen(APODArchive)
        html = response.read() 

        parser = ProcessPagesInArchive()
        parser.feed(html)

        print "Done"

    except ValueError:
        print "Error processing Archive"


ProcessAPODArchive()


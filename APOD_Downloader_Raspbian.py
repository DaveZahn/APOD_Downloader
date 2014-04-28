# -*- coding: utf-8 -*-
#this work with Python 2.7.5
#next line tells QPython to run this in the console
#qpy:console
from urllib import URLopener
from HTMLParser import HTMLParser
from time import sleep
import os
import shutil
from subprocess import call
from urllib import urlopen
from urllib import urlretrieve
# BS4 import for Nook/QPython
#from BeautifulSoup import BeautifulSoup
# BS4 import for Win7/8.1 and RPi
from bs4 import BeautifulSoup
from PIL import Image as PILImage, ImageDraw, ImageFont
#import re
# Error on ap051028.html

# Variables
global bDoWork
global bVerified
bVerified = False

# Settings that control behaviour 
# Folder to store the APOD images
global strAPODPicturesFolder
global strAPODDataFolder
global strAPODPicsWithText
global strAPODCache
global strAPODPicsVLF
strAPODPicsWithText = ""
strAPODPicsVLF = ""
#RPi
if os.path.isdir('/home/pi/pishare/'):
    strAPODPicturesFolder = '/home/pi/pishare/'
    strAPODDataFolder = '/home/pi/pishare/data/'
    strAPODCache = '/home/pi/pishare/cache/'
    strAPODPicsWithText = "/home/pi/pishare/cache_text_new/"
    strAPODPicsVLF = "/home/pi/pishare/cachevlf/"
#Nook HD+ 
if os.path.isdir('/mnt/ext_sdcard/Pictures/apod/'):
    strAPODPicturesFolder = '/mnt/ext_sdcard/Pictures/apod/'
    strAPODDataFolder = '/mnt/ext_sdcard/Pictures/apod/data/'
#Win7 Folder
if os.path.isdir("C:\\Users\\Dave\\Pictures\\apod\\"):
    strAPODPicturesFolder = "C:\\Users\\Dave\\Pictures\\apod\\"
    strAPODDataFolder = "C:\\Users\\Dave\\Pictures\\apod\\data\\"
    strAPODPicsWithText = "C:\\Users\\Dave\\Pictures\\apod\\cache_text\\"
#Win8 Folder
if os.path.isdir("G:\\apod\\"):
    strAPODPicturesFolder = "G:\\apod\\"
    strAPODDataFolder = "G:\\apod\\data\\"
    strAPODPicsWithText = "G:\\apod\\cache_text\\"
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
bOnlyRecent = True
print "APODPicFolder: " + strAPODPicturesFolder
def DownloadImageFromAPODPage(url):

    if "ap140302" in url:
        print "stop here"

    # Copy all of the content from the provided web page
    webpage = urlopen(url).read()
    #print "-"
    #print "URL: " + url
    global bDoWork
    global bCleanExtras
    global bVerified
    global strAPODPicturesFolder
    strAPODFileName = ""
    # Here I retrieve and print to screen the titles and links with just Beautiful Soup
    #print "Loading Soup"
    soup = BeautifulSoup(webpage)
    for url in soup.findAll("a"):
        imgurl = url.get('href')
        #print imgurl
        if not ('http://' in imgurl):
            imgurl = 'http://apod.nasa.gov/' + url.get('href')
            #sleep(lWaitTime)
            if imgurl[len(imgurl) - 3:len(imgurl)] == "jpg":
                #print "IMG: " + imgurl
                strAPODFileName = imgurl.strip().split('/')[-1]
                #print "strAPODFileName = " + strAPODFileName
                filename = strAPODPicturesFolder + strAPODFileName
                if bDoWork:
                    bDoWork = False
                    #filename = url.strip().split('/')[-1]
                    #print filename
                    if (not os.path.isfile(filename)) and ('apod.nasa.gov' in imgurl):
                        #print "Downloading: " + filename
                        image = URLopener()
                        image.retrieve(imgurl,filename) 
                        sleep(lWaitTime)
                    elif (os.path.isfile(filename)):
                        #print "Verified: " + filename
                        bVerified = True
                    if not bCleanExtras:
                        #if we are not cleaning extras we can break here
                        #print "Not Seeking Extras"
                        break
                else:
                    if (os.path.isfile(filename)):
                        #this is the logic to clean extra downloads/duplicates                
                        #print "Deleting " + filename
                        os.remove(filename)
    
    #print "Seeking Title"
    txtName = ""
    bForce = False

    for bTag in soup.findAll("title"):
        if (txtName == ""):
            #bForce = True
            txtName = bTag.text
            txtName = txtName.replace("APOD:", "").strip()
            if "\r" in txtName or "\n" in txtName:
                txtName = txtName.strip().replace("\r", ' ').replace("\n", " ").replace("  ", " ").replace("  ", " ")
                bForce = True
            #print txtName

    for bTag in soup.findAll("b"):
        if (txtName == ""):
            txtName = bTag.text
            txtName = txtName.strip()
            if "\r" in txtName or "\n" in txtName:
                txtName = txtName.strip().replace("\r", ' ').replace("\n", " ").replace("  ", " ").replace("  ", " ")
                bForce = True
            #print txtName

    #print "Loading Info"
    txtPName = ""
    for pTag in soup.findAll("p"):
        txtPName = pTag.text
        txtPName = txtPName.strip()
        if "Explanation:" in txtPName:
            iLoc = txtPName.find("Tomorrow's picture:")
            iLoc = iLoc - 1
            iLoc2 = txtPName.find("digg_url")
            if iLoc2 > 0:
                #txtPName = txtPName
                txtPName = txtPName[:iLoc2]
            iLoc2 = txtPName.find("APOD presents:")
            if iLoc2 > 0:
                #txtPName = txtPName
                txtPName = txtPName[:iLoc2]
            #The Amateur Astronomers Association of New York Presents:
            iLoc2 = txtPName.find("The Amateur Astronomers Association of New York Presents:")
            if iLoc2 > 0:
                #txtPName = txtPName
                txtPName = txtPName[:iLoc2]
            iLoc2 = txtPName.find("Presents:")
            if iLoc2 > 0:
                #txtPName = txtPName
                txtPName = txtPName[:iLoc2]
            iLoc2 = txtPName.find("What was that?:")
            if iLoc2 > 0:
                #txtPName = txtPName
                txtPName = txtPName[:iLoc2]
            iLoc2 = txtPName.find("Follow APOD on:")
            if iLoc2 > 0:
                #txtPName = txtPName
                txtPName = txtPName[:iLoc2]
                bForce = True
            if iLoc > 0 and (strAPODFileName <> ""):
                txtPName = txtPName[0:iLoc].strip().replace('\n', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace('Explanation: ', '')
                if bForce or not (os.path.isfile(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Title.txt'))):
                    #print "Title: " + txtName
                    #print "FN: " + strAPODFileName.replace('.jpg', '_Title.txt')
                    f = open(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Title.txt'), 'w')
                    f.write(txtName.encode('utf8'))
                    f.close
                if bForce or (txtPName.strip() <> "") or (iLoc2 > 0) or (not (os.path.isfile(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Info.txt')))):
                    #print "Info Paragraph: " + txtPName.encode('utf8')
                    #print "FN: " + strAPODFileName.replace('.jpg', '_Info.txt')
                    with open(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Info.txt'), 'w') as f:
                        #f = open(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Info.txt'), 'w')
                        f.write(txtPName.encode('utf8'))
                        #f.close
                        #f.flush

    #print "Checking for Title File"
    if (not strAPODFileName == "") and (not (os.path.isfile(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Title.txt')))):
        #print "Title not found"
        txtAllPageText = soup.get_text().replace("\r", ' ').replace("\n", " ").replace("  ", " ").replace("  ", " ")
        if "-" in txtAllPageText:
            iLoc1 = txtAllPageText.find("-")
            txtAllPageText = txtAllPageText[iLoc1 + 1:].strip()
            iLoc2 = txtAllPageText.find("Astronomy Picture of the Day")
            txtAllPageText = txtAllPageText[:iLoc2].strip()
            #print "Title: " + txtAllPageText
            #print "FN: " + strAPODFileName.replace('.jpg', '_Title.txt')
            f = open(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Title.txt'), 'w')
            f.write(txtAllPageText.encode('utf8'))
            f.close

    #print "Checking for Info File"
    if (not strAPODFileName == "") and (not (os.path.isfile(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Info.txt')))):
        #print "Info file found"
        txtAllPageText = soup.get_text().replace("\r", ' ').replace("\n", " ").replace("  ", " ").replace("  ", " ")
        if "Explanation:" in txtAllPageText:
            iLoc1 = txtAllPageText.find("Explanation:")
            txtAllPageText = txtAllPageText[iLoc1 + 12:].strip()
            iLoc2 = txtAllPageText.find("Tomorrow's picture:")
            txtAllPageText = txtAllPageText[:iLoc2].strip()
            iLoc2 = txtAllPageText.find("digg_url")
            if iLoc2 > 0:
                #txtPName = txtPName
                txtAllPageText = txtAllPageText[:iLoc2]
            iLoc2 = txtAllPageText.find("APOD Presents:")
            if iLoc2 > 0:
                #txtPName = txtPName
                txtAllPageText = txtAllPageText[:iLoc2]
            iLoc2 = txtAllPageText.find("Presents:")
            if iLoc2 > 0:
                #txtPName = txtPName
                txtAllPageText = txtAllPageText[:iLoc2]
            iLoc2 = txtAllPageText.find("What was that?:")
            if iLoc2 > 0:
                #txtPName = txtPName
                txtAllPageText = txtAllPageText[:iLoc2]
            iLoc2 = txtAllPageText.find("The Amateur Astronomers Association of New York Presents:")
            if iLoc2 > 0:
                #txtPName = txtPName
                txtAllPageText = txtAllPageText[:iLoc2]
            iLoc2 = txtAllPageText.find("Follow APOD on:")
            if iLoc2 > 0:
                #txtPName = txtPName
                txtAllPageText = txtAllPageText[:iLoc2]
            #print "Info Paragraph: " + txtAllPageText
            #print "FN: " + strAPODFileName.replace('.jpg', '_Info.txt')
            with open(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Info.txt'), 'w') as f:
                #f = open(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Info.txt'), 'w')
                f.write(txtAllPageText.encode('utf8'))
                #f.close

    os.fsync
    if (not strAPODFileName == "") and (os.path.isfile(strAPODPicturesFolder + strAPODFileName)):
        #print "APOD Image File Found"
        #This is True on Windows, should be set to false otherwise
        if False:
            strAPODDestCache = "G:\\apod\\cache_NookHD+\\"
            SaveCacheImage(strAPODPicturesFolder + strAPODFileName, strAPODDestCache + strAPODFileName, 1920.0, 1280.0) 
            strAPODDestCache = "G:\\apod\\cache_Nexus7_2013\\"
            SaveCacheImage(strAPODPicturesFolder + strAPODFileName, strAPODDestCache + strAPODFileName, 1920.0, 1104.0) 
        #save a PIL image containing the Title and Info
        if strAPODPicsWithText <> "":
            SavePILText(strAPODFileName)
        if strAPODCache <> "":
            SaveCacheImage(strAPODPicturesFolder + strAPODFileName, strAPODCache + strAPODFileName, 1920.0, 1080.0) 

def SavePILText(strAPODFileName):

    #use isfile logic to only create new ones, True to recreate them all    
    if not os.path.isfile(strAPODPicsWithText + strAPODFileName): #True:
        print "Building Image With Text"

        #strAPODDataFolder + strAPODFileName.replace('.jpg', '_Info.txt')
        strInfo = ""
        strTitle = ""
        strContents = ""
    
        #if strAPODFileName == "ison_encke_hi1_srem_a.jpg":
        #    print "stop here"
        #if strAPODFileName == "pileus_lowenstein_4320.jpg":
        #    print "stop here"

        try:
            with open(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Info.txt'), 'r') as content_file:
                strInfo = content_file.read()   
        except Exception as e:
            print str(e)
            
        try:
            with open(strAPODDataFolder + strAPODFileName.replace('.jpg', '_Title.txt'), 'r') as content_file:
                strTitle = content_file.read()   
        except Exception as e:
            print str(e)
 
        if strTitle.strip() <> "":
            strContents = strTitle.strip()
    
        if strInfo.strip() <> "":
            if strContents <> "":
                strContents = strContents + ': ' + strInfo.strip()
            else:
                strContents = strInfo.strip()
        else:
            strContents = strInfo.strip()

        try:
            TEXTCOLOR = (0, 0, 0)
            IMGCOLOR = (0, 0, 0, 255)
            OPCOLOR = (150, 150, 150, 255)
            X = 10
            Y = 3
            fontsize = 24
            #how to I manage this on linux?
            font = ImageFont.truetype('arial.ttf', fontsize)
            im = PILImage.new('RGBA',(1920, 1080), IMGCOLOR) # PILImage.open('G:\\blank.png') #.convert('RGB')
            imgWidth, imgHeight = im.size
            draw = ImageDraw.Draw(im)

            sngHeight = imgHeight * 1.0
            sngWidth = imgWidth * 1.0

            bImageToTop = True

            #INSERT THE ORIGINAL INTO THE CANVAS
            strSource = strAPODPicturesFolder + strAPODFileName
            if os.path.isfile(strSource):
                imIN = PILImage.open(strSource)
                imgWidthIN, imgHeightIN = imIN.size


                if strAPODPicsVLF <> "":
                    #print "checking for very large image"
                    #convert very large images on the Pi down to QHD
                    # if dimentions larger than 3840×2160 scale down to that size first
                    sngWidthQHD = 3840.0
                    sngHeightQHD = 2160.0
                    if imgWidthIN > sngWidthQHD or imgHeightIN > sngHeightQHD:
                        #convert titan5km_huygens_big.jpg -resize 3840x2160 test.jpg
                        #subprocess.call(["ls", "-l"])
                        print "converting VLF"
                        #strArgs = " '" +  + "'"
                        #print "convert " + strArgs
                        #call(["ls", "-l"])
                        call(["convert", strAPODPicturesFolder + strAPODFileName, "-resize", "3840x2160", strAPODPicsVLF + strAPODFileName])
                        print "reopening VLF"
                        imIN = PILImage.open(strAPODPicsVLF + strAPODFileName)
                        imgWidthIN, imgHeightIN = imIN.size

                
                bResized = False
                if imgHeightIN > sngHeight:
                    bResized = True
                    sngChange = sngHeight / imgHeightIN
                    imgHeightIN = int(sngHeight)
                    imgWidthIN = int(imgWidthIN * sngChange)
                if imgWidthIN > sngWidth:
                    bResized = True
                    sngChange = sngWidth / imgWidthIN
                    imgWidthIN = int(sngWidth)
                    imgHeightIN = int(imgHeightIN * sngChange)

                szNew = imgWidthIN, imgHeightIN
                if bResized:
                    imIN=imIN.resize(szNew, PILImage.ANTIALIAS)

                #does image go to right or to top?
                if ((imgWidthIN * 1.0) / imgHeightIN) > ((imgWidth * 1.0) / imgHeight):
                    #print "Input Image More Landscape - print to top"
                    if imgHeightIN < (1080 / 2):
                        offset=((imgWidth-imgWidthIN)/2,(1080 / 2) - imgHeightIN) #(imgHeight-imgHeightIN)/2)
                    else:
                        offset=((imgWidth-imgWidthIN)/2,0) #(imgHeight-imgHeightIN)/2)
                    im.paste(imIN,offset)
                else:
                    bImageToTop = False
                    #print "Input Image More Portrait - print to right"
                    offset=(min((1920 / 2),(imgWidth-imgWidthIN)),(imgHeight-imgHeightIN)/2)
                    im.paste(imIN,offset)

            #MANAGE THE TEXT OVERLAY
            #decide what gets printed on what line
            tmpLine = ""
            strLine = ""
            #print "Splitting Contents:" + strContents
            words = strContents.split(' ')
            #list of lines to print
            strLines = []
            bLines = False

            if bImageToTop == True:
                #print "printing image to top, text underneath"
                for word in words:
                    #print "10"
                    if strLine == "":
                        #print "20"
                        strLine = word
                    else:
                        #print "30"
                        strLine = strLine + ' ' + word
                    #print "35"
                    strLine = strLine.strip()
                    #print "40: " + strLine   
                    if strLine <> "":
                        #print "45"   
                        intWidth, intHeight = draw.textsize(strLine, font=font)
                        #print "50"
                        #print 'Text Render Width = ' + str(intWidth) + ', Text Render Height = ' + str(intHeight)
                        if intWidth > (imgWidth - 20):
                            #print "Drawing Text loop: " + tmpLine
                            #draw.text((X, Y), tmpLine, font=font, fill=TEXTCOLOR)
                            strLines.append(tmpLine)
                            #print "100 %s, %s", X, Y
                            #Y += 33 # intHeight * 1.1
                            #print "110"    
                            strLine = word
                            tmpLine = strLine            
                        else:
                            tmpLine = strLine
                #print "Drawing Text"
                #print "tmpLine = " + tmpLine
                if not tmpLine == "":
                    #draw.text((X, Y), tmpLine, font=font, fill=TEXTCOLOR)
                    strLines.append(tmpLine)
                else:
                    print "Nothing To Print"

                if True: #False:
                    #Print On The Opacity Layer behind the text
                    #print "making opacity background"
                    intLineEstimate = len(strLines)
                    intRectHeight = intLineEstimate * 33 # 250 # calced by length of text
                    intGradHeight = 40
                    sngGradVal = 0
                    intGradMaxOpacity = 210
                    intX = 1920
                    intY = 1080

                    bgimg = PILImage.new('RGBA',(intX, intY), OPCOLOR)
                    gradient = PILImage.new('L', (1,intY))

                    for y in range(intY):
                        if (y < (intY - (intRectHeight + intGradHeight))):
                            gradient.putpixel((0,y),0)
                        elif (y < (intY - intRectHeight)):
                            gradient.putpixel((0,y),int(sngGradVal))
                            sngGradVal = sngGradVal + ((intGradMaxOpacity * 1.0) / intGradHeight)
                        else:
                            gradient.putpixel((0,y),intGradMaxOpacity)

                    # resize the gradient to the size of im...
                    alpha = gradient.resize(bgimg.size)
                    # put alpha in the alpha band of im...
                    bgimg.putalpha(alpha)
                    #draw bgimg onto im
                    im.paste(bgimg,(0,0),bgimg)

                #print on the text
                bLines = False
                Y = (imgHeight - 10) - (len(strLines) * 33)
                for strLine in strLines:
                    if strLine <> "":
                        bLines = True
                        draw.text((X, Y), strLine, font=font, fill=TEXTCOLOR)
                        Y += 33
                        #print strLine
            else:
                intMaxDesiredLineWidth = max(20, min((1920 / 2), (1920 - imgWidthIN)) - (X * 2)) - 10
                #print "print image right, text to the left"
                if True:
                    #print "new logic"
                    intMaxLines = 32
                    intLinesUsed = 33
                    intTotalWidth, intTotalHeight = draw.textsize(strContents, font=font)
                    while intLinesUsed > intMaxLines:
                        #print "logic here"
                        #run draw logic to find number of current lines
                        intMaxDesiredLineWidth += 5
                        strLines[:] = []

                        #with PILImage.new('RGBA',(1920, 1080), IMGCOLOR) as imT:
                        if True:
                            imT = PILImage.new('RGBA',(1920, 1080), IMGCOLOR)
                            imgWidthT, imgHeightT = imT.size
                            drawT = ImageDraw.Draw(imT)
                        
                            for word in words:
                                if strLine == "":
                                    strLine = word
                                else:
                                    strLine = strLine + ' ' + word
                                strLine = strLine.strip()
                                if strLine <> "":
                                    intWidth, intHeight = drawT.textsize(strLine, font=font)
                                    if intWidth > (intMaxDesiredLineWidth - (X * 2)):
                                        strLines.append(tmpLine)
                                        strLine = word
                                        tmpLine = strLine            
                                    else:
                                        tmpLine = strLine
                            if not tmpLine == "":
                                strLines.append(tmpLine)
                            else:
                                print "Nothing To Print"
                            intLinesUsed = len(strLines)
                            strLine = ""
                            tmpLine = ""
                else:
                    print "old logic"
                    intTotalWidth, intTotalHeight = draw.textsize(strContents, font=font)
                    intTotalPossibleLines = int(1080 / 33.0) - 3
                    intMaxDesiredLineWidth = max(30, min((1920 / 2), (1920 - imgWidthIN)) - (X * 2))
                    intCurrentLines = intTotalWidth / (intMaxDesiredLineWidth - 10)
                    intCurrentLines = (intTotalWidth * 1.15) / (intMaxDesiredLineWidth)
                    #print "TotalPossibleLines: " + str(intTotalPossibleLines)
                    #print "TotalWidth: " + str(intTotalWidth)
                    #guess width per line
                    # if lines * maxdesiredlinewidth > inttotalwidth make maxdesiredlinewidth longer
                    while (intCurrentLines > intTotalPossibleLines) and (intMaxDesiredLineWidth < 1920):
                        #print "recalc intMaxDesiredLineWidth"
                        intMaxDesiredLineWidth += 10
                        #intCurrentLines = (intTotalWidth * 1.1) / (intMaxDesiredLineWidth) # - ((X * 2) + 30))
                        intCurrentLines = (intTotalWidth * 1.15) / (intMaxDesiredLineWidth) # - 10)

                if len(strLines) == intMaxLines:
                    print "stop here"

                strLines[:] = []
                for word in words:
                    #print "10"
                    if strLine == "":
                        #print "20"
                        strLine = word
                    else:
                        #print "30"
                        strLine = strLine + ' ' + word
                    #print "35"
                    strLine = strLine.strip()
                    #print "40: " + strLine   
                    if strLine <> "":
                        #print "45"   
                        intWidth, intHeight = draw.textsize(strLine, font=font)
                        #print "50"
                        #print 'Text Render Width = ' + str(intWidth) + ', Text Render Height = ' + str(intHeight)
                        if intWidth > (intMaxDesiredLineWidth - (X * 2)):
                            #print "Drawing Text loop: " + tmpLine
                            #draw.text((X, Y), tmpLine, font=font, fill=TEXTCOLOR)
                            strLines.append(tmpLine)
                            #print "100 %s, %s", X, Y
                            #Y += 33 # intHeight * 1.1
                            #print "110"    
                            #print "120"
                            strLine = word
                            tmpLine = strLine            
                        else:
                            tmpLine = strLine
                #print "Drawing Text"
                #print "tmpLine = " + tmpLine
                if not tmpLine == "":
                    #draw.text((X, Y), tmpLine, font=font, fill=TEXTCOLOR)
                    strLines.append(tmpLine)
                else:
                    print "Nothing To Print"

                if True: #False:
                    #Print On The Opacity Layer behind the text
                    #print "making opacity background"
                    #intLineEstimate = len(strLines)
                    intRectWidth = intMaxDesiredLineWidth # intLineEstimate * 33 # 250 # calced by length of text
                    intGradWidth = 40
                
                    intGradMaxOpacity = 210
                    sngGradVal = intGradMaxOpacity
                    intX = 1920
                    intY = 1080

                    bgimg = PILImage.new('RGBA',(intX, intY), OPCOLOR)
                    gradient = PILImage.new('L', (intX,1))

                    #make veritical into horizontal
                    for x in range(intX):
                        if (x < (intRectWidth)): # + intGradWidth)):
                            gradient.putpixel((x,0),intGradMaxOpacity)
                        #elif (x < (intRectWidth + intGradWidth)):
                        #    gradient.putpixel((x,0),int(sngGradVal))
                        #    sngGradVal = sngGradVal - ((intGradMaxOpacity * 1.0) / intGradWidth)
                        else:
                            gradient.putpixel((x,0),0)

                    # resize the gradient to the size of im...
                    alpha = gradient.resize(bgimg.size)
                    # put alpha in the alpha band of im...
                    bgimg.putalpha(alpha)
                    #draw bgimg onto im
                    im.paste(bgimg,(0,0),bgimg)

                #print on the text
                Y = max(10, ((imgHeight - 10) - (len(strLines) * 33)) / 2)
                if Y < 50:
                    print "Y = " + str(Y)
                for strLine in strLines:
                    if strLine <> "":
                        bLines = True
                        draw.text((X, Y), strLine, font=font, fill=TEXTCOLOR)
                        Y += 33
                        #print strLine


            if bLines == True:
                print "Saving File " + strAPODPicsWithText + strAPODFileName
                im.save(strAPODPicsWithText + strAPODFileName)
                print "Done Building Cache Image With Text"
        except Exception as e:
            print str(e)



def SaveCacheImage(strSource, strDest, sngWidth, sngHeight):
    if not os.path.isfile(strDest):
        print "Adding " + strDest + " to cache..."
        #from PIL import Image
        im = PILImage.open(strSource)
        imgWidth, imgHeight = im.size
        bResized = False
        #wndWidth, wndHeight =
        if imgHeight > sngHeight:
            bResized = True
            sngChange = sngHeight / imgHeight
            imgHeight = int(sngHeight)
            imgWidth = int(imgWidth * sngChange)
        if imgWidth > sngWidth:
            bResized = True
            sngChange = sngWidth / imgWidth
            imgWidth = int(sngWidth)
            imgHeight = int(imgHeight * sngChange)
        szNew = imgWidth, imgHeight
        #if bResized:
        #set to true to save all images to the cache
        if bResized:
            im=im.resize(szNew, PILImage.ANTIALIAS)
            #assume the destination directory exists
            if (not os.path.isfile(strDest)):
                try:
                    im.save(strDest)      
                except Exception as e:
                    print "save cache file problem: " + e.message        
            else:
                print "save cache file found"        
        else:
            shutil.copyfile(strSource, strDest)

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
                                #print "Downloading: " + filename
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
            #print "--processing ---"
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
                                print "URL: " + pageurl
                                #ProcessAPODPage(pageurl)
                                try:
                                    global bDoWork
                                    bDoWork = True
                                    if pageurl == 'http://apod.nasa.gov/apod/ap131120.html':
                                        print "Stop Here"
                                    DownloadImageFromAPODPage(pageurl)
                                    if (bDoWork):
                                        print "No JPG Found: " + pageurl
                                    sleep(lWaitTime)           
                                except Exception as e:
                                    print "page processing error-2: " + e.message        
        except Exception as e:
            print "page processing error-1: " + e.message        

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

#titan5km_huygens_big.jpg
#SavePILText('titan5km_huygens_big.jpg')
ProcessAPODArchive()


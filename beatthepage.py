################################
#
# c't Schlagseite downloader
# by benjamin schroedl
# benjamin[at]dev-tec.de
# 
# MIT License
# 
# Copyright (c) 2018 Benjamin Schrödl
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################


import os
import re
import requests
import sys

url_list = {}

print("heise.de Schlagseite downloader")
print("")


# create path if they not exist
if(not os.path.isdir("./img/")):
    print("image path does not exist ... creating it")
    os.makedirs("./img/")
    if(not os.path.isdir("./img/")):
        print("image path creation failed")
        sys.exit()
        
if(not os.path.isdir("./pdf/")):
    print("pdf path does not exist ... creating it")
    os.makedirs("./pdf/")
    if(not os.path.isdir("./img/")):
        print("pdf path creation failed")
        sys.exit()


# download Schlagseite overview
# extract urls and get amount of pages by pagination counter
print("parsing page 1");
r     = requests.get("https://www.heise.de/ct/entdecken/?hauptrubrik=%40ctmagazin&unterrubrik=Schlagseite");
urls  = re.findall("/ct/ausgabe/(.*).html\" title=\"(.*)\"", r.text)
pages = re.findall("/ct/entdecken/\?hauptrubrik=%40ctmagazin&unterrubrik=Schlagseite&seite=(.*)\" ", r.text)


# download rest of the Schlagseite overview pages
max_page = int(pages[-1])

if(type(max_page) == int and max_page > 1):
    for i in range (2, max_page):
        print("parsing page " + str(i));
        r     = requests.get("https://www.heise.de/ct/entdecken/?hauptrubrik=%40ctmagazin&unterrubrik=Schlagseite&seite=" + str(i));
        urls += re.findall("/ct/ausgabe/(.*).html\" title=\"(.*)\"", r.text)


# start with building the url url list for downloading
for x in urls:
    if(x[1] == "Schlagseite"):
        edition_str = str.split(x[0], "-")
        # use two characters for edition number
        if(len(edition_str[1]) < 2):
            edition_str[1] = "0" + edition_str[1]
        url_list[edition_str[0] + "-" + edition_str[1]] = "https://www.heise.de/ct/ausgabe/" + x[0] + ".html"
    elif(x[0] == "2015-14-c-t-2683362" and x[1] == "c't"):
        # wrong naming by heise but we accept it
        edition_str = str.split(x[0], "-")
        url_list[edition_str[0] + "-" + edition_str[1]] = "https://www.heise.de/ct/ausgabe/" + x[0] + ".html"
    else:
        print(x[1])
        print("??? unknown link detected >> " + str(x[0]) + " | " + str(x[1]))


print("found", len(url_list), "entries for Schlagseite")



# do the actual download of images and pdfs
print("")
print("downloading ...")

for elem in url_list:
    r_sub   = requests.get(url_list[elem]);
    img     = re.findall("/ct/zcontent/(.*).jpg\" class", r_sub.text)
    img_alt = re.findall("<a href=\"/select/ct/(.*).jpg\"", r_sub.text)

    if isinstance(img, list) and img:
        img_url = "https://www.heise.de/ct/zcontent/" + img[0] + ".jpg"
    else:
        img = img_alt
        img_url = "https://www.heise.de/select/ct/" + img[0] + ".jpg"

    r_img = requests.get(img_url);
    if(r_img.status_code == 200):
        img_file = "./img/" + elem + "-" + os.path.basename(img_url)
        if(os.path.exists(img_file)):
            print("download of " + os.path.basename(img_file) + " already exists")
        else:
            print("download of " + os.path.basename(img_file) + " successfull")
            with open(img_file, 'wb') as f:
                f.write(r_img.content)
    else:
        print("download of " + os.path.basename(img_file) + " failed")


    # for pdf we just have to append ?download=frei at the end of url
    r_pdf = requests.get(url_list[elem] + "?download=frei");
    if(r_pdf.status_code == 200):
        pdf_file = "./pdf/" + elem + "-" + os.path.splitext(os.path.basename(img_url))[0] + ".pdf"
        if(os.path.exists(pdf_file)):
            print("download of " + os.path.basename(pdf_file) + " already exists")
        else:
            print("download of " + os.path.basename(pdf_file) + " successfull")
            with open(pdf_file, 'wb') as f:
                f.write(r_pdf.content)
    else:
        print("download of " + os.path.basename(pdf_file) + " failed")
    

# final message before quiting
print("")
print("downloading ... finished")
print("")





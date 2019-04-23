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
# Angepasst von Thomas Ochs
# Url hat sich geändert. Deshalb musste das Script auf beide Verzeichnisse angepasst werden.
# Version 1.0
# vom 13.04.2019
#
# Kann ganze Jahrgänge holen oder alles, was noch bei Heise liegt.
# (leider geht das nach meiner Kenntnis nur bis 10/2012)
#
# Vor 2016 lagen die grossen Bilder in einer anderen Verzeichnisstruktur:
# /ct/zcontent/
#
# Heute liegn die grossen Bilder unter:
# /select/ct/
#
################################


import os
import re
import requests
import sys

url_list = {}

print("")
print("*****************************************************************************")
print("*                                                                           *")
print("* heise.de Schlagseite: Herunterladen der Schlagseiten in gross und als PDF *")
print("*                                                                           *")
print("*****************************************************************************")
print("")
print("     ohne Parameter    : alle Schlagseiten")
print("     Jahrgang z.B. 2018: Schlagseiten des Jahrgangs")
print("")
print("Version 1.0 vom 13.04.2019")
print("============================================================================")
anzahl_parameter = len(sys.argv)
jahrgang_start = "1993"
#print("Anzahl der Übergabeparameter", anzahl_parameter)
print("")
if(anzahl_parameter == 1):
	jangang_start = "1993"
	print("Hole alle Jahrgäng")
else:
	jahrgang_start = str(sys.argv[1])
	print("Hole Jahrgang: ", jahrgang_start)
print("")
print("***********")
print("* Phase 1 * (Vorbereitung)")
print("***********")
print("");

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
print("***********")
print("* Phase 2 * (Durchsuche Indexseiten nach vorhanden Jahrgängen)")
print("***********")
print("");
#print("hole Index-Seite 1")
if(jahrgang_start == "1993"):
	suchanfrage = "https://www.heise.de/ct/entdecken/?hauptrubrik=%40ctmagazin&unterrubrik=Schlagseite"
	suchanfrage_urls = "/ct/ausgabe/(.*).html\" title=\"(.*)\""
	suchanfrage_pages = "/ct/entdecken/\?hauptrubrik=%40ctmagazin&unterrubrik=Schlagseite&seite=(.*)\" "
else:
	suchanfrage = "https://www.heise.de/ct/entdecken/?hauptrubrik=%40ctmagazin&unterrubrik=Schlagseite&dmin=01-12-" + str(int(jahrgang_start)-1) + "&dmax=31-12-"+ jahrgang_start + "&sort=datum_ab"
	suchanfrage_urls = "/ct/ausgabe/(.*).html\" title=\"(.*)\""
	suchanfrage_pages = "/ct/entdecken/\?hauptrubrik=%40ctmagazin&unterrubrik=Schlagseite&dmin=01-12-" + str(int(jahrgang_start)-1) + "&dmax=31-12-"+ jahrgang_start + "&sort=datum_ab&seite=(.*)\" "
#print("Request: ",suchanfrage)
r     = requests.get(suchanfrage)
urls  = re.findall(suchanfrage_urls, r.text)
pages = re.findall(suchanfrage_pages, r.text)
#print("gefundene URLs: ",urls)
#print("Index-Seiten: ",pages)
laenge_seitenliste = len(pages)
#print("Länge der Seitenliste",laenge_seitenliste)
# download rest of the Schlagseite overview pages
if(laenge_seitenliste == 0):
	max_page = int(1)
else:
	max_page = int(pages[-1])
#print("letzte Seite: ",max_page)
#exit()


if(max_page > 1):
	for i in range(1, max_page):
		print("hole Index-Seite " + str(i+1));
		r     = requests.get(suchanfrage + "&seite=" + str(i+1));
		#print("Request weitere Seiten (",i+1,"): ",suchanfrage)
		urls += re.findall("/ct/ausgabe/(.*).html\" title=\"(.*)\"", r.text)
# start with building the url url list for downloading
for x in urls:
	if(x[1] == "Schlagseite"):
		edition_str = str.split(x[0], "-")
		# use two characters for edition number
		if(len(edition_str[1]) < 2):
			edition_str[1] = "0" + edition_str[1]
		url_list[edition_str[0] + "-" + edition_str[1]] = "https://www.heise.de/ct/ausgabe/" + x[0] + ".html"
		# print("URL (einzeln): ", edition_str[0], edition_str[1])
	elif(x[0] == "2015-14-c-t-2683362" and x[1] == "c't"):
		# wrong naming by heise but we accept it
		edition_str = str.split(x[0], "-")
		url_list[edition_str[0] + "-" + edition_str[1]] = "https://www.heise.de/ct/ausgabe/" + x[0] + ".html"
	else:
		print(x[1])
		print("??? unknown link detected >> " + str(x[0]) + " | " + str(x[1]))
print(len(url_list),"gefundene Bild-Einräge auf",max_page,"Indexseite")
#exit()

# print("URL-Liste:", url_list)

# do the actual download of images and pdfs
print("")
print("***********")
print("* Phase 3 * (Hole Bilder und PDF der Jahrgängen)")
print("***********")
print("")
gefundenes_bild = 0
durchsuchte_url = 0
for elem in url_list:
	r_sub   = requests.get(url_list[elem]);
	#print("Element/Bild: ", elem)
	elem_gespalten_str = str.split(elem, "-")
	#print("Element 0: ", elem_gespalten_str[0])
	#print("Element 1: ", elem_gespalten_str[1])
	if(elem_gespalten_str[0] == jahrgang_start or jahrgang_start == "1993"):
		# Umstellung der URL von /ct/zcontent/ auf /select/ct/
		# mit Ausgabe: 2016
		gefundenes_bild = gefundenes_bild  + 1
		if(int(elem_gespalten_str[0]) < 2016):
			#print("Text der Bildseite: ", r_sub.text)
			img     = re.findall("/ct/zcontent/(.*).jpg\" class", r_sub.text)
			img_url = "https://www.heise.de/ct/zcontent/" + img[0] + ".jpg";
		else:
			img     = re.findall("<a href=\"/select/ct/(.*).jpg\"", r_sub.text)
			# print("Bildname: ", img)
			img_url = "https://www.heise.de/select/ct/" + img[0] + ".jpg"
		print("Ausgabe: ", elem_gespalten_str[0],"-",elem_gespalten_str[1]," Bildname: ", img_url)
		print("Bild wird geladen")
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
		print("PDF wird geladen")
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
	durchsuchte_url = durchsuchte_url + 1
# final message before quiting
print("***********")
print("* Phase 4 * (Übertragung beendet)")
print("***********")
print("")
print("Anzahl der durchsuchten Seiten    : ", durchsuchte_url)
print("Anzahl der gefundenen Schlagseiten: ", gefundenes_bild)
print("")






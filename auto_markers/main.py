import tkinter
import tkinter.filedialog
import os
import xml.etree.ElementTree as ET
import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument("lighthouse")
parser.add_argument("locale")
args = vars(parser.parse_args())

print("Select the map file:")
root = tkinter.Tk()
root.withdraw()
root.update()
map_path = tkinter.filedialog.askopenfilename(initialdir=os.path.expanduser("~"))
root.update()

print("Select any number of marker files to add")
root = tkinter.Tk()
root.withdraw()
root.update()
markers = tkinter.filedialog.askopenfilenames(initialdir=os.path.expanduser("~"))
root.update()


data = {}

# parse the entire map
map = ET.parse(map_path)
root = map.getroot()
folders = root.findall(".{http://www.opengis.net/kml/2.2}Document/{http://www.opengis.net/kml/2.2}Folder")
community_mapping = folders[-1]
lighthouses = community_mapping.findall("./{http://www.opengis.net/kml/2.2}Folder")
for lh in lighthouses:
    lh_name = lh.find("./{http://www.opengis.net/kml/2.2}name").text
    locale_map = {}
    locales = lh.findall("./{http://www.opengis.net/kml/2.2}Folder")
    for locale in locales:
        locale_name = locale.find("./{http://www.opengis.net/kml/2.2}name").text
        enrollment, skilling, placement = locale.findall("./{http://www.opengis.net/kml/2.2}Folder")
        locale_map[locale_name] = {'enrollment': enrollment, 'skilling':skilling, 'placement': placement}
    data[lh_name] = locale_map


def get_placemark(name, lat, lng, status):
    template = """
<Placemark>
    <name>{}</name>
    <LookAt>
        <longitude>{}</longitude>
        <latitude>{}</latitude>
        <altitude>0</altitude>
        <heading>8.477988743497458e-005</heading>
        <tilt>28.80817332026854</tilt>
        <range>146.3098415937417</range>
        <gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>
    </LookAt>
    <styleUrl>{}</styleUrl>
    <Point>
        <gx:drawOrder>1</gx:drawOrder>
        <coordinates>73.83206315942401,18.57125562443015,0</coordinates>
    </Point>
</Placemark>""".format(name, lng, lat, status)
    return ET.fromstring(template)

def add_to_map(name, lat, lng, status, lh_name, locale_name):
    try:
        elem = data[lh_name][locale_name][status]
        # check if someone with this same name exists
        new_elem = get_placemark(name, lat, lng, status)
        elem.append(new_elem)        
    except KeyError:
        print("ERROR: could not find {} folder for locale {} in lighthouse {}".format(status, locale_name, lh_name))
    
for marker_file in markers:
    with open(marker_file, 'r') as csvfile:
        reader= csv.reader(csvfile, delimiter=',')
        for row in reader:
            ix, name, lat, lng, lh_name, locale_name = row
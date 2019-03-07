"""
Will take in an existing map file and a CSV set of markers.
If --erase specified, will completely erase the previous map of markers
If --erase, will attempt to intelligently merge all the new markers into the old map.
The merge strategy is as follows:
- If the person is not included at all in the map, add them as specified
- If the person is included already in the map, delete their old marker and add a new marker
- People are uniquely identified by name so this system will break down if two people have identical names
"""

import argparse
import csv
import os
import tkinter.filedialog
import xml.etree.ElementTree as ET


def parse_map(root):
    """
    :return: Gets all the markers currently on the map and return them in a dict from their names to the node
    """
    markers = {}
    data = {}

    folders = root.findall(".{http://www.opengis.net/kml/2.2}Document/{http://www.opengis.net/kml/2.2}Folder")
    community_mapping = folders[-1]
    lighthouses = community_mapping.findall("./{http://www.opengis.net/kml/2.2}Folder")
    for lh in lighthouses:
        lh_name = lh.find("./{http://www.opengis.net/kml/2.2}name").text.strip().lower()
        locale_map = {}
        locales = lh.findall("./{http://www.opengis.net/kml/2.2}Folder")
        for locale in locales:
            locale_name = locale.find("./{http://www.opengis.net/kml/2.2}name").text.strip().lower()
            categories = locale.findall("./{http://www.opengis.net/kml/2.2}Folder")
            category_map = {}
            for category in categories:
                category_name = category.find("./{http://www.opengis.net/kml/2.2}name").text.strip().lower()
                category_map[category_name] = category
                placemarks = category.findall("./{http://www.opengis.net/kml/2.2}Placemark")
                for placemark in placemarks:
                    name = placemark.find("./{http://www.opengis.net/kml/2.2}name").text.strip().lower()
                    if name in markers:
                        print("WARNING: duplicated name {} detected".format(name))
                    # category is the parent of the marker which we will need to remove from
                    markers[name] = category
            locale_map[locale_name] = category_map
        data[lh_name] = locale_map

    return data, markers


# # parse the entire map
# map = ET.parse(map_path)
# root = map.getroot()
# folders = root.findall(".{http://www.opengis.net/kml/2.2}Document/{http://www.opengis.net/kml/2.2}Folder")
# community_mapping = folders[-1]
# lighthouses = community_mapping.findall("./{http://www.opengis.net/kml/2.2}Folder")
# for lh in lighthouses:
#
#     locales = lh.findall("./{http://www.opengis.net/kml/2.2}Folder")
#     for locale in locales:
#         locale_name = locale.find("./{http://www.opengis.net/kml/2.2}name").text
#         enrollment, skilling, placement = locale.findall("./{http://www.opengis.net/kml/2.2}Folder")
#         locale_map[locale_name] = {'enrollment': enrollment, 'skilling': skilling, 'placement': placement}
#     data[lh_name] = locale_map


def get_placemark(name, lat, lng, status):
    styles = {
        'skilling': "#msn_shaded_dot000",
        'placement': "#msn_shaded_dot002",
        'enrollment': "#m_ylw-pushpin100",
    }
    # placemark = ET.Element("Placemark")
    # name_elem = ET.SubElement(placemark, "name")
    # name_elem.text = name
    #
    # # create marker
    # look_at = ET.SubElement(placemark, "LookAt")
    # longitude = ET.SubElement(look_at, "longitude")
    # latitude = ET.SubElement(look_at, "latitude")
    # altitude = ET.SubElement(look_at, "altitude")
    # heading = ET.SubElement(look_at, "heading")
    # tilt = ET.SubElement(look_at, "tilt")
    # range_elem = ET.SubElement(look_at, "range")
    # gx = ET.SubElement(look_at, "gx")
    # gx.set
    #
    # # fill in properties
    # longitude.text = lng
    # latitude.text = lat
    # altitude.text = 0
    # heading.text = "8.477988743497458e-005"
    # tilt.text = "28.80817332026854"
    # range_elem.text = 146.3098415937417
    # # TODO: how to create
    # gx.text = "relativeToSeaFloor"


    template = """
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2">
    <Document>
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
                <coordinates>{},{},0</coordinates>
            </Point>
        </Placemark>
    </Document>
</kml>
""".format(name, lng, lat, styles[status], lng, lat)
    doc = ET.fromstring(template)
    return doc[0][0]


def add_to_map(name, lat, lng, status, lh_name, locale_name):
    try:
        elem = data[lh_name][locale_name][status]
        new_elem = get_placemark(name, lat, lng, status)
        elem.append(new_elem)
    except KeyError:
        print("ERROR: could not find {} folder for locale {} in lighthouse {}".format(status, locale_name, lh_name))


def delete_marker(name, markers):
    """
    Assumes the marker already exists
    """
    parent = markers[name]
    placemarks = parent.findall("./{http://www.opengis.net/kml/2.2}Placemark")
    for placemark in placemarks:
        elem = placemark.find("./{http://www.opengis.net/kml/2.2}name").text
        if elem == name:
            parent.remove(elem)


def parse_lat_lng(raw):
    raw = raw.strip()
    parts = raw.split("°")
    integer = parts[0]
    decimal = ''.join([c for c in parts[1] if c not in '\'".NESW'])
    return "{}.{}".format(integer, decimal)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

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
    marker_files = tkinter.filedialog.askopenfilenames(initialdir=os.path.expanduser("~"))
    root.update()

    map = ET.parse(map_path)
    root = map.getroot()
    data, markers = parse_map(root)

    for marker_file in marker_files:
        with open(marker_file, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                ix, name, lat, lng, lh_name, locale_name, status = row
                lat = parse_lat_lng(lat)
                lng = parse_lat_lng(lng)
                lh_name = lh_name.strip().lower()
                locale_name = locale_name.strip().lower()
                status = status.strip().lower()
                if name in markers:
                    print("{} already found in map. Overwriting with new data...".format(name))
                    delete_marker(name, markers)
                add_to_map(name, lat, lng, status, lh_name, locale_name)

    map.write("output.xml")
    print("FINISHED!")

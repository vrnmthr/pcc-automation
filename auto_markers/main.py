"""
Will take in an existing map file and a CSV set of markers.
If --erase specified, will completely erase the previous map of markers
If not --erase, will attempt to intelligently merge all the new markers into the old map.
The merge strategy is as follows:
- If the person is not included at all in the map, add them as specified
- If the person is included already in the map, delete their old marker and add a new marker
- People are uniquely identified by name so this system will break down if two people have identical names
"""

import argparse
import csv
import os
import re
import tkinter.filedialog
import xml.etree.ElementTree as ET

import printer


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
                        print(printer.fail_string("WARNING: duplicated marker {} detected".format(name)))
                    # category is the parent of the marker which we will need to remove from
                    markers[name] = category
            locale_map[locale_name] = category_map
        data[lh_name] = locale_map

    return data, markers


def get_placemark(name, lat, lng, status):
    styles = {
        'skilling': "#msn_shaded_dot000",
        'placement': "#msn_shaded_dot002",
        'enrollment': "#m_ylw-pushpin100",
    }

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
        print(printer.fail_string(
            "ERROR: could not find {} folder for locale {} in lighthouse {}".format(status, locale_name, lh_name)))


def delete_all_markers():
    for lh_name in data:
        lh = data[lh_name]
        for locale_name in lh:
            locale = lh[locale_name]
            for status in locale:
                folder = locale[status]
                placemarks = folder.findall("./{http://www.opengis.net/kml/2.2}Placemark")
                for placemark in placemarks:
                    name = placemark.find("./{http://www.opengis.net/kml/2.2}name").text.strip().lower()
                    print(printer.fail_string("ERASING MARKER: {}").format(name))
                    folder.remove(placemark)


def delete_marker(name, markers):
    """
    Assumes the marker already exists
    """
    parent = markers[name]
    placemarks = parent.findall("./{http://www.opengis.net/kml/2.2}Placemark")
    for placemark in placemarks:
        elem = placemark.find("./{http://www.opengis.net/kml/2.2}name").text.strip().lower()
        if elem == name:
            print(printer.fail_string("ERASING MARKER: {}").format(name))
            parent.remove(placemark)


def parse_lat_lng(raw):
    """
    Converts string representation in degrees/minutes/seconds into decimal
    """
    parts = re.split(r'[°\'"]', raw.strip())
    degrees = float(parts[0])
    minutes = float(parts[1])
    seconds = float(parts[2])
    return degrees + minutes / 60 + seconds / 3600


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="output.kml", help="path to the file you wish the output to be written to")
    parser.add_argument("--erase", action='store_true', help="erase all the previous markers from this map")

    args = vars(parser.parse_args())
    if not args["output"].endswith(".kml"):
        args["output"] += ".kml"

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

    # map_path = "/Users/vrnmthr/Source/pcc-automation/auto_markers/pcc-formatted.xml"
    # marker_files = ["example.csv"]

    map = ET.parse(map_path)
    root = map.getroot()
    data, markers = parse_map(root)

    if args['erase']:
        delete_all_markers()
        markers = {}

    for marker_file in marker_files:
        with open(marker_file, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                ix, name, lat, lng, lh_name, locale_name, status = row
                lat = parse_lat_lng(lat)
                lng = parse_lat_lng(lng)
                processed_name = name.strip().lower()
                lh_name = lh_name.strip().lower()
                locale_name = locale_name.strip().lower()
                status = status.strip().lower()
                if processed_name in markers:
                    print(printer.warning_string("OVERWRITING MARKER: {}".format(processed_name)))
                    delete_marker(processed_name, markers)
                    add_to_map(name, lat, lng, status, lh_name, locale_name)
                else:
                    add_to_map(name, lat, lng, status, lh_name, locale_name)
                    print(printer.green_string("ADDED MARKER: {}".format(processed_name)))

    map.write(args['output'])
    print(printer.blue_string("FINISHED!"))

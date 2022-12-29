from pathlib import Path
import xml.etree.ElementTree as ElementTree
from zipfile import ZipFile

NS_KML = '{http://www.opengis.net/kml/2.2}'


def _kml_text(element: ElementTree.Element, tag: str) -> str:
    """Return the text of a tag of the given element."""
    return element.find(f'./{NS_KML}{tag}').text.strip()


def _parse_kml_object(self, tree: ElementTree.Element):
    if tree.tag == 'Document':
        o = KmlDocument()
    o.parse(tree)

    return o


class Kml(object):
    """Class for working with KML file. See:
        https://developers.google.com/kml/documentation and
        https://developers.google.com/kml/documentation/kmlreference"""
    _file: (Path or None) = None
    _objects: list = []

    def __init__(self):
        self._file = None
        self._objects = []

    @property
    def file(self) -> (Path or None):
        """Return the Path object for the KMZ file."""
        return self._file

    @file.setter
    def file(self, file: (Path or str)):
        """Set the path to the KMZ file."""
        self._file = Path(file)

    def load(self, file: (Path or str)):
        """Load the XML from a KML file."""
        self.file = file
        with self.file.open(mode='r', encoding='utf-8') as kml_fd:
            tree = ElementTree.parse(kml_fd)

        self.parse(tree)

    def parse(self, tree: ElementTree.ElementTree):
        """Parse the XML from a KML file."""
        kml = tree.getroot()
        for child in list(kml):
            self._objects.append(_parse_kml_object(child))

    #     top_folder = tree.getroot().find(f'./{NS_KML}Document/{NS_KML}Folder')
    #     self._parse_folder(top_folder)
    #     folders = top_folder.findall(f'./{NS_KML}Folder')
    #     for folder in folders:
    #         self._parse_folder(folder)
    #
    # def _parse_folder(self,
    #                   folder: ElementTree.Element, parent_name: str = ""):
    #     folder_name = _kml_text(folder, 'name')
    #     if len(parent_name) > 0:
    #         name = f'{parent_name}: {folder_name}'
    #     else:
    #         name = folder_name
    #
    #     place_marks = folder.findall(f'./{NS_KML}Placemark')
    #     for place_mark in place_marks:
    #         place_mark_name = _kml_text(place_mark, 'name')
    #         description = _kml_text(place_mark, 'description')
    #         xpath_coordinates = f'./{NS_KML}LineString/{NS_KML}coordinates'
    #         coordinates = place_mark.find(xpath_coordinates)
    #         line_string = LineString()
    #         line_string.add_coordinates_from_text(coordinates.text)
    #         line_string.name = f'{name}::{place_mark_name}'
    #         line_string.description = description
    #         self._objects.append(line_string)
    #
    #     for child_folder in folder.findall(f'./{NS_KML}Folder'):
    #         self._parse_folder(child_folder, name)


class KmlObject(object):
    _name: (str or None) = None

    def __init__(self):
        self._name = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name


class KmlDocument(KmlObject):
    _styles: dict = {}
    _style_maps: dict = {}

    def __init__(self):
        _styles = {}
        _style_maps = {}
        super().__init__()

    def parse(self, tree: ElementTree.Element):
        for child in list(tree):
            if child.tag == 'name':
                self._name = child.text.strip()
            elif child.tag == 'Style':
                style = KmlStyle()
                style.parse(child)
                self._styles[style.id] = style
        self.name = _kml_text(tree, 'name')


class KmlStyle(object):
    _id: (str or None) = None
    _properties: dict = {}

    def __init__(self):
        self._id = None
        self._properties = {}

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id_value: str):
        self._id = id_value

    def parse(self, tree: ElementTree.Element):
        self.id = tree.get('id')
        for child in list(tree):
            properties = {}

            self._properties[child.tag] = properties


class Kmz(object):
    """Class for working with KMZ files. The implementation follows
    https://developers.google.com/kml/documentation/kmzarchives"""
    _file: (Path or None) = None
    _kml: (Kml or None) = None

    def __init__(self):
        self._file = None
        self._kml = None

    @property
    def file(self) -> (Path or None):
        """Return the Path object for the KMZ file."""
        return self._file

    @file.setter
    def file(self, file: (Path or str)):
        """Set the path to the KMZ file."""
        self._file = Path(file)

    @property
    def kml(self) -> (Kml or None):
        """Return the KML object representing the KML file inside the
        KMZ archive."""
        return self._kml

    @kml.setter
    def kml(self, kml: Kml):
        """Set the KML object representing the KML file inside the
        KMZ archive."""
        self._kml = kml

    def load(self, file: (Path or str)):
        """Load the KMZ file and parse its contents."""
        self.file = file
        # A KMZ file is a ZIP file containing a single .KMZ file in the top
        # level directory (the first encountered will be used - if there are
        # any more files, they will be ignored.
        with ZipFile(file) as kmz_fd:
            kml_file = [f for f in kmz_fd.namelist()
                        if f[-4:].lower() == '.kml'][0]
            with kmz_fd.open(kml_file, mode='r') as kml_fd:
                tree = ElementTree.parse(kml_fd)

        self.kml = Kml()
        self.kml.file = kml_file
        self.kml.parse(tree)


class GeometryCollection(object):
    _objects: list = []

    def __init__(self):
        self._objects = []


class Geometry(object):
    _name: (str or None) = None
    _description: (str or None) = None
    _properties: dict = {}  # Arbitrary properties added by the user
    _type: str = None

    def __init__(self):
        self._type = 'Geometry'
        self._name = None
        self._description = None
        self._properties = {}

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description: str):
        self._description = description

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, properties: dict):
        self._properties = properties

    def set_property(self, key, value):
        self._properties[key] = value

    @property
    def type(self):
        return self._type


class LineString(Geometry):
    _coordinates: list = []

    def __init__(self):
        super().__init__()
        self._type = 'LineString'
        self._coordinates = []

    @property
    def coordinates(self):
        return self._coordinates

    def add_coordinates_from_text(self, coordinates: str):
        """Add coordinates from a multiline text document with
        the coordinates split by whitespace. This is for example the
        format used in KML/KMZ files for line strings. Example:

        151.1558240349751,-33.79173209283883,0 151.1557895035666,...

        The third component (altitude) is optional and defaults to 0.
        """

        for coordinate in coordinates.split():
            self._coordinates.append(Point(*coordinate.split(',')))

    def __repr__(self):
        points = ', '.join([str(point) for point in self._coordinates])
        if self.name is not None:
            return f'<{self.type} \'{self.name}\': {points}>'
        else:
            return f'<{self.type}: {points}>'

    def __eq__(self, other) -> bool:
        if len(self.coordinates) != len(other.coordinates):
            return False
        for i in range(len(self.coordinates)):
            if self.coordinates[i] != other.coordinates[i]:
                return False
        return True


class Point(Geometry):
    _longitude: float = 0.0
    _latitude: float = 0.0
    _altitude: float = 0.0

    def __init__(self, longitude: (float or None) = None,
                 latitude: (float or None) = None,
                 altitude: (float or None) = None):

        super().__init__()
        self._type = 'Point'
        self._longitude = 0.0
        self._latitude = 0.0
        self._altitude = 0.0
        if longitude is not None:
            self._longitude = longitude

        if latitude is not None:
            self._latitude = latitude

        if altitude is not None:
            self._altitude = altitude

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, longitude: float):
        self._longitude = longitude

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, latitude: float):
        self._latitude = latitude

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, altitude: float):
        self._altitude = altitude

    def __repr__(self):
        if self.name is not None:
            return f'<{self.type} \'{self.name}\': {self}>'
        else:
            return f'<{self.type}: {self}>'

    def __str__(self):
        return f'({self.longitude}, {self.latitude}, {self.altitude})'

    def __eq__(self, other) -> bool:
        return (self.longitude == other.longitude and
                self.latitude == other.latitude and
                self.altitude == other.altitude)

import argparse
from argparse import RawTextHelpFormatter
import json
from decimal import Decimal
from typing import Dict, List

import overpy


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

class BoundaryBox:
    def __init__(self, min_lat, min_lon, max_lat, max_lon):
        self.min_lat = min_lat
        self.min_lon = min_lon
        self.max_lat = max_lat
        self.max_lon = max_lon

    def as_arg(self) -> str:
        return f"{self.min_lat},{self.min_lon},{self.max_lat},{self.max_lon}"

class OverpassApi:
    def __init__(self):
        self.api = overpy.Overpass()

    def query_location_for_shelters(self, boundary_box: BoundaryBox, stuff: str) -> List:
        query: str = self._build_query(boundary_box, stuff)
        result = self.api.query(query)
        result_list: List[Dict] = []
        for node in result.nodes:
            if node.tags.get("name", "N/A") == "N/A":
                continue
            if node.lat == None:
                continue
            result_list.append({
                'id': node.id,
                'name': node.tags.get('name', 'N/A'),
                'latitude': node.lat,
                'longitude': node.lon
            })

        for way in result.ways:
            if way.tags.get("name", "N/A") == "N/A":
                continue
            if way.center_lat == None:
                continue
            result_list.append({
                'id': way.id,
                'name': way.tags.get('name', 'N/A'),
                'latitude': way.center_lat,
                'longitude': way.center_lon
            })

        for relation in result.relations:
            if relation.tags.get("name", "N/A") == "N/A":
                continue
            if relation.center_lat == None:
                continue
            result_list.append({
                'id': relation.id,
                'name': relation.tags.get('name', 'N/A'),
                'latitude': relation.center_lat,
                'longitude': relation.center_lon,
            })
        return result_list

    def _build_query(self, boundary_box: BoundaryBox, stuff: str) -> str:
        bbox = boundary_box.as_arg()
        return """
            (
              node["amenity"="%s"](%s);
              way["amenity"="%s"](%s);
              relation["amenity"="%s"](%s);
            );
            out body;
            >;
            out skel qt;
            """ % (stuff, bbox, stuff, bbox, stuff, bbox,)

def boundary_box_type(coord_str: str) -> BoundaryBox:
    try:
        coords = [float(coord) for coord in coord_str.split(",")]
        if len(coords) == 4:
            return BoundaryBox(coords[0], coords[1], coords[2], coords[3])
        else:
            raise ValueError("Coordinates must consist of four values.")
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid coordinate format. Use 'lat1,lon1,lat2,lon2'.")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Script to find possible shelter locations. Some interesting bounding boxes " \
            "might be: \n" \
            "Tallinn \"59.351129,24.524588,59.496780,24.947561\"\n" \
            "Gaza \"31.439715,34.381670,31.587522,34.551958\"",
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        '-b', '--boundary_box',
        type=boundary_box_type,
        required=True,
        help="Boundary box coordinates in the format 'lat1,lon1,lat2,lon2'",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    boundary_box: BoundaryBox = args.boundary_box
    print(boundary_box.as_arg())

    api = OverpassApi()
    shelters: Dict[str, List] = {}
    shelter_categories: List[str] = [
        "school",
        "place_of_worship",
        "hospital",
    ]

    for category_name in shelter_categories:
        category: List = api.query_location_for_shelters(boundary_box, category_name)
        shelters[category_name] = category

    json_string = json.dumps(shelters, indent=4, cls=DecimalEncoder)
    print(json_string)


if __name__ == "__main__":
    main()

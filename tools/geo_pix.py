import argparse
import json
from typing import List, Optional, Tuple

import pyproj
from osgeo import gdal


class CoordinateTransformer:
    def __init__(self, authority_code: str):
        source_crs = pyproj.CRS(f"EPSG:{authority_code}")
        target_crs = pyproj.CRS("EPSG:4326")
        self.transformer = pyproj.Transformer.from_crs(source_crs, target_crs)

    def transform(self, lat: float, lon: float) -> Tuple[float, float]:
        lat, lon = self.transformer.transform(lon, lat)
        return lat, lon

def get_authority_code(dataset) -> str:
    spatial_ref = dataset.GetProjection()
    srs = gdal.osr.SpatialReference()
    srs.ImportFromWkt(spatial_ref)
    return srs.GetAuthorityCode(None)

def parse_args():
    parser = argparse.ArgumentParser(description="Process a TIFF file's pixels into geographical points.")
    parser.add_argument("-i", "--input_file", required=True, help="Path to the input TIFF file")
    parser.add_argument("--hop", required=False, default=1, type=int,
                        help="Define the hop that skips some of the pixels.")
    parser.add_argument("-d", "--decimal_points", required=False, default=8, type=int,
                        help="Define the hop that skips some of the pixels.")
    return parser.parse_args()

def get_geo_pixels(
        data,
        transformer: CoordinateTransformer,
        geotransform: Tuple,
        hop: int,
        decimal_points: int,
        intensity_max: Optional[float] = None
        ):
    pixels = []
    for y in range(0, data.shape[0], hop):
        for x in range(0, data.shape[1], hop):
            pixel_value = data[y, x]
            if pixel_value > 0:
                latitude: float = geotransform[3] + y * geotransform[5]
                longitude: float = geotransform[0] + x * geotransform[1]
                (lat, lon) = transformer.transform(latitude, longitude)
                intensity: float = 1.0
                if intensity_max != None:
                    intensity = round(pixel_value / intensity_max, 2)
                pixels.append([round(lat, decimal_points), round(lon, decimal_points), intensity])
    return pixels


def main():
    gdal.UseExceptions()
    args = parse_args()

    dataset = gdal.Open(args.input_file, gdal.GA_ReadOnly)

    # For TIFF files with georeference.
    authority_code: str = get_authority_code(dataset)
    geotransform = dataset.GetGeoTransform()

    # For TIFF files without georeference.
    # authority_code: str = "32636"
    # geotransform = (600000.0, 10.0, 0.0, 3500040.0, 0.0, -10.0)

    intensity_max: Optional[float] = 220

    transformer = CoordinateTransformer(authority_code)
    band = dataset.GetRasterBand(1)
    data = band.ReadAsArray()

    pixels: List = get_geo_pixels(data, transformer, geotransform, args.hop, args.decimal_points,
                                  intensity_max)
    print(json.dumps(pixels))


if __name__ == "__main__":
    main()

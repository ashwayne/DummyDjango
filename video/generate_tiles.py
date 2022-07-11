import io
import json
import os
import morecantile
from PIL import Image
from rio_tiler.io import COGReader
from django.conf import settings

from .models import OrthoImage


def tile_gen(path, file_id):
    tms = morecantile.tms.get("WebMercatorQuad")
    try:
        os.mkdir(os.path.join(path, str(file_id)))
    except FileExistsError:
        pass
    ortho_obj = OrthoImage.objects.get(id=file_id)
    coordinates = {}
    prev_tile = []
    with COGReader(f"{settings.BASE_DIR}/orthophoto.tif") as cog:
        ortho_obj.latitude = (cog.geographic_bounds[1] + cog.geographic_bounds[3])/2
        ortho_obj.longitude = (cog.geographic_bounds[0] + cog.geographic_bounds[2])/2

        for zoom in range(18, 21):
            tile_cover = list(tms.tiles(*cog.geographic_bounds, zooms=zoom))
            first_run = True
            for index, tile in enumerate(tile_cover):
                img = cog.tile(*tile)
                byte_data = img.render()
                img = Image.open(io.BytesIO(bytearray(byte_data)))
                img.save(f"{path}/{file_id}/{tile.z}_{tile.x}_{tile.y}.png")

                if first_run:
                    coordinates.update({str(tile.z): [[str(tile.x)], [str(tile.y)]]})
                    if prev_tile:
                        coordinates[prev_tile[0]][0].extend([prev_tile[1]])
                        coordinates[prev_tile[0]][1].extend([prev_tile[2]])
                    first_run = False
                prev_tile = [str(tile.z), str(tile.x), str(tile.y)]
        coordinates[str(prev_tile[0])][0].extend([prev_tile[1]])
        coordinates[str(prev_tile[0])][1].extend([prev_tile[2]])
        coordinates = json.dumps(coordinates, indent=4)
        ortho_obj.tile_coordinates = str(coordinates)
        ortho_obj.save()
        print(coordinates)

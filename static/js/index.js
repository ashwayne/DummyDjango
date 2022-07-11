function initMap() {
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 18,
    center: { lat: 17.5176878, lng: 78.2753824 },
    mapTypeId: 'satellite'
  });
  const bounds = {
    18: [
      [188070, 188071],
      [118112, 118113],
    ],
    19: [
      [376140, 376142],
      [236224, 236226],
    ],
    20: [
      [752281, 752285],
      [472449, 472453],
    ],
    21: [
      [1504563, 1504570],
      [944899, 944907],
    ],
  };
  const imageMapType = new google.maps.ImageMapType({
    getTileUrl: function (coord, zoom) {
      if (
        zoom < 18 || zoom > 21 ||
        bounds[zoom][0][0] > coord.x ||
        coord.x > bounds[zoom][0][1] ||
        bounds[zoom][1][0] > coord.y ||
        coord.y > bounds[zoom][1][1]
      ) {
        return "";
      }
      var img_url = [
        "http://3.111.214.0/ortho_viewer/",
        zoom,
        "_",
        coord.x,
        "_",
        coord.y,
        ".png",
      ].join("");
      return img_url;
    },
    tileSize: new google.maps.Size(256, 256),
  });

  map.overlayMapTypes.push(imageMapType);
}

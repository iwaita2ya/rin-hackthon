var m_mono = new L.tileLayer('https://tile.mierune.co.jp/mierune_mono/{z}/{x}/{y}.png', {
    attribution: "Maptiles by <a href='http://mierune.co.jp/' target='_blank'>MIERUNE</a>, under CC BY. Data by <a href='http://osm.org/copyright' target='_blank'>OpenStreetMap</a> contributors, under ODbL."
});

var map = L.map('map', {
    center: [35.6892463, 139.6918553],
    zoom: 18,
    zoomControl: true,
    layers: [m_mono]
});

/* クリックした場所を中心にして移動. */
map.on('click', function (e) {
    map.panTo(e.latlng);
    console.log("lat:" + e.latlng.lat + " lng:" + e.latlng.lng);
});
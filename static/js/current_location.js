/**
 * Created by Ogiwara on 2017/09/02.
 */
//==================================================================================================
//  位置取得 成功時に実行される
//==================================================================================================
function cmanGetOk(argPos) {
    var latitude = argPos.coords.latitude;
    var longitude = argPos.coords.longitude;

    var locationCenter = new google.maps.LatLng(latitude, longitude);
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({
        "latLng": locationCenter
    }, function (results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            var lat = results[0].geometry.location.lat(),
                lng = results[0].geometry.location.lng();
            document.getElementById("latitude").innerHTML = lat;
            document.getElementById("longitude").innerHTML = lng;
            document.getElementById("latitude_v").value = lat;
            document.getElementById("longitude_v").value = lng;
            console.log(lat, lng);
        }
    });

}

//==================================================================================================
//  位置取得 失敗時に実行される
//==================================================================================================
function cmanGetErr(argErr) {
    var wErrMsg = "";
    switch (argErr.code) {
        case 1 :
            wErrMsg = "位置情報の利用が許可されていません";
            break;
        case 2 :
            wErrMsg = "デバイスの位置が判定できません";
            break;
        case 3 :
            wErrMsg = "タイムアウトしました";
            break;
    }
    if (wErrMsg == "") {
        wErrMsg = argErr.message;
    }

    // --- エラーメッセージ出力 --------------------------------------------------------------------
    document.getElementById("getErrMag").innerHTML = wErrMsg;
}

//==================================================================================================
//  位置取得 実行
//==================================================================================================
function cmanPosGet() {
    // --- ブラウザが対応しているかチェック --------------------------------------------------------
    if (typeof navigator.geolocation === 'undefined') {
        document.getElementById("getErrMag").innerHTML = 'ブラウザが位置情報取得に対応していません';
        cmanGetDisplayCtrl('ERR');
        return false;
    }

    // --- オプション設定 --------------------------------------------------------------------------
    var wOptions = {
        "enableHighAccuracy": true,                       // true : 高精度
        "timeout": 10000,                                 // タイムアウト : ミリ秒
        "maximumAge": 0                                  // データをキャッシュ時間 : ミリ秒
    };

    // --- 位置取得 --------------------------------------------------------------------------------
    navigator.geolocation.getCurrentPosition(cmanGetOk,   // 位置取得成功時に実行される関数
        cmanGetErr,  // 位置取得失敗時に実行される関数
        wOptions);  // オプション
}

/**
 * Adapted from OpenWPM Extension by Marek Schauer
 */
(function () {
    const encode_utf8 = function(s) {
        return unescape(encodeURIComponent(s));
    }

    const escapeString = function(str) {
        // Convert to string if necessary
        if (typeof str != "string") {
            str = String(str);
        }

        return encode_utf8(str);
    };

    const escapeUrl = function(url, stripDataUrlData = true) {
        url = escapeString(url);
        // data:[<mediatype>][;base64],<data>
        if (
            url.substr(0, 5) === "data:" &&
            stripDataUrlData &&
            url.indexOf(",") > -1
        ) {
            url = url.substr(0, url.indexOf(",") + 1) + "<data-stripped>";
        }
        return url;
    };

    // Base64 encoding, found on:
    // https://stackoverflow.com/questions/12710001/how-to-convert-uint8-array-to-base64-encoded-string/25644409#25644409
    const Uint8ToBase64 = function(u8Arr) {
        const CHUNK_SIZE = 0x8000; // arbitrary number
        let index = 0;
        const length = u8Arr.length;
        let result = "";
        let slice;
        while (index < length) {
            slice = u8Arr.subarray(index, Math.min(index + CHUNK_SIZE, length));
            result += String.fromCharCode.apply(null, slice);
            index += CHUNK_SIZE;
        }
        return btoa(result);
    };

    const boolToInt = function(bool) {
        return bool ? 1 : 0;
    };

    window.WEB_API_MANAGER.stringUtils = {
        encode_utf8,
        escapeString,
        escapeUrl,
        Uint8ToBase64,
        boolToInt
    }
}());
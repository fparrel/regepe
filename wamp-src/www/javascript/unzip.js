// require js-unzip.js and js-inflate.js

function unzip(contents) {
    var unzipper = new JSUnzip(contents);
    if(unzipper.isZipFile()) {
        unzipper.readEntries();
        if (unzipper.entries.length>0) {
            var entry = unzipper.entries[0];
            if (entry.compressionMethod==8) {
                var uncompressed = JSInflate.inflate(entry.databuf,entry.uncompressedSize);
                return uncompressed;
            }
        }
    }
    return null;
}

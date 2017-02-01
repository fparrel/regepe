import zipfile
try:
    from flask_babel import gettext
except:
    def gettext(text):
        return text

def unzipOne(fname):
    if not zipfile.is_zipfile(fname):
        raise Exception(gettext('%s is not a zip file') % fname)
    zip = zipfile.ZipFile(fname,'r')
    l = zip.namelist()
    if len(l)!=1:
        raise Exception(gettext('%s contains more than one file') % fname)
    contents = zip.read(l[0])
    zip.close()
    return contents

def iszip(fname):
    return zipfile.is_zipfile(fname)

def main():
    print unzipOne('../work/windsurf.kmz')

if __name__=='__main__':
    main()

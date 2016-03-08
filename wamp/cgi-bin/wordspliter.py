# ','.join(map(lambda a: ("'%c'" % a),range(48,58)+range(65,91)+range(97,123)+range(128,152)+[153,154]+range(160,165)+range(224,240)))

#characters = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K' \
#,'L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f' \
#,'g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

from textutils import remove_accents

characters = map(lambda i: ('%c' % i),range(48,58)+range(65,91)+range(97,123)+range(128,152)+[153,154]+range(160,165)+range(224,240))


def IsLetter(character):
    try:
        if characters.index(character)>-1:
            return True
    except ValueError:
        return False


def SplitWords(value):
    #value = remove_accents(value)
    value = remove_accents(value,'utf-8')
    wordslist = []
    currentword = ''
    for i in value:
        if IsLetter(i):
            currentword = currentword + i
        else:
            if currentword!='':
                wordslist.append(currentword)
                currentword = ''
    #last one
    if currentword!='':
        wordslist.append(currentword)
    return wordslist


def main():
    print(SplitWords('Hello, World !!!'))

if __name__ == '__main__':
   main()


from textutils import remove_accents

characters = map(lambda i: ('%c' % i),range(48,58)+range(65,91)+range(97,123)+range(128,152)+[153,154]+range(160,165)+range(224,240))


def IsLetter(character):
    try:
        if characters.index(character)>-1:
            return True
    except ValueError:
        return False


def SplitWords(value):
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

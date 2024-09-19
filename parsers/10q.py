from PyPDF2 import PdfReader
import time
import sys


def netincome(read): 
    #helper function to get just the net income table. from page 15 on docs
    #takes PdfReader object as an arg
    page = read.pages[14]
    # print(page.extract_text())
    sys.stdout.write(page.extract_text())
    if "ENTERGY CORPORATION AND SUBSIDIARIES\nMANAGEMENT" in page.extract_text():
        print('found it')

    return page.extract_text()


def tojson(path): #"main" function, writes the results from helper function to a json file
    write = path[:len(path)-4]
    read = PdfReader(path)
    # print(len(read.pages))
    # count = len(read.pages)

    try:
        open(f'{write}.txt', 'x')
    except FileExistsError:
        pass
    f = open(f'{write}.txt', 'w')

    f.write(netincome(read))

    return f


start = time.time()
tojson('etr-20240630.pdf')
print(f'Task completed in {time.time()-start} seconds')
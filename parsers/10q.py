from PyPDF2 import PdfReader
import time
import re
import json
import os

def is_number_or_parenthesis_number(s, i):
    if s[i].isdigit():
        return True
    if s[i] == '(' and i + 1 < len(s) and s[i + 1].isdigit():
        return True
    return False

def hardstringtoint(text):
    text = text.replace(",",'')
    if "(" in text:
        text = text.replace("(",'-')
        text = text.replace(')','')
    return(int(text))



def netincomevar(read): 
    #helper function to get just the net income variance table. from page 15 on docs
    #takes PdfReader object as an arg

    num = -1
    for i in range(len(read.pages)): #find page number containing net income variances
        text = read.pages[i].extract_text()
        # print(i)
        if "ENTERGY CORPORATION AND SUBSIDIARIES\nMANAGEMENT" in text and "S FINANCIAL DISCUSSION AND ANALYSIS" in text:
            print(f'found it on page {i}')
            num = i
            break
    
    page = read.pages[num]
    text = page.extract_text()
    
    out = {}
    out['Net Income Variance'] = {}
    key = ''

    for i in text:
        key += i
        if i == '\n':

            if "Quarter" in key:
                quarter = ''
                for j in key:
                    quarter += j
                    if j == 'C':
                        quarter = quarter[:len(quarter)-2]
                        print(quarter)
                        out['Quarter'] = quarter

            if bool(re.search(r'\d+,\d+', key)):
                name = ''
                index = 0
                # print(key)
                for j in key:
                    if is_number_or_parenthesis_number(key,index) and "Net Income" not in key:
                        # print(name)
                        key = key.replace(name,'')
                        key = key.replace('—','0')
                        print(key)
                        key = key.split()
                        
                        # print(key)
                        out['Net Income Variance']['Scale'] = 'Thousands of Dollars'
                        out['Net Income Variance'][name] = {}
                        out['Net Income Variance'][name]['Utility'] = hardstringtoint(key[0])
                        out['Net Income Variance'][name]['Parent & Other'] = hardstringtoint(key[1])
                        out['Net Income Variance'][name]['Entergy'] = hardstringtoint(key[2])
                        break

                    name += j
                    index += 1

            key = ''

    print(out)
    return out


def tojson(path): #"main" function, writes the results from helper function to a json file
    write = path[:len(path)-4]
    print(write)
    read = PdfReader(path)
    

    with open(f'{write}.json', 'w') as fp:
        du = json.dumps(netincomevar(read), indent=4)  
        fp.write(du)

    # f.write(netincome(read))

    return


start = time.time()
tojson('etr-20240331.pdf')
# tojson('etr-20240630.pdf')
print(f'Task completed in {time.time()-start} seconds')
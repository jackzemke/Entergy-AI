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

def is_hyphen(s, i):
    # Ensure the index is within valid range
    if i > 1 and i < len(s) - 2:
        # print(s[i])
        return (
            (s[i - 2].isdigit() and s[i - 1] == ' ' and s[i] == '—') or 
            (s[i] == '—' and s[i + 1] == ' ' and (s[i + 2] == '—' or s[i + 2].isdigit()))
        )
    return False

def hardstringtoint(text):
    text = text.replace(",",'')
    if "(" in text:
        text = text.replace("(",'-')
        text = text.replace(')','')
    text = text.replace("$",'')
    return(int(float(text)))

def extractheaders(text):
    text = text.replace(',',)



def netincomevar(read): 
    #helper function to get just the net income variance table. from page 15 on docs
    #takes PdfReader object as an arg

    num = -1
    for i in range(len(read.pages)): #find page number containing net income variances
        text = read.pages[i].extract_text()
        # print(i)
        if "Following are income statement variances for" in text:
            print(f'found it on page {i}')
            num = i
            break
    
    page = read.pages[num]
    text = page.extract_text()
    # print(text)
    
    out = {}
    out['Net Income Variance'] = {}
    key = ''

    for i in range(len(text)):
        key += text[i]
        # print(key)
        if text[i] == '\n':
            # print(key)

            if "Quarter" in key:
                quarter = ''
                for j in key:
                    quarter += j
                    if j == 'C':
                        quarter = quarter[:len(quarter)-2]
                        print(quarter)
                        out['Quarter'] = quarter

            if "Following are income statement variances for" in key:

                keyadd = ''
                if "comparing" not in key:
                    # print("*****" + i)
                    for k in range(1,30):
                        keyadd += text[i+k]
                        if "comparing" in keyadd:
                            keyadd = keyadd.split()
                            break
                    
                
                temp = key.split()
                temp.extend(keyadd)

                print()
                print("TESTING IDENTIFICATIONS")
                # print(temp)
                head = []
                header = []
                for j in range(temp.index("for")+1,temp.index('comparing')):
                    # print(temp[j])
                    head.append(temp[j])
                    if ',' in temp[j]:
                        l = ' '.join(head)
                        l = l.replace(',','')
                        header.append(l)
                        l = ''
                        head = []
                header.append(temp[temp.index('comparing')-1])
                print(header)
                # print(key)
                print()

            if bool(re.search(r'\d+,\d+', key)):
                name = ''
                index = 0
                # print(f'key: {key}')
                for j in key:
                    if (is_number_or_parenthesis_number(key,index) or is_hyphen(key,index)) and "Net Income" not in key:
                        key = key.replace(name,'')
                        key = key.replace('—','0')
                        # print(key)
                        key = key.split()
                        name = name.replace('$','')
                        
                        print(f'name: {name}')
                        print(f'ending key: {key}')
                        
                        out['Net Income Variance']['Scale'] = 'Thousands of Dollars'
                        out['Net Income Variance'][name] = {}
                        for i in range(len(key)):
                            out['Net Income Variance'][name][header[i]] = hardstringtoint(key[i])
                        break

                    name += j
                    index += 1

            key = ''

    print(out)
    return out


def tojson(path): #"main" function, writes the results from helper function to a json file
    write = path[:len(path)-4]
    # write = os.path.splitext(os.path.basename(path))[0]
    print(write)
    read = PdfReader(path)
    

    with open(f'{write}.json', 'w') as fp:
        du = json.dumps(netincomevar(read), indent=4)  
        fp.write(du)

    # f.write(netincome(read))

    return


start = time.time()
# tojson('etr-20240331.pdf')
# tojson('../data/10QsEntergy/etr-20230630.pdf')
print(f'Task completed in {time.time()-start} seconds')


def iterate_directory(directory_path):
    parent_directory = os.path.dirname(directory_path)
    output_dir = os.path.join(parent_directory, "output")
    print(output_dir)
    print()
    # Iterate over all the files in the directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            print()
            print("*"*10 + "new doc" + "*"*10)
            # Construct the full path of the file
            file_path = os.path.join(root, file)
            # file_path = directory_path
            if ".json" in file_path or ".pdf" not in file_path:
                print(f"doc is {file_path}, skipping")
                continue
            # Pass the file name to the function
            tojson(file_path)

# Specify the directory path
directory = "../data/10QsEntergy"

# Call the function to start iterating over the files
iterate_directory(directory)


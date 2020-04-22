from selenium import webdriver
from PIL import Image
from io import BytesIO
import time, re, math, os, pandas as pd

name, count, touch = '', 0, 0
links = []
try:
    if os.name=='nt':
        cwd=os.getcwd()+'\geckodriver.exe'
    else:
        cwd = os.getcwd() + '/geckodriver'
except:
    print('Operating System not supported by this python script.')
driver = webdriver.Firefox(executable_path=cwd)
driver.minimize_window()


def getUserName():
    global name
    name = input('Enter username')


def verifyaccount(name):
    global links, count, touch
    driver.get('https://www.instagram.com/' + name)
    SCROLL_PAUSE_TIME = 10
    last_height = driver.execute_script("return document.body.scrollHeight")
    while count <= 100:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        element = driver.find_elements_by_tag_name('a')
        for elem in element:
            x = re.search(r'^https://www.instagram.com/p/', elem.get_attribute('href'))
            if (x):
                links.append(elem.get_attribute('href'))
                count += 1
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    if len(links) <= 0:
        print('Sorry, there is no public post associated with ' + name + ' username.')
    else:
        print('Found ' + str(len(links)) + ' latest post, trying to download ', end='')
        if len(links) <= 10:
            print('most liked post.')
            touch = 1
        else:
            print(str(math.ceil(len(links) / 6)) + ' most liked posts.')
            touch = math.ceil(len(links) / 6)


def fetch(links, touch):
    dF = []
    for i in links:
        try:
            driver.get(i)
            x = driver.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/div/div/article/div[2]/section[2]/div/div/button/span')
            dF.append([i, int(x.text.replace(',', ''))])
        except:
            pass
    df = pd.DataFrame(dF, columns=['Post', 'Like'])
    datas = df.sort_values(by='Like', ascending=False)

    return datas[:touch]

def downloadImages(id):
    data=id.to_numpy()
    count=1
    for d in data:
        driver.get(d[0])
        try:
            element = driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div/article/div[1]/div/div/div[1]/img').screenshot_as_png
            im = Image.open(BytesIO(element))
            im.save('Pic '+str(count)+' of '+name+'.png')
            count+=1
        except:
            pass

try:
    getUserName()
    verifyaccount(name)
    datas=fetch(links, touch)
    downloadImages(datas)
except:
    print('Some error occured.')
driver.close()

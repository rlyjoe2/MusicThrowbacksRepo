import requests
import csv
from time import sleep
from bs4 import BeautifulSoup


def createUrl(year:int):
    return "https://www.billboard.com/charts/year-end/{}/hot-100-songs/".format(year)

def html_fetcher(url):
    response = requests.get(url)
    if(response.status_code == 200):
        return response.content
    else:
        print(response.status_code)
        print("Critical Error with html_fetcher")

def parse_page(html:str, year:int):
    soup = BeautifulSoup(html,'html.parser')
    songList = []
    
    songs = soup.find_all('div', class_='o-chart-results-list-row-container')

    # HINT: print reviews to see what http tag to extract
    for song in songs:
       song_name = str(song.find('h3', id='title-of-a-story').text.strip())
       #song_position = int(song.find("span", itemprop = "c-label  a-font-primary-bold-l u-font-size-32@tablet u-letter-spacing-0080@tablet"['content']))
       song_position = song.find("span", class_= "c-label a-font-primary-bold-l u-font-size-32@tablet u-letter-spacing-0080@tablet").getText().strip()
       song_artist = song.find(class_= lambda x: x and x.startswith('c-label a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block')).getText(strip = True)

       revComp = { 'author': song_artist, 'name': song_name, 'rank': song_position, 'date': year}
       songList.append(revComp)
    return songList

def main():
    #years = list(range(2006, 2023, 1))
    # ok for some reason the billboard website is just broken LOL.
    # years 2008 and 2015 is missing, error 404 or something
    years = [2006,2007,2009,2010,2011,2012,2013,2014,2016,2017,2018,2019,2020,2021,2022]
    


    links = []
    for year in years:
        links.append(createUrl(year))
    data = []

    for link, year in zip(links, years):
        html = html_fetcher(link)
        data.append(parse_page(html, year))
        sleep(5)
        
    #Remove these strings if you want the data to be exported yourself.
    """with open("exported_data.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    """
    pass

if __name__ == "__main__":
    main()
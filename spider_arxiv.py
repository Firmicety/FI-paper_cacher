import requests
import time
import os
from components import TIMEOUT_COMMAND
import json
import random

class Articles():
    def __init__(self, title, authors, areas, doi, date):
        self.title = title.replace(' ','_').replace('(','\(').replace(')','\)').replace('/','-')
        self.authors = authors
        self.path = ""
        self.areas = areas
        self.doi = doi
        self.date = date
    def to_dict(self):
        return {
            "title":self.title,
            "authors":self.authors.__str__(),
            "path":self.path,
            "areas":self.areas.__str__(),
            "doi":self.doi
        }

    def download_pdf(self):
        #url = "http://img.saraba1st.com/forum/201901/09/113946rlm9g4roqcquz78x.jpg"
        url = "https://arxiv.org/pdf/%s.pdf"%self.doi
        date = self.date
        path = "./content/%s"%date
        if not os.path.exists(path):
            os.makedirs(path)
        path = path+"/%s.pdf"%self.title
        if not os.path.exists(path):
            cmd = 'curl %s -o %s --fail --silent --show-error'%(url, path)
            result = TIMEOUT_COMMAND(cmd, 3600)
            if result:
                self.path = path
                print("%s succeed"%self.title)
            else:
                if os.path.exists(path):
                    os.remove("%s"%path)
                print("%s failed"%self.title)
        else:
            self.path = path
    
    def __str__(self):
        return self.to_dict().__str__()
    
    

class ArxivSpider():
    def __init__(self, areas_file, date):
        areas, keywords = self.read(areas_file)
        self.areas = areas
        self.articles = {}
        self.date = date

    def read(self, areas_file):
        areas = []
        with open(areas_file) as f:
            content = json.load(f)
            for area in content:
                areas.append(area)
        return areas, []


    def find_total_number(self, strhtml):
        pos1 = strhtml.find("<small>[ total of ")
        pos2 = strhtml.find(" entries:  <b>")
        total_number = strhtml[pos1+18:pos2]
        return total_number

    def find_this_week(self, strhtml):
        new_articles = []
        pos1 = strhtml.find("</h3>",0)
        pos2 = strhtml.find("<h3>",pos1+1)
        item = 0
        while pos1 < pos2:
            new_dt_pos1 = strhtml.find("<dt>",pos1)+4
            new_dt_pos2 = strhtml.find("</dt>",pos1)
            new_dd_pos1 = strhtml.find("<dd>",pos1)+4
            new_dd_pos2 = strhtml.find("</dd>",pos1)
            pos1 = new_dd_pos2+1

            #Title
            title_start_word = '<span class="descriptor">Title:</span> '
            title_end_word = '\n</div>'
            title_pos1 = strhtml.find(title_start_word, new_dt_pos1)+len(title_start_word)
            title_pos2 = strhtml.find(title_end_word, new_dt_pos1)
            title = strhtml[title_pos1:title_pos2]

            #doi
            doi_start_word ='[<a href="/pdf/'
            doi_end_word = '"Download PDF">pdf</a>'
            doi_pos1 = strhtml.find(doi_start_word, new_dt_pos1)+len(doi_start_word)
            doi_pos2 = strhtml.find(doi_end_word, new_dt_pos1)
            doi = strhtml[doi_pos1:doi_pos2-8]

            #Authors
            authors_q_word = '<a href="/search/cs?searchtype=author&query='
            authors_start_word = '">'
            authors_end_word = '</a>'
            authors_next_pos = new_dd_pos1
            authors = []
            while authors_next_pos < new_dd_pos2:
                authors_q_pos = strhtml.find(authors_q_word, authors_next_pos)+1
                authors_pos1 = strhtml.find(authors_start_word, authors_q_pos)+len(authors_start_word)
                authors_pos2 = strhtml.find(authors_end_word, authors_q_pos)
                author = strhtml[authors_pos1:authors_pos2]
                authors_next_pos = authors_q_pos
                authors.append(author)
            
            #area
            areas_start_word = '<span class="primary-subject">'
            areas_end_word = '\n\n</div>'
            areas = []
            areas_pos1 = strhtml.find(areas_start_word, new_dd_pos1)+len(areas_start_word)
            areas_pos2 = strhtml.find(areas_end_word, new_dd_pos1)
            areas_detailed = strhtml[areas_pos1:areas_pos2].split(';')
            for area_detailed in areas_detailed:
                areas.append(area_detailed[area_detailed.find('(')+1: area_detailed.find(')')])

            new_article = Articles(title=title, authors=authors, doi=doi, areas=areas, date=self.date)
            #print(new_article)
            new_articles.append(new_article)

        return new_articles

    def getArxivArticle(self):       
        content_strhtml = {} 
        all_areas = False
        import pdb; pdb.set_trace()
        while not all_areas:
            all_areas = True
            for area in self.areas:
                if area in content_strhtml:
                    if content_strhtml[area] != []:
                        continue

                all_areas = False
                time.sleep(random.random()*10)
                area_url = 'https://arxiv.org/list/%s/'%area + '/pastweek?skip=0&show=%s'
                try:
                    init_strhtml = requests.get(area_url%'0').text
                    total_number = self.find_total_number(init_strhtml)
                    time.sleep(random.random()*10)
                    content_strhtml[area] = requests.get(area_url%total_number).text
                    self.articles[area] = []
                    print("%s content get"%area)
                except Exception as e:
                    content_strhtml[area] = [] 
                    print("Get Resource Error, area: %s"%area)
            for area in self.areas:
                if area in self.articles:
                    self.articles[area] = self.find_this_week(content_strhtml[area])
                    print("%s articles info get"%area)
        #for area_article_list in 
    


if __name__ == '__main__':
    spider = ArxivSpider("./configs/areas_and_keywords.json")
    spider.getArxivArticle()
    all_downloaded = False
    while not all_downloaded and remain < 10:
        all_downloaded = True
        remain = 0
        for area_articles in spider.articles:
            for article in spider.articles[area_articles]:
                if article.path == "":
                    remain += 1
                    all_downloaded = False
                    article.download_pdf()
    undownloaded = []
    for area_articles in spider.articles:
        for article in spider.articles[area_articles]:
            if article.path == "":
                undownloaded.append({"%s"%(article.title):"%s"%article.doi})
    
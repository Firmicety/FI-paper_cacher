import datetime
from datetime import timedelta
from spider_arxiv import ArxivSpider
from email_sender import EmailSender
from components import myThread
import os
import time

last_day = ''
this_day = ''

import pdb; pdb.set_trace()
for i in range(1):
#while True:
    now = datetime.datetime.now()
    day_time = now.hour
    day = timedelta(days=now.weekday()).days
    if day != 6 or day != 0:
        this_day = '%d-%02d-%02d'%(now.year, now.month, now.day)
        if last_day != this_day:
            #grasp data and download
            spider = ArxivSpider("configs/areas_and_keywords.json", this_day)
            spider.getArxivArticle()

            #--------------------------------
            all_downloaded = False
            last_remain_articles = []
            remain_articles = []
            fail_count = 0
            #--------------------------------

            while not all_downloaded:

                #-----------------------------
                all_downloaded = True
                #-------------------------------

                # Threads
                threads = []
                for area_articles in spider.articles:
                    for article in spider.articles[area_articles]:

                        if article.path == "":
                            #-------------------
                            all_downloaded = False
                            remain_articles.append(article.__str__())
                            #------------------------
                            threads.append(myThread(i, article.title, article))
                for task in threads:
                    task.start()
                for task in threads:
                    task.join()
                if len(remain_articles) == len(last_remain_articles):
                    fail_count += 1
                if fail_count > 5:
                    break

            # zip
            #TODO: copy to onedrive file or send to file server
            result = os.system('zip -r zips/%s.zip content/%s'%(this_day,this_day))
            
            # Generate list
            with open("zips/list-%s.txt"%this_day, 'w+') as f:
                for area_articles in spider.articles:
                    for article in spider.articles[area_articles]:
                        f.write(article.__str__()+'\n')

            # send
            sender = EmailSender(file_path='zips/list-%s.txt'%this_day)
            sender.send_email()
        else:
            print("no")
            break
    else:
        print("no_new_article_today")
    print(this_day)
    last_day = this_day
    time.sleep(43200)

    

def GetArticles():
    return
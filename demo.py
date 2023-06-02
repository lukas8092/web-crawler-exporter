import requests
from pyquery import PyQuery as pq
import os
import re
import time
import pickle

cookies = {
    "MOODLEID1_": r"%25F0%25FD%259FR",
    "MoodleSession": r"l3chq5jmtggernmqpffiratt3f"
}

url = "https://moodle.spsejecna.cz/mod/page/view.php?id=7998"
r = requests.get(url,cookies=cookies)

with open("demo.html","wt", encoding='utf-8') as f:
    f.write(r.text)


class Web():
    def __init__(self,title,links,url,html) -> None:
        self.title = title
        self.links = links
        self.url = url
        self.html = html

class PageSave():
    def __init__(self,cookies) -> None:
        self.cookies = cookies

    def _get_page(self,url):
        time.sleep(6)
        r = requests.get(url,cookies=self.cookies)
        return r.text
    
    def parse(self,raw_html,url):
        web = pq(raw_html)
        links_raw = web("a")
        title = web("title").text()
        links = set()
        for l in links_raw:
            try:
                href = pq(l).attr("href")
                if "moodle.spsejecna.cz" in href:
                    links.add(href)
            except:
                pass
        return Web(title,links,url,raw_html)
    
    def write_to_file(self,name,path,html):
        try:
            strs = r'[\/:*?"<>|]'
            name = re.sub(strs, '', name)
            path = re.sub(strs, '', path)
            first_path = f"./moodle/{path}/"
            second_part_path = f"{first_path}{name}.html"
            if not os.path.exists(path):
                try:
                    os.mkdir(first_path)
                except:
                    pass
            with open(second_part_path,"wt", encoding='utf-8') as f:
                f.write(html)
            print(f"Saved:{second_part_path}")
        except Exception as e:
            print(e)
    
    def save_to_file(self,web: Web):
        if "page" in web.url:
            course = web.title.split(":")[0]
            self.write_to_file(web.title,course,web.html)
        if "/course/" in web.url:
            self.write_to_file(web.title,"course",web.html)
        else:
            self.write_to_file(web.title,"other",web.html)
    


    def save(self,url):
        html = self._get_page(url)
        web = self.parse(html,url)
        self.save_to_file(web)
        return web
    

class WebExportCrawler():
    def __init__(self,url,cookies) -> None:
        self.url = url
        self.cookies = cookies
        try:
            with open("visited.pickle","rb") as f:
                self.links_to_crawl = pickle.load(f)
        except:
            self.links_to_crawl = set()
        try:
            with open("links.pickle","rb") as f:
                self.visited_links = pickle.load(f)
        except:
            self.visited_links = set()
        self._start()
    
    def _start(self):
        p = PageSave(cookies)
        base_web = p.save(self.url)
        self.visited_links.add(self.url)
        for link in base_web.links:
            if link not in self.visited_links:
                self.links_to_crawl.add(link)
        while True:
            try:
                if len(self.links_to_crawl) == 0:
                    break
                url_now = self.links_to_crawl.pop()
                self.visited_links.add(url_now)
                web = p.save(url_now)
                for link in web.links:
                    if link not in self.visited_links:
                        self.links_to_crawl.add(link)
            except Exception as e:
                print(f"Err:{e}")
                with open("visited.pickle","wb") as f:
                    pickle.dump(self.visited_links,f)
                with open("links.pickle","wb") as f:
                    pickle.dump(self.links_to_crawl,f)
                break
        print("End")



if __name__ == "__main__":
    c = WebExportCrawler("https://moodle.spsejecna.cz/my/courses.php",cookies)
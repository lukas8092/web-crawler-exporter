import requests
from pyquery import PyQuery as pq
import os
import re
import time
import re
import json


def check_file(text):
    if re.match(r".+\.php$", text):
        return False
    patt = r".+\.[\w]+$"
    return bool(re.match(patt, text))


def parse_url(url: str, base_domain=r"(?:[\w\d-]+\.)+[\w]+"):
    if check_file(url):
        return None
    pattern_html = r"https?:\/\/(?:www\.)?("+base_domain+")((?:\/[\w\d-]+)*)"
    match_html = re.match(pattern_html, url)
    if match_html:
        groups = match_html.groups()
        if len(groups) == 2:
            if groups[1] != "":
                return (groups[1], groups[0])
            else:
                return ("/", groups[0])
    pattern_path = r"^((\/)|(\.\/))([\w\d-]+(\/)?)+"
    match_path = re.match(pattern_path, url)
    if match_path:
        if "?" in url:
            return (url[0:url.find("?")], None)
        else:
            return (url, None)
    return None


class Web():
    def __init__(self, title, links, html) -> None:
        self.title = title
        self.links = links
        self.html = html


class PageSave():
    def __init__(self, base_domain, name, cookies) -> None:
        self.cookies = cookies
        self.name = name
        self.base_domain = base_domain

    def _get_page(self, url):
        with open("cookies.json", "rb") as f:
            biscits = json.load(f)
        time.sleep(0.5)
        r = requests.get(url, cookies=biscits)
        return r.text

    def parse(self, raw_html):
        web = pq(raw_html)
        links_raw = web("a")
        title = web("title").text()
        links = set()
        for l in links_raw:
            try:
                href = pq(l).attr("href")
                parsed = parse_url(url=href, base_domain=self.base_domain)
                if parsed != None:
                    links.add(href)
            except:
                pass
        return Web(title, links, raw_html)

    def make_path(self, path):
        root_path = f"websites/{self.base_domain}-{self.name}"
        if not os.path.isdir(root_path):
            os.makedirs(root_path)
        path = root_path + path
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def save_to_file(self, web: Web, path):
        try:
            dir_path = self.make_path(path)
            strs = r'[\/:*?"<>|]'
            title = re.sub(strs, '', web.title)
            file_path = f"{dir_path}/{title}.html"
            with open(file_path, "wt", encoding='utf-8') as f:
                f.write(web.html)
                print(f"File saved:{file_path}")
        except Exception as e:
            print(f"Error while saving({file_path}):{e}")

    def request(self, url, path):
        html = self._get_page(url)
        web = self.parse(html)
        self.save_to_file(web, path)
        return web


class WebExportCrawler():
    def __init__(self, name, url, cookies) -> None:
        self.name = name
        self.root_url = url
        self.cookies = cookies
        self.links_to_crawl = set()
        self.visited_links = set()

        self._start()

    def add_links_to_visit(self, links):
        for link in links:
            if re.match(r"^http", link) and link not in self.visited_links:
                self.links_to_crawl.add(link)
            else:
                link_edited = f"{self.root_url.split(':')[0]}://{self.base_domain}{link}"
                if link_edited not in self.visited_links:
                    self.links_to_crawl.add(link_edited)

    def _start(self):
        parsed_root_url = parse_url(self.root_url)
        self.base_domain = parsed_root_url[1]
        p = PageSave(self.base_domain, self.name, self.cookies)
        root_web = p.request(self.root_url, parsed_root_url[0])
        self.visited_links.add(self.root_url)
        self.add_links_to_visit(root_web.links)
        while True:
            try:
                if len(self.links_to_crawl) == 0:
                    break
                next_url = self.links_to_crawl.pop()
                parsed_url = parse_url(next_url)
                web = p.request(next_url, parsed_url[0])
                self.visited_links.add(next_url)
                self.add_links_to_visit(web.links)
                print(f"Links left:{len(self.links_to_crawl)}")
            except Exception as e:
                print(f"Error:{e}")
                time.sleep(1)
                self.links_to_crawl.add(next_url)


if __name__ == "__main__":
    c = WebExportCrawler("jecna-ja", "https://www.spsejecna.cz/", None)

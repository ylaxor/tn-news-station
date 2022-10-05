import requests
from bs4 import BeautifulSoup
import urllib

class Fetcher:

    def __init__(self, mainpage_url,  container_find_kwargs, items_find_kwargs, item_title_kwargs, item_link_kwargs):
        self.mainpage_url = mainpage_url
        self.container_find_kwargs = container_find_kwargs
        self.items_find_kwargs = items_find_kwargs
        self.item_title_kwargs = item_title_kwargs
        self.item_link_kwargs = item_link_kwargs
        
    @staticmethod
    def get_elements(parent, **find_kwargs):
        if "child_id" in find_kwargs: 
            return parent.find(id=find_kwargs["child_id"])
        else:
            assert "child_type" in find_kwargs and "child_class" in find_kwargs
            return parent.find_all(find_kwargs["child_type"], class_=find_kwargs["child_class"])

    def get_container(self):
        page = requests.get(self.mainpage_url)
        soup = BeautifulSoup(page.content, "html.parser")
        container = self.get_elements(parent=soup, **self.container_find_kwargs)
        if isinstance(container, list):
            self.container = container[0]
        else:
            self.container = container
        return self
    
    def get_items(self):
        self.items = self.get_elements(parent=self.container, **self.items_find_kwargs)
        return self
    
    def get_item_title(self, item):
        title = self.get_elements(parent=item, **self.item_title_kwargs)[0]
        return title

    def get_item_link(self, item):
        link = self.get_elements(parent=item, **self.item_link_kwargs)[0]
        return link
    
    def get_paired_title_link(self):
        self.paired_items = [(self.get_item_title(item), self.get_item_link(item)) for item in self.items]
        return self
    
    def postprocess(self, title_postprocessor, link_postprocessor):
        self.final_pairs = [(title_postprocessor(p[0]), link_postprocessor(p[1])) for p in self.paired_items]
        return self

def ShemsFM_title_processor(title_html):
    return title_html.attrs["title"]

def ShemsFM_link_processor(link_html):
    return "https://www.shemsfm.net"+link_html.attrs["href"]

def MosaiqueFM_title_processor(title_html):
    a = title_html.find("a", "")
    return a.attrs["title"] 

def MosaiqueFM_link_processor(link_html):
    a = link_html.find("a", "")
    return "https://www.mosaiquefm.net" + a.attrs["href"]

def Jomhouria_title_processor(title_html):
    a = title_html.find("a", "")
    title = a.attrs["href"].split("_")[1]
    return title

def Jomhouria_link_processor(link_html):
    a = link_html.find("a", "")
    link = a.attrs["href"]
    return ("https://www.jomhouria.com/" + link).replace(" ", "%20")


def Assarih_title_processor(title_html):
    title = title_html.attrs["title"]
    return title

def Assarih_link_processor(link_html):
    link = link_html.attrs["href"]
    return link

def fetch_pages(nb_pages):
    shems = []
    mosa = []
    jomhouria = []
    assarih = []
    for i in range(1, nb_pages+1):

        ShemsFM_fetcher = Fetcher(
            mainpage_url="https://www.shemsfm.net/amp/ar/actualites/%D8%A7%D9%84%D8%A3%D8%AE%D8%A8%D8%A7%D8%B1-%D8%A3%D8%AE%D8%A8%D8%A7%D8%B1-%D8%AA%D9%88%D9%86%D8%B3/64/"+str(i),
            container_find_kwargs={"child_type": "div", "child_class": "container"},
            items_find_kwargs={"child_type": "div", "child_class": "item"},
            item_title_kwargs={"child_type": "a", "child_class": "" },
            item_link_kwargs={"child_type": "a", "child_class": "" },
            )

        MosaiqueFM_fetcher = Fetcher(
            mainpage_url="https://www.mosaiquefm.net/ar/actualites/"+str(i), 
            container_find_kwargs={"child_type": "section", "child_class": "homeNews2"},
            items_find_kwargs={"child_type": "div", "child_class": "item"},
            item_title_kwargs={"child_type": "h3", "child_class": "" },
            item_link_kwargs={"child_type": "h3", "child_class": "" },
            )

        Jomhouria_fetcher = Fetcher(
            mainpage_url="https://www.jomhouria.com/index.php?art=1&page="+str(i), 
            container_find_kwargs={"child_id": "maincon"},
            items_find_kwargs={"child_type": "li", "child_class": "clearfix"},
            item_title_kwargs={"child_type": "h2", "child_class": "" },
            item_link_kwargs={"child_type": "h2", "child_class": "" },
            )

        Assarih_fetcher = Fetcher(
            mainpage_url="https://www.assarih.com/category/%D9%88%D8%B7%D9%86%D9%8A%D8%A9/page/"+str(i), 
            container_find_kwargs={"child_type": "div", "child_class": "content-inner"},
            items_find_kwargs={"child_type": "div", "child_class": "p-wrap"},
            item_title_kwargs={"child_type": "a", "child_class": "p-flink" },
            item_link_kwargs={"child_type": "a", "child_class": "p-flink" },
            )

        ShemsFM_fetcher = ShemsFM_fetcher.get_container().get_items().get_paired_title_link().postprocess(ShemsFM_title_processor, ShemsFM_link_processor)
        MosaiqueFM_fetcher = MosaiqueFM_fetcher.get_container().get_items().get_paired_title_link().postprocess(MosaiqueFM_title_processor, MosaiqueFM_link_processor)
        Jomhouria_fetcher = Jomhouria_fetcher.get_container().get_items().get_paired_title_link().postprocess(Jomhouria_title_processor, Jomhouria_link_processor)
        Assarih_fetcher = Assarih_fetcher.get_container().get_items().get_paired_title_link().postprocess(Assarih_title_processor, Assarih_link_processor)

        shems.extend(ShemsFM_fetcher.final_pairs)
        mosa.extend(MosaiqueFM_fetcher.final_pairs)
        jomhouria.extend(Jomhouria_fetcher.final_pairs)
        assarih.extend(Assarih_fetcher.final_pairs)
    
    return {"Mosaique FM":mosa, "Shems FM":shems, "Jomhouria":jomhouria, "Assarih":assarih}
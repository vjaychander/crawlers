"""
  Module to crawl the Zerodha
"""

import os
import re
import sys
from collections import OrderedDict
import requests
from bs4 import BeautifulSoup


class Zerodha(object):
    """Main class"""
    def __init__(self, url):

        if not os.path.exists("zerodha"):
            os.mkdir("zerodha")
        else:
            self.path = os.path.abspath("zerodha")

        self.url = url
        self._handler = None
        self.modules = self._get_modules()

    def get_comments(self, module=None, chapter=None):
        """ Function to crawl the comments
		    Args: Module, Chapter
		"""

        if module:
            if chapter:
                if module == 5 and chapter == 1:
                    print "Something wrong with HTML"
                    sys.exit(0)
                self._load_comments(module, chapter)

        if not module and not chapter:
            for module_item in self.modules:
                chapters = self.modules[module_item]["chapters"]
                if module_item == "module5": # skips module 5 chapter 1
                    chapters = chapters[1:]
                for chapter_item in range(1, len(chapters)+1):
                    self._load_comments(module_item, chapter_item)

    def _get_modules(self):
        """Returns Modules with chapters as a dictionary"""

        # Main Page (prettify data)
        content = requests.get(self.url).text
        soup = BeautifulSoup(content, "html.parser")

        # modules section
        module_section = soup.find("section", class_="modules")
        ul_links = module_section.find("ul", class_="noul row")
        mod_links = ul_links.find_all("li", class_="module")

        modules_dict = OrderedDict()

        # prints chapters in each module
        for count, module in enumerate(mod_links):
            link = module.find("a")
            chapters = self._get_chapters(link["href"])
            modules_dict[count+1] = dict(url=link["href"], title=link.text, chapters=chapters)
            print "Module %s -" %str(count+1), link.text, " [Chapters - %s]" % len(chapters)
            print

        return modules_dict

    def _get_chapters(self, module):
        """ Returns module chapters as a list"""

        content = requests.get(module)

        # module page
        soup = BeautifulSoup(content.text, "html.parser")
        content_div = soup.find("div", id="content")
        content_div_ul = content_div.find("ul", class_="noul")

        # chapters links
        links = content_div_ul.find_all("li", class_="item")
        chapters = []
        for chapter in links:
            title = chapter.find("h4", class_="title").findChild("a")
            chapters.append(title["href"])
        return chapters

    def _load_comments(self, module=None, chapter=None):
        """Loads the comment html"""

        try:
            module_info = self.modules.get(module, None)
            if module_info:
                print "Reading comments from Module %s, Chapter %s\n" %(module, chapter)

                banner = 80*"=" + "\n"
                banner += 10*" " + "[Module-%s] Chapter-%s\n\n" % (module, chapter)
                banner += 5*" " +  "Module  URL: %s\n" % module_info["url"]
                banner += 5*" " +  "Chapter URL: %s\n" % module_info["chapters"][chapter-1]
                banner += 80*"=" + "\n\n\n"

                file_name = "Module_%s_%s.txt" % (module, chapter)
                file_path = os.path.join(self.path, file_name)
                self._handler = open(file_path, "w")
                self._handler.write(banner)

                chapter = self._get_chapters(module_info["url"])[chapter-1]

                # Chapter Content
                content = requests.get(chapter).text
                soup = BeautifulSoup(content, "html.parser")
                main_div = soup.find("div", id="main")
                main_div_section = main_div.find("section", class_="single-chapter")

                # Comment Section
                comments_section = main_div_section.find("ol", class_="commentlist")
                li_child = comments_section.findChild("li")
                if not li_child.has_attr("class"):
                    print "Missing Class Attribute.."
                    sys.exit(0)

                # sudo code to get the level, not useful
                #if "depth-1" in li_child["class"]:
                #    level = 1

                # considering level=1 by default
                level = 1
                self._load_comment_section(comments_section, level)

        except Exception as error:
            print "Exception Occurred '%s' \n\n Please try again.." % str(error)

    def _load_comment_section(self, comments_section, level):
        """Recursive function to crawl all comments"""

        # define attribute for class name
        class_attr = "depth-%d" % level
        comments = comments_section.find_all("li", class_=re.compile(class_attr))
        level += 1

        for comment in comments:
            comment_id = comment.get("id", None)
            if comment_id:
                comment_div = comment.find("div", id="div-%s" %comment_id)
                author_div = comment_div.find("div", class_="comment-author vcard")
                author_name = str(author_div.cite.text.encode("utf-8"))
                comment_meta = comment_div.find("div", class_="comment-meta commentmetadata")
                timestamp = str(comment_meta.a.text.encode("utf-8").strip())
            if comment.div.p:
                comments_list = [item.text.encode('ascii', 'ignore') \
                                 for item in comment.div.find_all("p")]
                author_comment_info = "[%s - %s]\n" % (author_name, timestamp)
                line = (level-2)*"\t" + author_comment_info
                line += (level-2)*"\t"+"".join(comments_list).replace("\n", "\n"+(level-2)*"\t")
                self._handler.write(line + "\n\n")
                self._handler.flush()
            if comment.ul:
                self._load_comment_section(comment.ul, level)


URL = r"https://zerodha.com/varsity"

if "__name__" == "__main__":

    obj = Zerodha(URL)
    obj.get_comments()

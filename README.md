# crawlers

### Project-1 : Zerodha(https://zerodha.com/varsity/)

<span>
  <b>The program to crawl comments from Zerodha</b>
  <ul>
    <li>The script crawls all the comments from the url</li>
    <li>The URL has many modules and each module has chapters</li>
    <li>The script crawls comments from all the chapters of every module</li>
  </ul>  
</span>


```
# Sample Code

#create object
obj = Zerodha(url)

#comments of specific module and chapter
obj.get_comments(module=None, chapter=None)

#comments of all chapters
obj.get_comments()
```

##### Note: I've skipped the Chapter-1 of Module-6 since the html is different

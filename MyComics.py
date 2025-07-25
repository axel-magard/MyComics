import asyncio
import requests
from datetime import datetime, timedelta
import comics
from bs4 import BeautifulSoup
import time
from quart import Quart, request


app = Quart(__name__)

head = """
<head>
<style>
.comic {float: left;}
.nav {min-width: 200px; float: left; }
.content {float: left; width: calc(100% - 200px);}
div.messages {width: 200px;}
</style>
</head>
"""

body = """
<body>
<div class='nav'>
%s
</div>
<div class='content'>
%s
</div>
</body>
"""

rootURL = "https://www.gocomics.com/"

entry = "<div class='comic'><a href='%s' target=_NEW_><img src='%s'/></a></div>\n"

form = """
<form action='/'>
<button id="buttBack" formaction="/back" type="submit"><</button>
<input
  type="date"
  id="start"
  name="dateSelected"
  value="%s"
  min="1980-01-01"
  max="%s" />
<button id="buttForw" formaction="/forw" type="submit">></button> 
<input
  type="hidden"
  id="maxDate"
  name="maxDate"
  value="%s" />  
<p><div class="messages">%s</div></p>  
<p><button autofocus>Submit</button></p>
<button id="buttToday" formaction="/today" type="submit">Today</button>
</form>  
"""

def showTimeElapsed(clock):
    if clock:
        elapsed = clock.elapsed()
        msg = "Time elapsed: %s" % fmtTime(elapsed)
        print(msg)

class Stopwatch():
    def __init__(self):
        self.starttime = time.time()
    def elapsed(self,reset=False):
        t = time.time() - self.starttime
        if reset:
            self.reset()
        return t
    def reset(self):
        self.starttime = time.time()

def fmtTime(t):
    str = "%4.2f seconds" % t
    if t > 60:
        str = "%4.2f minutes " % (t/60)
    if t > 3600:
        str = "%4.2f hours   " % (t/3600)
    return str        

def getImgFromWeb(url):
    imgURL = ""
    r = requests.get(url)  
    soup = BeautifulSoup(r.text, features="html.parser")
    for div in soup.find_all(isComicViewer):
        for img in div.find_all('img'):
            if img:
                if "featureassets" in img.attrs["src"]:
                    imgURL = img.attrs["src"]
        break # We only want the first comic strip on that page ! 
    return imgURL

async def fetchComic(comic, date, queue, messages):
    try:
        co = comics.search(comic, date=date)
        e = entry % (rootURL+comic+"/"+date.replace("-","/"),co.image_url)             
        queue.put_nowait((e,date,messages))
        queue.task_done()
    except comics.exceptions.InvalidDateError:
        queue.put_nowait(("<div></div>",date,messages))
        queue.task_done()    
    except requests.exceptions.ConnectionError:
        messages += "Can not connect to '%s' page for date %s.\n" % (comic,date)    
        queue.put_nowait(("<div></div>",date,messages))
        queue.task_done()  

def makeListOfComics():
    with open("comics.lst") as f:
        myComics = [s for s in f.read().split("\n") if not s.startswith("#")]
    return myComics   

@app.route("/")
async def main(button=None):
    clock = Stopwatch()
    queue = asyncio.Queue()
    tasks = []
    messages = ""
    day = request.args.get("dateSelected")
    if button:
        day = newDay(button,day)
    if not day:
        day = datetime.today().strftime("%Y-%m-%d") 
    if button == "Today":
        day = datetime.today().strftime("%Y-%m-%d")               
    maxDate = request.args.get("maxDate")
    if not maxDate:
        maxDate = day
    content = ""
    myComics = makeListOfComics()
    for comic in myComics:       
        task = asyncio.create_task(fetchComic(comic, day, queue, messages))
        tasks.append(task)    
        await task
    await queue.join()
    # Cancel our worker tasks.
    for task in tasks:
        task.cancel()    
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)
    while not queue.empty():
        obj = await queue.get()
        c,dat,messages = obj
        content += c        
    f = form % (dat,maxDate,maxDate,messages)
    nav_html = "<div><p>%s</p><p>%s</p></div>" % (dat,f)   
    showTimeElapsed(clock)                      
    return "<html>" + head + (body % (nav_html,content)) + "</html>"    

@app.route("/forw")
async def forward():
    html = await main("Forw")
    return html

@app.route("/back")
async def backward():
    html = await main("Back")
    return html

@app.route("/today")
async def today():
    html = await main("Today")
    return html

def makeDTValue(txt,year):
    arr = txt.split(" ")[1:]
    arr.append(year)
    return datetime.strptime(" ".join(arr), '%B %d %Y')

def newDay(button, day):
    d = datetime.strptime(day, '%Y-%m-%d')    
    if button == "Forw":
        d += timedelta(1)
    elif button == "Back":
        d -= timedelta(1)    
    return(d.strftime('%Y-%m-%d'))

def isComicViewer(tag):
    return tag.has_attr('data-aspect-ratio')
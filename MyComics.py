import asyncio
import requests
from datetime import datetime, timedelta
import comics
from bs4 import BeautifulSoup
import time
import random
from quart import Quart, request, render_template_string, session, redirect, url_for
from MyComicsHTML import head, body, body_o, rootURL, entry, form, form_o, opt, checkbox, hidden


app = Quart(__name__)
app.config['SECRET_KEY'] = 'ahfjkahw hawui666'

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

async def retrieveComics(favs,day):
    messages = ""
    content = ""
    tasks = []
    queue = asyncio.Queue()     
    for comic in favs:       
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
    return content,day,messages     


@app.before_request
def make_session_permanent():
    session.permanent = True        
    
@app.route("/")
async def main(button=None):
    clock = Stopwatch()
    day = request.args.get("dateSelected")
    if button:
        day = newDay(button,day)
    if not day:
        day = datetime.today().strftime("%Y-%m-%d") 
    if button == "Today":
        day = datetime.today().strftime("%Y-%m-%d")               
    maxDate = request.args.get("maxDate")
    if not maxDate or button == "Today":
        maxDate = day
    favs = request.args.getlist("favorites")
    myComics = request.args.getlist("comic")    
    if not myComics:
        myComics = session['myComics']   
    if not favs:
        favs = session['favs'] 
    
    print(myComics,favs)
    content,dat,messages = await retrieveComics(favs,day)
    
    listbox = ""
    for comic in myComics:
        sel = ""
        if comic in favs:
            sel = "selected"
        listbox += opt % (comic,sel,comic)              
    f = form % (dat,maxDate,maxDate,listbox,messages)
    nav_html = "<div><p>%s</p><p>%s</p></div>" % (dat,f)
    showTimeElapsed(clock)
    resp = render_template_string("<html>" + head + (body % (nav_html,content)) + "</html>") 
    session['myComics'] = myComics
    session['favs'] = favs
    return await resp

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

@app.route("/options")
async def options(button=None):
    myComics = session['myComics']
    favs = session['favs']
    favs = request.args.getlist("favorites")
    listbox = ""
    for comic in comics.directory.listall():
        attr = ""
        if comic in myComics:
            attr = "checked"
        listbox += checkbox % (comic,attr,comic,comic)
    for comic in favs:      # Add favs as hidden fields to pass on ....
        listbox += hidden % ("favorites",comic,comic)
    day = request.args.get("dateSelected")         
    listbox += hidden % ("dateSelected",day,day)
    f = form_o % (listbox,)
    content = ""
    if button == "Random":
        favs = []
        favs.append(random.choice(comics.directory.listall()))
        content,dat,messages = await retrieveComics(favs,day)
        content = "<h1>" + favs[0] + "</h1>" + content
    return "<html>" + head + (body_o % (f,content)) + "</html>"

@app.route("/random")
async def handleRandom():
    html = await options("Random")
    return html

@app.route("/clear")
def handleClear():
    session['myComics'] = []
    session['favs'] = []
    return redirect(url_for('options')) 

@app.route("/demo")
def handleDemo():
    session['myComics'] = ["peanuts", "garfield", "wizardofid", "marmaduke", "herman", "bc", "realitycheck", "moderately-confused"]
    session['favs'] = ["peanuts", "garfield", "wizardofid", "marmaduke", "herman", "bc", "realitycheck", "moderately-confused"]
    return redirect(url_for('main'))

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
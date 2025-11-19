head = """
<head>
<style>
.comic {float: left;}
.nav {min-width: 200px; float: left; }
.content {float: left; width: calc(100% - 200px);}
select {width: 200px;}
div.messages {width: 200px;}
div.options {display: inline-block; height: 80%; overflow-y:scroll; border: 5px solid #DDDDDD;}
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

body_o = """
<body>
<div class='nav'>
%s
</div>
<div class='randomComic'>
%s
</div>
</body>
"""

rootURL = "https://www.gocomics.com/"

entry = "<div class='comic'><a href='%s' target=_NEW_><img src='%s'/></a></div>\n"
entryRSS = "<div class='comic'><h2>%s</h2><a href='%s' target=_NEW_>%s</a></div>\n"

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
<p>
<label for="favorites">Favorite comics:</label>
</p><p>
<select name="favorites" multiple>
%s
</select>
</p>
<p><div class="messages">%s</div></p>
<p><button autofocus>Submit</button>
<button id="buttOpt" formaction="/options" type="submit">⚙️</button>
<button id="buttToday" formaction="/today" type="submit">Today</button></p>
</form>
"""

form_o = """
<form action='/'>
<p>
<label for="comics">Comics available:</label>
</p><p>
<div class="options">
%s
</div>
</p>
<button autofocus type="submit">OK</button>
<button id="buttRandom" formaction="/random" type="submit">Random</button>
</p>
</form>
"""

opt = """
<option value="%s" %s>%s</option>
"""

checkbox = """
<input name="comic" value="%s" type="checkbox" %s>
<label for="%s">%s</label><br/>
"""

hidden = """
<input name="%s" value="%s" type="hidden" %s>
<br/>
"""
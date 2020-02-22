import markdown, urllib2, datetime, re, string, argparse, os
from bs4 import BeautifulSoup

def get_key(index, li, title):
	title = title.replace("  ", "-")
	title = title.replace("  ", "-")
	title = title.replace(" ", "-")
	#title = re.sub(r'\([^)]*\)', '', title)
	title = pattern.sub('', title)

	if title == "":
		return None

	i = 0
	while True:
		key = title
		if i > 0:
			key = key + "_" + str(i)
		i = i + 1
		try:
			existing = index[key]
		except KeyError:
			return key

#
# Downloading lua_api.txt
#
print("Downloading lua_api.txt...")

url = "https://raw.githubusercontent.com/minetest/minetest/master/doc/lua_api.txt"
text = urllib2.urlopen(url).read()
text = unicode(text, "utf-8")


print("Pre-generation replacements...")

header = """Minetest Lua Modding API Reference
=================================="""
text = text.replace(header, "")

#
# Generating HTML
#
print("Generating HTML...")
md = markdown.Markdown(extensions=['markdown.extensions.toc'])
html = md.convert(text)

print("Post-generation replacements...")
links = """<ul>
<li>More information at <a href="http://www.minetest.net/">http://www.minetest.net/</a></li>
<li>Developer Wiki: <a href="http://dev.minetest.net/">http://dev.minetest.net/</a></li>
</ul>"""

html = html.replace("{{", "{ {")
html = html.replace(links, "")


credit = "This page was last updated "
credit += datetime.date.today().strftime("%d/%B/%Y")
credit += ".<br />See <a href=\"https://github.com/minetest/minetest/blob/master/doc/lua_api.txt\">doc/lua_api.txt</a> for the latest version (in plaintext)."
credit += "<br />Generated using <a href=\"https://github.com/rubenwardy/minetest_modding_book/blob/gh-pages/update_lua_api.py\">a Python script</a>."
links += credit
html = html.replace("<h2 id=\"programming-in-lua\">", links + "<h2 id=\"programming-in-lua\">")

print("Parsing HTML...")
soup = BeautifulSoup(html, 'html.parser')

pattern = re.compile('[\W]+')
lis = soup.find_all("li")
index = {}

# Build index of anchors
headings = soup.find_all({"h1", "h2", "h3", "h4", "h5", "h6"})
for tag in headings:
	if tag.has_attr("id"):
		index[tag["id"]] = True
	if tag.has_attr("name"):
		index[tag["name"]] = True

# Add anchors to <li>s containing <code>
for li in lis:
	code = li.find_all('code')
	if len(code) > 0:
		key = get_key(index, li, code[0].string)
		if key is not None:
			index[key] = True
			#print("Created " + key)
			new_tag = soup.new_tag('a', href="#" + key)
			new_tag['class'] = "anchor"
			new_tag['name'] = key
			new_tag.string = "#"
			li.insert(0, new_tag)

# Prepare for writing
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--darkmode", help="use a dark theme", action="store_true")
args = parser.parse_args()

html = str(soup)

frames = """
<frameset cols="25%,*">
    <frame src="toc.html" name="toc">
    <frame src="lua_api.html" name="content">
</frameset>
"""

toc = md.toc
toc = re.sub('<a href="(.+?)"', '<a href="lua_api.html\\1" target="content"', toc)

if args.darkmode:
	darkmode = """
	<style>
	body {
	background-color: black;
	color: white;
	}
	a:link {
	color: #338AFF
	}
	a:visited {
	color: #338AFF
	}
    </style>\n
	"""
	html = darkmode + html
	toc = darkmode + toc
	frames = darkmode + frames

#
# Writing to file
#
if not os.path.isdir("out/"):
	os.mkdir("out/")
print("Writing content.html...")
file = open("out/lua_api.html", "w")
file.write("---\ntitle: Lua Modding API Reference\nlayout: default\n---\n")
file.write("<div class='notice notice-info'>\n")
file.write("<h2>This is lua_api.txt nicely formated: I did not write this</h2>\n")
file.write(credit)
file.write(html)
file.close()

print("Writing toc.html.....")
file = open("out/toc.html", "w")
file.write("</div>\n")
file.write("<h2 id=\"table-of-contents\">Table of Contents</h2>\n")
file.write(toc)

print("Writing frames.html......")
file = open("out/index.html", "w")
file.write(frames)

print("Done")

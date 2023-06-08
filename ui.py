from nicegui import ui
import json

page = 0
debuggingDump = [{"Name":"Root","Type":None,"MaxChildren": -1,"Children":[]}]
mermaidTextConst = "graph LR;\n0[\"Root\"];\n"

def encodePath(path):
	return "-".join([str(x) for x in path])

def escape(name):
	return name.replace('"', '&quot')

def getElementText(element):
	name = escape(str(element["Name"]))
	ttype = escape(str(element["Type"]))
	maxC = " (" + str(element["MaxChildren"]) + ")"
	
	if element["Type"] == "parenObject":
		return ttype + (" " + maxC if element["MaxChildren"] != -1 else "")
	return ((ttype + ":") if element["Type"] != None else "") + name + (" " + maxC if element["MaxChildren"] != -1 else "")

def recursiveMermaidText(element, soFar, path):
	thisText = getElementText(element)
	thisID = encodePath(path)
	soFar.append(f"{thisID}[\"{thisText}\"];")
	
	for i, child in enumerate(element["Children"]):
		childID = encodePath(path + [i])
		
		arrow = "-->"
		if child["Type"] == "parenObject":
			if child["Name"]:
				arrow = "--x"
		
		soFar.append(f"{thisID} {arrow} {childID};")
		soFar = recursiveMermaidText(child, soFar, path + [i])
	
	return soFar
	
def reloadInterface():
	global page
	element = debuggingDump[page]
	print(element)
	mermaidText = mermaidTextConst + "\n".join(recursiveMermaidText(element, [], [0]))
	print(mermaidText)
	
	body.clear()
	body.set_content(mermaidText)
	if page == 0:
		bL.disable()
	else:
		bL.enable()
	if page == len(debuggingDump)-1:
		bR.disable()
	else:
		bR.enable()
	pg.set_text(page)

def reloadFile(interfaceToo=True):
	global page, debuggingDump
	with open("logOut.json", "r") as f:
		debuggingDump = json.load(f)

	page = 0
	if interfaceToo:
		reloadInterface()
	
def buttonDown():
	global page
	if page > 0:
		page+= -1
	reloadInterface()
	
def buttonUp():
	global page
	if page < len(debuggingDump)-1:
		page+= 1
	reloadInterface()


reloadFile(False)

with ui.row():
	reloadFileBtn = ui.button(on_click=reloadFile).props('icon=refresh')
	bL = ui.button('<<<', on_click=buttonDown)
	pg = ui.label(page).style("font-size:1.8em;")
	bR = ui.button('>>>', on_click=buttonUp)
	
body = ui.mermaid(mermaidTextConst).style('width: 100%;')
reloadInterface()

ui.run()
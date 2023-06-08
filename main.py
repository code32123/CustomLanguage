import json

def lexer(exp):
	tokens = []
	scope = None
	escaped = False
	escapes = {
		"n":"\n",
	}
	for char in exp:
		if scope == "string":
			if escaped:
				tokens[-1] += escapes[char]
				escaped = False
			elif char == "\\":
				escaped = True
			elif char == '"':
				escaped = False
				scope = None
				tokens[-1] += char
			else:
				tokens[-1] += char
			continue
			
		if char == '"':
			scope = "string"
			tokens.append(char)
			continue
		if char.isalnum() and len(tokens) > 0 and tokens[-1].isalnum():
			tokens[-1] += char
		elif char not in [" ", "\t"]:
			tokens.append(char)
	return tokens

class Item:
	token = None
	ttype = None
	maxChildren = 0 # -1 means unlimited
	
	def __init__(self, content):
		self.token = content
		self.identify(content)
			
	def __str__(self):
		return (self.ttype + ":" + str(self.token)) if self.ttype != None else self.token
		
	def identify(self, content):
		if content == "Root":
			self.token = content
			self.maxChildren = -1
		elif content == "(":
			self.token = "openParen"
		elif content == ")":
			self.token = "closeParen"
		elif content == ",":
			self.token = "comma"
		elif content == "parenObject":
			self.token = False
			self.ttype = "parenObject"
			self.maxChildren = 1
		elif content in ["*", "-", "+"]:
			self.token = content
			self.ttype = "op"
			self.maxChildren = 2
		elif content == ";":
			self.token = "semicolon"
		elif content.isdigit():
			self.token = content
			self.ttype = "num"
		elif content.isalnum() and not content[0].isdigit():
			self.token = content
			self.ttype = "id"
		elif content[0] == '"' and content[-1] == '"':
			self.token = content
			self.ttype = "str"
		else:
			raise ValueError(f"Couldn't handle token '{content}'")


class treeNode:
	children = []
	item = None
	def __init__(self, item):
		self.children = []
		self.item = item
	def __str__ (self):
		return str(self.item) + ">[" + ", ".join([str(x) for x in self.children if x != None]) + "]"
		
	def print(self, level = 0, lr = ""):
		print("  "*level + lr + str(self.item))
	
		if self.children == None:
			return
		for child in self.children:
			child.print(level+1)
		
	# Returns False for Full/failed to append, and True for a successful append		
	def treeAppend(self, node):
		# Returns if this is a full parenthesis object
		if self.item.ttype == "parenObject":
			if self.item.token:
				return False
			if node.item.token == "comma":
				self.item.maxChildren += 1
				return True
				
		# Has no children
		if len(self.children) == 0:
			canHaveChildren = self.item.maxChildren != 0
			canHaveChildren = canHaveChildren or (self.item.ttype == "id" and node.item.ttype == "parenObject")
			if canHaveChildren:
				self.children.append(node)
			return canHaveChildren

		# Has children
		for i in range(len(self.children)):
			child = self.children[i]
			
			if child.item.ttype == "op" and node.item.ttype == "op":
				# print("Order of Operations relevent")
				childMult = child.item.token in ["*"]
				nodeMult = node.item.token in ["*"]
				if childMult and not nodeMult:
					# print("OO Violation, resolving")
					self.children[i] = node
					self.children[i].children = [child]
					return True

			
			results = child.treeAppend(node)
			if results:
				return True
				
		# All children are full
		for i in range(len(self.children)-1, -1, -1):
			child = self.children[i]

			if child.item.ttype in ["num", "parenObject", "id"] and node.item.ttype == "op":
				# print(f"{child.item.ttype} supplanted by {node.item.ttype}")
				self.children[i] = node
				self.children[i].children = [child]
				return True

		# All children are full
		if len(self.children) < self.item.maxChildren or self.item.maxChildren == -1:
			self.children.append(node)
			return True
		return False
	
	def Dict(self):
		return {
			"Name":self.item.token,
			"Type":self.item.ttype,
			"MaxChildren":self.item.maxChildren,
			"Children":[child.Dict() for child in self.children],
		}

def prettyPrintList(li):
	print("[\n" + "".join(["    " + str(i) + "\n" for i in li]) + "]")


def main(exp, dumpDebugs=False, silent = False, outputDebugs = False):
	tokens = lexer(exp)
	if not silent:
		print(exp)
		prettyPrintList(tokens)
	items = [Item(t) for t in tokens]
	if not silent:
		prettyPrintList(items)

	AST = treeNode(Item("Root"))
	Scope = []

	debuggingDump = []

	for item in items:
		# print()
		# AST.print()
		debuggingDump.append(AST.Dict())
		#print(item, "\t"*2,AST)
		if item.token == "openParen":
			newParenScope = treeNode(Item("parenObject"))
			AST.treeAppend(newParenScope)
			Scope.append(newParenScope)
		elif item.token == "closeParen":
			lastScope = Scope[-1]
			if lastScope.item.ttype != "parenObject":
				print("Tried to pop a paren off the scope stack, but found a", lastScope.item.token)
				raise ValueError
			# Lock the paren obj
			lastScope.item.token = True
			del Scope[-1]
		elif item.token == "semicolon":
			pass
		else:
			AST.treeAppend(treeNode(item))
	if dumpDebugs:
		with open("logOut.json", "w+") as f:
			json.dump(debuggingDump, f, indent=2)
	if outputDebugs:
		return AST, debuggingDump
	return AST
	


if __name__ == '__main__':

	# exp = "print((4*var+1)*2);"
	exp = "print(\"Math:\", (4*var+1)*2);"

	AST = main(exp, True)
	# print("Math:", (4*var+1)*2);
	print()
	print()
	print(AST)
	print()
	AST.print()
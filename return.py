# Scary RETURN interpreter
# By Ben "GreaseMonkey" Russell, 2010
# Public domain.

import sys

global GETCHBUF
GETCHBUF = ""

def getch():
	while not GETCHBUF:
		GETCHBUF = raw_input("")
	
	c = GETCHBUF[0]
	GETCHBUF = GETCHBUF[1:]
	
	return c

def getint():
	v = 0
	while True:
		c = ord(getch()) - '0'
		if c >= 0 and c <= 9:
			v *= 10
			v += c
		else:
			break
	
	return v

class Tape:
	def __init__(self):
		self.l = [0]
		self.p = 0
	
	def left(self):
		self.p -= 1
		if self.p < 0:
			self.p = 0
	
	def right(self):
		self.p += 1
		while self.p >= len(self.l):
			self.l.append(0)
	
	def get(self):
		return self.l[self.p]

	def put(self, v):
		self.l[self.p] = int(v) & 0xFF

class A:
	def __init__(self, inv):
		self.cq = []
		self.cv = 0
		self.cp = None
		self.__call__(inv)
	
	def __call__(self, inv):
		if inv == self.__class__:
			self.cq.append(None)
		else:
			self.cq.append(inv)
			inv.cp = self
		
		self.cv += 1
		
		return self
	
	def run(self, tape, ci = 0, first = True):
		i = 0
		while i < len(self.cq):
			o = self.cq[i]
			if o:
				i = o.run(tape, i, False)
			i += 1
		
		if not first:
			i = ci
			q = self.cv
			if q == 1: # 1. Add 1 
				tape.put(tape.get()+1)
			elif q == 3: # 3. Subtract 1 
				tape.put(tape.get()-1)
			elif q == 5: # 5. Move pointer right 
				tape.right()
			elif q == 7: # 7. Move pointer left 
				tape.left()
			elif q == 9: # 9. Put character (optional) 
				sys.stdout.write(chr(tape.get()))
			elif q == 11: # 11. Put number 
				sys.stdout.write(tape.get())
			elif q == 13: # 13. Get character (optional) 
				tape.put(getch())
			elif q == 15: # 15. Get number 
				tape.put(getint())
			elif q == 17: # 17. While nonzero repeat what's in the next group of brackets
				i += 1
				o = self.cp.cq[i]
				while tape.get():
					if o:
						o.run(tape, False)
			elif q == 19: # 19. If nonzero skip next group of brackets 
				if not tape.get():
					i += 1
			elif q == 21: # 21. While zero repeat what's in the next group of brackets 
				i += 1
				o = self.cp.cq[i]
				while not tape.get():
					if o:
						o.run(tape, False)
			elif q == 23: # 23. If zero skip next group of brackets 
				if tape.get():
					i += 1
			elif q == 25: # 25. Exit with return code 0 
				sys.exit(0)
			elif q == 27: # 27. Exit with return code defined at pointer 
				sys.exit(tape.get())
		
			return i

fp = open(sys.argv[1],"r")
fdata = ""
for c in fp.read():
	if c == "(":
		fdata += "(A"
	elif c == ")":
		fdata += ")"

fdata = "A" + fdata + ".run(Tape())"

exec fdata

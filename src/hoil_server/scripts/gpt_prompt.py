prompt="""
Given a json file of list {id, stmt}, You will take the role of an interpretor and translate sentences into Python expressions.
Note that you cannot use arbitrary variables and functions to fulfil your task. You must only use variables specified in the sentence or functions that are known (Provided to you as json later).

You cannot read,write variables and access functions normally. Use the following functions to access them instead:

* self.Decl(str, val) -> Declare a new variable str with value val. Omit val to declare variable without initialisation.
* self.Assign(str, val) -> Assign val to variable str.
* self.ValueOf(str) -> Get the value of variable str. You should use this to access and read variables.
* self.Call(str, args) -> Call the function with args. Args is a list and is empty for functions that do not take any arguments. It will return a value too if the callee function does so.

Example:
self.Decl('x', 1) # x = 1
self.Decl('y', 2) # y = 2
self.Decl('z', self.ValueOf('x') + self.ValueOf('y')) # z = x + y
self.Assign('z', self.ValueOf('z') * 2) # z = z * 2. Note that you cannot do z = self.ValueOf('z') * 2 or self.Assign('z', z * 2)
self.Call('my_function', [self.ValueOf('x'), "hi", 1 + 2]) # my_function(x, "hi", 1 + 2)
self.Call('empty_function', []) # empty_function()

you ONLY write one Python expression and it MUST BE self-contained. Rule of thumb, if a sentence appears to be conditional or a loop, just write the expression that goes inside the condition:
"If x is 12" -> self.value = x == 12

Note the self.value = ...- For expressions that may result in a value (and conditional, loop boolean expressions), you must store the value in self.value.
Sentences may appear to be conditional, loop, assignment, or expression.

Provide your answer in a form of Json array {id, exec}, where id is the id of the expression (should be equal to the input id) and exec is a string of your translation in Python-expression.
Do not write anything other than json string.

You may use the following functions (in addition to the four functions to access variables and functions) to achieve your goal:
"""
class Thing(object):
    def __init__(self, name):
        self.name = name
        self.properties = {}
        self.children = {}
        self.is_methods = {}
        self.has_methods = {}

    def __getattr__(self, item):
        if item.startswith('is_a_'):
            return item[len('is_a_'):] in self.properties and self.properties[item[len('is_a_'):]]
        elif item.startswith('is_not_a_'):
            return item[len('is_not_a_'):] not in self.properties or not self.properties[item[len('is_not_a_'):]]
        elif item.startswith('is_the_'):
            return self.properties[item[len('is_the_'):]]
        elif item.startswith('has_'):
            key = item[len('has_'):]
            if key not in self.children:
                self.children[key] = []
            return HasBuilder(self.children[key], self)
        elif item.startswith('can_'):
            key = item[len('can_'):]
            return CanBuilder(key, self)

    def __setattr__(self, key, value):
        if key.startswith('is_a_') or key.startswith('is_not_a_'):
            self.properties[key[len('is_a_'):]] = value
        elif key.startswith('is_the_'):
            self.properties[key[len('is_the_'):]] = value
        else:
            super().__setattr__(key, value)

    def __str__(self):
        return self.name

class HasBuilder(object):
    def __init__(self, lst, thing):
        self.lst = lst
        self.thing = thing

    def __getattr__(self, item):
        if item.startswith('having_'):
            key = item[len('having_'):]
            obj = Thing(key)
            self.thing.__dict__[key] = obj
            self.lst.append(obj)
            return obj
        elif item.startswith('each'):
            return self.lst[0] if len(self.lst) == 1 else self.lst
        else:
            return self

    def __setattr__(self, key, value):
        if key.startswith('having_'):
            self.thing.__dict__[key[len('having_'):]] = value
        else:
            super().__setattr__(key, value)

class CanBuilder(object):
    def __init__(self, key, thing):
        self.key = key
        self.thing = thing

    def __call__(self, method, past=''):
        def method_wrapper(*args, **kwargs):
            result = method(*args, **kwargs)
            if past:
                if self.key not in self.thing.has_methods:
                    self.thing.has_methods[self.key] = []
                self.thing.has_methods[self.key].append(result)
            return result
        self.thing.is_methods[self.key] = method_wrapper
        return method_wrapper
      

      jane = Thing('Jane')
test.describe('jane =  Thing("Jane")')
test.describe('jane.name')
test.it('should be "Jane"')
test.assert_equals(jane.name, 'Jane')

test.describe('#is_a')
test.describe('is_a.woman (dynamic key)')
jane.is_a.woman
test.it('jane.is_a_woman should return true')
test.assert_equals(jane.is_a_woman, True)

test.describe('#is_not_a')
test.describe('is_not_a.man (dynamic key)')
jane.is_not_a.man
test.it('jane.is_a_man should return false')
test.assert_equals(jane.is_a_man, False)



test.describe('#has')

test.describe('jane.has(2).arms')
jane = Thing('Jane')
jane.has(2).arms
test.it('should define an arms method that is tuple subclass')
test.assert_equals(isinstance(jane.arms, tuple), True)
test.it('should populate 2 new Thing instances within the tuple subclass')
test.assert_equals(len(jane.arms), 2)
test.assert_equals(all(isinstance(v, Thing) for v in jane.arms), True)
test.it('should call each thing by its singular form (aka "arm")')
test.assert_equals(all(v.name=="arm" for v in jane.arms), True)
test.it('should have is_arm == true for each arm instance')
test.assert_equals(all(v.is_arm for v in jane.arms), True)

test.describe('jane.having(2).arms (alias)')
test.it('should populate 2 new Thing instances within the tuple subclass')
jane = Thing('Jane')
jane.having(2).arms
test.assert_equals(len(jane.arms), 2)
test.assert_equals(all(isinstance(v, Thing) for v in jane.arms), True)

test.describe('jane.has(1).head')
jane = Thing('Jane')
jane.has(1).head
test.it('should define head method that is a reference to a new Thing')
test.assert_equals(isinstance(jane.head, Thing), True)
test.it('should name the head thing "head"')
test.assert_equals(jane.head.name, "head")

test.describe('jane.has(1).head.having(2).eyes')
jane = Thing('Jane')
jane.has(1).head.having(2).eyes
test.it('should create 2 new things on the head')
test.assert_equals(len(jane.head.eyes), 2)
test.assert_equals(all(isinstance(v, Thing) for v in jane.head.eyes), True)
test.it('should name the eye things "eye"')
test.assert_equals(all(v.name=='eye' for v in jane.head.eyes), True)


test.describe('#each')
test.describe('jane.has(2).arms.each.having(5).fingers')
jane = Thing('Jane')
jane.has(2).arms.each.having(5).fingers
test.it('should cause 2 arms to be created each with 5 fingers')
test.assert_equals(all(len(v.fingers)==5 for v in jane.arms), True)


test.describe('#is_the')

test.describe('jane.is_the.parent_of.joe')
jane = Thing('Jane')
jane.is_the.parent_of.joe
test.it('should set jane.parent_of == "joe"')
test.assert_equals(jane.parent_of, "joe")

test.describe('#being_the')

test.describe('jane.has(1).head.having(2).eyes.each.being_the.color.blue')
test.it("jane's eyes should both be blue")
jane = Thing('Jane')
jane.has(1).head.having(2).eyes.each.being_the.color.blue
test.assert_equals(all(v.color=='blue' for v in jane.head.eyes), True)

test.describe('jane.has(2).eyes.each.being_the.color.blue.and_the.shape.round')
test.it('should allow chaining via the and_the method')
jane = Thing('Jane')
jane.has(2).eyes.each.being_the.color.blue.and_the.shape.round
test.assert_equals(all(v.color=='blue' for v in jane.eyes), True)
test.assert_equals(all(v.shape=='round' for v in jane.eyes), True)

test.describe('jane.has(2).eyes.each.being_the.color.green.having(2).pupils.each.being_the.color.black')
test.it('should allow nesting by using having')
jane = Thing('Jane')
jane.has(2).eyes.each.being_the.color.green.having(1).pupil.being_the.color.black
test.assert_equals(all(v.color=='green' for v in jane.eyes), True)
test.assert_equals(all(v.pupil.color=='black' for v in jane.eyes), True)


test.describe('#can')

test.describe('jane.can.speak(lambda phrase: "#%s says: #%s" % (name, phrase))')
jane = Thing('Jane')
def fnc(phrase): 
    return "%s says: %s" % (name, phrase)
jane.can.speak(fnc)
test.it('should create a speak method on the instance')
test.assert_equals(jane.speak('hi'), "Jane says: hi")

test.describe('jane.can.speak(lambda phrase: "#%s says: #%s" % (name, phrase), "spoke")')
jane = Thing('Jane')
fnc = lambda phrase: "%s says: %s" % (name, phrase)
jane.can.speak(fnc, 'spoke')
jane.speak('hi')
test.it('should add a "spoke" attribute that tracks all speak call results')
test.assert_equals(jane.spoke, ["Jane says: hi"])
jane.speak('goodbye')
test.assert_equals(jane.spoke, ["Jane says: hi", "Jane says: goodbye"])

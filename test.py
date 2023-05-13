class thing:
    def getThing(self):
        return self.subThing

    def subThing(self):
        return 5


ting = thing()

func = ting.getThing()

print(func, func())

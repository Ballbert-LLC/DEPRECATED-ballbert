from inspect import isfunction


def makeRegistrar():
    registry = {}

    def outer(*args, **kwargs):
        """
        Decorator that decorates a param generator for generating possible paramiters

        Args:
        name (str, optional): name for the param_id style of skill_id.action_id.paramiter defaults to function name

        """

        # argName is the first argName if it exists and is a string
        argName = (args[0] if type(args[0]) == str else None) if len(args) > 0 else None
        # kwargName is the keyword argument name if it exits
        kwargName = kwargs["name"] if "name" in kwargs else None
        # name is whichever is the name either as a posititonal arg or keyword if both it prefers keyword
        name = kwargName or argName

        # the function would be the first argument if the decorator is not called ex. @dec intead of @dec()
        func = (args[0] if isfunction(args[0]) else None) if len(args) > 0 else None

        # because if the decorator is not called ex. @dec it does not get to the registrar function so it needs to be able to be called from the registrar and not returned
        should_run_on_call = func != None

        # if it should be run on call ex @reg that means that the outer function is the init function therefor it should be the one adding it to the registry
        if should_run_on_call:
            name = name if name != None else func.__name__
            skill = func.__module__.split("-")[0]
            registry[f"{skill}-{name}"] = func

        if should_run_on_call:
            # if the function should be ran when registrar is called ex @reg then it should run the functions with it's arguments when called
            def registrar(*args, **kwargs):
                func(*args, **kwargs)

        else:
            # if the function should be init and returned when registrar is called ex @reg() or @reg(name="ex name")
            def registrar(func=func, name=name):
                # add functions that are not called to the registry the reason it is done in the inner function here is becasuae if it is done outside then it does not have access to the fucntion name unless it is said explicitly
                name = name if name != None else func.__name__
                skill = func.__module__.split("-")[0]
                registry[f"{skill}-{name}"] = func

                return func

        return registrar

    outer.all = registry
    return outer


paramRegistrar = makeRegistrar()

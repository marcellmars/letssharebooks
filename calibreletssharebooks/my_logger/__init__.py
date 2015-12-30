import time
import inspect


class Om:
    def __getattr__(self, name):
        def catch_all(*args, **kwargs):
            pass
        return catch_all


class MyLogger:
    def __init__(self,
                 file_name="/tmp/letssharebooks_debug.log",
                 inspekt_global=None,
                 inspekt_depth=2):

        self.f = open(file_name, "w")
        self.inspect_global = inspekt_global
        self.inspect_depth = inspekt_depth

    def print_log(self, message):
        timestamp = time.strftime("%d.%m.%Y %H:%M:%S".format(time.gmtime()))
        self.f.write("{}: {}\n".format(timestamp, message))
        self.f.flush()

    def debug(self, message, inspekt=None):
        if inspekt or self.inspect_global:
            # https://gist.github.com/techtonik/2151727
            stack = inspect.stack()
            start = 0 + self.inspect_depth
            if len(stack) < start + 1:
                return ''
            parentframe = stack[start][0]

            name = []
            module = inspect.getmodule(parentframe)
            if module:
                name.append(module.__name__)
            if 'self' in parentframe.f_locals:
                name.append(parentframe.f_locals['self'].__class__.__name__)
            codename = parentframe.f_code.co_name
            if codename != '<module>':
                name.append(codename)
            del parentframe
            self.print_log("INSPECT_{}: {}".format(".".join(name), message))
        else:
            self.print_log("{}{}".format("DEBUG: ", message))

    def info(self, message):
        self.print_log("{}{}".format("INFO: ", message))

    def warning(self, message):
        self.print_log("{}{}".format("WARNING: ", message))

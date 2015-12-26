import time
import inspect


def om(*args, **kwargs):
    return


class MyLogger:
    def __init__(self,
                 file_name="/tmp/letssharebooks_debug.log",
                 inspekt_global=None,
                 inspekt_depth=2,
                 enabled=True):

        if enabled:
            self.f = open(file_name, "w")
        else:
            self.debug = om
            self.info = om
            self.warning = om
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

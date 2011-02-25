import hotshot, hotshot.stats

def profileit(printlines=1):
    def _my(func):
        def _func(*args, **kargs):
            prof = hotshot.Profile("profiling.data")
            res = prof.runcall(func, *args, **kargs)
            prof.close()
            stats = hotshot.stats.load("profiling.data")
            stats.strip_dirs()
            stats.sort_stats('time', 'calls')
            print "\n// --> Begin profiling print for %s" % func.func_name
            stats.print_stats(printlines)
            return res
        return _func
    return _my
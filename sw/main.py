import t3
try:
    from os import remove as unlink
except ImportError:
    from uos import unlink

t3.start_task(t3._sys_task())

try:
    f = open('selected-game')
except OSError:
    import splash
    import launcher
    t3.start_task(splash.splash())
else:
    with f:
        name = f.read().strip()
    unlink('selected-game')
    module = __import__(name)
    t3.start_task(module.main())

t3.run()

# 1/5  000000 000000 000000  000000 000000 000000  000000 000000 000000

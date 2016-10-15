import t3
try:
    from os import remove as unlink
except ImportError:
    from uos import unlink

if not hasattr(t3.machine, '_t3_emulated'):
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

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

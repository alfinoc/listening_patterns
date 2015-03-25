colors = {
   'red': '#C75646',
   'teal': '#218693',
   'purple': '#C8A0D1',
   'blue': '#72B3CC',
   'green': '#8EB33B',
   'yellow': '#D0B03C'
}

def printRadioStyles(key):
   print 'paper-radio-button.' + key + '::shadow #offRadio,'
   print 'paper-radio-button.'+ key + '::shadow #onRadio {'
   print '   border-color: ' + colors[key] + ';'
   print '}'
   print 'paper-radio-button.' + key + '::shadow #onRadio {'
   print '   background-color: ' + colors[key] + ';'
   print '}'
   print

for c in colors:
   printRadioStyles(c)

smyck = {
   'red': '#C75646',
   'teal': '#218693',
   'purple': '#C8A0D1',
   'blue': '#72B3CC',
   'green': '#8EB33B',
   'yellow': '#D0B03C'
}

mat_design = {
   'Red': '#e57373',
   'Pink': '#f06292',
   'Purple': '#ba68c8',
   'Deep_Purple': '#9575cd',
   'Indigo': '#7986cb',
   'Blue': '#64b5f6',
   'Light_Blue': '#4fc3f7',
   'Cyan': '#4dd0e1',
   'Teal': '#4db6ac',
   'Green': '#81c784',
   'Light_Green': '#aed581',
   'Lime': '#dce775',
   'Yellow': '#fff176',
   'Amber': '#ffd54f',
   'Orange': '#ffb74d',
   'Deep_Orange': '#ff8a65',
   'Brown': '#a1887f',
   'Grey': '#e0e0e0',
   'Blue_Grey': '#90a4ae'
}

colors = mat_design

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

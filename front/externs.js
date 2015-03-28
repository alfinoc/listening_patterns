utils = {};

// Returns a list of points {series, x, y} where series is uniformly the provided
// value and each (x, y) corresponds to a histogram entry (date, count). If any
// dates in histogram are not in domain, they are added as 0 counts.
utils.histogramToChartPoints = function(histogram, series, domain) {
   var result = [];
   var i = 0;
   var seen = {};
   for (date in histogram) {
      var pt = {
         series: series,
         x: domain[date],
         y: histogram[date],
      };
      seen[date] = true;
      result.push(pt);
   }
   for (date in domain) {
      if (!(date in seen)) {
         result.push({
            series: series,
            x: domain[date],
            y: 0
         });
      }
   }
   result.sort(function(a, b) { return a.x - b.x; })
   return result;
};

// Returns the complete domain across all given histograms as a set (dict).
utils.getDomain = function(histograms) {
   var domain = {};
   for (album in histograms)
      for (date in histograms[album])
         domain[date] = parseInt(date) * 1000;
   return domain;
};

// Returns a NVD3 stacked multi-bar chart with formatting options for displaying
// a histogram of play counts across time.
utils.formattedChart = function(data, domain, parent) {
   var chart = nv.models.multiBarChart();
   chart.options({
      showControls: false,
      tooltips: false,
      showXAxis: true,
      showYAxis: true,
      showLegend: false,
      stacked: true
   });
   chart.xAxis.axisLabel('Date Played').tickFormat(
      function(d) {
         str = d3.time.format('%b. %e \'%y ')(new Date(d))
         if (str.indexOf('NaN') != -1) {
            console.log('whyyy');
            console.log(d);
         }

         return str;
      }
   );
   chart.yAxis.axisLabel('Play Count').tickFormat(d3.format('d'));
   chart.xDomain(domain);
   d3.select(parent).datum(data).transition().duration(0).call(chart);
   return chart;
};

utils.sortedValues = function(dict) {
   return Object.keys(dict).map(function(val) { return dict[val]; }).sort();
};

utils.fullArray = function(len, dflt) {
   return Array.apply(null, Array(len)).map(function() { return dflt; });
};

utils.allTrue = function(a) {
   for (var i = 0; i < a.length; i++)
      if (!a[i])
         return false;
   return true;
};

colors = {};

colors.code = { Red: '#e57373',
  Pink: '#f06292',
  Purple: '#ba68c8',
  Deep_Purple: '#9575cd',
  Indigo: '#7986cb',
  Blue: '#64b5f6',
  Light_Blue: '#4fc3f7',
  Cyan: '#4dd0e1',
  Teal: '#4db6ac',
  Green: '#81c784',
  Light_Green: '#aed581',
  Lime: '#dce775',
  Yellow: '#fff176',
  Amber: '#ffd54f',
  Orange: '#ffb74d',
  Deep_Orange: '#ff8a65',
  Brown: '#a1887f',
  Grey: '#e0e0e0',
  Blue_Grey: '#90a4ae' }

colors.priority = ['Blue', 'Green', 'Red' , 'Purple', 'Orange', 'Cyan', 'Yellow', 'Indigo', 'Pink', 'Blue_Grey', 'Brown', 'Light_Green']
//colors.priority = ['red', 'teal', 'purple', 'green', 'yellow'];

colors.get = function(i) {
   return colors.priority[i % colors.priority.length];
};

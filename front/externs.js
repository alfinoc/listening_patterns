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

colors.code = {
   'red': '#C75646',
   'teal': '#218693',
   'purple': '#C8A0D1',
   'blue': '#72B3CC',
   'green': '#8EB33B',
   'yellow': '#D0B03C'
};

colors.priority = ['red', 'teal', 'purple', 'green', 'yellow'];

colors.get = function(i) {
   return colors.priority[i % colors.priority.length];
};

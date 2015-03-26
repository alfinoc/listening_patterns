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
         x: parseInt(date),
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
         domain[date] = parseInt(date);
   return domain;
};

// Returns a NVD3 stacked multi-bar chart with formatting options for displaying
// a histogram of play counts across time.
utils.formattedChart = function() {
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
      function(d) { return /*d3.time.format('%b. %d')(new Date(d)) + ' ' + */ d; }
   );
   chart.yAxis.axisLabel('Play Count').tickFormat(d3.format('d'));
   return chart;
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

colors.priority = ['red', 'teal', 'purple', 'blue', 'green', 'yellow'];

colors.get = function(i) {
   return colors.priority[i % colors.priority.length];
};

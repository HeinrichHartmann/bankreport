HTML_HEAD = """
<script src="https://code.jquery.com/jquery-1.7.1.min.js"></script>

<script>
$(document).ready(function(){
  var $rows = $('table tbody tr');
  $('#filter').keyup(function() {
    var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
    $rows.show().filter(function() {
      var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
      return !~text.indexOf(val);
    }).hide();
  });
});
</script>

<style>
  table {
      width: 100%;
      text-align: left;
      border-collapse: collapse;
  }
  table td, table th {
      border: 1px solid #000000;
      padding: 5px 4px;
  }
  table tbody td {
      font-size: 13px;
  }
  table thead {
      background: #CFCFCF;
      background: -moz-linear-gradient(top, #dbdbdb 0%, #d3d3d3 66%, #CFCFCF 100%);
      background: -webkit-linear-gradient(top, #dbdbdb 0%, #d3d3d3 66%, #CFCFCF 100%);
      background: linear-gradient(to bottom, #dbdbdb 0%, #d3d3d3 66%, #CFCFCF 100%);
      border-bottom: 2px solid #000000;
  }
  table thead th {
      font-size: 15px;
      font-weight: bold;
      color: #000000;
      text-align: left;
  }

  #filter {
  width: 100%;
  }

</style>
<input type="search" id="filter" placeholder="Filter" autofocus="autofocus">
"""

HTML_THEAD = """
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th style="width:60px">Account</th>
      <th style="width:80px">Date</th>
      <th>Text</th>
      <th style="width:100px">Value</th>
      <th style="width:150px">Category</th>
    </tr>
  </thead>
"""

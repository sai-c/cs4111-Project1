$( document ).ready(function() {
    $('select').formSelect();
    $('#specialization').change(function() {
        $("#specform").submit();
    }
    )
    $('.specselect').click(function() {
        console.log("printe")
        dataval=$(this).attr("data-val")
        $("#spec2").attr("value", dataval)
        $(".specselectform").submit();
    }
    )

    var ctx = document.getElementById("myChart");
    var myChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Salary',
          data: salaries,
          backgroundColor: 'rgb(255, 99, 132)',
        }, 
        ],
      },
    });
});


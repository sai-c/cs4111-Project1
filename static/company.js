$( document ).ready(function() {
    var ctx = document.getElementById("myChart");
    var myChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Base',
          data: dataset1,
          backgroundColor: 'rgb(255, 99, 132)',
        }, 
          {
            label: 'Stock',
            data: dataset2,
            backgroundColor: 'rgb(54, 162, 235)',
          },
          {
            label: 'Bonus',
            data: dataset3,
            backgroundColor: 'rgb(75, 192, 192)',
          },
        ],
      },
      options: {
        scales: {
            x: {
              stacked: true,
            },
            y: {
              stacked: true
            },        
          }      
      }
    });
});


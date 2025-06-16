function kpiTemplate(icon, value, label) {
  return '<div class="flex items-center"><i data-lucide="' + icon + '" class="mr-2"></i><div><div class="text-2xl font-bold">' + value + '</div><div class="text-sm">' + label + '</div></div></div>';
}

$(function () {
  $.getJSON('/comptes/dashboard/data/', function (data) {
    $('#kpi-effectif').html(kpiTemplate('users', data.effectif, 'Élèves'));
    $('#kpi-classes').html(kpiTemplate('layers', data.n_classes, 'Classes'));
    $('#kpi-cours').html(kpiTemplate('book', data.n_cours, 'Cours'));
    $('#kpi-encaisse').html(kpiTemplate('credit-card', data.total_encaisse, 'Encaissements'));
    $('#kpi-presence').html(kpiTemplate('check-circle', data.taux_presence + '%', 'Présence'));

    new Chart(document.getElementById('chart-ca'), {
      type: 'bar',
      data: {
        labels: data.chart.labels,
        datasets: [{ label: 'Encaissements', data: data.chart.values }]
      },
      options: { responsive: true }
    });

    data.timeline.forEach(function (item) {
      $('#timeline').append('<div>' + item + '</div>');
    });

    if (window.lucide) {
      lucide.createIcons();
    }
  });
});

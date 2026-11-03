
const ctx = document.getElementById("performanceChart");

if (ctx && window.performanceData) {
    const data = window.performanceData;

    new Chart(ctx, {
        type: "bar",

        data: {
            labels: data.labels,

            datasets: [
                {
                    label: data.baselineLabel,
                    data: data.baseline
                },
                {
                    label: data.candidateLabel,
                    data: data.candidate
                }
            ]
        },

        options: {
            responsive: true,

            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: "Performance (%)"
                    }
                }
            }
        }
    });
}

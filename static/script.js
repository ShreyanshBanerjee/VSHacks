document.getElementById('generate-plan').addEventListener('click', function() {
    const partyCode = this.getAttribute('data-code');
    const team1 = this.getAttribute('data-team1');
    const team2 = this.getAttribute('data-team2');

    fetch(`/generate/${partyCode}/${team1}-${team2}`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('generated-plan-container');
            container.innerHTML = `
                <div class="plan-card" style="background: #e0f7fa; padding: 15px; margin-top: 15px; border-radius: 5px;">
                    <h3>Generated Plan</h3>
                    <p>${data.plan}</p>
                </div>
            `;
        })
        .catch(error => console.error('Error:', error));
});
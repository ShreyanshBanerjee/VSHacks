const button = document.getElementById("generate-plan");

button.addEventListener("click", function () {
    const code = button.dataset.code;
    const team1 = button.dataset.team1;
    const team2 = button.dataset.team2;

    fetch(`/generate/${code}/${team1}-${team2}`)
        .then(response => response.json())
        .then(data => {
            const foodText =
                data.foods && data.foods.length > 0
                    ? data.foods.join(", ")
                    : "Budget too low";

            const musicText =
                data.music && data.music.length > 0
                    ? data.music
                        .map(song => `<li>${song}</li>`)
                        .join("")
                    : "<li>No music recommendations available</li>";

            document.getElementById("generated-plan-container").innerHTML = `
                <div class="plan-card">
                    <h2>${data.team1} vs ${data.team2}</h2>

                    <p>
                        <strong>Food per person:</strong>
                        ${foodText}
                    </p>

                    <p>
                        <strong>Cost per person:</strong>
                        $${data.cost_per_person.toFixed(2)}
                    </p>

                    <p>
                        <strong>Remaining budget:</strong>
                        $${data.remaining_budget.toFixed(2)}
                    </p>

                    <h3>Recommended Music</h3>
                    <ol class="music-list">
                        ${musicText}
                    </ol>
                </div>
            `;
            document.getElementById("generated-plan-container").style.display = "flex"; 
        })
        .catch(error => console.error('Error:', error));

});

function toClipboard(link) {
    navigator.clipboard.writeText(window.location.origin + link)
        .then(() => {
            alert("Link copied!");
        })
        .catch(() => {
            alert("Failed to copy link");
        });
}

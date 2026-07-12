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
                    ? data.foods.map(food => `<span class="food-pill">${food}</span>`).join("")
                    : `<span class="food-pill">Budget too low</span>`;

            const musicText =
                data.music && data.music.length > 0
                    ? data.music
                        .map(song => `<li>${song}</li>`)
                        .join("")
                    : "<li>No music recommendations available</li>";

            document.getElementById("generated-plan-container").innerHTML = `
                <div class="plan-card main_menu_inner">
                    <h1 class="title">Generated Plan</h1>
                    <div class="large_text">Match: ${data.team1} vs ${data.team2}</div>
                    <div class="card" style="width:75%">
                      <div class="large_text" style="margin:0 padding:0">Stuff to eat 😋</div>
                      <div class="text">
                        <br>
                        Recommended Snacks:
                        <div class="food-pills">${foodText}</div>
                        Cost per person: <strong>$${data.cost_per_person.toFixed(2)}</strong> <br>
                        Remaining budget:<strong> $${data.remaining_budget.toFixed(2)}</strong>
                      </div>
                    </div>
                    <h2 class="title" style="margin-bottom: 0; padding-left: 20px;">🎵 Recommended Music:</h2>
                    <div class="card" style="width:75%">
                      <ol class="music-list">
                        ${musicText}
                      </ol>
                    </div>
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

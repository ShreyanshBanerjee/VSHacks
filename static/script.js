function submit() {
  console.log("user submitted: ");
  console.log("team: ", document.getElementById("team").value);
  console.log("budget: ", document.getElementById("budget").value);
  console.log("date: ", document.getElementById("date").value);
  
  const button = document.getElementById("submit");
  button.disabled = true;
  button.textContent = "Created";

  document.getElementById("code").textContent = "A6xZae";
  document.getElementById("code_div").style.display = "block";
}

const teams = [
  "France",
  "Norway",
  "..."
];

document.addEventListener("DOMContentLoaded", () => {
  const team_select = document.getElementById("team");

  for (const item of teams) {
       team_select.add(new Option(item, item));
  }
});

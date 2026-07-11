function submit() {
  console.log("user submitted: ");
  console.log("team: ", document.getElementById("team").value);
  console.log("budget: ", document.getElementById("budget").value);
  console.log("date: ", document.getElementById("date").value);
  console.log("code: ", document.getElementById("code").value)
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

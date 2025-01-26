document.getElementById("fetch-data").addEventListener("click", async () => {
  const squadName = document.getElementById("squad-name").value.trim();
  const errorMessage = document.getElementById("error-message");
  const table = document.getElementById("result-table");
  const tableBody = table.querySelector("tbody");
  const downloadButton = document.getElementById("download-csv");

  // Clear any previous errors or table content
  errorMessage.classList.add("hidden");
  table.classList.add("hidden");
  downloadButton.classList.add("hidden");
  tableBody.innerHTML = "";

  if (!squadName) {
    errorMessage.textContent = "Please enter a squad name.";
    errorMessage.classList.remove("hidden");
    return;
  }

  try {
    console.log(`Fetching members for squad: ${squadName}`);
    const response = await fetch(`https://wbapi.wbpjs.com/squad/getSquadMembers?squadName=${squadName}`);
    const members = await response.json();
    console.log("Squad Members Response:", members);

    if (!members || members.length === 0) {
      throw new Error("No members found for the specified squad.");
    }

    const data = await Promise.all(
      members.map(async (member) => {
        console.log(`Fetching data for member UID: ${member.uid}`);
        const playerResponse = await fetch(`https://wbapi.wbpjs.com/players/getPlayer?uid=${member.uid}`);
        const playerData = await playerResponse.json();
        console.log("Player Data:", playerData);

        return {
          nick: member.nick,
          uid: member.uid,
          time: new Date(playerData.time * 1000),
          relativeTime: timeSince(new Date(playerData.time * 1000))
        };
      })
    );

    console.log("Final Data:", data);
    populateTable(data);
    table.classList.remove("hidden");
    downloadButton.classList.remove("hidden");
  } catch (error) {
    console.error("Error:", error);
    errorMessage.textContent = error.message;
    errorMessage.classList.remove("hidden");
  }
});

function populateTable(data) {
  const tableBody = document.querySelector("#result-table tbody");
  tableBody.innerHTML = "";

  data.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.nick}</td>
      <td>${row.uid}</td>
      <td>${row.time.toUTCString()}</td>
      <td>${row.relativeTime}</td>
    `;
    tableBody.appendChild(tr);
  });

  makeTableSortable(data);
}

function timeSince(date) {
  const seconds = Math.floor((new Date() - date) / 1000);
  const intervals = [
    { label: "year", seconds: 31536000 },
    { label: "month", seconds: 2592000 },
    { label: "day", seconds: 86400 },
    { label: "hour", seconds: 3600 },
    { label: "minute", seconds: 60 },
    { label: "second", seconds: 1 }
  ];

  for (const interval of intervals) {
    const count = Math.floor(seconds / interval.seconds);
    if (count > 0) {
      return `${count} ${interval.label}${count !== 1 ? "s" : ""} ago`;
    }
  }
  return "just now";
}

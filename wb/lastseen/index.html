document.getElementById("fetch-data").addEventListener("click", async () => {
  const squadName = document.getElementById("squad-name").value.trim();
  const errorMessage = document.getElementById("error-message");
  const table = document.getElementById("result-table");
  const tableBody = table.querySelector("tbody");
  const downloadButton = document.getElementById("download-csv");

  errorMessage.classList.add("hidden");
  table.classList.add("hidden");
  downloadButton.classList.add("hidden");

  if (!squadName) {
    errorMessage.textContent = "Please enter a squad name.";
    errorMessage.classList.remove("hidden");
    return;
  }

  try {
    const response = await fetch(`https://wbapi.wbpjs.com/squad/getSquadMembers?squadName=${squadName}`);
    const members = await response.json();

    if (!members || members.length === 0) {
      throw new Error("No members found for the specified squad.");
    }

    const data = await Promise.all(
      members.map(async (member) => {
        const playerResponse = await fetch(`https://wbapi.wbpjs.com/players/getPlayer?uid=${member.uid}`);
        const playerData = await playerResponse.json();
        return {
          nick: member.nick,
          uid: member.uid,
          time: new Date(playerData.time * 1000),
          relativeTime: timeSince(new Date(playerData.time * 1000))
        };
      })
    );

    populateTable(data);
    table.classList.remove("hidden");
    downloadButton.classList.remove("hidden");
  } catch (error) {
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

function makeTableSortable(data) {
  const headers = document.querySelectorAll("th.sortable");
  let sortState = {};

  headers.forEach((header) => {
    const column = header.getAttribute("data-column");

    header.addEventListener("click", () => {
      const isAsc = sortState[column] === "asc";
      sortState = { [column]: isAsc ? "desc" : "asc" };

      const sortedData = data.slice().sort((a, b) => {
        if (column === "time") {
          return isAsc ? a.time - b.time : b.time - a.time;
        } else if (column === "relativeTime") {
          return isAsc
            ? parseRelativeTime(a.relativeTime) - parseRelativeTime(b.relativeTime)
            : parseRelativeTime(b.relativeTime) - parseRelativeTime(a.relativeTime);
        }
        return isAsc ? a[column].localeCompare(b[column]) : b[column].localeCompare(a[column]);
      });

      populateTable(sortedData);

      headers.forEach((h) => {
        h.classList.remove("active");
        h.querySelector(".arrow").textContent = "";
      });

      header.classList.add("active");
      header.querySelector(".arrow").textContent = isAsc ? "▲" : "▼";
    });
  });
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

function parseRelativeTime(relativeTime) {
  const [value, unit] = relativeTime.split(" ");
  const seconds = {
    second: 1,
    minute: 60,
    hour: 3600,
    day: 86400,
    month: 2592000,
    year: 31536000
  };
  return parseInt(value) * seconds[unit.replace(/s$/, "")];
}

document.getElementById("download-csv").addEventListener("click", () => {
  const rows = Array.from(document.querySelectorAll("#result-table tr"));
  const csvContent = rows
    .map((row) => Array.from(row.querySelectorAll("td, th")).map((cell) => `"${cell.textContent}"`).join(","))
    .join("\n");

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "squad_last_seen.csv";
  link.click();
});

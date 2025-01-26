document.addEventListener("DOMContentLoaded", () => {
  const squadInput = document.getElementById("squadName");
  const fetchDataButton = document.getElementById("fetchData");
  const errorMessage = document.getElementById("errorMessage");
  const tableSection = document.getElementById("table-section");
  const lastSeenTable = document.getElementById("lastSeenTable").querySelector("tbody");
  const downloadCSVButton = document.getElementById("downloadCSV");

  let tableData = []; // To store fetched and sorted data
  let currentSort = { column: null, order: null }; // Track sorting state

  // Fetch Squad Members
  fetchDataButton.addEventListener("click", async () => {
    const squadName = squadInput.value.trim();
    if (!squadName) {
      errorMessage.textContent = "Please enter a squad name.";
      return;
    }

    errorMessage.textContent = "";
    tableSection.style.display = "none";
    lastSeenTable.innerHTML = "";
    tableData = []; // Clear previous data

    try {
      const squadResponse = await fetch(`https://wbapi.wbpjs.com/squad/getSquadMembers?squadName=${encodeURIComponent(squadName)}`);
      if (!squadResponse.ok) throw new Error("Failed to fetch squad members.");
      const squadData = await squadResponse.json();

      if (!Array.isArray(squadData) || squadData.length === 0) {
        errorMessage.textContent = "No members found for the given squad.";
        return;
      }

      const currentTime = Math.floor(Date.now() / 1000);

      const playerPromises = squadData.map(member =>
        fetch(`https://wbapi.wbpjs.com/players/getPlayer?uid=${encodeURIComponent(member.uid)}`)
          .then(res => {
            if (!res.ok) throw new Error(`Failed to fetch data for UID: ${member.uid}`);
            return res.json();
          })
      );

      const playerData = await Promise.all(playerPromises);

      tableData = playerData.map(player => ({
        nick: player.nick,
        uid: player.uid,
        time: player.time,
        lastSeenGMT: new Date(player.time * 1000).toGMTString(),
        timeAgo: currentTime - player.time,
      }));

      renderTable(tableData);
      tableSection.style.display = "block";
    } catch (error) {
      console.error(error);
      errorMessage.textContent = "An error occurred while fetching data. Please try again.";
    }
  });

  // Render Table Data
  function renderTable(data) {
    lastSeenTable.innerHTML = "";
    data.forEach(row => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.nick}</td>
        <td>${row.uid}</td>
        <td>${row.lastSeenGMT}</td>
        <td>${getRelativeTime(row.timeAgo)}</td>
      `;
      lastSeenTable.appendChild(tr);
    });
  }

  // Sort Table Data
  document.querySelectorAll("#lastSeenTable thead th").forEach(th => {
    th.addEventListener("click", () => {
      const column = th.dataset.sort;
      const isAscending = currentSort.column === column ? !currentSort.order : true;
      currentSort = { column, order: isAscending };

      tableData.sort((a, b) => {
        if (column === "time" || column === "relative") {
          return isAscending ? a[column] - b[column] : b[column] - a[column];
        } else {
          return isAscending ? a[column].localeCompare(b[column]) : b[column].localeCompare(a[column]);
        }
      });

      renderTable(tableData);
      updateSortIcons(th, isAscending);
    });
  });

  // Update Sort Icons
  function updateSortIcons(th, isAscending) {
    document.querySelectorAll(".sort-icon").forEach(icon => (icon.textContent = "⬍"));
    th.querySelector(".sort-icon").textContent = isAscending ? "⬆" : "⬇";
  }

  // Convert time difference to relative format
  function getRelativeTime(seconds) {
    if (seconds < 60) return `${seconds} seconds ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} minutes ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hours ago`;
    const days = Math.floor(hours / 24);
    return `${days} days ago`;
  }

  // Download Table as CSV
  downloadCSVButton.addEventListener("click", () => {
    const rows = [["Nickname", "UID", "Last Seen (GMT)", "Time Ago"]];
    tableData.forEach(row => {
      rows.push([row.nick, row.uid, row.lastSeenGMT, getRelativeTime(row.timeAgo)]);
    });

    const csvContent = rows.map(row => row.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${squadInput.value.trim()}_last_seen.csv`;
    a.click();
    URL.revokeObjectURL(url);
  });
});

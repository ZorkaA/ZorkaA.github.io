document.addEventListener("DOMContentLoaded", () => {
  const squadInput = document.getElementById("squadName");
  const fetchDataButton = document.getElementById("fetchData");
  const errorMessage = document.getElementById("errorMessage");
  const tableSection = document.getElementById("table-section");
  const lastSeenTable = document.getElementById("lastSeenTable").querySelector("tbody");
  const downloadCSVButton = document.getElementById("downloadCSV");

  let playerData = [];
  let currentSortColumn = null;
  let currentSortOrder = "asc"; // Default sort order is ascending

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
    playerData = []; // Clear previous data

    try {
      // Step 1: Fetch squad members
      const squadResponse = await fetch(`https://wbapi.wbpjs.com/squad/getSquadMembers?squadName=${encodeURIComponent(squadName)}`);
      if (!squadResponse.ok) throw new Error("Failed to fetch squad members.");
      const squadData = await squadResponse.json();

      if (!Array.isArray(squadData) || squadData.length === 0) {
        errorMessage.textContent = "No members found for the given squad.";
        return;
      }

      const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds

      // Step 2: Fetch each player's data and build the table
      const playerPromises = squadData.map(member =>
        fetch(`https://wbapi.wbpjs.com/players/getPlayer?uid=${encodeURIComponent(member.uid)}`)
          .then(res => {
            if (!res.ok) throw new Error(`Failed to fetch data for UID: ${member.uid}`);
            return res.json();
          })
      );

      playerData = await Promise.all(playerPromises);

      renderTable(playerData, currentTime);
      tableSection.style.display = "block";
    } catch (error) {
      console.error(error);
      errorMessage.textContent = "An error occurred while fetching data. Please try again.";
    }
  });

  // Render the table
  function renderTable(data, currentTime) {
    lastSeenTable.innerHTML = "";
    data.forEach(player => {
      const lastSeenGMT = new Date(player.time * 1000).toGMTString();
      const timeAgo = getRelativeTime(currentTime - player.time);

      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${player.nick}</td>
        <td>${player.uid}</td>
        <td data-date="${player.time}">${lastSeenGMT}</td>
        <td data-relative="${currentTime - player.time}">${timeAgo}</td>
      `;
      lastSeenTable.appendChild(row);
    });
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

  // Sorting logic
  const tableHeaders = document.querySelectorAll("#lastSeenTable th");
  tableHeaders.forEach((header, index) => {
    header.addEventListener("click", () => {
      const sortKey = header.textContent.trim();
      const columnKey = ["nick", "uid", "time", "relative"][index];
      currentSortOrder = currentSortColumn === columnKey && currentSortOrder === "asc" ? "desc" : "asc";
      currentSortColumn = columnKey;

      let sortedData;
      if (columnKey === "time" || columnKey === "relative") {
        // Numeric sorting for date/relative time
        sortedData = [...playerData].sort((a, b) => {
          const valA = columnKey === "time" ? a.time : currentTime - a.time;
          const valB = columnKey === "time" ? b.time : currentTime - b.time;
          return currentSortOrder === "asc" ? valA - valB : valB - valA;
        });
      } else {
        // String/UID sorting
        sortedData = [...playerData].sort((a, b) => {
          const valA = columnKey === "nick" ? a.nick.toLowerCase() : a.uid.toLowerCase();
          const valB = columnKey === "nick" ? b.nick.toLowerCase() : b.uid.toLowerCase();
          return currentSortOrder === "asc" ? valA.localeCompare(valB) : valB.localeCompare(valA);
        });
      }

      renderTable(sortedData, currentTime);
    });
  });

  // Download table as CSV
  downloadCSVButton.addEventListener("click", () => {
    const rows = [["Nickname", "UID", "Last Seen (GMT)", "Time Ago"]];
    Array.from(lastSeenTable.querySelectorAll("tr")).forEach(row => {
      const cells = Array.from(row.querySelectorAll("td")).map(cell => cell.textContent);
      rows.push(cells);
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

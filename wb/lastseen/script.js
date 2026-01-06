document.addEventListener("DOMContentLoaded", () => {
  const squadInput = document.getElementById("squadName");
  const fetchDataButton = document.getElementById("fetchData");
  const errorMessage = document.getElementById("errorMessage");
  const tableSection = document.getElementById("table-section");
  const lastSeenTable = document.getElementById("lastSeenTable").querySelector("tbody");
  const downloadCSVButton = document.getElementById("downloadCSV");

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

    try {
      // Step 1: Fetch squad members
      const squadResponse = await fetch(`https://wbv.vercel.app/api/get-squad-details?name=${encodeURIComponent(squadName)}`);
      if (!squadResponse.ok) throw new Error("Failed to fetch squad members.");
      const squadResponseData = await squadResponse.json();

      // The API returns [{"name":"BOT","members":[...]}] (an array with one object)
      const squadData = (Array.isArray(squadResponseData) && squadResponseData.length > 0) ? squadResponseData[0].members : [];

      if (!Array.isArray(squadData) || squadData.length === 0) {
        errorMessage.textContent = "No members found for the given squad.";
        return;
      }

      const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds

      // Step 2: Fetch each player's data and build the table
      const playerPromises = squadData.map(member =>
        fetch(`https://wbv.vercel.app/api/get-player-stats?uid=${encodeURIComponent(member.uid)}`)
          .then(res => {
            if (!res.ok) throw new Error(`Failed to fetch data for UID: ${member.uid}`);
            return res.json();
          })
      );

      const playerData = await Promise.all(playerPromises);

      playerData.forEach(player => {
        const row = document.createElement("tr");
        const lastSeenGMT = new Date(player.time * 1000).toGMTString();
        const timeAgo = getRelativeTime(currentTime - player.time);

        row.innerHTML = `
          <td>${player.nick}</td>
          <td>${player.uid}</td>
          <td>${lastSeenGMT}</td>
          <td>${timeAgo}</td>
        `;
        lastSeenTable.appendChild(row);
      });

      tableSection.style.display = "block";
    } catch (error) {
      console.error(error);
      errorMessage.textContent = "An error occurred while fetching data. Please try again.";
    }
  });

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

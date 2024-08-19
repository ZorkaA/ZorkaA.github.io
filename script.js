async function queryUserData() {
    const userId = document.getElementById("userIdInput").value.trim();
    if (!userId) {
        alert("Please enter a User ID.");
        return;
    }

    const resultDiv = document.getElementById("result");
    resultDiv.innerHTML = "Loading...";

    const response = await fetch('data/wbuserdata.csv');
    const data = await response.text();
    
    const rows = data.split('\n').map(row => row.split(','));
    const headers = rows[0];
    const userRows = rows.filter(row => row.includes(userId));

    if (userRows.length > 0) {
        let html = `<table><tr>${headers.map(header => `<th>${header}</th>`).join('')}</tr>`;
        userRows.forEach(row => {
            html += `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`;
        });
        html += `</table>`;
        resultDiv.innerHTML = html;
    } else {
        resultDiv.innerHTML = "No data found for the given User ID.";
    }
}

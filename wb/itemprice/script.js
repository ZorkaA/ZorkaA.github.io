document.getElementById('fetchPricesButton').addEventListener('click', () => {
    const tokenInput = document.getElementById('tokenInput').value.trim();
    const idInput = document.getElementById('idInput').value.trim();

    // Ensure token is provided
    if (!tokenInput) {
        alert('Please enter a valid token.');
        return;
    }

    // Prepare the API URL
    const apiUrl = `https://store1.warbrokers.io/301//get_item_list.php?token=${encodeURIComponent(tokenInput)}`;
    console.log('Fetching data from URL:', apiUrl);

    fetch(apiUrl)
        .then(response => {
            console.log('Response received:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text(); // Get the response as a string
        })
        .then(data => {
            console.log('Raw data received:', data);

            let parsedData;
            try {
                parsedData = JSON.parse(data); // Parse the JSON response
                console.log('Parsed data:', parsedData);
            } catch (error) {
                throw new Error('Failed to parse JSON data.');
            }

            const items = parsedData.items;

            // Process input IDs or fetch all items if 'test' is entered
            const itemIds = idInput.toLowerCase() === 'test'
                ? items.map(item => item.id)
                : idInput.split(',').map(id => id.trim());

            console.log('Filtered item IDs:', itemIds);

            const resultTable = document.getElementById('outputTable');
            resultTable.innerHTML = ''; // Clear previous results

            // Populate the table with results
            const filteredItems = items.filter(item => itemIds.includes(item.id));
            console.log('Filtered items:', filteredItems);

            if (filteredItems.length === 0) {
                alert('No matching items found.');
                return;
            }

            filteredItems.forEach(item => {
                const row = resultTable.insertRow();
                row.insertCell(0).textContent = item.id;
                row.insertCell(1).textContent = Math.round(item.price); // Round price to nearest whole number
            });

            document.getElementById('downloadButton').style.display = 'block'; // Show download button
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred: ' + error.message);
        });
});

document.getElementById('downloadButton').addEventListener('click', () => {
    const rows = document.querySelectorAll('#outputTable tr');
    if (rows.length === 0) {
        alert('No data to download.');
        return;
    }

    let csvContent = 'id,price\n';
    rows.forEach(row => {
        const cols = row.querySelectorAll('td');
        const rowContent = Array.from(cols).map(col => col.textContent).join(',');
        csvContent += `${rowContent}\n`;
    });

    // Create a Blob and download the CSV file
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'item_prices.csv';
    a.click();
    URL.revokeObjectURL(url);
});

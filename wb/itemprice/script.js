document.getElementById('fetch-prices').addEventListener('click', async () => {
    const userToken = document.getElementById('user-token').value;
    const itemIds = document.getElementById('item-ids').value;

    // Mock function to simulate API call (replace with your real API logic)
    async function fetchPrices(token, ids) {
        return ids.map(id => ({ id, price: Math.round(Math.random() * 1000) }));
    }

    let itemIdsArray;
    if (itemIds.trim().toLowerCase() === 'test') {
        itemIdsArray = Array.from({ length: 100 }, (_, i) => `item_${i + 1}`);
    } else {
        itemIdsArray = itemIds.split(',').map(id => id.trim());
    }

    try {
        const prices = await fetchPrices(userToken, itemIdsArray);
        displayResults(prices);
        document.getElementById('download-csv').disabled = false;
    } catch (error) {
        document.getElementById('output').textContent = 'Error fetching prices.';
        console.error(error);
    }
});

function displayResults(data) {
    const outputDiv = document.getElementById('output');
    outputDiv.innerHTML = `
        <table border="1">
            <thead>
                <tr>
                    <th>Item ID</th>
                    <th>Price</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(item => `<tr><td>${item.id}</td><td>${item.price}</td></tr>`).join('')}
            </tbody>
        </table>
    `;

    // Attach data to CSV button
    document.getElementById('download-csv').onclick = () => downloadCSV(data);
}

function downloadCSV(data) {
    const csvContent = 'Item ID,Price\n' + data.map(item => `${item.id},${item.price}`).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'item_prices.csv';
    a.click();

    URL.revokeObjectURL(url);
}

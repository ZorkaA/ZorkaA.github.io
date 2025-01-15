document.addEventListener('DOMContentLoaded', () => {
    // Fetch button and input fields
    const fetchPricesButton = document.getElementById('fetch-prices');
    const tokenInput = document.getElementById('user-token');
    const idsInput = document.getElementById('item-ids');
    const outputDiv = document.getElementById('output');
    const downloadButton = document.getElementById('download-csv');

    fetchPricesButton.addEventListener('click', async () => {
        const token = tokenInput.value.trim();
        const itemIds = idsInput.value.trim();

        // Validate inputs
        if (!token || !itemIds) {
            outputDiv.innerHTML = `<p style="color: red;">Please provide both token and item IDs.</p>`;
            return;
        }

        // Fetch prices
        try {
            const response = await fetch(`https://store1.warbrokers.io/301//get_item_list.php?token=${token}`);
            const data = await response.json();

            // If 'test' is entered, display all items
            let itemsToShow = [];
            if (itemIds.toLowerCase() === 'test') {
                itemsToShow = data.items;
            } else {
                const idsArray = itemIds.split(',').map(id => id.trim());
                itemsToShow = data.items.filter(item => idsArray.includes(item.id));
            }

            // Generate table
            if (itemsToShow.length === 0) {
                outputDiv.innerHTML = `<p style="color: red;">No items found for the provided IDs.</p>`;
                return;
            }

            const tableHtml = `
                <table border="1">
                    <thead>
                        <tr>
                            <th>Item ID</th>
                            <th>Price</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${itemsToShow.map(item => `<tr><td>${item.id}</td><td>${Math.round(item.price)}</td></tr>`).join('')}
                    </tbody>
                </table>
            `;
            outputDiv.innerHTML = tableHtml;

            // Enable CSV download
            downloadButton.disabled = false;
            downloadButton.onclick = () => downloadCSV(itemsToShow);
        } catch (error) {
            console.error('Error fetching item prices:', error);
            outputDiv.innerHTML = `<p style="color: red;">Failed to fetch item prices. Please try again later.</p>`;
        }
    });

    const downloadCSV = (items) => {
        const csvContent = 'data:text/csv;charset=utf-8,' +
            ['Item ID,Price', ...items.map(item => `${item.id},${Math.round(item.price)}`)].join('\n');
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', 'item_prices.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
});

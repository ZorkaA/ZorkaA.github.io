document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const fetchPricesButton = document.getElementById('fetch-prices');
    const idsInput = document.getElementById('item-ids');
    const outputDiv = document.getElementById('output');
    const downloadButton = document.getElementById('download-csv');

    fetchPricesButton.addEventListener('click', async () => {
        const itemIds = idsInput.value.trim();

        // Validate input
        if (!itemIds) {
            outputDiv.innerHTML = `<p style="color: red;">Please provide item IDs.</p>`;
            return;
        }

        try {
            // Fetch all items
            const response = await fetch('https://store1.warbrokers.io/301//get_item_list.php');
            const rawData = await response.text();  // Get raw response as text

            // Split the string into pairs (id, price)
            const itemsArray = rawData.split(',');  // Split by commas
            const items = [];

            for (let i = 0; i < itemsArray.length; i += 2) {
                const id = itemsArray[i];
                const price = parseInt(itemsArray[i + 1], 10);
                items.push({ id, price });
            }

            // Filter items by input
            const idsArray = itemIds.split(',').map(id => id.trim());
            const itemsToShow = items.filter(item => idsArray.includes(item.id));

            if (itemsToShow.length === 0) {
                outputDiv.innerHTML = `<p style="color: red;">No items found for the provided IDs.</p>`;
                return;
            }

            // Generate table
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

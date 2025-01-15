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

            // If "test" is entered, show all items
            if (itemIds.toLowerCase() === 'test') {
                outputItems(items);
            } else {
                // Filter items by input
                const idsArray = itemIds.split(',').map(id => id.trim());
                const itemsToShow = items.filter(item => idsArray.includes(item.id));

                if (itemsToShow.length === 0) {
                    outputDiv.innerHTML = `<p style="color: red;">No items found for the provided IDs.</p>`;
                    return;
                }

                // Output filtered items
                outputItems(itemsToShow);
            }

        } catch (error) {
            console.error('Error fetching item prices:', error);
            outputDiv.innerHTML = `<p style="color: red;">Failed to fetch item prices. Please try again later.</p>`;
        }
    });

    const getItemImageUrl = (itemId) => {
        let imageUrl = '';

        // Check for flags (fxxx)
        if (itemId.startsWith('f') && itemId.length === 4) {
            imageUrl = `https://stats.warbrokers.io/images/cosmetics/flags/${itemId}.png`;
        }
        // Check for decals (dxxx)
        else if (itemId.startsWith('d') && itemId.length === 4) {
            imageUrl = `https://stats.warbrokers.io/images/cosmetics/decals/${itemId}.png`;
        }
        // Check for vxxixxx (items)
        else if (itemId.startsWith('v') && itemId.length === 7 && itemId[3] === 'i') {
            imageUrl = `https://stats.warbrokers.io/images/cosmetics/items/${itemId}.png`;
        }
        // Check for vxxcxxx (different items)
        else if (itemId.startsWith('v') && itemId.length === 7 && itemId[3] === 'c') {
            imageUrl = `https://stats.warbrokers.io/images/cosmetics/items/${itemId}.png`;
        }
        // Check for v1xcxxx, v2cxxx, v4xcxxx, v5xcxxx (vehicle items)
        else if ((itemId.startsWith('v1c') || itemId.startsWith('v2c') || itemId.startsWith('v4c') || itemId.startsWith('v5c')) && itemId.length === 7) {
            imageUrl = `https://camo.warbrokers.io/store/vehicles/${itemId}.jpg`;
        }
        // Check for heads (hxxx)
        else if (itemId.startsWith('h') && itemId.length === 4) {
            imageUrl = `https://stats.warbrokers.io/images/cosmetics/heads/${itemId}.png`;
        }

        return imageUrl;
    };

    const checkIfImageExists = (url) => {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => resolve(false);
            img.src = url;
        });
    };

    const outputItems = async (items) => {
        // Await image check for all items before rendering
        const itemsWithImages = [];
        
        for (const item of items) {
            const imageUrl = getItemImageUrl(item.id);
            const isValidImage = await checkIfImageExists(imageUrl);
            const imageElement = isValidImage ? `<img src="${imageUrl}" alt="${item.id}" width="50" height="50">` : 'No Image';
            itemsWithImages.push({ ...item, imageElement });
        }

        // Generate table with image column
        const tableHtml = `
            <table border="1">
                <thead>
                    <tr>
                        <th>Item ID</th>
                        <th>Price</th>
                        <th>Image</th>
                    </tr>
                </thead>
                <tbody>
                    ${itemsWithImages.map(item => `
                        <tr>
                            <td>${item.id}</td>
                            <td>${Math.round(item.price)}</td>
                            <td>${item.imageElement}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        outputDiv.innerHTML = tableHtml;

        // Enable CSV download
        downloadButton.disabled = false;
        downloadButton.onclick = () => downloadCSV(itemsWithImages);
    };

    const downloadCSV = (items) => {
        const csvContent = 'data:text/csv;charset=utf-8,' +
            ['Item ID,Price,Image URL', ...items.map(item => `${item.id},${Math.round(item.price)},${getItemImageUrl(item.id)}`)].join('\n');
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', 'item_prices_with_images.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
});

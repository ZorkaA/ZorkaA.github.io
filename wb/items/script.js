const fetchPrices = async () => {
    const idsInput = document.getElementById("item-ids").value.trim();
    const outputDiv = document.getElementById("output");
    const downloadButton = document.getElementById("download-csv");

    let ids = idsInput.split(",").map(id => id.trim());
    if (idsInput.toLowerCase() === "test") {
        ids = []; // Fetch all items if "test" is entered
    }

    try {
        const response = await fetch("https://store1.warbrokers.io/301//get_item_list.php");
        const data = await response.text();
        const itemsArray = data.split(",").reduce((acc, val, index, array) => {
            if (index % 2 === 0) acc.push({ id: val, price: parseInt(array[index + 1], 10) });
            return acc;
        }, []);

        // Filter items based on input or show all
        const filteredItems = ids.length === 0 ? itemsArray : itemsArray.filter(item => ids.includes(item.id));

        // Generate table with images
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
                    ${filteredItems.map(item => {
                        const imageUrl = getItemImageUrl(item.id);
                        return `
                            <tr>
                                <td>${item.id}</td>
                                <td>${Math.round(item.price)}</td>
                                <td>
                                    <img src="${imageUrl}" alt="${item.id}" 
                                         style="max-width: 100px; max-height: 100px; object-fit: contain;">
                                </td>
                            </tr>`;
                    }).join('')}
                </tbody>
            </table>
        `;
        outputDiv.innerHTML = tableHtml;

        // Enable CSV download
        downloadButton.disabled = false;
        downloadButton.onclick = () => downloadCSV(filteredItems);
    } catch (error) {
        outputDiv.textContent = `Error fetching item prices: ${error}`;
    }
};

// Get image URL based on item ID
const getItemImageUrl = (id) => {
    // All icons are now located in /data/icons/<itemname>.png
    return `/data/icons/${id}.png`;
};

// Download CSV
const downloadCSV = (items) => {
    const csvContent = "data:text/csv;charset=utf-8," +
        ["Item ID,Price"].concat(items.map(item => `${item.id},${item.price}`)).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "items.csv");
    document.body.appendChild(link); // Required for Firefox
    link.click();
    document.body.removeChild(link);
};

// Attach event listener to the button
document.getElementById("fetch-prices").addEventListener("click", fetchPrices);

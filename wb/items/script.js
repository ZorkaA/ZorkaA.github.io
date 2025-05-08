const fetchPrices = async (missingOnly = false) => {
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

        // Determine which items to display
        const filteredItems = missingOnly
            ? itemsArray.filter(item => !ids.includes(item.id)) // Items not in the user's list
            : ids.length === 0
            ? itemsArray // Show all items if no IDs are provided
            : itemsArray.filter(item => ids.includes(item.id)); // Items in the user's list

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
    const basePath = "/data/icons/";
    if (id.startsWith("f")) return `${basePath}flags/${id}.png`;
    if (id.startsWith("d")) return `${basePath}decals/${id}.png`;
    if (id.startsWith("h")) return `${basePath}heads/${id}.png`;
    if (id.startsWith("t")) return `${basePath}emotes/${id}.png`;
    if (/^v\d{2}i\d{3}$/.test(id)) return `${basePath}p_items/${id}.png`;
    if (/^v\d{2}c\d{3}$/.test(id)) return `${basePath}vehicles/${id}.png`;
    if (/^v30c\d{3}$/.test(id)) return `${basePath}p_camo/${id}.png`;
    if (/^w\d{2}c\d{3}$/.test(id)) return `${basePath}skins/${id}.png`;
    if (/^w\d+$/.test(id)) return `${basePath}weapons/${id}.png`;
    return "/data/icons/placeholder.png"; // Placeholder image for unknown items
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

// Handle token submission
const handleTokenSubmission = async () => {
    const tokenInput = document.getElementById("token-input");
    const errorDiv = document.getElementById("token-error");
    const itemIdsBox = document.getElementById("item-ids");

    const token = tokenInput.value.trim();
    if (!token) {
        errorDiv.textContent = "Please enter a token.";
        return;
    }

    try {
        const response = await fetch(`https://store1.warbrokers.io/301//get_items.php?token=${token}`);
        const data = await response.text();

        if (data === "Error! Bad token") {
            errorDiv.textContent = "Invalid token. Please try again.";
        } else {
            errorDiv.textContent = ""; // Clear error
            const existingIds = itemIdsBox.value.trim();
            itemIdsBox.value = existingIds
                ? `${existingIds},${data}`
                : data; // Append or overwrite
        }
    } catch (error) {
        errorDiv.textContent = `Error fetching items: ${error}`;
    }
};

// Attach event listeners
document.getElementById("fetch-prices").addEventListener("click", () => fetchPrices(false));
document.getElementById("fetch-missing-items").addEventListener("click", () => fetchPrices(true));
document.getElementById("paste-items").addEventListener("click", handleTokenSubmission);

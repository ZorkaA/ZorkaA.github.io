const outputItems = async (items) => {
    // Create an array of promises to check images
    const itemsWithImagesPromises = items.map(async (item) => {
        const imageUrl = getItemImageUrl(item.id);
        const isValidImage = await checkIfImageExists(imageUrl);
        const imageElement = isValidImage
            ? `<img src="${imageUrl}" alt="${item.id}" style="max-width: 50px; max-height: 50px; object-fit: contain;">`
            : 'No Image';
        return { ...item, imageElement };
    });

    // Wait for all promises to resolve
    const itemsWithImages = await Promise.all(itemsWithImagesPromises);

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

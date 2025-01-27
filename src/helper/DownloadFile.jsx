export const downloadCSV = (finalTableData) => {
    if (!finalTableData.length) return;

    // Define CSV headers
    const headers = Object.keys(finalTableData[0]).join(",");

    // Format rows as CSV
    const rows = finalTableData
        .map(row =>
            Object.values(row)
                .map(value => `"${value}"`) // Wrap each value in double quotes
                .join(",")
        )
        .join("\n");

    // Combine headers and rows
    const csvContent = `${headers}\n${rows}`;

    // Create a blob and link for downloading
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    // Create a temporary link to trigger download
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "final_prioritization.csv");
    document.body.appendChild(link);
    link.click();

    // Cleanup
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
};
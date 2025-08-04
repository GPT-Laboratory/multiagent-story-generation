import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";


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



export const downloadPRD = (finalTableData) => {
    if (!finalTableData.length) return;

    const doc = new jsPDF();

    // Add PRD Title
    doc.setFontSize(16);
    doc.text("Product Requirement Document (PRD)", 20, 20);
    doc.setFontSize(12);
    doc.text("Project: AI-Based Multi-Agent Prioritization", 20, 30);
    doc.text("Date: " + new Date().toLocaleDateString(), 20, 40);

    // Convert table data to array format
    const headers = Object.keys(finalTableData[0]);
    const rows = finalTableData.map(row => headers.map(header => row[header]));

    // Add Table to PDF
    autoTable(doc, {
        startY: 50,
        head: [headers],
        body: rows,
    });

    // Save PDF
    doc.save("Product_Requirement_Document.pdf");
};



export const handleDownloadReport = async (selectedUserStoryId) => {
    console.log(selectedUserStoryId?._id);
    
    try {
        const response = await fetch(`/api/get-report/${selectedUserStoryId?._id}`, {
            method: "GET",
        });

        if (!response.ok) {
            throw new Error("Failed to fetch the report");
        }

        // Convert response to a blob
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        // Create download link
        const a = document.createElement("a");
        a.href = url;
        a.download = `Project_Report_${selectedUserStoryId}.docx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error("Error fetching the report:", error);
        notification.error({
            message: "Failed to Download Report",
            description: error.message || "Something went wrong.",
        });
    }
};


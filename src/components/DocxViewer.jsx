import { useEffect, useState, useRef } from "react";
import { renderAsync } from "docx-preview"; // Correct import
import { Button, List, Typography, Card } from "antd";
import { useSelector } from "react-redux";
const { Title, Text } = Typography;

const DocxViewer = ({ fileId }) => {
    const [error, setError] = useState("");
    const docxContainerRef = useRef(null);
    const [selectedFileId, setSelectedFileId] = useState(fileId);
    const reports = useSelector((state) => state.reports.reports);


    console.log("file id", fileId);


    useEffect(() => {
        const fetchDocx = async () => {
            if (!selectedFileId) return;
            try {
                const response = await fetch(`/api/get-report/${selectedFileId}`);
                console.log("Response:", response);

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const blob = await response.blob();
                console.log("Blob received:", blob);

                if (docxContainerRef.current) {
                    docxContainerRef.current.innerHTML = ""; // Clear previous content
                    await renderAsync(blob, docxContainerRef.current); // Correct usage
                }
            } catch (err) {
                console.error("Error loading DOCX:", err);
                setError("Failed to load document.");
            }
        };

        fetchDocx();
    }, [selectedFileId]);


    // Function to Download the DOCX File
    const handleDownload = async () => {
        if (!selectedFileId) return;
        try {
            const response = await fetch(`/api/get-report/${selectedFileId}`);
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = `document_${selectedFileId}.docx`; // Dynamic Filename
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error("Download Error:", err);
        }
    };

    return (
        <div
            style={{ display: "flex", padding: "16px", background: "#f5f5f5", height: "80vh", overflow: "hidden" }}
        >
            {/* <Card title="Reports"
                style={{
                    width: "300px",
                    background: "#fff",
                    position: "sticky",
                    top: "0",
                    height: "100%",
                    // overflowY: "auto",
                    borderRadius: "8px",
                    flexShrink: 0, // Prevents shrinking when resizing
                }}
            >
                <List
                    dataSource={reports}
                    renderItem={(report, index) => (
                        <List.Item
                            key={report.file_id}
                            actions={[
                                <Button type="primary" onClick={() => setSelectedFileId(report.file_id)}>
                                    Open
                                </Button>,
                            ]}
                        >
                            <Text>Report {index + 1}</Text>
                        </List.Item>
                    )}
                />
            </Card> */}

            {/* Right - Document Viewer */}
            <Card variant="outlined" style={{ marginLeft: "16px",  overflowY: "auto", width:'100%' }}>
                <div style={{

                    position: "sticky",
                    top: "0",
                    background: "#fff",
                    zIndex: 10,
                    padding: "10px",
                    borderBottom: "1px solid #ddd",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                }}>
                    <Title level={4} style={{ margin: 0 }}>
                        Document Preview
                    </Title>
                    <Button type="primary" onClick={handleDownload} disabled={!selectedFileId}>
                        Download
                    </Button>
                </div>
                {error ? (
                    <Text type="danger">{error}</Text>
                ) : (
                    <div ref={docxContainerRef} style={{ border: "1px solid #ddd", padding: "16px", minHeight: "300px", background: "#fff", borderRadius: "8px" }}></div>
                )}
            </Card>
        </div>
    );
};

export default DocxViewer;

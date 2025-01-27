import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import App from "./App";
import EditItem from "./EditItem";
import Layout from "./Layout";
import "./App.css";

const Root = () => {
  const [result1, setResult1] = useState([]);

  const handleUpdateItem = (updatedItem) => {
    setResult1((prevResult) =>
      prevResult.map((item) =>
        item.key === updatedItem.key ? updatedItem : item
      )
    );
  };

  return (
    <Router>
      <Routes>
        {/* Route for the main App */}
        <Route
          path="/"
          element={<App result1={result1} setResult1={setResult1} />}
        />
        {/* Route for the Edit page wrapped with Layout */}
        <Route
          path="/edit/:key"
          element={
            <Layout>
              <EditItem onUpdate={handleUpdateItem} />
            </Layout>
          }
        />
      </Routes>
    </Router>
  );
};

ReactDOM.createRoot(document.getElementById("root")).render(<Root />);

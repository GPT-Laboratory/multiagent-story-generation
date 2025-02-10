import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import App from "./App";
import EditItem from "./EditItem";
import Layout from "./Layout";
import "./App.css";
import AddItem from "./AddItem";
import { addKeyToResponse } from "./utilityFunctions";
import Personas_list from "./helper/Personas_list";
import Add_Personas from "./helper/Add_Personas";

const Root = () => {
  const [result1, setResult1] = useState([]);

  const handleUpdateItem = (updatedItem) => {
    setResult1((prevResult) =>
      prevResult.map((item) =>
        item.key === updatedItem.key ? updatedItem : item
      )
    );
  };

  // const handleAddItem = (newItem) => {
  //   setResult1((prevResult) => [...prevResult, newItem]);
  // };

  const handleAddItem = (newItem) => {
    setResult1((prevResult) => {
      const updatedResult = [...prevResult, newItem];
      const responseDataWithKeys = addKeyToResponse(updatedResult);
      console.log("Updated result with keys: ", responseDataWithKeys);
      return responseDataWithKeys;
    });
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

        <Route
          path="/add"
          element={
            <Layout>
              <AddItem onUpdate={handleAddItem} />
            </Layout>
          }
        />

        <Route
          path="/add_agent"
          element={
            <Layout>
              <Add_Personas />
            </Layout>
          }
        />

        <Route
          path="/agent_list"
          element={
            <Layout>
              <Personas_list />
            </Layout>
          }
        />

      </Routes>
    </Router>
  );
};

ReactDOM.createRoot(document.getElementById("root")).render(<Root />);

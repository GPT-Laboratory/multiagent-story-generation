import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
const EditItem = ({ onUpdate }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const item = location.state?.item || {};

  const [formData, setFormData] = useState({ ...item });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleUpdate = (e) => {
    e.preventDefault();
    onUpdate(formData);
    navigate("/");
  };
  
  return (
    <div style={{ padding: "20px", maxWidth: "600px", margin: "0 auto" }}>
      <h2>Edit Item</h2>
      <form onSubmit={handleUpdate}>
    {Object.keys(formData).map(
      (key) =>
        key !== "key" && (
          <div key={key} style={{ marginBottom: "10px" }}>
            <label style={{ display: "block", marginBottom: "5px" }}>
              {key}
            </label>
            <input
              type="text"
              name={key}
              value={formData[key] || ""}
              onChange={handleChange}
              style={{
                width: "100%",
                padding: "8px",
                border: "1px solid #ccc",
                borderRadius: "5px",
              }}
            />
          </div>
        )
    )}
    <button
      type="submit"
      style={{
        backgroundColor: "rgba(52, 170, 52, 0.74)",
        color: "white",
        padding: "10px 20px",
        border: "none",
        borderRadius: "5px",  
          cursor: "pointer",
        }}
      >
        Update
        </button>
      </form>
    </div>
  );
};

export default EditItem;

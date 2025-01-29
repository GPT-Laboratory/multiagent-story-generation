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
    <div style={containerStyles}>
      <div style={formStyles}>
        <h2 style={headingStyles}>Edit Item</h2>
        <form onSubmit={handleUpdate}>
          {Object.keys(formData).map(
            (key) =>
              key !== "key" && (
                <div key={key} style={fieldContainerStyles}>
                  <label style={labelStyles}>{key}</label>
                  {key === "user_story" || key === "description" ? (
                    <textarea
                      name={key}
                      value={formData[key] || ""}
                      onChange={handleChange}
                      style={textareaStyles}
                      rows="4"
                    ></textarea>
                  ) : (
                    <input
                      type="text"
                      name={key}
                      value={formData[key] || ""}
                      onChange={handleChange}
                      style={inputStyles}
                    />
                  )}
                </div>
              )
          )}
          <div style={buttonContainerStyles}>
            <button type="submit" style={updateButtonStyles}>Update</button>
            <button type="button" onClick={() => navigate("/")} style={cancelButtonStyles}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Styling
const containerStyles = {
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  // height: "100vh",
  // backgroundColor: "#f4f4f9",
};

const formStyles = {
  backgroundColor: "white",
  padding: "25px",
  borderRadius: "12px",
  boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
  maxWidth: "500px",
  width: "100%",
  border: "1px solid #ddd",
};

const headingStyles = {
  textAlign: "center",
  marginBottom: "20px",
  color: "#333",
};

const fieldContainerStyles = {
  marginBottom: "15px",
};

const labelStyles = {
  display: "block",
  marginBottom: "5px",
  fontWeight: "bold",
  color: "#555",
};

const inputStyles = {
  width: "100%",
  padding: "10px",
  border: "1px solid #ccc",
  borderRadius: "8px",
  fontSize: "16px",
};

const textareaStyles = {
  ...inputStyles,
  resize: "vertical",
  fontFamily: "inherit",
};

const buttonContainerStyles = {
  display: "flex",
  justifyContent: "space-between",
  marginTop: "15px",
};

const updateButtonStyles = {
  backgroundColor: "#34aa34",
  color: "white",
  padding: "10px 20px",
  border: "none",
  borderRadius: "8px",
  cursor: "pointer",
  flex: 1,
  marginRight: "10px",
  fontSize: "16px",
};

const cancelButtonStyles = {
  backgroundColor: "#dc3545",
  color: "white",
  padding: "10px 20px",
  border: "none",
  borderRadius: "8px",
  cursor: "pointer",
  flex: 1,
  fontSize: "16px",
};

export default EditItem;

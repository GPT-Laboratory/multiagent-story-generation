import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const AddItem = ({ onUpdate }) => {
  const [formData, setFormData] = useState({ epic: "", user_story: "", description: "", status: "" });
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpdate(formData); // Add the new item
    navigate("/"); // Navigate back to the main page
  };

  return (
    <div style={modalStyles.container}>
      <div style={modalStyles.content}>
        <h2>Add New Item</h2>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "10px" }}>
            <label style={{ display: "block", marginBottom: "5px" }}>Epic</label>
            <input
              type="text"
              name="epic"
              value={formData.epic}
              onChange={handleChange}
              style={inputStyles}
            />
          </div>
          <div style={{ marginBottom: "10px" }}>
            <label style={{ display: "block", marginBottom: "5px" }}>User Story</label>
            <textarea
              name="user_story"
              value={formData.user_story}
              onChange={handleChange}
              style={textareaStyles}
              rows="3"
            />
          </div>
          <div style={{ marginBottom: "10px" }}>
            <label style={{ display: "block", marginBottom: "5px" }}>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              style={textareaStyles}
              rows="4"
            />
          </div>
          <div style={{ marginBottom: "10px" }}>
            <label style={{ display: "block", marginBottom: "5px" }}>Status</label>
            <input
              type="text"
              name="status"
              value={formData.status}
              onChange={handleChange}
              style={inputStyles}
            />
          </div>
          <button type="submit" style={buttonStyles}>
            Submit
          </button>
          <button
            type="button"
            onClick={() => navigate("/")}
            style={{ ...buttonStyles, backgroundColor: "rgba(220, 53, 69, 0.9)", marginLeft: "10px" }}
          >
            Cancel
          </button>
        </form>
      </div>
    </div>
  );
};

// Styles for the modal and form elements
const modalStyles = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  content: {
    backgroundColor: "white",
    padding: "20px",
    borderRadius: "10px",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
    maxWidth: "500px",
    width: "90%",
  },
};

const inputStyles = {
  width: "100%",
  padding: "8px",
  border: "1px solid #ccc",
  borderRadius: "5px",
};

const textareaStyles = {
  width: "100%",
  padding: "8px",
  border: "1px solid #ccc",
  borderRadius: "5px",
  resize: "vertical",
  fontFamily: "inherit",
};

const buttonStyles = {
  backgroundColor: "rgba(52, 170, 52, 0.74)",
  color: "white",
  padding: "10px 20px",
  border: "none",
  borderRadius: "5px",
  cursor: "pointer",
};

export default AddItem;

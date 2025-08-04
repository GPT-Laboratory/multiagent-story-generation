
// import React, { useState, useEffect, useRef } from "react";
// import { Table, Input, Button, Form, message, Breadcrumb } from "antd";
// import { Link } from "react-router-dom";

// const Personas_list = () => {
//   const [personas, setPersonas] = useState([]);
//   const [form] = Form.useForm();
//   const inputRef = useRef(null); // Ref for input field
//   const addPersonaRef = useRef(null); // Ref for "Add New Persona" section
//   const listPersonasRef = useRef(null);
//   useEffect(() => {
//     // Scroll to "Add New Persona" section
//     addPersonaRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });

//     // Auto-focus the input field
//     inputRef.current?.focus();
//   }, []);

//   // Fetch personas from backend
//   useEffect(() => {
//     const fetchPersonas = async () => {
//       try {
//         const response = await fetch("/api/personas");
//         const data = await response.json();
//         setPersonas(data);
//       } catch (error) {
//         console.error("Error fetching personas:", error);
//       }
//     };
  
//     fetchPersonas();
//   }, []);

  
//   // Table columns
//   const columns = [
//     // { title: "ID", dataIndex: "id", key: "id", width: 100 },
//     { title: "ID", dataIndex: "index", key: "index", width: 100 },
//     { title: "Name", dataIndex: "name", key: "name", width: 200 },
//     { title: "Role", dataIndex: "role", key: "role", width: 130 },
//     {
//       title: "Icon",
//       dataIndex: "default_icon",
//       key: "default_icon",
//       width: 100,
//       render: (icon) => <span style={{ fontSize: "13px" }}>{icon}</span>,
//     },
//     {
//       title: "Tasks",
//       dataIndex: "tasks",
//       key: "tasks",
//       render: (tasks) => (
//         <ul>
//           {tasks.map((task) => (
//             <li key={task.taskId}>
//               <b>{task.taskLabel}:</b> {task.prompt}
//             </li>
//           ))}
//         </ul>
//       ),
//     },
//   ];

//   return (
//     <>
//     <Breadcrumb
//       separator=""
//       items={[
//         {
//           title: <Link to="/">Home</Link>, // Use Link instead of href
//         },
//         {
//           type: 'separator',
//         },
//         {
//           title: <Link to="/add_agent">Add Agent</Link>, // Use Link for navigation
//         },
//         {
//           type: 'separator',
//         },
//         {
//           title: <Link to="/agent_list">Agents List</Link>, // Use Link for navigation
//         },

//       ]}
//     />
//     <div style={{ padding: "20px", display: "flex", flexDirection: "column", alignItems: "center" }}>
//       {/* <h2>List of Personas</h2> */}

//       <h2 ref={listPersonasRef}>List of Personas</h2>

//       {/* Personas Table */}
//       <Table
//         scroll={{ x: 2000, y: 600 }}
//         style={{ width: "100%" }}
//         // dataSource={personas}
//         dataSource={personas.map((persona, index) => ({ ...persona, index: index + 1 }))}
//         columns={columns}
//         // rowKey="id"
//         rowKey="index"
//         pagination={false}
//       />
//     </div>
//     </>

//   );
// };

// export default Personas_list;


import React, { useState, useEffect } from "react";
import { Table, Button, message, Breadcrumb } from "antd";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeftOutlined } from "@ant-design/icons";

const Personas_list = () => {
  const [personas, setPersonas] = useState([]);
  const navigate = useNavigate();
  const { id } = useParams();

  useEffect(() => {
    fetchPersonas();
  }, []);

  // const fetchPersonas = async () => {
  //   try {
  //     const response = await fetch("/api/personas");
  //     const data = await response.json();
  //     setPersonas(data);
  //   } catch (error) {
  //     console.error("Error fetching personas:", error);
  //   }
  // };

  const fetchPersonas = async () => {
    try {
      const response = await fetch(`/api/personas/${id}`); // Send project_id
      const data = await response.json();
      setPersonas(data);
    } catch (error) {
      console.error("Error fetching personas:", error);
    }
  };

  const handleEdit = (persona) => {
    navigate(`/add_agent/${id}`, { state: { persona } }); // Send persona data to Add_Personas
  };

  const handleDelete = async (id) => {
    try {
      const response = await fetch(`/api/delete-persona/${id}`, { method: "DELETE" });
      if (response.ok) {
        message.success("Persona deleted successfully");
        fetchPersonas();
      } else {
        message.error("Failed to delete persona");
      }
    } catch (error) {
      console.error("Error deleting persona:", error);
    }
  };

  const columns = [
    { title: "ID", dataIndex: "index", key: "index", width: 100 },
    { title: "Name", dataIndex: "name", key: "name", width: 200 },
    { title: "Role", dataIndex: "role", key: "role", width: 130 },
    {
      title: "Tasks",
      dataIndex: "tasks",
      key: "tasks",
      render: (tasks) => (
        <ul>
          {tasks.map((task) => (
            <li key={task.taskId}>
              <b>{task.taskLabel}:</b> {task.prompt}
            </li>
          ))}
        </ul>
      ),
    },
    {
      title: "Actions",
      key: "actions",
      render: (_, record) => (
        <>
          <Button color="purple" variant="filled" style={{marginBottom:'5px', width:'100%'}} onClick={() => handleEdit(record)}>Edit</Button>
          <Button color="danger" variant="filled" danger style={{ width:'100%'}} onClick={() => handleDelete(record._id)}>Delete</Button>
        </>
      ),
    },
  ];

  return (
    <>
      <Breadcrumb
      style={{
        margin: '20px',
        marginLeft:'40px'
      }}
      >
        <Breadcrumb.Item><Link to="/">Projects list</Link></Breadcrumb.Item>
        <Breadcrumb.Item><Link to={`/project/${id}`}>Home</Link></Breadcrumb.Item>
        <Breadcrumb.Item><Link to={`/add_agent/${id}`}>Add Agent</Link></Breadcrumb.Item>
        <Breadcrumb.Item><Link to={`/agent_list/${id}`}>Agents List</Link></Breadcrumb.Item>
      </Breadcrumb>

      <div style={{ padding: "20px", }}>
      <ArrowLeftOutlined
            style={{ fontSize: '20px', cursor: 'pointer', marginRight: '12px' }} 
            onClick={() => navigate(`/project/${id}`)}
          />
        <div style={{
          display:'flex',
          justifyContent:'space-between',
        }}>
        <h2> List of Personas</h2> 
        <Button type="primary"  onClick={() => navigate(`/add_agent/${id}`)}>Add New Persona Profile</Button>
        </div>
        
        <Table
          scroll={{ x: 500 }}
          dataSource={personas.map((persona, index) => ({ ...persona, index: index + 1 }))}
          columns={columns}
          rowKey="_id"
        />
      </div>
    </>
  );
};

export default Personas_list;

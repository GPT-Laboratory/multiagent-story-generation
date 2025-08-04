// import React, { useState } from "react";
// import ReactDOM from "react-dom/client";
// import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
// import App from "./App";
// import EditItem from "./EditItem";
// // import Layout from "./Layout";
// import "./App.css";
// import AddItem from "./AddItem";
// import { addKeyToResponse } from "./utilityFunctions";
// import Personas_list from "./helper/Personas_list";
// import Add_Personas from "./helper/Add_Personas";
// import CreateProject from "./components/CreateProject";
// import Layout from "./components/Layout";
// import { AuthProvider } from "./components/authUserContext"
// import Auth from "./components/Auth";
// import Protectedroutes from "./components/Protectedroutes";
// import { Provider } from "react-redux";
// import store from "./redux-Store/store.jsx"

// const Root = () => {
//   const [result1, setResult1] = useState([]);

//   const handleUpdateItem = (updatedItem) => {
//     setResult1((prevResult) =>
//       prevResult.map((item) =>
//         (item._id ? item._id === updatedItem._id : item.key === updatedItem.key) 
//           ? updatedItem 
//           : item
//       )
//     );
// };

//   const handleAddItem = (newItem) => {
//     setResult1((prevResult) => {
//       const updatedResult = [...prevResult, newItem];
//       const responseDataWithKeys = addKeyToResponse(updatedResult);
//       console.log("Updated result with keys: ", responseDataWithKeys);
//       return responseDataWithKeys;
//     });
//   };

//   const handleUpgradeItem = async (data) => {
//     try {
//       const response = await fetch("/api/upgrade_story", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify(data),
//       });

//       if (!response.ok) {
//         throw new Error("Failed to upgrade story");
//       }

//       const result = await response.json();
//       console.log("Upgraded Story Response:", result);

//       setResult1((prevResult) =>
//         prevResult.map((item) =>
//           item.key === data.key ? { ...item, user_story: result.upgraded_story } : item
//         )
//       );
//     } catch (error) {
//       console.error("Error upgrading story:", error);
//     }
//   };


//   return (
//     <Provider store={store} >
//     <AuthProvider>


//       <Router>

//         <Routes>
//           {/* Wrap everything inside Layout to always show Header & Footer */}
//           <Route path="/" element={<Layout />}>
//             <Route index
//               element={
//                 <Protectedroutes>
//                 <CreateProject />
//                 </Protectedroutes>  
//               }
//             />
//             <Route path="project/:id"
//               element={
//                 <Protectedroutes>
//                   <App result1={result1} setResult1={setResult1} />
//                 </Protectedroutes>}
//             />
//             <Route path="project/:id/:id"
//               element={
//                 <Protectedroutes>
//                   <App result1={result1} setResult1={setResult1} />
//                 </Protectedroutes>}
//             />
//             <Route path="edit/:key/:id"
//               element={
//                 <Protectedroutes>
//                   <EditItem onUpdate={handleUpdateItem} onUpgrade={handleUpgradeItem} />
//                 </Protectedroutes>}
//             />
//             <Route path="add"
//               element={
//                 <Protectedroutes>
//                   <AddItem onUpdate={handleAddItem} />
//                 </Protectedroutes>}
//             />
//             <Route path="add_agent/:id"
//               element={
//                 <Protectedroutes>
//                   <Add_Personas />
//                 </Protectedroutes>}
//             />
//             <Route path="agent_list/:id"
//               element={
//                 <Protectedroutes>
//                   <Personas_list />
//                 </Protectedroutes>}
//             />
//             <Route path="/login" element={<Auth />} />
//           </Route>
//         </Routes>
//       </Router>

//     </AuthProvider>
//     </Provider>
//   );
// };

// ReactDOM.createRoot(document.getElementById("root")).render(<Root />);

import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import App from "./App";
import EditItem from "./EditItem";
// import Layout from "./Layout";
import "./App.css";
import AddItem from "./AddItem";
import { addKeyToResponse } from "./utilityFunctions";
import Personas_list from "./helper/Personas_list";
import Add_Personas from "./helper/Add_Personas";
import CreateProject from "./components/CreateProject";
import Layout from "./components/Layout";
import { AuthProvider } from "./components/authUserContext"
import Auth from "./components/Auth";
import Protectedroutes from "./components/Protectedroutes";
import { Provider } from "react-redux";
import store from "./redux-Store/store.jsx"
import { AppWindowMac } from "lucide-react";

const Root = () => {


  return (
    <Provider store={store} >
      <AuthProvider>


        <Router>

          <Routes>
            {/* Wrap everything inside Layout to always show Header & Footer */}
            <Route path="/" element={<Layout />}>
              <Route index
                element={
                  <Protectedroutes>
                    <CreateProject />
                  </Protectedroutes>
                }
              />
              <Route path="project/:id"
                element={
                  <Protectedroutes>
                    <App />
                  </Protectedroutes>}
              />
              <Route path="project/:id/:id"
                element={
                  <Protectedroutes>
                    <App />
                  </Protectedroutes>}
              />
              <Route path="edit/:key/:id"
                element={
                  <Protectedroutes>
                    <EditItem />
                  </Protectedroutes>}
              />
              <Route path="add"
                element={
                  <Protectedroutes>
                    <AddItem />
                  </Protectedroutes>}
              />
              <Route path="add_agent/:id"
                element={
                  <Protectedroutes>
                    <Add_Personas />
                  </Protectedroutes>}
              />
              <Route path="agent_list/:id"
                element={
                  <Protectedroutes>
                    <Personas_list />
                  </Protectedroutes>}
              />
              {/* <Route path="/login" element={<Auth />} /> */}
              <Route path="/login" element={<Auth handle={() => {}} hideBtn={<span></span>} />} />


            </Route>
          </Routes>
        </Router>

      </AuthProvider>
    </Provider>
  );
};

ReactDOM.createRoot(document.getElementById("root")).render(<Root />);


import { configureStore } from "@reduxjs/toolkit";
import MainSlice from "../features/MainSlice.jsx"; // Import your reducers
import TableStoriesResponse from "../features/TableStoriesResponse.jsx"; // Import your reducers
import reportsReducer from "../features/ReportSlice.jsx"

const store = configureStore({
  reducer: {
    main: MainSlice, // Add your reducers here
    tablestoriesresponse: TableStoriesResponse,
    reports: reportsReducer,
  },
});

export default store;

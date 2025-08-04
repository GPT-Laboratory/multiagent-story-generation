import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Async thunk to fetch all reports for a selected user story
export const fetchAllReports = createAsyncThunk(
    "reports/fetchAllReports",
    async (selectedUserStoryId, { rejectWithValue }) => {
        try {
            const response = await fetch(`/api/get-all-reports/${selectedUserStoryId}`);

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            return data.reports;
        } catch (error) {
            return rejectWithValue(error.message);
        }
    }
);

const ReportSlice = createSlice({
    name: "reports",
    initialState: {
        reports: [],
        loading: false,
        error: null,
    },
    reducers: {
        clearReports: (state) => {
            state.reports = [];
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchAllReports.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchAllReports.fulfilled, (state, action) => {
                state.loading = false;
                state.reports = action.payload;
                console.log("reports comes",state.reports);
                
            })
            .addCase(fetchAllReports.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            });
    },
});

export const { clearReports } = ReportSlice.actions;
export default ReportSlice.reducer;

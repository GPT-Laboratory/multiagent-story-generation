import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";
import { getUserId } from "../components/GetLoginUserId.jsx";

// Async thunks for API interactions
export const fetchProjects = createAsyncThunk(
  "main/fetchProjects",
  async (_, { rejectWithValue }) => {
    const userId = getUserId();
    if (!userId) {
      return rejectWithValue("User not logged in");
    }
    try {
      const response = await axios.get(`/api/projects?user_id=${userId}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || "Failed to fetch projects");
    }
  }
);

export const fetchUserStories = createAsyncThunk(
  "main/fetchUserStories",
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get("/api/user_stories");
      return response.data || [];
    } catch (error) {
      return rejectWithValue(error.response?.data || "Failed to fetch user stories");
    }
  }
);

export const createProject = createAsyncThunk(
  "main/createProject",
  async (projectName, { rejectWithValue }) => {
    const userId = getUserId();
    if (!userId) {
      return rejectWithValue("User not logged in");
    }
    try {
      const response = await axios.post("/api/create-project", {
        project_name: projectName,
        user_id: userId,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || "Failed to create project");
    }
  }
);

export const deleteProject = createAsyncThunk(
  "main/deleteProject",
  async (projectId, { rejectWithValue }) => {
    try {
      await axios.delete(`/api/delete-project/${projectId}`);
      return projectId;
    } catch (error) {
      return rejectWithValue(error.response?.data || "Failed to delete project");
    }
  }
);

export const deleteUserStoryVersion = createAsyncThunk(
  "main/deleteUserStoryVersion",
  async (storyId, { rejectWithValue }) => {
    try {
      await axios.delete(`/api/delete-user-story-version/${storyId}`);
      return storyId;
    } catch (error) {
      return rejectWithValue(error.response?.data || "Failed to delete user story");
    }
  }
);

export const fetchFinalTablePrioritization = createAsyncThunk(
  "finalTable/fetchByStoryId",
  async (storyId, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/get-final-table-prioritization/${storyId}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to fetch data");
      }

      return data.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchFinalPrioritization = createAsyncThunk(
  "finalResponse/fetchByStoryId",
  async (storyId, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/get-final-prioritization/${storyId}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to fetch data");
      }

      return data.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  counter: 0,
  projects: [],
  userStories: [],
  prioritization: [],
  prioritization_response: [],
  user_story_selected: null,
  loading: false,
  error: null,
};

const MainSlice = createSlice({
  name: "main",
  initialState,
  reducers: {
    increment: (state) => {
      state.counter += 1;
    },
    decrement: (state) => {
      state.counter -= 1;
    },
    setUserStorySelected: (state, action) => {
      state.user_story_selected = action.payload; // Update selected story
      console.log("story _ id:", state.user_story_selected);
      
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Projects
      .addCase(fetchProjects.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchProjects.fulfilled, (state, action) => {
        state.loading = false;
        state.projects = action.payload;
        state.error = null;
      })
      .addCase(fetchProjects.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Fetch User Stories
      .addCase(fetchUserStories.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchUserStories.fulfilled, (state, action) => {
        state.loading = false;
        state.userStories = action.payload;
        console.log("userStories",state.userStories);
        
        state.error = null;
      })
      .addCase(fetchUserStories.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Create Project
      .addCase(createProject.pending, (state) => {
        state.loading = true;
      })
      .addCase(createProject.fulfilled, (state, action) => {
        state.loading = false;
        state.projects.push(action.payload);
        state.error = null;
      })
      .addCase(createProject.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Delete Project
      .addCase(deleteProject.pending, (state) => {
        state.loading = true;
      })
      .addCase(deleteProject.fulfilled, (state, action) => {
        state.loading = false;
        state.projects = state.projects.filter(project => project.id !== action.payload);
        state.error = null;
      })
      .addCase(deleteProject.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Delete User Story
      .addCase(deleteUserStoryVersion.pending, (state) => {
        state.loading = true;
      })
      .addCase(deleteUserStoryVersion.fulfilled, (state, action) => {
        state.loading = false;
        state.userStories = state.userStories.filter(story => story.id !== action.payload);
        state.error = null;
      })
      .addCase(deleteUserStoryVersion.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // fetch final_prioritization_table
      .addCase(fetchFinalTablePrioritization.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchFinalTablePrioritization.fulfilled, (state, action) => {
        state.loading = false;
        state.prioritization = action.payload;
        console.log(state.prioritization);
        
      })
      .addCase(fetchFinalTablePrioritization.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // fetch final_response 
      // fetch final_prioritization_table
      .addCase(fetchFinalPrioritization.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchFinalPrioritization.fulfilled, (state, action) => {
        state.loading = false;
        state.prioritization_response = action.payload;
        console.log(state.prioritization_response);
        
      })
      .addCase(fetchFinalPrioritization.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { increment, decrement, setUserStorySelected } = MainSlice.actions;
export default MainSlice.reducer;
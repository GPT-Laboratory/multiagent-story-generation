import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Async thunk for upgrading the story
export const upgradeItem = createAsyncThunk("stories/upgradeItem", async (data, { rejectWithValue }) => {
  console.log("Upgrading story with data: ", data);

  try {
    const response = await fetch("/api/upgrade_story", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error("Failed to upgrade story");
    }

    const result = await response.json();
    return { _id: data._id, upgraded_story: result.upgraded_story }; // Return updated data
  } catch (error) {
    return rejectWithValue(error.message);
  }
});

export const updateItem = createAsyncThunk(
  "stories/updateItem",
  async (formData, { rejectWithValue }) => {
    try {
      const response = await fetch("/api/update_story", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error("Failed to update story");
      }

      const result = await response.json();
      return formData; // Return updated story data
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const deleteItem = createAsyncThunk("stories/deleteItem", async (_id, { rejectWithValue }) => {
  try {
    const response = await fetch(`/api/delete-user-story/${_id}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error("Failed to delete user story");
    }

    return _id; // Return the deleted story's _id
  } catch (error) {
    return rejectWithValue(error.message);
  }
});



const initialState = {
  result1: [],
  approvedStories: [],
  loading: false,
  error: null
};

const tableStoriesResponse = createSlice({
  name: "tablestoriesresponse",
  initialState,
  reducers: {
    setResult1: (state, action) => {
      state.result1 = action.payload;
    },
    addApprovedStory: (state, action) => {
      state.approvedStories.push(action.payload); // Add the approved story to the array
      console.log("approved_stories",state.approvedStories);
      
    },
    removeApprovedStory: (state, action) => {
      state.approvedStories = state.approvedStories.filter(
        (item) => item._id !== action.payload._id
      ); // Remove the approved story
      console.log("approved_stories",state.approvedStories);
    },
    approveAllStories: (state, action) => {
      state.approvedStories = action.payload; // Add all stories to approvedStories
    },
    addItem: (state, action) => {
      state.result1.push(action.payload);
    },
    deleteItem: (state, action) => {
      state.result1 = state.result1.filter((item) => item._id !== action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      // upgrade user story
      .addCase(upgradeItem.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(upgradeItem.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.result1.findIndex((item) => item._id === action.payload._id);
        if (index !== -1) {
          state.result1[index].user_story = action.payload.upgraded_story;
        }
      })
      .addCase(upgradeItem.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // update user story
      .addCase(updateItem.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateItem.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.result1.findIndex((item) => item._id === action.payload._id);
        if (index !== -1) {
          state.result1[index] = action.payload;
        }
      })
      .addCase(updateItem.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // delete user story
      .addCase(deleteItem.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteItem.fulfilled, (state, action) => {
        state.loading = false;
        state.result1 = state.result1.filter((item) => item._id !== action.payload);
      })
      .addCase(deleteItem.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { setResult1, addItem, addApprovedStory, removeApprovedStory, approveAllStories } = tableStoriesResponse.actions;
export default tableStoriesResponse.reducer;

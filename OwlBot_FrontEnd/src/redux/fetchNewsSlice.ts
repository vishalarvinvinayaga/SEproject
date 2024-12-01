import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { fetchNewsFromApi } from "../api/newsApi";

// Define the article type
interface Article {
    source: {
        id: string | null;
        name: string;
    };
    author: string | null;
    title: string;
    description: string;
    url: string;
    urlToImage: string;
    publishedAt: string;
    content: string;
}

// Define the state type
interface NewsState {
    articles: Article[];
    loading: boolean;
    error: string | null;
}

const initialState: NewsState = {
    articles: [],
    loading: false,
    error: null,
};

// Async thunk for fetching news
export const fetchNews = createAsyncThunk(
    "news/fetchNews",
    async (_, { rejectWithValue }) => {
        try {
            const articles = await fetchNewsFromApi();
            return articles;
        } catch (error:any) {
            return rejectWithValue(error.message);
        }
    }
);

const newsSlice = createSlice({
    name: "news",
    initialState,
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(fetchNews.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchNews.fulfilled, (state, action) => {
                state.loading = false;
                state.articles = action.payload;
            })
            .addCase(fetchNews.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload as string;
            });
    },
});

export default newsSlice.reducer;

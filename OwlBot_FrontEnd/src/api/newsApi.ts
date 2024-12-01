import axios from "axios";

const News_API = "https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=3a728d526e5349dd89913977b65f8280";

export const fetchNewsFromApi = async () => {
    try {
        const response = await axios.get(News_API);
        return response.data.articles;
    } catch (error:any) {
        throw new Error(
            error.response?.data?.message || "Failed to fetch news"
        );
    }
};

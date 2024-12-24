import axios from 'axios';

const API_URL = process.env.GRAPH_RAG_API_URL;

export async function searchQuery(
  queryString: string,
) {
  try {

    const response = await axios.get(`${API_URL}/search`, {
      params: { q: queryString }
    });

    console.log('Full response:', response.data);

    const results = response.data?.result;

    if (!results) {
      console.error('No results found in response');
      process.exit(1);
    }

    console.log(results);
  } catch (error: any) {
    console.error('Search failed:', error.response?.data || error.message);
    process.exit(1);
  }
} 
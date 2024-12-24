import axios from 'axios';
import { getAuthToken } from './utils';

const API_URL = process.env.GRAPH_RAG_API_URL;

export async function searchQuery(
  queryString: string,
  authToken?: string,
  limit?: number,
  outputFormat: string = 'text'
) {
  try {
    authToken = authToken || getAuthToken();

    const response = await axios.get(`${API_URL}/search`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
      params: { q: queryString, limit }
    });

    const results = response.data.results;

    if (outputFormat === 'json') {
      console.log(JSON.stringify(results, null, 2));
    } else {
      results.forEach((result: any) => {
        console.log(`Title: ${result.title}`);
        console.log(`Snippet: ${result.snippet}`);
        console.log('---');
      });
    }
  } catch (error: any) {
    console.error('Search failed:', error.response?.data || error.message);
    process.exit(1);
  }
} 
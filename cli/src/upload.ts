import axios from 'axios';
import fs from 'fs';
import path from 'path';
import { getAuthToken } from './utils';

const API_URL = process.env.GRAPH_RAG_API_URL;

export async function uploadFile(
  filePath: string,
  authToken?: string,
  outputFormat: string = 'text'
) {
  try {
    authToken = authToken || getAuthToken();

    const fileStream = fs.createReadStream(filePath);
    const fileName = path.basename(filePath);

    // Upload file to the storage bucket
    const uploadResponse = await axios.post(`${API_URL}/upload`, fileStream, {
      headers: {
        'Content-Type': 'application/octet-stream',
        'Authorization': `Bearer ${authToken}`,
        'File-Name': fileName
      }
    });

    const blobUrl = uploadResponse.data.blobUrl;

    // Register the blob URL with the backend
    const registerResponse = await axios.post(
      `${API_URL}/register`,
      { blobUrl },
      { headers: { 'Authorization': `Bearer ${authToken}` } }
    );

    if (outputFormat === 'json') {
      console.log(JSON.stringify({ status: 'success', blob_url: blobUrl }, null, 2));
    } else {
      console.log('Uploaded and registered file:', blobUrl);
    }
  } catch (error: any) {
    console.error('File upload failed:', error.response?.data || error.message);
    process.exit(1);
  }
} 
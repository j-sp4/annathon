import { uploadFile } from './upload';
import fs from 'fs';
// import { getAuthToken } from './utils';
import axios from 'axios';
export async function indexFiles(
  filePaths: string[],
  fileListPath?: string,
  // authToken?: string,
) {
  try {
    // authToken = authToken || getAuthToken();

    if (fileListPath) {
      const fileListContent = fs.readFileSync(fileListPath, 'utf-8');
      filePaths = fileListContent.split('\n').filter(Boolean);
    }

    if (!filePaths || filePaths.length === 0) {
      throw new Error('No files provided for indexing.');
    }

    const blobUrls = [];

    for (const filePath of filePaths) {
      blobUrls.push(await uploadFile(filePath));
    }
    const blobRequest = {
      urls: blobUrls,
      download_urls: blobUrls,
      pathnames: filePaths,
      content_types: ["text/plain"],
      content_dispositions: ["attachment"]
    }
    axios.post(`${process.env.GRAPH_RAG_API_URL}/create_graph`, blobRequest);

    console.log('All files uploaded and indexed successfully.');
  } catch (error: any) {
    console.error('Indexing failed:', error.message);
    process.exit(1);
  }
} 
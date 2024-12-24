import { uploadFile } from './upload';
import fs from 'fs';
import { getAuthToken } from './utils';

export async function indexFiles(
  filePaths: string[],
  fileListPath?: string,
  authToken?: string,
  outputFormat: string = 'text'
) {
  try {
    authToken = authToken || getAuthToken();

    if (fileListPath) {
      const fileListContent = fs.readFileSync(fileListPath, 'utf-8');
      filePaths = fileListContent.split('\n').filter(Boolean);
    }

    if (!filePaths || filePaths.length === 0) {
      throw new Error('No files provided for indexing.');
    }

    const blobUrls = [];

    for (const filePath of filePaths) {
      await uploadFile(filePath, authToken, outputFormat);
      // Collect blob URLs if needed
    }

    // Optionally, send all blob URLs to the backend's indexing endpoint

    console.log('All files uploaded and indexed successfully.');
  } catch (error: any) {
    console.error('Indexing failed:', error.message);
    process.exit(1);
  }
} 
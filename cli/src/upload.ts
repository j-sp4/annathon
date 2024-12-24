import fs from 'fs';
import path from 'path';
import { put } from "@vercel/blob";


export async function uploadFile(
  filePath: string,
) {
  try {

    const fileStream = fs.createReadStream(filePath);
    const fileName = path.basename(filePath);

    // Upload file to the storage bucket
    const { url } = await put(fileName, fileStream, { access: 'public', token:"vercel_blob_rw_WhbuSkkKWA2z9Cv3_1Ci1wCsDZbqN6FvlZs08fO33szTMRc" });

    return url
  } catch (error: any) {
    console.error('File upload failed:', error.response?.data || error.message);
    process.exit(1);
  }
} 
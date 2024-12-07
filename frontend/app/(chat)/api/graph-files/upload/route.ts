import { put } from '@vercel/blob';
import { NextResponse } from 'next/server';
import { z } from 'zod';
import axios from 'axios';


import { auth } from '@/app/(auth)/auth';

// Use Blob instead of File since File is not available in Node.js environment
const FileSchema = z.object({
  file: z
    .instanceof(Blob)
    .refine((file) => file.size <= 5 * 1024 * 1024, {
      message: 'File size should be less than 5MB',
    })
    // Update the file type based on the kind of files you want to accept
    .refine((file) => ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'].includes(file.type), {
      message: 'File type should be TXT, PDF, or DOCX',
    }),
});

export async function POST(request: Request) {
  const session = await auth();

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  if (request.body === null) {
    return new Response('Request body is empty', { status: 400 });
  }

  try {
    const formData = await request.formData();
    const file = formData.get('file') as Blob;

    if (!file) {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
    }

    const validatedFile = FileSchema.safeParse({ file });

    if (!validatedFile.success) {
      const errorMessage = validatedFile.error.errors
        .map((error) => error.message)
        .join(', ');

      return NextResponse.json({ error: errorMessage }, { status: 400 });
    }

    // Get filename from formData since Blob doesn't have name property
    const filename = (formData.get('file') as File).name;
    const fileBuffer = await file.arrayBuffer();

    try {
      const data = await put(`graph-files/${filename}`, fileBuffer, {
        access: 'public',
      });
      
      // Transform the data to match the PutBlobResult model
      const graphPayload = {
        url: data.url,
        download_url: data.downloadUrl,  // snake_case to match Python model
        pathname: data.pathname,
        content_type: data.contentType,  // snake_case to match Python model
        content_disposition: data.contentDisposition  // snake_case to match Python model
      };
      
      const response = await axios.post(`${process.env.GRAPH_RAG_API_URL}/create_graph/`, graphPayload);
      console.log(response);
      return NextResponse.json(data);
    } catch (error) {
      return NextResponse.json({ error: 'Upload failed' }, { status: 500 });
    }
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 },
    );
  }
}

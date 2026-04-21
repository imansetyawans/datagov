import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const pathStr = path.join('/');
  const url = `${BACKEND_URL}/api/v1/${pathStr}${request.url.includes('?') ? '?' + request.url.split('?')[1] : ''}`;
  const response = await fetch(url, {
    headers: {
      'Authorization': request.headers.get('Authorization') || '',
      'Content-Type': 'application/json',
    },
  });
  const data = await response.json();
  return NextResponse.json(data);
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const pathStr = path.join('/');
  const body = await request.text();
  const url = `${BACKEND_URL}/api/v1/${pathStr}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': request.headers.get('Authorization') || '',
      'Content-Type': 'application/json',
    },
    body,
  });
  const data = await response.json();
  return NextResponse.json(data);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const pathStr = path.join('/');
  const url = `${BACKEND_URL}/api/v1/${pathStr}`;
  const response = await fetch(url, {
    method: 'DELETE',
    headers: {
      'Authorization': request.headers.get('Authorization') || '',
    },
  });
  const data = await response.json();
  return NextResponse.json(data);
}
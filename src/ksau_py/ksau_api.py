# SPDX-License-Identifier: Apache-2.0
#
# Copyright 2025 Global Index Source developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from aiohttp import ClientSession

KSAU_BASE_URL: str = "https://project.ksauraj.eu.org"
ENDPOINTS = {
    "upload": "/upload",
    "token": "/token"
}

@dataclass
class TokenResponse:
    access_token: str
    refresh_token: str
    expires_in: int
    client_id: str
    client_secret: str
    drive_id: str
    drive_type: str
    base_url: str
    upload_root_path: str

async def get_upload_token(remote: str) -> TokenResponse:
    """Get upload token from the API."""
    url = f"{KSAU_BASE_URL}{ENDPOINTS['token']}?remote={remote}"
    
    async with ClientSession() as session:
        async with session.get(url) as response:
            if not response.ok:
                error_text = await response.text()
                raise RuntimeError(f"Failed to get upload token: {error_text}")
            
            data = await response.json()
            return TokenResponse(**data)

async def create_upload_session(access_token: str, remote_file_path: str, upload_root_path: str) -> str:
    """Create an upload session for chunked file upload."""
    # Build the complete remote path using the provided upload_root_path
    clean_path = f"{upload_root_path.strip('/')}/{remote_file_path}"
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{clean_path}:/createUploadSession"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    async with ClientSession() as session:
        async with session.post(
            url,
            headers=headers,
            json={
                "item": {
                    "@microsoft.graph.conflictBehavior": "rename",
                }
            }
        ) as response:
            if not response.ok:
                error_text = await response.text()
                raise RuntimeError(f"Failed to create upload session: {error_text}")
            
            data = await response.json()
            return data["uploadUrl"]

async def upload_file_in_chunks(
    file_path: str,
    upload_url: str,
    chunk_size_mb: int = 5,
    on_progress: Optional[callable] = None
) -> None:
    """Upload file in chunks to the specified upload URL."""
    chunk_size = chunk_size_mb * 1024 * 1024
    file_size = Path(file_path).stat().st_size
    uploaded = 0
    
    async with ClientSession() as session:
        with open(file_path, "rb") as f:
            while uploaded < file_size:
                chunk_end = min(uploaded + chunk_size, file_size)
                content_range = f"bytes {uploaded}-{chunk_end-1}/{file_size}"
                
                # Read the chunk
                f.seek(uploaded)
                chunk = f.read(chunk_size)
                # Upload the chunk
                async with session.put(
                    upload_url,
                    headers={
                        "Content-Range": content_range,
                        "Content-Length": str(len(chunk))
                    },
                    data=chunk
                ) as response:
                    if not response.ok:
                        error_text = await response.text()
                        raise RuntimeError(f"Failed to upload chunk {content_range}, status: {response.status}, error: {error_text}")
                
                uploaded = chunk_end
                if on_progress:
                    progress = (uploaded / file_size) * 100
                    on_progress(round(progress))

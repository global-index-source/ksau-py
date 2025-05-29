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

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import aiofiles
from aiohttp import ClientSession, FormData

KSAU_BASE_URL: str = "https://project.ksauraj.eu.org"
ENDPOINTS = {
    "upload": "/upload", 
    "token": "/token",
    "system": "/system",
    "neofetch": "/neofetch", 
    "quota": "/quota"
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


@dataclass
class UploadResponse:
    status: str
    message: str
    download_url: str
    file_size: int
    file_name: str


@dataclass
class QuotaInfo:
    total: str
    used: str
    remaining: str
    deleted: str


async def get_upload_token(remote: str) -> TokenResponse:
    """Get upload token from the API."""
    url = f"{KSAU_BASE_URL}{ENDPOINTS['token']}?remote={remote}"

    async with ClientSession() as session, session.get(url) as response:
        if not response.ok:
            error_text = await response.text()
            msg = f"Failed to get upload token: {error_text}"
            raise RuntimeError(msg)

        data = await response.json()
        return TokenResponse(**data)


async def upload_file_api(
    file_path: str, 
    remote: str, 
    remote_folder: str = "", 
    chunk_size: int = 32,
    custom_filename: str = None
) -> UploadResponse:
    """Upload file using the project API."""
    url = f"{KSAU_BASE_URL}{ENDPOINTS['upload']}"
    
    file_path_obj = Path(file_path)
    filename = custom_filename if custom_filename else file_path_obj.name
    
    async with ClientSession() as session:
        # Create form data with file opened in context manager
        data = FormData()
        data.add_field('remote', remote)
        data.add_field('remoteFolder', remote_folder)
        data.add_field('chunkSize', str(chunk_size))
        
        with open(file_path, "rb") as fp:
            data.add_field("file", fp, filename=filename)
            
            async with session.post(url, data=data) as response:
                if not response.ok:
                    error_text = await response.text()
                    msg = f"Failed to upload file: {error_text}"
                    raise RuntimeError(msg)
                
                result = await response.json()
                return UploadResponse(
                    status=result['status'],
                    message=result['message'],
                    download_url=result['downloadURL'],
                    file_size=result['fileSize'],
                    file_name=result['fileName']
                )


async def upload_file_binary(
    file_path: str,
    remote: str, 
    remote_folder: str = "",
    chunk_size: int = 32,
    filename: str = None
) -> UploadResponse:
    """Upload file using binary upload method."""
    url = f"{KSAU_BASE_URL}{ENDPOINTS['upload']}"
    
    file_path_obj = Path(file_path)
    if filename is None:
        filename = file_path_obj.name
    
    headers = {
        'Content-Type': 'application/octet-stream',
        'X-Remote': remote,
        'X-Remote-Folder': remote_folder,
        'X-Filename': filename,
        'X-Chunk-Size': str(chunk_size)
    }
    
    async with ClientSession() as session:
        async with aiofiles.open(file_path, 'rb') as f:
            async with session.post(url, headers=headers, data=f) as response:
                if not response.ok:
                    error_text = await response.text()
                    msg = f"Failed to upload file: {error_text}"
                    raise RuntimeError(msg)
                
                result = await response.json()
                return UploadResponse(
                    status=result['status'],
                    message=result['message'],
                    download_url=result['downloadURL'],
                    file_size=result['fileSize'],
                    file_name=result['fileName']
                )


async def get_system_info() -> Dict[str, Any]:
    """Get system information from the API."""
    url = f"{KSAU_BASE_URL}{ENDPOINTS['system']}"
    
    async with ClientSession() as session, session.get(url) as response:
        if not response.ok:
            error_text = await response.text()
            msg = f"Failed to get system info: {error_text}"
            raise RuntimeError(msg)
        
        return await response.json()


async def get_neofetch_info() -> Dict[str, Any]:
    """Get neofetch-style information from the API."""
    url = f"{KSAU_BASE_URL}{ENDPOINTS['neofetch']}"
    
    async with ClientSession() as session, session.get(url) as response:
        if not response.ok:
            error_text = await response.text()
            msg = f"Failed to get neofetch info: {error_text}"
            raise RuntimeError(msg)
        
        return await response.json()


async def get_quota_info() -> Dict[str, QuotaInfo]:
    """Get storage quota information for all remotes."""
    url = f"{KSAU_BASE_URL}{ENDPOINTS['quota']}"
    
    async with ClientSession() as session, session.get(url) as response:
        if not response.ok:
            error_text = await response.text()
            msg = f"Failed to get quota info: {error_text}"
            raise RuntimeError(msg)
        
        result = await response.json()
        quota_data = {}
        
        for remote_name, data in result['data'].items():
            quota_data[remote_name] = QuotaInfo(
                total=data['total'],
                used=data['used'],
                remaining=data['remaining'],
                deleted=data['deleted']
            )
        
        return quota_data


async def create_upload_session(access_token: str, remote_file_path: str, upload_root_path: str) -> str:
    """Create an upload session for chunked file upload."""
    # Build the complete remote path using the provided upload_root_path
    clean_path = f"{upload_root_path.strip('/')}/{remote_file_path}"
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{clean_path}:/createUploadSession"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    async with (
        ClientSession() as session,
        session.post(
            url,
            headers=headers,
            json={
                "item": {
                    "@microsoft.graph.conflictBehavior": "replace",
                }
            },
        ) as response,
    ):
        if not response.ok:
            error_text = await response.text()
            msg = f"Failed to create upload session: {error_text}"
            raise RuntimeError(msg)

        data = await response.json()
        return data["uploadUrl"]

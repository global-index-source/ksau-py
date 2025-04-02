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

from aiohttp import ClientSession

KSAU_BASE_URL: str = "https://project.ksauraj.eu.org"
ENDPOINTS = {"upload": "/upload", "token": "/token"}


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

    async with ClientSession() as session, session.get(url) as response:
        if not response.ok:
            error_text = await response.text()
            msg = f"Failed to get upload token: {error_text}"
            raise RuntimeError(msg)

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

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


@dataclass
class RemoteCredentials:
    access_token: str
    refresh_token: str
    expires_in: int
    client_id: str
    client_secret: str
    drive_id: str
    drive_type: str
    base_url: str
    upload_root_path: str


async def get_remote_credentials(remote: str) -> RemoteCredentials:
    async with ClientSession() as session:
        resp = await session.get(f"{KSAU_BASE_URL}/token?remote={remote}")

        return RemoteCredentials(**await resp.json())

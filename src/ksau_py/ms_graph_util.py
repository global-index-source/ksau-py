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

from azure.identity.aio import ClientSecretCredential
from msgraph.graph_service_client import GraphServiceClient

from ksau_py import ksau_api


async def get_graph_client(remote: str) -> GraphServiceClient:
    credential: ksau_api.RemoteCredentials = await ksau_api.get_remote_credentials(remote)

    client_credential: ClientSecretCredential = ClientSecretCredential(
        credential.drive_id,
        credential.client_id,
        credential.client_secret,
    )

    return GraphServiceClient(client_credential)

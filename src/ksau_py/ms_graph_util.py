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

import datetime
from dataclasses import dataclass

from azure.core.credentials import AccessToken, TokenCredential
from msgraph.graph_service_client import GraphServiceClient

from ksau_py import ksau_api


class ExistingAccessToken(TokenCredential):
    def __init__(self, token: str, expires_in: int) -> None:
        self.token = token
        self.expires_in = expires_in

    def get_token(self, *_, **__) -> AccessToken:
        return AccessToken(self.token, int(datetime.datetime.now(datetime.timezone.utc).timestamp()) + self.expires_in)


@dataclass
class Client:
    graph_service_client: GraphServiceClient
    credential: ksau_api.RemoteCredentials


async def get_graph_client(remote: str) -> Client:
    credential: ksau_api.RemoteCredentials = await ksau_api.get_remote_credentials(remote)
    return Client(
        graph_service_client=GraphServiceClient(ExistingAccessToken(credential.access_token, credential.expires_in)),
        credential=credential,
    )

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

import sys
from asyncio import Semaphore, TaskGroup
from typing import TYPE_CHECKING, cast

from aiohttp import ClientSession
from anyio import Path
from msgraph.generated.drives.item.items.item.create_upload_session.create_upload_session_post_request_body import (
    CreateUploadSessionPostRequestBody,
)
from msgraph.generated.models.drive_item_uploadable_properties import DriveItemUploadableProperties
from msgraph.generated.models.upload_session import UploadSession
from rich import print  # noqa: A004

from ksau_py import REMOTES, app, console, event_loop
from ksau_py.ms_graph_util import Client, get_graph_client

if TYPE_CHECKING:
    from msgraph.generated.drives.item.drive_item_request_builder import DriveItemRequestBuilder


@app.command("upload", short_help="Upload file to a remote")
def upload(file: str, folder: str, remote: str | None = None) -> int:
    if remote not in REMOTES:
        print(f"[bold red]Remote [bold white]'{remote}'[/bold white] does not exist![/bold red]")
        sys.exit(1)

    print(f"[bold cyan]Uploading to remote [bold white]'{remote}'[/bold white]...[/bold cyan]")

    exit_code: int = event_loop.run_until_complete(upload_async(file, folder, remote))

    sys.exit(exit_code)


async def create_upload_session(client: Client, folder: str) -> UploadSession:
    drive: DriveItemRequestBuilder = client.graph_service_client.drives.by_drive_id(client.credential.drive_id)

    upload_item: DriveItemUploadableProperties = DriveItemUploadableProperties(
        additional_data={"@microsoft.graph.conflictBehavior": "rename"}
    )
    upload_session_body: CreateUploadSessionPostRequestBody = CreateUploadSessionPostRequestBody(item=upload_item)

    upload_session: UploadSession | None = await drive.items.by_drive_item_id(
        f"root:{folder}"
    ).create_upload_session.post(upload_session_body)
    if upload_session:
        return upload_session

    msg = "failed to create upload session"
    raise RuntimeError(msg)


async def upload_async(file_path: str, folder: str, remote: str) -> int:
    file: Path = Path(file_path)
    if not await file.exists():
        console.print(f"[bold red] file [bold white]'{file_path}'[/bold white] does not exist![/bold red]")
        return 1

    if not await file.is_file():
        console.print(f"[bold red][bold white]'{file_path}'[/bold white] is not a file![/bold red]")
        return 1

    client: Client = await get_graph_client(remote)

    upload_session: UploadSession = await create_upload_session(client, folder)

    async with await file.open("rb") as f, TaskGroup() as tg, ClientSession() as session:
        semaphore: Semaphore = Semaphore(2)

        while chunk := await f.read(327680):
            tg.create_task(upload_chunk(chunk, semaphore, upload_session, session))

    return 0


async def upload_chunk(
    chunk: bytes,
    semaphore: Semaphore,
    upload_session: UploadSession,
    session: ClientSession,
) -> None:
    async with semaphore:
        upload_url = cast(str, upload_session.upload_url)
        print(f"{upload_url=}")
        session.put(upload_url, data=chunk)

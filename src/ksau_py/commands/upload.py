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
from asyncio import Semaphore, TaskGroup, wait

from anyio import Path
from msgraph.graph_service_client import GraphServiceClient
from rich import print  # noqa: A004
from rich.console import Console

from ksau_py import REMOTES, app, console, event_loop
from ksau_py.ms_graph_util import get_graph_client


@app.command("upload", short_help="Upload file to a remote")
def upload(file: str, folder: str, remote: str | None = None) -> int:
    if remote not in REMOTES:
        print(f"[bold red]Remote [bold white]'{remote}'[/bold white] does not exist![/bold red]")
        sys.exit(1)

    print(f"[bold cyan]Uploading to remote [bold white]'{remote}'[/bold white]...[/bold cyan]")

    exit_code: int = event_loop.run_until_complete(upload_async(file, folder, remote))

    sys.exit(exit_code)


async def upload_async(file_path: str, folder: str, remote: str) -> int:
    file: Path = Path(file_path)
    if not await file.exists():
        console.print(f"[bold red] file [bold white]'{file_path}'[/bold white] does not exist![/bold red]")
        return 1

    if not await file.is_file():
        console.print(f"[bold red][bold white]'{file_path}'[/bold white] is not a file![/bold red]")
        return 1

    client: GraphServiceClient = await get_graph_client(remote)

    drive = await client.me.drive.get()
    console.print(drive.items)

    async with await file.open("rb") as f, TaskGroup() as tg:
        semaphore: Semaphore = Semaphore(5)

        while chunk := await f.read(327680):
            tg.create_task(upload_chunk(chunk, semaphore))

    return 0


async def upload_chunk(chunk: bytes, semaphore: Semaphore) -> None:
    pass

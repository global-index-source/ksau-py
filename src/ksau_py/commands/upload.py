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

import base64
from asyncio import Task, wait
from collections.abc import Callable
from pathlib import Path

import click
from aiohttp import ClientSession
from anyio import open_file
from quickxorhash import quickxorhash
from rich.progress import Progress

from ksau_py import REMOTES, app, console, coro
from ksau_py.ksau_api import create_upload_session, get_upload_token

progress: Progress = Progress(console=console)


@app.command("upload")
@click.argument("remote_path", type=str)
@click.argument("remote", type=click.Choice(REMOTES))
@click.argument("files", nargs=-1, type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option("-c", "--chunk-size", type=int, default=5, is_flag=True)
@coro
async def upload(remote_path: str, remote: str, files: list[str], chunk_size: int = 5) -> None:
    """Upload a file to remote storage.

    Arguments:
        remote_path(str): Destination path in remote storage
        remote(str): Remote storage to use (oned, hakimidrive, or saurajcf)
        files(list[str]): List of files to be uploaded.
        chunk_size(int): Upload chunk size in MB (default: 5)
    """
    progress.start()
    tasks: list[Task] = [Task(upload_handler(remote_path, remote, file, chunk_size)) for file in files]
    await wait(tasks)


async def upload_handler(remote_path: str, remote: str, file_path: str, chunk_size: int = 5) -> None:
    """Upload a file to remote storage.

    Arguments:
        remote_path(str): Destination path in remote storage
        remote(str): Remote storage to use (oned, hakimidrive, or saurajcf)
        file_path(str): Path to file to be uploaded
        chunk_size(int): Upload chunk size in MB (default: 5)
    """
    try:
        token = await get_upload_token(remote)
        local_file = Path(file_path)
        remote_dir = remote_path.strip("/")
        new_name = f"{local_file.stem}{local_file.suffix}"

        # If remote path is given, append it to the upload root path
        final_remote_path = f"{remote_dir}/{new_name}" if remote_dir else new_name

        upload_url = await create_upload_session(token.access_token, final_remote_path, token.upload_root_path)

        upload_task = progress.add_task("[cyan]Uploading...", total=100)
        quickxor_task = progress.add_task("[cyan]Computing QuickXorHash...", total=Path(file_path).stat().st_size)

        def update_quickxor_task(value: int) -> None:
            progress.update(quickxor_task, completed=value)

        def update_upload_progress(value: int) -> None:
            progress.update(upload_task, completed=value)

        local_hash = await compute_local_quickxorhash(Path(file_path), update_quickxor_task)
        console.print(f"[cyan]Local file QuickXorHash: [/cyan][bold green]{local_hash}[/bold green]")

        # Upload file
        quickxor_upload = await upload_file_in_chunks(file_path, upload_url, chunk_size, update_upload_progress)

        # Calculate and display download info
        base_url = token.base_url.rstrip("/")
        download_path = f"{final_remote_path}"
        download_url = f"{base_url}/{download_path}"

        console.print("\n[green]✓ Upload completed successfully![/green]")
        console.print(f"[cyan]✓ QuickXorHash: [/cyan][bold]{quickxor_upload}[/bold]")
        console.print("\n[bold]Download Information:[/bold]")
        console.print(f"[yellow]URL:[/yellow] {download_url}")

    except (KeyboardInterrupt, SystemExit) as e:
        console.print("[red]Error: aborted by user[/red]")
        raise click.Abort from e

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort from e


async def compute_local_quickxorhash(file: Path, update_progress: Callable) -> bytes:
    hash_ = quickxorhash()
    computed: int = 0

    async with await open_file(file.as_posix(), "rb") as f:
        while chunk := await f.read(320 * 1024):
            hash_.update(chunk)
            computed += len(chunk)

            update_progress(computed)

    return base64.b64encode(hash_.digest())


async def upload_file_in_chunks(
    file_path: str, upload_url: str, chunk_size_mb: int = 5, on_progress: Callable | None = None
) -> bytes:
    """Upload file in chunks to the specified upload URL."""
    chunk_size = chunk_size_mb * 1024 * 1024
    file_size = Path(file_path).stat().st_size
    uploaded = 0
    hash_ = quickxorhash()

    async with ClientSession() as session, await open_file(file_path, "rb") as f:
        while chunk := await f.read(chunk_size):
            chunk_end = min(uploaded + chunk_size, file_size)
            content_range = f"bytes {uploaded}-{chunk_end - 1}/{file_size}"

            # Upload the chunk
            async with session.put(
                upload_url, headers={"Content-Range": content_range, "Content-Length": str(len(chunk))}, data=chunk
            ) as response:
                if not response.ok:
                    error_text = await response.text()
                    msg = f"Failed to upload chunk {content_range}, status: {response.status}, error: {error_text}"
                    raise click.Abort(msg)
                hash_.update(chunk)

                uploaded = chunk_end
                if on_progress:
                    progress = (uploaded / file_size) * 100
                    on_progress(round(progress))

    return base64.b64encode(hash_.digest())

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

from collections.abc import Callable
from pathlib import Path

import click
from aiohttp import ClientSession
from anyio import open_file
from rich.progress import Progress

from ksau_py import REMOTES, app, console, coro
from ksau_py.ksau_api import create_upload_session, get_upload_token


@app.command("upload")
@click.argument("file_path", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument("remote_path", type=str)
@click.argument("remote", type=click.Choice(REMOTES))
@click.argument("chunk_size", type=int, default=5)
@coro
async def upload(file_path: str, remote_path: str, remote: str, chunk_size: int = 5) -> None:
    """Upload a file to remote storage.

    Arguments:
        file_path(str): Path to the local file to upload
        remote_path(str): Destination path in remote storage
        remote(str): Remote storage to use (oned, hakimidrive, or saurajcf)
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

        # Setup progress bar
        with Progress() as progress:
            task = progress.add_task("[cyan]Uploading...", total=100)

            def update_progress(value: int) -> None:
                progress.update(task, completed=value)

            # Upload file
            await upload_file_in_chunks(file_path, upload_url, chunk_size, update_progress)

        # Calculate and display download info
        base_url = token.base_url.rstrip("/")
        download_path = f"{final_remote_path}"
        download_url = f"{base_url}/{download_path}"

        console.print("\n[green]✓ Upload completed successfully![/green]")
        console.print("\n[bold]Download Information:[/bold]")
        console.print(f"[yellow]URL:[/yellow] {download_url}")

    except (KeyboardInterrupt, SystemExit) as e:
        console.print("[red]Error: aborted by user[/red]")
        raise click.Abort from e

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort from e


async def upload_file_in_chunks(
    file_path: str, upload_url: str, chunk_size_mb: int = 5, on_progress: Callable | None = None
) -> None:
    """Upload file in chunks to the specified upload URL."""
    chunk_size = chunk_size_mb * 1024 * 1024
    file_size = Path(file_path).stat().st_size
    uploaded = 0

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

                uploaded = chunk_end
                if on_progress:
                    progress = (uploaded / file_size) * 100
                    on_progress(round(progress))

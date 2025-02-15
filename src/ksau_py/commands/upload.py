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
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress
from rich import print as rprint

from ksau_py import app, coro
from ksau_py.ksau_api import get_upload_token, create_upload_session, upload_file_in_chunks

console = Console()
VALID_REMOTES = ["oned", "hakimidrive", "saurajcf"]

@app.command("upload")
@click.argument("file_path", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument("remote_path", type=str)
@click.argument("remote", type=click.Choice(VALID_REMOTES))
@click.argument("chunk_size", type=int, default=5)
@coro
async def upload(file_path: str, remote_path: str, remote: str, chunk_size: int) -> None:
    """Upload a file to remote storage.
    
    Arguments:
        FILE_PATH: Path to the local file to upload
        REMOTE_PATH: Destination path in remote storage
        REMOTE: Remote storage to use (oned, hakimidrive, or saurajcf)
        CHUNK_SIZE: Upload chunk size in MB (default: 5)
    """
    try:
        file_stats = Path(file_path).stat()
        token = await get_upload_token(remote)
        local_file = Path(file_path)
        remote_dir = remote_path.strip('/')
        new_name = f"{local_file.stem}{local_file.suffix}"
        
        # If remote path is given, append it to the upload root path
        if remote_dir:
            final_remote_path = f"{remote_dir}/{new_name}"
        else:
            final_remote_path = new_name
        
        upload_url = await create_upload_session(
            token.access_token,
            final_remote_path,
            token.upload_root_path
        )
        
        # Setup progress bar
        with Progress() as progress:
            task = progress.add_task("[cyan]Uploading...", total=100)
            
            def update_progress(value: int):
                progress.update(task, completed=value)
            
            # Upload file
            await upload_file_in_chunks(
                file_path,
                upload_url,
                chunk_size,
                update_progress
            )
        
        # Calculate and display download info
        base_url = token.base_url.rstrip("/")
        download_path = f"{final_remote_path}"
        download_url = f"{base_url}/{download_path}"
        
        rprint("\n[green]✓ Upload completed successfully![/green]")
        rprint("\n[bold]Download Information:[/bold]")
        rprint(f"[yellow]URL:[/yellow] {download_url}")
        
    except Exception as e:
        rprint(f"[red]Error: {str(e)}[/red]")
        raise click.Abort()

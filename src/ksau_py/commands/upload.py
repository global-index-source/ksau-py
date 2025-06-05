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

import hashlib
import secrets
import random
import string
import time
from pathlib import Path

import click
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from ksau_py import REMOTES, app, console, coro
from ksau_py.ksau_api import upload_file_api, get_quota_info


def add_random_string(filename: str) -> str:
    """Generate new filename with random strings at last (before extension if present).
    new name for 'myfile.txt' -> 'myfile-78e11b8c.txt'
    new name for 'myfile' -> 'myfile-78e11b8c'
    """
    file_path = Path(filename)
    extension = file_path.suffix
    name = file_path.stem
    # 8-hex-char cryptographically-strong random suffix
    random_string = secrets.token_hex(4)
    
    if extension:
        return f"{name}-{random_string}{extension}"
    else:
        return f"{name}-{random_string}"


def select_remote_random() -> str:
    """Select remote randomly."""
    if not REMOTES:
        raise click.ClickException("No remotes configured. Cannot upload.")
    return random.choice(REMOTES)


async def select_remote_most_free() -> str:
    """Select remote with most free space."""
    try:
        quota_info = await get_quota_info()
        max_remaining = 0
        best_remote = REMOTES[0]
        
        for remote_name, quota in quota_info.items():
            # Parse remaining space (assuming format like "1.5 TB")
            qty, unit = quota.remaining.replace(',', '').split()[:2]
            factor = {"B":1, "KB":2**10, "MB":2**20, "GB":2**30, "TB":2**40}.get(unit.upper(), 1)
            remaining_val = float(qty) * factor
            try:
                remaining_val = float(remaining_str)
                if remaining_val > max_remaining:
                    max_remaining = remaining_val
                    best_remote = remote_name
            except ValueError:
                continue
        
        return best_remote
    except Exception:
        console.print("[yellow]Warning: Could not check free space. Using random remote.[/yellow]")
        return select_remote_random()


@app.command("upload")
@click.argument("files", nargs=-1, type=click.Path(exists=True, dir_okay=False, resolve_path=True), required=True)
@click.argument("folder", default="", type=str)
@click.option("-r", "--add-random", is_flag=True, help="Add random string to filename")
@click.option("-q", "--quiet", is_flag=True, help="Suppress output, only print download link")
@click.option("-c", "--remote", type=click.Choice(REMOTES), help="Upload to specific remote")
@click.option("--chunk-size", type=click.IntRange(2, 32), default=32, help="Chunk size in MB (2-32)")
@coro
async def upload(
    files: list[str], 
    folder: str, 
    add_random: bool = False, 
    quiet: bool = False,
    remote: str = None,
    chunk_size: int = 32
) -> None:
    """Upload files to remote storage.

    Arguments:
        files: Paths to files to be uploaded
        folder: Destination folder in remote storage (optional)
    """
    try:
        if not files:
            if not quiet:
                console.print("[red]No files specified for upload[/red]")
            raise click.Abort
            
        results = []
        total_files = len(files)
        
        for i, file in enumerate(files, 1):
            file_path = Path(file)
            original_filename = file_path.name
            
            # Generate new filename if random string option is enabled
            if add_random:
                upload_filename = add_random_string(original_filename)
            else:
                upload_filename = original_filename
            
            # Select remote for each file
            if remote:
                selected_remote = remote
                if not quiet and total_files > 1:
                    console.print(f"[{i}/{total_files}] Using requested remote: [green]{selected_remote}[/green]")
            else:
                file_size = file_path.stat().st_size
                if file_size < 100 * 1024 * 1024:  # < 100MB
                    selected_remote = select_remote_random()
                    if not quiet and total_files > 1:
                        console.print(f"[{i}/{total_files}] File size is <100MB, selecting random remote: [green]{selected_remote}[/green]")
                else:
                    selected_remote = await select_remote_most_free()
                    if not quiet and total_files > 1:
                        console.print(f"[{i}/{total_files}] Using remote with most free space: [green]{selected_remote}[/green]")
            
            if not quiet:
                if total_files > 1:
                    console.print(f"[{i}/{total_files}] Initializing upload process for {original_filename}...")
                else:
                    console.print("Initializing upload process...")
                
                # Create progress bar
                progress = Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    console=console,
                )
                
                with progress:
                    task = progress.add_task(f"Uploading {original_filename}...", total=100)
                    
                    # Upload file using the API
                    result = await upload_file_api(
                        file_path=str(file_path),
                        remote=selected_remote,
                        remote_folder=folder,
                        chunk_size=chunk_size,
                        custom_filename=upload_filename if add_random else None
                    )
                    
                    progress.update(task, completed=100)
            else:
                # Quiet mode - just upload without progress
                result = await upload_file_api(
                    file_path=str(file_path),
                    remote=selected_remote,
                    remote_folder=folder,
                    chunk_size=chunk_size,
                    custom_filename=upload_filename if add_random else None
                )
            
            results.append(result)
            
            if quiet:
                # Only print the download URL in quiet mode
                print(result.download_url)
            else:
                console.print(f"\n[green]✓ Upload completed successfully![/green]")
                console.print(f"[cyan]File:[/cyan] {result.file_name}")
                console.print(f"[cyan]Size:[/cyan] {result.file_size:,} bytes")
                console.print(f"[yellow]Download link:[/yellow] [link]{result.download_url}[/link]")
                if total_files > 1 and i < total_files:
                    console.print()  # Add spacing between multiple files
        
        if not quiet and total_files > 1:
            console.print(f"\n[green]✓ All {total_files} files uploaded successfully![/green]")

    except (KeyboardInterrupt, SystemExit) as e:
        if not quiet:
            console.print("[red]Upload aborted by user[/red]")
        raise click.Abort from e
    except Exception as e:
        if not quiet:
            console.print(f"[red]Upload failed: {e}[/red]")
        else:
            print(f"Error: {e}")
        raise click.Abort from e

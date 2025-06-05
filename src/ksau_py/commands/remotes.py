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

import aiohttp
from rich.table import Table

from ksau_py import REMOTES, app, console, coro
from ksau_py.ksau_api import get_quota_info


@app.command("list", short_help="List available remotes with usage information")
@coro
async def list_remotes() -> None:
    """List available remotes and show their storage usage information."""
    try:
        console.print("[bold cyan]Available remotes and their usage:[/bold cyan]\n")
        
        quota_info = await get_quota_info()
        
        # Create a table for better formatting
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Remote", style="cyan", width=20)
        table.add_column("Total", style="green", width=15)
        table.add_column("Used", style="yellow", width=15)
        table.add_column("Remaining", style="blue", width=15)
        table.add_column("Deleted", style="red", width=15)
        
        for remote_name in REMOTES:
            if remote_name in quota_info:
                quota = quota_info[remote_name]
                table.add_row(
                    remote_name,
                    quota.total,
                    quota.used,
                    quota.remaining,
                    quota.deleted
                )
            else:
                table.add_row(
                    remote_name,
                    "N/A",
                    "N/A", 
                    "N/A",
                    "N/A"
                )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error fetching quota information: {e}[/red]")
        console.print("[cyan]Available remotes:[/cyan]", REMOTES)


@app.command("list-remotes", short_help="Simple list of available remotes", hidden=True)
def simple_list_remotes() -> None:
    """Simple list of available remotes (legacy command)."""
    console.print("[bold cyan]Available remotes:[/bold cyan]", REMOTES)

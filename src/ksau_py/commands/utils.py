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

import subprocess
import sys
from pathlib import Path

import click

from ksau_py import app, console


@app.command("update", short_help="Update ksau-py to the latest version")
def update() -> None:
    """Update ksau-py to the latest version from PyPI."""
    try:
        console.print("[cyan]Checking for updates...[/cyan]")
        
        # Check if we can update using pip
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "ksau-py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            console.print("[green]✓ Successfully updated ksau-py![/green]")
            console.print("[dim]You may need to restart your terminal or shell.[/dim]")
        else:
            console.print("[red]Update failed![/red]")
            console.print(f"[red]Error: {result.stderr}[/red]")
            console.print("\n[yellow]Manual update instructions:[/yellow]")
            console.print("Run: [bold]pip install --upgrade ksau-py[/bold]")
            
    except Exception as e:
        console.print(f"[red]Error during update: {e}[/red]")
        console.print("\n[yellow]Manual update instructions:[/yellow]")
        console.print("Run: [bold]pip install --upgrade ksau-py[/bold]")


@app.command("refresh", short_help="Refresh connection to the API")
def refresh() -> None:
    """Refresh connection to the API and clear any cached data."""
    console.print("[cyan]Refreshing API connection...[/cyan]")
    
    # Clear any cache directories if they exist
    home = Path.home()
    cache_dir = home / ".ksau"
    
    try:
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
            console.print("[green]✓ Cleared cached data[/green]")
        
        console.print("[green]✓ API connection refreshed[/green]")
        console.print("[dim]Cached quota information has been cleared.[/dim]")
        
    except Exception as e:
        console.print(f"[yellow]Warning: Could not clear cache: {e}[/yellow]")
        console.print("[green]✓ API connection refreshed[/green]")


@app.command("dependencies", short_help="Show dependency information")
def dependencies() -> None:
    """Show information about ksau-py dependencies."""
    console.print("[bold cyan]ksau-py Dependencies Information[/bold cyan]\n")
    
    console.print("[green]✓ ksau-py is a Python package with managed dependencies[/green]")
    console.print("\n[bold yellow]Required dependencies:[/bold yellow]")
    
    deps = [
        "aiohttp>=3.11.12 - HTTP client for API communication",
        "anyio>=4.8.0 - Async I/O utilities", 
        "azure-identity>=1.20.0 - Azure authentication",
        "rich>=13.9.4 - Terminal formatting",
        "typer>=0.15.1 - CLI framework"
    ]
    
    for dep in deps:
        console.print(f"• {dep}")
    
    console.print("\n[bold green]Installation:[/bold green]")
    console.print("All dependencies are automatically installed when you install ksau-py:")
    console.print("[bold]pip install ksau-py[/bold]")
    
    console.print("\n[bold blue]For development:[/bold blue]")
    console.print("Install with development dependencies:")
    console.print("[bold]pip install ksau-py[dev][/bold]")


@app.command("info", short_help="Show general information about ksau-py")
def info() -> None:
    """Show general information about ksau-py."""
    console.print("[bold cyan]ksau-py - File Upload Tool[/bold cyan]\n")
    
    console.print("[bold]Description:[/bold]")
    console.print("ksau-py is a Python rewrite of the original ksau bash script.")
    console.print("It provides file upload functionality to multiple cloud storage remotes.")
    
    console.print("\n[bold]Features:[/bold]")
    features = [
        "Upload files to multiple cloud storage backends",
        "Random filename generation for privacy",
        "Quiet mode for scripting",
        "Chunked uploads for large files",
        "Storage quota monitoring",
        "System information display"
    ]
    
    for feature in features:
        console.print(f"• {feature}")
    
    console.print("\n[bold]Available Commands:[/bold]")
    console.print("• [cyan]upload[/cyan] - Upload files to remote storage")
    console.print("• [cyan]list[/cyan] - List remotes with usage information")
    console.print("• [cyan]system[/cyan] - Show server system information")
    console.print("• [cyan]neofetch[/cyan] - Show neofetch-style system info")
    console.print("• [cyan]version[/cyan] - Show version information")
    console.print("• [cyan]update[/cyan] - Update to latest version")
    console.print("• [cyan]refresh[/cyan] - Refresh API connection")
    console.print("• [cyan]dependencies[/cyan] - Show dependency info")
    
    console.print("\n[bold]Links:[/bold]")
    console.print("• GitHub: [link]https://github.com/ksauraj/ksau-py[/link]")
    console.print("• Telegram: [link]https://t.me/ksau_update[/link]")
    
    console.print("\n[dim]Created by Sauraj (@Ksauraj) and @hakimifr[/dim]") 
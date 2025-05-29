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

from rich.table import Table
from rich.panel import Panel

from ksau_py import app, console, coro
from ksau_py.ksau_api import get_system_info, get_neofetch_info


@app.command("system", short_help="Show system information")
@coro
async def system() -> None:
    """Show system information from the server."""
    try:
        data = await get_system_info()
        
        if data.get('status') == 'success':
            system_data = data.get('data', {})
            
            # Create main info table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Component", style="cyan", width=20)
            table.add_column("Information", style="green")
            
            # System information
            system_info = system_data['system']
            table.add_row("Hostname", system_info['hostname'])
            table.add_row("OS", system_info['os'])
            table.add_row("Platform", system_info['platform'])
            table.add_row("Kernel", system_info['kernel'])
            table.add_row("Architecture", system_info['architecture'])
            table.add_row("Uptime", f"{system_info['uptime']} seconds")
            table.add_row("Server Time", system_info['server_time'])
            
            # CPU information
            cpu_info = system_data['cpu']
            table.add_row("CPU Model", cpu_info['model'])
            table.add_row("CPU Cores", str(cpu_info['cores']))
            table.add_row("CPU Usage", f"{cpu_info['usage']:.2f}%")
            
            # Memory information
            memory_info = system_data['memory']
            table.add_row("Memory Total", f"{memory_info['total']:,} bytes")
            table.add_row("Memory Used", f"{memory_info['used']:,} bytes")
            table.add_row("Memory Free", f"{memory_info['free']:,} bytes")
            table.add_row("Memory Usage", f"{memory_info['used_percent']:.2f}%")
            
            console.print(Panel(table, title="[bold blue]System Information[/bold blue]"))
            
        else:
            console.print("[red]Failed to retrieve system information[/red]")
            
    except aiohttp.ClientError as e:
        console.print(f"[red]Network error: {e}[/red]")
    except KeyError as e:
        console.print(f"[red]Unexpected response format: missing {e}[/red]")


@app.command("neofetch", short_help="Show neofetch-style system information")
@coro
async def neofetch() -> None:
    """Show neofetch-style system information from the server."""
    try:
        data = await get_neofetch_info()
        
        if data['status'] == 'success':
            neofetch_data = data['data']
            
            # Display ASCII art and system info side by side
            ascii_art = neofetch_data.get('ascii_art', '')
            system_info = neofetch_data.get('system', {})
            performance = neofetch_data.get('performance', {})
            
            # Safely get primary color with validation
            primary_color = neofetch_data.get("colors", {}).get("primary", "white")
            # Validate color string to prevent markup errors
            if not primary_color or not isinstance(primary_color, str) or '[' in primary_color or ']' in primary_color:
                primary_color = "white"
            
            # Create the neofetch display
            console.print(f"[{primary_color}]{ascii_art}[/{primary_color}]")
            console.print(f"\n[bold]{system_info.get('user', 'unknown')}@{system_info.get('hostname', 'unknown')}[/bold]")
            console.print("-" * 40)
            console.print(f"[cyan]OS:[/cyan] {system_info.get('distro', 'Unknown')}")
            console.print(f"[cyan]Kernel:[/cyan] {system_info.get('kernel', 'Unknown')}")
            console.print(f"[cyan]Uptime:[/cyan] {system_info.get('uptime', 'Unknown')}")
            console.print(f"[cyan]Shell:[/cyan] {system_info.get('shell', 'Unknown')}")
            console.print(f"[cyan]CPU:[/cyan] {system_info.get('cpu', 'Unknown')}")
            console.print(f"[cyan]Memory:[/cyan] {system_info.get('memory', 'Unknown')}")
            console.print(f"[cyan]Disk Usage:[/cyan] {system_info.get('disk_usage', 'Unknown')}")
            console.print(f"[cyan]Local IP:[/cyan] {system_info.get('local_ip', 'Unknown')}")
            console.print(f"[cyan]Server Time:[/cyan] {system_info.get('server_time', 'Unknown')}")
            
            # Performance metrics
            console.print(f"\n[bold yellow]Performance Metrics:[/bold yellow]")
            console.print(f"[cyan]CPU Usage:[/cyan] {performance.get('cpu_usage', 0):.2f}%")
            console.print(f"[cyan]Memory Usage:[/cyan] {performance.get('memory_usage', 0):.2f}%")
            console.print(f"[cyan]CPU Frequency:[/cyan] {performance.get('cpu_frequency', 0):.2f} MHz")
            
            load_avg = system_info.get('load_average', [0.0, 0.0, 0.0])
            if isinstance(load_avg, list) and len(load_avg) >= 3:
                console.print(f"[cyan]Load Average:[/cyan] {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
            else:
                console.print(f"[cyan]Load Average:[/cyan] N/A")
            
        else:
            console.print("[red]Failed to retrieve neofetch information[/red]")
            
    except Exception as e:
        console.print(f"[red]Error fetching neofetch information: {e}[/red]") 
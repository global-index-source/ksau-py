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
import functools
from collections.abc import Callable
from typing import Any

from rich.console import Console
from typer import Typer

REMOTES: list[str] = [
    "hakimionedrive",
    "saurajcf",
    "oned",
]

# Create app with custom help
app = Typer(
    name="ksau-py",
    help="""
    ksau-py - Fast Cloud File Upload Tool
    
    A Python rewrite of the original ksau bash script for uploading files 
    to multiple cloud storage backends.
    
    Features:
    • Upload to multiple cloud storage remotes
    • Random filename generation for privacy (-r)
    • Quiet mode for scripting (-q)
    • Specific remote selection (-c)
    • Storage quota monitoring
    • System information display
    
    Examples:
      ksau-py upload myfile.txt Public
      ksau-py upload -r myfile.txt Public  
      ksau-py upload -q myfile.txt Public
      ksau-py list
    
    Support: https://t.me/ksau_update
    Created by Sauraj (@Ksauraj) and @hakimifr
    """,
    add_completion=False,
    rich_markup_mode="rich"
)

console: Console = Console()


def coro(f: Callable) -> Callable:
    """Decorator to run async functions in click/typer commands."""

    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        return asyncio.run(f(*args, **kwargs))

    return wrapper

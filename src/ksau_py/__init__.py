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
from typing import Any, Callable

import click
from typer import Typer

REMOTES: list[str] = [
    "hakimionedrive",
    "saurajcf",
    "oned",
]

app = Typer(name="ksau-py")

def coro(f: Callable) -> Callable:
    """Decorator to run async functions in click/typer commands."""
    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(f(*args, **kwargs))
    return wrapper

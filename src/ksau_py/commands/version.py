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

from ksau_py import app, console

# Version information
KSAU_PY_VERSION = "1.0.0"
KSAU_PY_VERSION_STRING = f"ksau-py Version {KSAU_PY_VERSION}"


@app.command("version", short_help="Show ksau-py version")
def version() -> None:
    """Show the current version of ksau-py."""
    console.print(f"[orange1]{KSAU_PY_VERSION_STRING}[/orange1]")
    console.print("[dim]Python rewrite of the original ksau tool[/dim]")
    console.print("[dim]Tool by Sauraj (@Ksauraj) and @hakimifr[/dim]") 
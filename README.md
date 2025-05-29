# ksau-py

A Python rewrite of the original ksau bash script for fast cloud file uploads.

## Features

- Upload files to multiple cloud storage remotes (hakimionedrive, oned, saurajcf)
- Random filename generation for privacy (`-r` option)
- Quiet mode for scripting (`-q` option)
- Specific remote selection (`-c` option)
- Storage quota monitoring
- Server system information display
- Chunked uploads for large files (2-32MB chunks)

## Installation

```bash
pip install ksau-py
```

## Usage

### Basic Upload

```bash
# Upload to Public folder
ksau-py upload myfile.txt Public

# Upload with random filename
ksau-py upload -r myfile.txt Public

# Upload quietly (only show download link)
ksau-py upload -q myfile.txt Public

# Upload to specific remote
ksau-py upload -c oned myfile.txt Public
```

### Other Commands

```bash
# List remotes with usage info
ksau-py list

# Show system information
ksau-py system

# Show version
ksau-py version

# Get help
ksau-py --help
```

## Available Remotes

- `hakimionedrive` - OneDrive storage
- `oned` - Primary OneDrive remote
- `saurajcf` - CloudFlare storage

Files <100MB use random remotes for load balancing. Larger files automatically select the remote with most free space.

## Upload Options

| Option             | Description                               |
| ------------------ | ----------------------------------------- |
| `-r, --add-random` | Add random string to filename             |
| `-q, --quiet`      | Suppress output, only print download link |
| `-c, --remote`     | Upload to specific remote                 |
| `--chunk-size`     | Chunk size in MB (2-32, default: 32)      |

## API Integration

Uses the API at `https://project.ksauraj.eu.org` for all operations:

- File upload via `/upload` endpoint
- Storage quota via `/quota` endpoint
- System info via `/system` and `/neofetch` endpoints

## Limits

- Maximum file size: 5GB
- Chunk size range: 2-32MB

## Development

```bash
git clone https://github.com/ksauraj/ksau-py
cd ksau-py
pip install -e .
```

## Links

- **GitHub**: https://github.com/ksauraj/ksau-py
- **Telegram**: https://t.me/ksau_update
- **Original ksau**: https://github.com/ksauraj/global_index_source

## License

Apache-2.0 License

---

_Created by Sauraj (@Ksauraj), @hakimifr, and Pratham (@prathamdby)_

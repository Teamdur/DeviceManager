# DeviceManager

## Development Setup

### Prerequisites

#### Mise installation

The latest mise installation can be found at [the official mise website](https://mise.jdx.dev/getting-started.html)

For short version, you can run the following commands:

```bash
$ curl https://mise.run | sh
$ echo 'export PATH="$HOME/.mise/bin:$PATH"' >> ~/.bashrc; echo 'export PATH="$HOME/.mise/bin:$PATH"' >> ~/.zshrc
```

Restart your terminal

* Restart Bash
```bash
$ exec bash
```
* Restart Zsh
```bash
$ exec zsh
```

Verify the installation by running the following command:
```bash
$ mise version
2024.4.5 linux-arm64 (d60d850 2024-04-15)
```

#### System dependencies

* Debian/Ubuntu

```bash
sudo apt install build-essential gdb lcov pkg-config \
      libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
      libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
      lzma lzma-dev tk-dev uuid-dev zlib1g-dev libmariadb-dev
```

Up-to-date dependencies can be found at [python developer's guide](https://devguide.python.org/getting-started/setup-building/index.html#install-dependencies)

### Setting up the project

1. Clone the repository

```bash
$ git clone https://github.com/Teamdur/DeviceManager.git
```

2. Change directory to the project

```bash
$ cd DeviceManager
```

3. Initialize mise

```bash
$ mise trust
$ mise settings set experimental true
$ mise install
```

4. Run setup task

```bash
$ mise run setup-dev
```

5. Run the development server

```bash
$ mise run dev
```

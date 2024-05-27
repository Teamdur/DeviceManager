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

## Production setup

### App environment variables

The following environment variables are required to run the app in production:

- `SECRET_KEY`: A secret key for the app
- `MYSQL_USER`: The database user
- `MYSQL_PASSWORD`: The database password
- `MYSQL_DATABASE`: The database host
- `MYSQL_HOST`: The database host address

For email sending, the following environment variables are required:

- `EMAIL_BACKEND` should be set to `django.core.mail.backends.smtp.EmailBackend`
- `EMAIL_HOST`: The email host
- `EMAIL_PORT`: The email port
- `EMAIL_HOST_USER`: The email host user
- `EMAIL_HOST_PASSWORD`: The email host password
- `EMAIL_USE_SSL`: Should be set to `True` if the email host uses SSL
- `EMAIL_USE_TLS`: Should be set to `True` if the email host uses TLS

For OIDC Authentication, the following environment variables should be provided however default values are provided:

- `GOOGLE_CLIENT_ID`: The Google client ID
- `GOOGLE_CLIENT_SECRET`: The Google client secret
- `GITHUB_CLIENT_ID`: The Github client ID
- `GITHUB_CLIENT_SECRET`: The Github client secret
- `AUTHENTIK_CLIENT_ID`: The Authentik client ID
- `AUTHENTIK_CLIENT_SECRET`: The Authentik client secret

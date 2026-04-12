# envault

> A CLI tool for securely managing and rotating environment secrets across multiple deployment targets.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

Initialize a new vault in your project:

```bash
envault init
```

Add a secret:

```bash
envault set API_KEY "your-secret-value" --env production
```

Rotate secrets across all deployment targets:

```bash
envault rotate --env production --env staging
```

Inject secrets into a running process:

```bash
envault run --env production -- python app.py
```

List all managed secrets:

```bash
envault list --env production
```

---

## Configuration

Envault uses a `.envault.toml` file at the root of your project to define targets and policies. Run `envault init` to generate a starter config.

---

## License

This project is licensed under the [MIT License](LICENSE).
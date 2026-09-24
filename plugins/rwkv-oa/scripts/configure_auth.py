"""Configure only this installed RWKV OA plugin. Python 3.9+, standard library."""
import argparse
import getpass
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import warnings


OA_URL = "https://mcp.oa.rwkvos.com/mcp"
MAX_INPUT = 65536


class ConfigError(Exception):
    """Messages are fixed strings and never contain input or config values."""


def require(condition, message):
    if not condition:
        raise ConfigError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON keys are not supported.")
        result[key] = value
    return result


def read_object(raw):
    try:
        value = json.loads(raw, object_pairs_hook=unique_object)
    except (ValueError, UnicodeError, RecursionError):
        raise ConfigError("Invalid JSON.") from None
    require(isinstance(value, dict), "Expected a JSON object.")
    return value


def normalize_token(value):
    require(isinstance(value, str), "Token must be a string.")
    require("\r" not in value and "\n" not in value, "Multiline tokens are not allowed.")
    token = value.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    require(bool(token), "Token is empty.")
    require(re.fullmatch(r"[A-Za-z0-9._~+/-]+=*", token) is not None,
            "Token contains unsupported characters.")
    return token


def extract_token(raw):
    require(len(raw) <= MAX_INPUT, "Token input is too large.")
    if not raw.lstrip().startswith("{"):
        return normalize_token(raw)
    obj = read_object(raw)
    if "mcpServers" in obj:
        servers = obj["mcpServers"]
        require(isinstance(servers, dict), "Invalid MCP snippet.")
        obj = servers.get("oa_plugin")
        require(isinstance(obj, dict), "MCP snippet must contain oa_plugin.")
    elif "oa_plugin" in obj:
        obj = obj["oa_plugin"]
        require(isinstance(obj, dict), "Invalid oa_plugin snippet.")
    candidates = []
    if "bearer_token" in obj:
        candidates.append(normalize_token(obj["bearer_token"]))
    if "http_headers" in obj:
        headers = obj["http_headers"]
        require(isinstance(headers, dict), "Invalid headers in snippet.")
        for key, value in headers.items():
            if key.lower() == "authorization":
                candidates.append(normalize_token(value))
    require(bool(candidates), "No supported token field found.")
    require(len(set(candidates)) == 1, "Conflicting token fields.")
    return candidates[0]


def cache_directory():
    home = os.environ.get("CODEX_HOME")
    return (Path(home).expanduser() if home else Path.home() / ".codex") / "plugins" / "cache"


def load_target(plugin_root, cache_root):
    root = Path(plugin_root).resolve(strict=True)
    cache = Path(cache_root).resolve(strict=True)
    try:
        parts = root.relative_to(cache).parts
    except ValueError:
        raise ConfigError("Target is not an installed plugin cache.") from None
    require(len(parts) == 3 and parts[1] == "rwkv-oa",
            "Target is not an installed RWKV OA plugin.")
    manifest_path = root / ".codex-plugin" / "plugin.json"
    require(manifest_path.resolve(strict=True) == manifest_path, "Linked manifest is not supported.")
    manifest = read_object(manifest_path.read_bytes())
    require(manifest.get("name") == "rwkv-oa", "Unexpected plugin identity.")
    require(manifest.get("version") == parts[2], "Plugin version does not match cache path.")
    require(manifest.get("mcpServers") == "./.mcp.json", "Unexpected MCP config path.")
    target = root / ".mcp.json"
    require(target.resolve(strict=True) == target, "Linked MCP config is not supported.")
    original = target.read_bytes()
    config = read_object(original)
    servers = config.get("mcpServers")
    require(isinstance(servers, dict), "Missing MCP servers.")
    server = servers.get("oa_plugin")
    require(isinstance(server, dict), "Missing oa_plugin service.")
    require(server.get("type") == "http" and server.get("url") == OA_URL,
            "Unexpected OA service type or address.")
    for name in ("http_headers", "env_http_headers"):
        if name in server:
            require(isinstance(server[name], dict) and
                    all(isinstance(v, str) for v in server[name].values()),
                    "Invalid MCP header configuration.")
    return target, original, config, server


def atomic_write(target, original, config):
    content = (json.dumps(config, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".oa-auth-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            # Retain a read-only file's protection; new secrets are owner-only on POSIX.
            mode = stat.S_IMODE(target.stat().st_mode)
            os.chmod(temporary, mode & 0o600 if os.name != "nt" else mode)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        require(target.read_bytes() == original, "Config changed during update; retry.")
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def configure(plugin_root, cache_root, mode, raw=None):
    require(mode in ("token", "env"), "Unsupported authentication mode.")
    target, original, config, server = load_target(plugin_root, cache_root)
    token = extract_token(raw) if mode == "token" and isinstance(raw, str) else None
    require(mode == "env" or token is not None, "Token input is required.")
    # Authorization from an environment header also conflicts with these modes.
    for name in ("http_headers", "env_http_headers"):
        if name in server:
            server[name] = {k: v for k, v in server[name].items() if k.lower() != "authorization"}
            if not server[name]:
                del server[name]
    server.pop("bearer_token", None)
    if mode == "token":
        server.pop("bearer_token_env_var", None)
        server.setdefault("http_headers", {})["Authorization"] = "Bearer " + token
    else:
        server["bearer_token_env_var"] = "RWKV_OA_TOKEN"
    atomic_write(target, original, config)
    return target


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse's default error can echo accidentally supplied secret arguments.
        raise ConfigError("Invalid arguments; use --help. Tokens must use stdin or hidden input.")


def main(argv=None):
    mode = "unknown"
    root = Path(__file__).resolve().parent.parent
    target = root / ".mcp.json"
    try:
        parser = SafeParser(description=__doc__)
        parser.add_argument("--mode", required=True, choices=("token", "env"))
        parser.add_argument("--stdin", action="store_true", help="Read a raw token or JSON from stdin through EOF.")
        args = parser.parse_args(argv)
        mode = args.mode
        require(not args.stdin or mode == "token", "--stdin requires token mode.")
        load_target(root, cache_directory())  # Validate before prompting for a secret.
        raw = None
        if mode == "token":
            if args.stdin:
                raw = sys.stdin.read(MAX_INPUT + 1)
            else:
                with warnings.catch_warnings():
                    warnings.simplefilter("error", getpass.GetPassWarning)
                    raw = getpass.getpass("OA Token (hidden): ")
        configure(root, cache_directory(), mode, raw)
        print(f"OK mode={mode} target={target}")
        return 0
    except (ConfigError, OSError, UnicodeError, EOFError, getpass.GetPassWarning, KeyboardInterrupt) as error:
        reason = str(error) if isinstance(error, ConfigError) else "Cannot complete update; check path, permissions, or terminal input."
        print(f"ERROR mode={mode} target={target}: {reason}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

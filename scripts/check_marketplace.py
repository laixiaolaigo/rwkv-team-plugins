"""Static checks for this team's local-source marketplace. No network or credentials needed."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTIFIER = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    result = json.loads(path.read_text(encoding='utf-8-sig'))
    require(isinstance(result, dict), f'{path.relative_to(ROOT)}: expected JSON object')
    return result


def within(base, relative):
    require(isinstance(relative, str) and relative.startswith('./'), 'Path must start with ./')
    resolved = (base / relative).resolve()
    require(resolved != base.resolve() and base.resolve() in resolved.parents, 'Path must stay inside its root')
    require(resolved.exists(), f'Missing path: {relative}')
    return resolved


def no_literal_auth(value, context):
    if isinstance(value, dict):
        for key, item in value.items():
            require(key.lower() not in {'bearer_token', 'authorization', 'token', 'api_key', 'password'},
                    f'{context}: use environment-based authentication, not {key}')
            no_literal_auth(item, context)
    elif isinstance(value, list):
        for item in value:
            no_literal_auth(item, context)


def main():
    catalog = read_json(ROOT / '.agents/plugins/marketplace.json')
    require(IDENTIFIER.fullmatch(catalog.get('name', '')), 'Invalid marketplace name')
    plugins = catalog.get('plugins')
    require(isinstance(plugins, list) and plugins, 'Marketplace must contain plugins')
    names = set()
    skill_count = 0
    for entry in plugins:
        name = entry.get('name', '')
        require(IDENTIFIER.fullmatch(name) and name not in names, 'Invalid or duplicate plugin name')
        names.add(name)
        source = entry.get('source', {})
        require(source.get('source') == 'local', f'{name}: this checker supports local sources')
        plugin = within(ROOT, source.get('path'))
        require(plugin.name == name, f'{name}: plugin folder name mismatch')
        policy = entry.get('policy', {})
        require(policy.get('installation') in {'AVAILABLE', 'INSTALLED_BY_DEFAULT', 'NOT_AVAILABLE'}, f'{name}: invalid installation policy')
        require(policy.get('authentication') in {'ON_INSTALL', 'ON_USE'}, f'{name}: invalid authentication policy')
        require(bool(entry.get('category')), f'{name}: category required')
        manifest = read_json(plugin / '.codex-plugin/plugin.json')
        require(manifest.get('name') == name, f'{name}: manifest name mismatch')
        require(re.fullmatch(r'\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?', manifest.get('version', '')), f'{name}: invalid version')
        require(manifest.get('interface', {}).get('displayName'), f'{name}: display name required')
        skills = within(plugin, manifest.get('skills'))
        files = list(skills.glob('*/SKILL.md'))
        require(files, f'{name}: at least one skill required')
        for skill in files:
            body = skill.read_text(encoding='utf-8')
            frontmatter = re.match(r'^---\r?\n(.*?)\r?\n---(?:\r?\n|$)', body, re.S)
            require(frontmatter, f'{name}: missing skill frontmatter')
            header = frontmatter.group(1)
            require(re.search(r'^name:\s*' + re.escape(skill.parent.name) + r'\s*$', header, re.M), f'{name}: skill name mismatch')
            require(re.search(r'^description:\s*\S', header, re.M), f'{name}: description required')
            ui = skill.parent / 'agents/openai.yaml'
            require(ui.is_file(), f'{name}: missing skill UI metadata')
            require('$' + skill.parent.name in ui.read_text(encoding='utf-8'), f'{name}: default prompt must mention skill')
            skill_count += 1
        if manifest.get('mcpServers'):
            mcp = read_json(within(plugin, manifest['mcpServers']))
            servers = mcp.get('mcpServers')
            require(isinstance(servers, dict) and servers, f'{name}: MCP servers required')
            no_literal_auth(mcp, name)
            for server in servers.values():
                require(server.get('type') == 'http' and server.get('url', '').startswith('https://'), f'{name}: expected HTTPS MCP')
                env_name = server.get('bearer_token_env_var')
                if env_name is not None:
                    require(re.fullmatch(r'[A-Z][A-Z0-9_]*', env_name), f'{name}: invalid token variable name')
        print(f'OK {name} {manifest["version"]}')
    print(f'Validated {len(names)} plugins and {skill_count} skills in {catalog["name"]}.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, TypeError, AttributeError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(1)

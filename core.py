import re

def run(p):
    source = p.get('dockerfile', '')
    if not isinstance(source, str) or len(source) > 100000:
        raise ValueError('Dockerfile must be text under 100000 characters')
    lines = []
    acc = ''
    for line in source.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        acc += line[:-1] + ' ' if line.endswith('\\') else line
        if not line.endswith('\\'):
            lines.append(acc)
            acc = ''
    if acc:
        raise ValueError('Unfinished Dockerfile continuation')
    if not any((x.upper().startswith('FROM ') for x in lines)):
        raise ValueError('Dockerfile needs a FROM instruction')
    findings = []

    def add(rule, severity, evidence, fix):
        findings.append(dict(rule=rule, severity=severity, evidence=evidence, remediation=fix))
    last_from = max((i for i, x in enumerate(lines) if x.upper().startswith('FROM ')))
    final = lines[last_from:]
    users = [x.split(None, 1)[1] for x in final if x.upper().startswith('USER ')]
    if not users or users[-1].split(':')[0].lower() in ['root', '0']:
        add('non_root', 'high', 'Final USER is absent or root', 'Set an explicit non-root numeric UID in the final stage.')
    if not any((x.upper().startswith('HEALTHCHECK ') and 'NONE' not in x.upper() for x in final)):
        add('healthcheck', 'medium', 'No enabled healthcheck', 'Add a bounded healthcheck for the final service.')
    for line in lines:
        if line.upper().startswith('FROM ') and '@sha256:' not in line:
            add('base_digest', 'medium', line, 'Pin the real base image digest after verifying it; do not invent a digest.')
        if re.match('COPY\\s+\\.\\s', line, re.I):
            add('copy_scope', 'low', line, 'Use .dockerignore and copy only required source files.')
        if re.match('(ENV|ARG)\\s+\\w*(TOKEN|PASSWORD|SECRET|API_KEY)', line, re.I):
            add('build_secret', 'high', re.split('[=\\s]+', line, maxsplit=2)[0] + ' ' + re.split('[=\\s]+', line, maxsplit=2)[1], 'Use runtime secret files; do not bake credentials into an image.')
    compose = p.get('compose', {})
    services = compose.get('services', {})
    if not isinstance(services, dict):
        raise ValueError('compose.services must be an object')
    for name, svc in services.items():
        if svc.get('privileged'):
            add('privileged', 'high', name, 'Remove privileged mode.')
        if svc.get('network_mode') == 'host':
            add('host_network', 'high', name, 'Use a scoped bridge network.')
        for mount in svc.get('volumes', []):
            if '/var/run/docker.sock' in str(mount):
                add('docker_socket', 'high', name, 'Avoid mounting the host Docker socket.')
        env = svc.get('environment', {})
        for key in env.keys() if isinstance(env, dict) else [str(x).split('=')[0] for x in env]:
            if re.search('TOKEN|PASSWORD|SECRET|API_KEY', key, re.I):
                add('runtime_secret', 'medium', name + ':' + key, 'Prefer mounted secret files; never commit values.')
    return {'findings': findings, 'high_count': sum((x['severity'] == 'high' for x in findings)), 'policy_passed': not any((x['severity'] == 'high' for x in findings)), 'scope': 'static heuristics, not CVE analysis'}

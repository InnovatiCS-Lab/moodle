"""Fresh install + HTTP boundary + container replacement; disposable resources only."""
import os
import secrets
import subprocess
import time
import uuid

image = os.environ.get('TEST_IMAGE', 'ghcr.io/innovatics-lab/moodle:5.3.0')
dbimage = os.environ.get('TEST_DB_IMAGE', 'mariadb:11.4.13')
prefix = 'moodle-install-' + uuid.uuid4().hex
network, db, web = prefix, prefix + '-db', prefix + '-web'
volumes = [prefix + '-code', prefix + '-data']
password = secrets.token_hex(24)

def docker(*args, check=True):
    return subprocess.run(['docker', *args], text=True, capture_output=True, check=check, timeout=600)

def wait_for(args, seconds=180):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        result = docker(*args, check=False)
        if result.returncode == 0:
            return
        time.sleep(2)
    raise RuntimeError('Readiness timeout: ' + result.stderr + result.stdout)

webargs = ['run', '-d', '--name', web, '--network', network,
           '-v', volumes[0] + ':/innovatics/moodle', '-v', volumes[1] + ':/innovatics/moodledata']
for key, value in {
    'MOODLE_DB_HOST': db, 'MOODLE_DB_NAME': 'moodle', 'MOODLE_DB_USER': 'moodle',
    'MOODLE_DB_PASSWORD': password, 'MOODLE_DB_PREFIX': 'mdl_',
    'MOODLE_WWWROOT': 'http://localhost', 'MOODLE_EMAIL_ENABLED': 'no',
}.items():
    webargs += ['-e', key + '=' + value]
webargs += [image]
try:
    docker('network', 'create', '--internal', network)
    docker('run', '-d', '--name', db, '--network', network,
           '-e', 'MARIADB_ROOT_PASSWORD=' + password, '-e', 'MARIADB_DATABASE=moodle',
           '-e', 'MARIADB_USER=moodle', '-e', 'MARIADB_PASSWORD=' + password, dbimage)
    wait_for(['exec', db, 'healthcheck.sh', '--connect', '--innodb_initialized'])
    print('Database ready; initialising Moodle code.', flush=True)
    docker(*webargs)
    wait_for(['exec', web, 'test', '-f', '/innovatics/moodle/config.php'])
    print('Installing Moodle database.', flush=True)
    result = docker('exec', '--user', 'www-data', web, 'php', 'admin/cli/install_database.php',
                    '--agree-license', '--fullname=Container test', '--shortname=Test',
                    '--adminuser=testadmin', '--adminpass=' + secrets.token_urlsafe(24) + 'aA1!',
                    '--adminemail=admin@example.com')
    wait_for(['exec', web, 'php', '/opt/moodle/readiness.php'])
    print('Installation ready; checking HTTP boundaries.', flush=True)
    # Non-public dependency/configuration files must never be served by Apache.
    for path in ['/composer.json', '/composer.lock', '/vendor/autoload.php', '/config.php', '/.git/config']:
        result = docker('exec', web, 'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost' + path)
        assert result.stdout in ('403', '404'), (path, result.stdout)
    docker('exec', '--user', 'www-data', web, 'sh', '-ec', 'echo retained > /innovatics/moodledata/test-marker')
    docker('rm', '-f', web)
    docker(*webargs)
    wait_for(['exec', web, 'php', '/opt/moodle/readiness.php'])
    assert docker('exec', web, 'cat', '/innovatics/moodledata/test-marker').stdout.strip() == 'retained'
    print('PASS: fresh database install, HTTP readiness, protected files, container replacement and data persistence')
except subprocess.CalledProcessError as error:
    # Avoid printing command arguments, which include temporary test passwords.
    raise RuntimeError(error.stdout + error.stderr) from None
finally:
    for container in (web, db):
        docker('rm', '-fv', container, check=False)
    for volume in volumes:
        docker('volume', 'rm', volume, check=False)
    docker('network', 'rm', network, check=False)

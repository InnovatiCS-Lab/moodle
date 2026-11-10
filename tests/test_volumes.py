"""Isolated image tests. Uses only unique disposable test volumes; no database/network."""
import os
import subprocess
import uuid

image = os.environ.get('TEST_IMAGE', 'ghcr.io/innovatics-lab/moodle:5.0.2')
prefix = 'moodle-ci-' + uuid.uuid4().hex
volumes = [prefix + '-code', prefix + '-data']
base = ['docker', 'run', '--rm', '--network', 'none', '-v', volumes[0] + ':/innovatics/moodle', '-v', volumes[1] + ':/innovatics/moodledata']

def run(command, bypass=False, success=True):
    args = base + (['--entrypoint', 'sh'] if bypass else []) + [image]
    args += ['-ec', command] if bypass else ['sh', '-ec', command]
    result = subprocess.run(args, capture_output=True, text=True)
    if success != (result.returncode == 0):
        raise AssertionError(result.stdout + result.stderr)
    return result

try:
    for volume in volumes:
        subprocess.run(['docker', 'volume', 'create', volume], check=True, stdout=subprocess.DEVNULL)
    # Two entrypoints compete to seed the same empty volume.
    args = base + [image, 'sh', '-ec', 'test -s version.php; test -s config.php']
    jobs = [subprocess.Popen(args) for _ in range(2)]
    statuses = [job.wait() for job in jobs]
    assert statuses == [0, 0], statuses
    run('apache2ctl -t; php -l /opt/moodle/runtime/config.php; php -l /opt/moodle/readiness.php; mkdir -p theme/test_extension; echo retained > theme/test_extension/marker; echo retained > /innovatics/moodledata/marker')
    run('test "$(cat theme/test_extension/marker)" = retained; test "$(cat /innovatics/moodledata/marker)" = retained')
    run('touch .image-init-incomplete', bypass=True)
    result = run('true', success=False)
    assert 'interrupted' in result.stderr
    run('rm .image-init-incomplete; cp version.php /innovatics/moodledata/version.saved; echo mismatch >> version.php', bypass=True)
    result = run('true', success=False)
    assert 'does not match' in result.stderr
    run('test "$(tail -1 version.php)" = mismatch; cp /innovatics/moodledata/version.saved version.php; echo private-config > config.php', bypass=True)
    result = run('true', success=False)
    assert 'requires explicit migration' in result.stderr
    run('test "$(cat config.php)" = private-config', bypass=True)
    print('PASS: concurrent initialisation, syntax, persistence, incomplete-copy guard, version guard and config preservation')
finally:
    for volume in volumes:
        subprocess.run(['docker', 'volume', 'rm', volume], check=False, stdout=subprocess.DEVNULL)

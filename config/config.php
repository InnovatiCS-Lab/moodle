<?php
// Environment-configured runtime. Email is disabled unless explicitly enabled.
unset($CFG);
$CFG = new stdClass();
function required_env(string $key): string {
    $value = getenv($key);
    if ($value === false || $value === '') {
        throw new RuntimeException("Missing configuration: " . $key);
    }
    return $value;
}
$CFG->dbtype = 'mariadb';
$CFG->dblibrary = 'native';
$CFG->dbhost = getenv('MOODLE_DB_HOST') ?: 'database';
$CFG->dbname = required_env('MOODLE_DB_NAME');
$CFG->dbuser = required_env('MOODLE_DB_USER');
$CFG->dbpass = required_env('MOODLE_DB_PASSWORD');
$CFG->prefix = required_env('MOODLE_DB_PREFIX');
$CFG->dboptions = ['dbpersist' => false, 'dbport' => (int)(getenv('MOODLE_DB_PORT') ?: 3306),
    'dbsocket' => '', 'dbcollation' => 'utf8mb4_unicode_ci'];
$CFG->wwwroot = required_env('MOODLE_WWWROOT');
if (!preg_match('/^[a-zA-Z0-9_]+$/', $CFG->prefix)) {
    throw new RuntimeException('Invalid database prefix');
}
$url = parse_url($CFG->wwwroot);
if (!$url || !isset($url['host']) || !in_array($url['scheme'] ?? '', ['http', 'https'], true)
    || isset($url['user']) || isset($url['pass']) || isset($url['query']) || isset($url['fragment'])) {
    throw new RuntimeException('MOODLE_WWWROOT must be an HTTP(S) site URL');
}
$CFG->wwwroot = rtrim($CFG->wwwroot, '/');
$CFG->dataroot = '/innovatics/moodledata';
$CFG->admin = 'admin';
$CFG->directorypermissions = 02770;
// Email stays disabled unless explicitly enabled after validation.
$CFG->noemailever = getenv('MOODLE_EMAIL_ENABLED') !== 'yes';
// Enable only behind a trusted TLS-terminating proxy with no direct public backend.
$CFG->sslproxy = getenv('MOODLE_SSL_PROXY') === 'yes';
$CFG->cronclionly = true;
$CFG->debug = 0;
$CFG->debugdisplay = false;
$CFG->disableupdateautodeploy = true;
require_once('/innovatics/moodle/lib/setup.php');

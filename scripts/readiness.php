<?php
// Read-only DB schema probe plus HTTP availability. Does not bootstrap Moodle.
try {
    mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
    $db = mysqli_init();
    $db->options(MYSQLI_OPT_CONNECT_TIMEOUT, 5);
    $db->real_connect(getenv('MOODLE_DB_HOST') ?: 'database', getenv('MOODLE_DB_USER'),
        getenv('MOODLE_DB_PASSWORD'), getenv('MOODLE_DB_NAME'), (int)(getenv('MOODLE_DB_PORT') ?: 3306));
    $prefix = getenv('MOODLE_DB_PREFIX');
    if (!preg_match('/^[a-zA-Z0-9_]+$/', $prefix)) { exit(1); }
    $result = $db->query("SELECT value FROM `{$prefix}config` WHERE name='version'");
    if (!$result->fetch_row()) { exit(1); }
    $ch = curl_init('http://127.0.0.1/login/index.php');
    $authority = parse_url(getenv('MOODLE_WWWROOT'), PHP_URL_HOST);
    $port = parse_url(getenv('MOODLE_WWWROOT'), PHP_URL_PORT);
    if (!$authority) { exit(1); }
    $host = $authority . ($port ? ':' . $port : '');
    curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 10,
        CURLOPT_HTTPHEADER => ['Host: ' . $host]]);
    $body = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    exit($body !== false && $code === 200 && stripos($body, '</html>') !== false ? 0 : 1);
} catch (Throwable $e) { exit(1); }

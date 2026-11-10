# Pass an approved PHP 8.2 Apache Bookworm image pinned by digest.
ARG PHP_IMAGE
FROM ${PHP_IMAGE} AS core
ARG MOODLE_REF=v5.0.2
ARG MOODLE_COMMIT
RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates util-linux libicu-dev libzip-dev libpng-dev libjpeg62-turbo-dev \
    libfreetype6-dev libxml2-dev libonig-dev libpq-dev \
 && docker-php-ext-configure gd --with-freetype --with-jpeg \
 && docker-php-ext-install -j2 mysqli intl zip gd soap exif opcache mbstring \
 && rm -rf /var/lib/apt/lists/*
RUN test -n "$MOODLE_COMMIT" \
 && git init /tmp/moodle \
 && cd /tmp/moodle \
 && git remote add origin https://github.com/moodle/moodle.git \
 && git fetch --depth 1 origin "refs/tags/$MOODLE_REF" \
 && test "$(git rev-parse FETCH_HEAD^{commit})" = "$MOODLE_COMMIT" \
 && mkdir -p /opt/moodle/core \
 && git archive FETCH_HEAD | tar -x -C /opt/moodle/core \
 && rm -rf /tmp/moodle
COPY config/config.php /opt/moodle/runtime/config.php
COPY config/php.ini /usr/local/etc/php/conf.d/zz-moodle.ini
COPY config/apache.conf /etc/apache2/conf-available/moodle.conf
COPY scripts/entrypoint.sh scripts/cron.sh scripts/init-code.sh /usr/local/bin/
COPY scripts/readiness.php /opt/moodle/readiness.php
RUN a2enconf moodle \
 && chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/cron.sh /usr/local/bin/init-code.sh \
 && mkdir -p /innovatics/moodle /innovatics/moodledata \
 && chown www-data:www-data /innovatics/moodledata \
 && rmdir /var/www/html \
 && ln -s /innovatics/moodle /var/www/html \
 && php -r 'foreach (["mysqli","intl","zip","gd","soap","mbstring","curl","sodium","xml","Zend OPcache"] as $e) { if (!extension_loaded($e)) {fwrite(STDERR, "Missing extension: $e\n"); exit(1);} }' \
 && php -l /opt/moodle/runtime/config.php \
 && php -l /opt/moodle/readiness.php
WORKDIR /innovatics/moodle
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["apache2-foreground"]


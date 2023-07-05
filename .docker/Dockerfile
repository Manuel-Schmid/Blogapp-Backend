FROM python:3.9
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV WEB_CONCURRENCY 1

ARG USER_ID=1001
ARG GROUP_ID=1001
ARG WATCHMAN_VERSION="v2021.05.10.00"

# switch user
USER root

# Add netcat
RUN apt-get update && apt-get install -y \
        netcat-traditional

# Add Watchman
RUN wget "https://github.com/facebook/watchman/releases/download/$WATCHMAN_VERSION/watchman-$WATCHMAN_VERSION-linux.zip" \
&& unzip watchman-*-linux.zip \
&& mkdir -p /usr/local/{bin,lib} /usr/local/var/run/watchman \
&& cp "watchman-$WATCHMAN_VERSION-linux/bin/"* /usr/local/bin \
&& cp "watchman-$WATCHMAN_VERSION-linux/lib/"* /usr/local/lib \
&& chmod 755 /usr/local/bin/watchman \
&& chmod 2777 /usr/local/var/run/watchman \
&& rm -r watchman-*-linux*

RUN groupadd www-user -g $GROUP_ID
RUN adduser --home "/home/www-user" --uid $USER_ID --gid $GROUP_ID www-user
ENV PATH="${PATH}:/home/www-user/.local/bin/"

# Add entrypoint
COPY ./.docker/docker-entrypoint.sh /usr/local/bin/docker-entrypoint
RUN chmod +x /usr/local/bin/docker-entrypoint

# Prepare project destination
RUN mkdir -p /opt/app-root/src
RUN chown -R www-user:www-user /opt/app-root/src

USER www-user

WORKDIR /opt/app-root/src

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY --chown=www-user:www-user . /opt/app-root/src
COPY --chown=www-user:www-user app/wsgi.py /opt/app-root/src

EXPOSE 8080

ENTRYPOINT ["docker-entrypoint"]
CMD ["/usr/libexec/s2i/run"]

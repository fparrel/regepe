FROM centos:8

# Correct the new repo url
RUN sed -i s/mirror.centos.org/vault.centos.org/g /etc/yum.repos.d/CentOS-*.repo
RUN sed -i s/^#.*baseurl=http/baseurl=http/g /etc/yum.repos.d/CentOS-*.repo
RUN sed -i s/^mirrorlist=http/#mirrorlist=http/g /etc/yum.repos.d/CentOS-*.repo

# Install nginx + uwsgi + python + flask
# Note: gcc and python-devel are needed for pip install uwsgi
# java is needed for minify tool
RUN dnf install -y nginx python2 python2-devel gcc java-1.8.0-openjdk python2-setuptools
RUN dnf install -y python2-pip
RUN dnf install -y npm
RUN pip2 install uwsgi flask flask_babel polyline

VOLUME /regepe

# Copy regepe code
COPY . /regepe
# Copy default config files
COPY config-default.json /regepe/vps/config/config.json
COPY keysnpwds-default.json /regepe/vps/config/keysnpwds.json

# copy nginx configuration file
COPY regepe-nginx.conf /etc/nginx/nginx.conf

# Some modification for nginx + uwsgi
RUN chown -R nginx.nginx /regepe
RUN chmod -R a+r /regepe 
RUN mkdir /var/log/uwsgi
RUN chmod 777 /var/log/uwsgi
RUN chmod o+x /regepe/vps/static

# Minify and compile translations
RUN cd /regepe/vps && ./minify.sh && ./translations_compile.sh

# Debug
EXPOSE 8080
ENTRYPOINT cd /regepe/vps && python2 regepe_flask_server.py 0.0.0.0

# Prod
#EXPOSE 80
#CMD cd /regepe/vps && uwsgi --ini /regepe/uwsgi-regepe.ini & nginx && while true; do echo 'regepe alive'; sleep 10; done


FROM centos:7

# Add nginx repo
RUN rpm -ivh http://nginx.org/packages/centos/7/noarch/RPMS/nginx-release-centos-7-0.el7.ngx.noarch.rpm
# Install nginx + uwsgi + python + flask
# Note: gcc and python-devel are needed for pip install uwsgi
# java is needed for minify tool
RUN yum install -y nginx python python-devel python-setuptools gcc sudo java
RUN easy_install pip
RUN pip install uwsgi flask flask_babel

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
#EXPOSE 8080
#ENTRYPOINT cd /regepe/vps && python regepe_flask_server.py 0.0.0.0

# Prod
EXPOSE 80
CMD cd /regepe/vps && uwsgi --ini /regepe/uwsgi-regepe.ini & nginx && while true; do echo 'regepe alive'; sleep 10; done


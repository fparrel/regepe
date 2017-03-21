FROM centos:7

# Add nginx repo
RUN rpm -ivh http://nginx.org/packages/centos/7/noarch/RPMS/nginx-release-centos-7-0.el7.ngx.noarch.rpm
# Install nginx + uwsgi + python + flask
# Note: gcc and python-devel are needed for pip install uwsgi
RUN yum install -y nginx python python-devel python-setuptools gcc sudo
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

# Expose ports
EXPOSE 80
EXPOSE 8080

# Debug
ENTRYPOINT cd /regepe/vps && python regepe_flask_server.py 0.0.0.0

# Prod
#ENTRYPOINT sudo -u nginx uwsgi --ini /regepe/uwsgi-regepe.ini & nginx && while true; do echo 'regepe alive'; sleep 10; done


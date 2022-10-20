#
# PADS Website Demo, Container Edition
# Using Django Development Web Server and SQLite DB Driver
# for evaluation and hacking only (not for production use)!
#
FROM python:3-alpine as pads-env
ARG PADS_DIR=/usr/share/
ARG PADS_PROJECT=pads
CMD mkdir -p ${PADS_DIR}
WORKDIR ${PADS_DIR}/
RUN pip install django==2.2.*
RUN django-admin startproject ${PADS_PROJECT}

FROM pads-env as pads
ARG PADS_DIR=/usr/share/
ARG PADS_PROJECT=pads
ARG PADS_PORT=9180
WORKDIR ${PADS_DIR}/${PADS_PROJECT}/${PADS_PROJECT}
# Perform surgical edits on Django config files.
# These edit are run in one compound command to avoid
# excess image layers.
# Please do not trim the spaces. The exact number
# of spaces must be maintained, as we are editing
# Python code.
RUN sed -i s/"from django.urls import path"/"&,include"/ urls.py; \
sed -i s/"urlpatterns = \["/"&\n    path\('pads\/', include\('padsweb.urls'\)\),"/ urls.py; \
sed -i /"admin.site.urls"/d urls.py; \
sed -i s/"INSTALLED_APPS = \["/"&\n    'padsweb.apps.PadswebConfig',"/ settings.py
COPY padsweb ${PADS_DIR}/${PADS_PROJECT}/padsweb/
WORKDIR ${PADS_DIR}/${PADS_PROJECT}/
RUN python manage.py makemigrations padsweb; python manage.py migrate
EXPOSE ${PADS_PORT}/tcp
CMD python manage.py runserver 0.0.0.0:80

#!/bin/sh

SRC=http://community.nuxeo.com/static/releases/nuxeo-5.4.2/nuxeo-dm-5.4.2-tomcat.zip

mkdir $HOME/nuxeocloud
mkdir $HOME/nuxeocloud/instances
mkdir $HOME/nuxeocloud/models

(
cd $HOME/nuxeocloud/models
wget $SRC
unzip *.zip
)



FROM ubuntu:18.04
MAINTAINER lilf <lf97310@gmail.com>

ENV TZ=Asia/Shanghai

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone  && \
    sed -i s@/archive.ubuntu.com/@/mirrors.tuna.tsinghua.edu.cn/@g /etc/apt/sources.list && \
    apt-get clean && \
    apt-get update -y && \
    apt-get install tzdata -y && \
    dpkg-reconfigure --frontend noninteractive tzdata

RUN apt upgrade -y && \
    apt-get install -y vim && \
    apt-get install -y software-properties-common
    #add-apt-repository ppa:jonathonf/python-3.6

RUN apt-get update && \
    apt upgrade -y && \
    apt install -y python3.6 python3-pip

RUN apt-get install -y python3.6-dev python3.6-venv

# 并更新pip
RUN python3.6 -m pip install pip --upgrade -i https://pypi.douban.com/simple && \
    python3.6 -m pip install wheel -i https://pypi.douban.com/simple

# 设置pip源
RUN pip3 config set global.index-url http://mirrors.aliyun.com/pypi/simple/ && \
    pip3 config set global.trusted-host mirrors.aliyun.com

RUN apt-get update -y && \
    apt-get install -y locales && \
    locale-gen en_US.UTF-8

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN pip3 install --no-cache-dir numpy scipy pycrypto pymongo && \
    pip3 install --no-cache-dir requests uwsgi thrift thriftpy2 PyJWT

RUN pip3 install --no-cache-dir flask Flask-Logger Flask-login flask-mongoengine Flask-Script Flask-Session && \
    pip3 install --no-cache-dir 'Flask-APScheduler==1.11.0'

RUN pip3 install --no-cache-dir redis 'kombu==4.6.3' 'celery[redis]==4.3.0' 'vine==1.3.0'

EXPOSE 5000

WORKDIR /expression-api
COPY ./ /expression-api

ENTRYPOINT ["uwsgi", "--ini", "uwsgi.ini"]
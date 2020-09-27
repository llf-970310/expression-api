FROM python:3.6.7-alpine3.7
MAINTAINER dylanchu <chdy.uuid@gmail.com>

ARG ALI_REPO="http://mirrors.aliyun.com/alpine/v3.7/main/\nhttp://mirrors.aliyun.com/alpine/v3.7/community/"
RUN echo -e $ALI_REPO > /etc/apk/repositories && \
    pip config set global.index-url http://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com

RUN apk add --no-cache tzdata && \
    cp -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    rm /usr/share/zoneinfo/ -rf && \
    mkdir -p /usr/share/zoneinfo/Asia/ && \
    cp -f /etc/localtime /usr/share/zoneinfo/Asia/Shanghai

RUN apk add --no-cache make cmake gcc g++ gfortran && \
    pip install numpy pycrypto gevent && \
    apk del make cmake gcc g++ gfortran && \
    rm -rf /root/.cache/pip

RUN apk add --no-cache make cmake gcc g++ gfortran && \
    pip install webrtcvad python-levenshtein pymongo pypinyin zhon && \
    apk del make cmake gcc g++ gfortran && \
    rm -rf /root/.cache/pip

RUN pip install redis 'kombu==4.6.3' 'celery[redis]==4.3.0'  && \
#    pip install --upgrade https://github.com/celery/celery/tarball/master && \
    pip install tornado==5.1.1 && \
#    pip install flower && \
    rm -rf /root/.cache/pip

RUN pip install requests && \
    rm -rf /root/.cache/pip

RUN apk add --no-cache ffmpeg

EXPOSE 50080

COPY expression /expression
WORKDIR expression
#ENTRYPOINT ["celery", "worker", "-A", "celery_tasks.app"]
ENTRYPOINT ["./entrypoint.sh"]

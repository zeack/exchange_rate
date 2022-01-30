FROM rockylinux:8.5
RUN mkdir /code
COPY . /code
WORKDIR /code
RUN yum update -y & yum install -y epel-release python3.9 python3-devel
RUN pip3 install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 3000
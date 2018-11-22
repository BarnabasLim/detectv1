FROM tensorflow/tensorflow:1.12.0-devel-py3
RUN apt-get update
RUN apt-get -y install python3-matplotlib python3-tk
RUN apt-get -y install python-opencv
RUN pip3 install Cython jupyter slackclient
RUN pip3 install pillow lxml
RUN pip3 install imutils
RUN pip3 uninstall -y matplotlib
RUN pip3 install opencv-python

RUN mkdir -p /tensorflow
WORKDIR /tensorflow
RUN git clone https://github.com/armindocachada/models 
RUN mkdir -p /data/videos/incoming
COPY intruder_detection_service.sh /etc/init.d/intruder_detection_service
COPY config.ini /tensorflow/models/research/object_detection/
RUN chmod u+x  /etc/init.d/intruder_detection_service
COPY security_camera_object_detection.ipynb /tensorflow/models/research/object_detection/
RUN curl -OL https://github.com/google/protobuf/releases/download/v3.6.1/protoc-3.6.1-linux-x86_64.zip
RUN unzip -o protoc-3.6.1-linux-x86_64.zip -d /usr/local bin/protoc
RUN cd /tensorflow/models/research && protoc object_detection/protos/*.proto --python_out=.
RUN cd /tensorflow/models/research && export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim && python3 object_detection/builders/model_builder_test.py
RUN jupyter nbconvert --to script /tensorflow/models/research/object_detection/security_camera_object_detection.ipynb

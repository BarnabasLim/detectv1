FROM macgyvertechnology/tensorflow
RUN pip install Cython jupyter matplotlib slackclient
RUN apt-get -y install python-pil python-lxml python-tk python-opencv
RUN mkdir -p /tensorflow
WORKDIR /tensorflow
RUN git clone https://github.com/armindocachada/models 
RUN mkdir -p /data/videos/incoming
#COPY example_videos/* /data/videos/incoming/
COPY intruder_detection_service.sh /etc/init.d/intruder_detection_service
COPY config.ini /tensorflow/models/research/object_detection/
RUN chmod u+x  /etc/init.d/intruder_detection_service
COPY object_detection_tutorial.ipynb /tensorflow/models/research/object_detection/
RUN curl -OL https://github.com/google/protobuf/releases/download/v3.5.1/protoc-3.5.1-linux-x86_64.zip
RUN unzip -o protoc-3.5.1-linux-x86_64.zip -d /usr/local bin/protoc
RUN cd /tensorflow/models/research && protoc object_detection/protos/*.proto --python_out=.
#RUN pip install absl-py
RUN cd /tensorflow/models/research && export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim && python3 object_detection/builders/model_builder_test.py
RUN jupyter nbconvert --to script /tensorflow/models/research/object_detection/object_detection_tutorial.ipynb


#protoc research/object_detection/protos/*.proto --python_out=.
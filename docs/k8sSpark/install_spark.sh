#!/bin/bash


sudo apt-get install wget openjdk-8-jdk-headless -y
wget -q https://archive.apache.org/dist/spark/spark-3.0.0/spark-3.0.0-bin-hadoop3.2.tgz
tar xf spark-3.0.0-bin-hadoop3.2.tgz
rm spark-3.0.0-bin-hadoop3.2.tgz

echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> ~/.bashrc
echo "export SPARK_HOME=/home/leo/flowi/k8sSpark/spark-3.0.0-bin-hadoop3.2" >> ~/.bashrc
echo "export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin"

#!/bin/bash

elastic-mapreduce \
  --create \
  --name "test" \
  --bootstrap-action s3://elasticmapreduce/bootstrap-actions/configurations/latest/memory-intensive \
  --jar s3n://kdd12/parallel.jar \
  --arg 1 \
  --arg s3n://kdd12/input/ \
  --arg s3n://kdd12/output/output1/ \
  --arg s3n://kdd12/output/output2/ \
  --log-uri s3n://kdd12/logs/ \
  --num-instances 2 \
  --instance-type m1.xlarge \
  --master-instance-type m1.xlarge 

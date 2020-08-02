#!/bin/bash
#
# Given two S3 locations, this script copies files from source to destination by
# downloading the source object to local filesystem and then uploading it to the destination
# This is meant for scenarios where the bucket owners are different and ACL cannot be applied.
#
# Usage: bash s3_data_copier.sh
#
# NOTE: Ensure trailing `/` for SOURCE_PREFIX and  DEST_PREFIX values 
# Source config #
SOURCE_BUCKET=
SOURCE_PREFIX=
SOURCE_PROFILE=
SOURCE_REGION=

# Destination config #
DEST_BUCKET=
DEST_PREFIX=
DEST_PROFILE=
DEST_REGION=

UUID=$(uuidgen)
FILES=$(aws s3 ls s3://${SOURCE_BUCKET}/${SOURCE_PREFIX} --recursive --profile ${SOURCE_PROFILE} --region ${SOURCE_REGION} | awk '{print $4}')
for F in ${FILES}
do
    echo "INFO: downloading s3://${SOURCE_BUCKET}/${F}"
    FILE_NAME=${F##*/}
    aws s3 cp s3://${SOURCE_BUCKET}/${F} /mnt/${UUID}/${FILE_NAME} --profile ${SOURCE_PROFILE} --region ${SOURCE_REGION}
    if [ $? -eq 0 ]
    then 
        echo "INFO: uploading to s3://${DEST_BUCKET}/${DEST_PREFIX}"
        aws s3 cp /mnt/${UUID}/${FILE_NAME} s3://${DEST_BUCKET}/${DEST_PREFIX}${FILE_NAME} --profile ${DEST_PROFILE} --region ${DEST_REGION}
        if [ $? -eq 0 ]
        then
            rm /mnt/${UUID}/${FILE_NAME}
        else 
            echo "ERROR: failed to upload ${FILE_NAME} to s3://${DEST_BUCKET}/${DEST_PREFIX}"
        fi
    else
        echo "ERROR: failed to download s3://${SOURCE_BUCKET}/${F}"
        continue
    fi
done

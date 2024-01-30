#!/bin/bash

MAX_LOG_FILE_SIZE=256000
LOG_BCK_FILE='$1.tar.gz'

if [[ -f '$1' ]]; then
    file_size=$(stat -c %s '$1')
    if [ $file_size -gt $MAX_LOG_FILE_SIZE ]; then
        
        if [[ -f '$LOG_BCK_FILE' ]]; then
            rm -f $LOG_BCK_FILE
        fi

        tar -czf $LOG_BCK_FILE $1
        rm -f $1
    fi
fi

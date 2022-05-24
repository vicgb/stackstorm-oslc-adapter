#!/bin/bash

mongo <<EOF
rs.initiate({
     "_id": "rs",
     "version": 1,
     "members": [
         {
             "_id": 0,
             "host": "fd6bd9c7f88c:27017",
             "priority": 3
         },
         {
             "_id": 1,
             "host": "9c27972b5baa:27017",
             "priority": 2
         },
         {
             "_id": 2,
             "host": "04fe511d95d3:27017",
             "priority": 2
         }
     ]
 })

rs.status();
EOF
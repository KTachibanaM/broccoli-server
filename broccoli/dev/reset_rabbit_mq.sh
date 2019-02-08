#!/usr/bin/env bash

sudo rabbitmqctl stop_app
sudo rabbitmqctl reset    # Be sure you really want to do this!
sudo rabbitmqctl start_app

sudo rabbitmqctl add_user test test
sudo rabbitmqctl set_user_tags test administrator
sudo rabbitmqctl set_permissions -p / test ".*" ".*" ".*"

sudo rabbitmq-plugins enable rabbitmq_management

#!/usr/bin/env bash
set -e

psql -h localhost -U postgres -c "DROP DATABASE stockwatch"
psql -h localhost -U postgres -c "CREATE DATABASE stockwatch"

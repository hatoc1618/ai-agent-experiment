#!/bin/bash
# Macから実行する
# 1. まずスクリプトをNucBoxに転送
scp "$(dirname "$0")/install_pyrevit.ps1" IN@100.102.217.90:"C:\\Users\\IN\\install_pyrevit.ps1"
# 2. NucBox上でPowerShellスクリプトを実行
ssh IN@100.102.217.90 "powershell -ExecutionPolicy Bypass -File C:\Users\IN\install_pyrevit.ps1"

FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

# Remove the broken Yarn repo BEFORE features try to run apt-get update
RUN rm -f /etc/apt/sources.list.d/yarn.list
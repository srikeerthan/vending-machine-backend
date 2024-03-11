# Use the official PostgreSQL image from Docker Hub
FROM postgres:latest

LABEL authors="srikeerthanred.aluri"

# Set environment variables for PostgreSQL
ENV POSTGRES_DB=vending_machine
ENV POSTGRES_USER=sri
ENV POSTGRES_PASSWORD=BlackVulture

# Copy SQL scripts to initialize the database
COPY init.sql /docker-entrypoint-initdb.d/

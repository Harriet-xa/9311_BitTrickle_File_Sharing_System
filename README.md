# BitTrickle File Sharing System

A permissioned peer-to-peer file sharing system with a centralized indexing server.

## Overview
This project implements a simplified file sharing system called **BitTrickle**.  
It consists of:

- a **central server** for user authentication, peer activity tracking, and file indexing
- multiple **clients** that can publish, search, and download files

The system combines both **client-server** and **peer-to-peer** communication models:

- **UDP** is used for all client-server communication
- **TCP** is used for peer-to-peer file transfers

## Features
- User authentication with credentials file
- Heartbeat mechanism for active peer tracking
- List active peers (`lap`)
- Publish file (`pub <filename>`)
- List published files (`lpf`)
- Search files by substring (`sch <substring>`)
- Download file from another peer (`get <filename>`)
- Unpublish file (`unp <filename>`)
- Graceful client exit (`xit`)

## System Design
### Server
The server is responsible for:
- authenticating users
- storing active peer information
- tracking published files
- helping peers discover each other

### Client
Each client:
- communicates with the server over UDP
- sends heartbeat messages periodically
- listens for incoming TCP download requests
- supports interactive command-line operations

### Concurrency
The client is designed with multithreading to support:
- user input handling
- periodic heartbeat sending
- concurrent file upload servicing

## Project Structure
```text
.
├── client.py
├── server.py
├── credentials.txt   # server-side only, not committed in real submission
├── helpers.py        # optional
└── report.pdf

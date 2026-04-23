# Scope and specifications
The following are the technical requirements for the implementation of
[RFC-959](https://www.rfc-editor.org/rfc/rfc959). The features proposed
by the Design Project specification are:
1. Client/Server connection management
2. Client may list files and directories
3. Client may move within the allowed work tree
4. Client may create directories
5. Client may download a selected file
6. Client may upload a selected file

## Commands (RFC-959 4.1)
The commands relevant for the scope of the project are (by category)
  1. **Access Control**
  - User Name (USER)
  - Password (PASS)
  - Change Working Directory (CWD)
  - Change to Parent Directory (CDUP)
  - Logout (QUIT)
  2. **Data Transfer Parameters**
  - Passive (PASV): Response includes the host, p1 and p2
  (e.g. 192,168,1,10,192,18). Formula for the port is `(p1 << 8) | p2`.<br/>
  `Note: Data transfer ports should be in the ephemeral range (49152-65535)`
  - File Structure (STRU): Will only support File (F)  option (Default in the RFC).
  - Transfer Mode (MODE): Will only support Stream (S) option (Default in the RFC).
  3. **Services**
  - Retrieve (RETR)
  - Store (STOR)
  - Make Directory (MKD)
  - Print Working Directory (PWD)
  - List (LIST)
  - Help (HELP) # Optional: Nice to have
  - NOOP (NOOP) # Optional: Helpful for testing

## FTP Replies (RFC-959 4.2)
### Good, Bad, or Incomplete
1. Positive
  - 1xx (Prelim - Expect another reply from server)
  - 2xx (Complete)
  - 3xx (Interm - Expect another command from client)
2. Negative
  - 4xx (Neg Completion - Not accepted. User should try again from beginning)
  - 5xx (Permanent Neg Completion - Not accepted. User should not try again)
### Kind
1. x0x (Syntax)
2. x1x (Information)
3. x2x (Connections)
4. x3x (Auth)
5. x4x (Unspecified)
6. x5x (File Sys)
**Note: Visit section RFC-959 4.2.1 for full list of Reply Codes**

## Caveats
The implementation will only support ASCII (A), Non-print (N), Passive mode,
and File-structure.

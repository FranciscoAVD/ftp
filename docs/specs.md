# RFC-959
The following are the technical requirements for the implementation of
[RFC-959](https://www.rfc-editor.org/rfc/rfc959)

## Commands (4.1)
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
  - Rename From (RNFR)
  - Reanme To (RNTO)
  - Delete (DELE)
  - Remove Directory (RMD)
  - Make Directory (MKD)
  - Print Working Directory (PWD)
  - List (LIST)
  - Status (STAT)
  - Help (HELP)
  - NOOP (NOOP)  
  
## Caveats
The implementation will only support ASCII (a), Non-print (N), Passive mode,
and File-structure.

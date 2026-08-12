# Target Architecture

**Status:** DESIGNED

The target architecture distributes load asynchronously for scalability and multi-tenancy.

Frontend -> API -> PostgreSQL -> Redis -> Worker -> Object Storage
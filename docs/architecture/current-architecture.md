# Current Architecture

**Status:** IMPLEMENTED

TradeFlow is currently built as a monolithic, synchronously processing web application running on SQLite and the local filesystem.

Frontend -> FastAPI -> Application -> Domain -> Infrastructure -> SQLite / Local filesystem
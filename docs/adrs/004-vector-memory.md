# ADR-004: Selection of Vector Search Engine

**Status**: DRAFT  
**Date**: 2026-01-16  
**Context**:  
The ICGL requires "Semantic Memory" to allow agents to recall relevant policies, past ADRs, and historical decisions based on meaning rather than exact keyword matches. This is detecting "Drift".

**Decision**:  
We will use **Qdrant** as the Vector Search Engine.

**Rationale**:

1. **Sovereignty**: Qdrant is fully open-source and can be self-hosted via Docker (No Cloud Dependency).
2. **Performance**: Written in Rust, highly performant for local vector search.
3. **Developer Experience**: Simple Python client (`qdrant-client`) and local file storage mode for development.

**Consequences**:

- **Positive**: Enables "Fuzzy Search" for agents. Explicit dependency on `qdrant-client`.
- **Negative**: Adds a Docker dependency for production (though local mode works for now).

**Alternatives Considered**:

- **Chroma**: Good Python integration, but persistence stability has been mixed.
- **Pinecone**: Rejected due to Cloud dependency (Violates P-CORE-01).

# General Rules

## CORE PRINCIPLES
These rules define the foundation of code development in this project:

### R1: CLEAN AND CONCISE CODE
- **No unnecessary comments**
  - Code should be self-explanatory
  - Only document complex decisions or non-obvious logic
  - Avoid comments that repeat what the code already says

### R2: PROGRESSIVE DEVELOPMENT
- **No placeholder functionalities**
  - Implement complete and usable features
  - Avoid code marked "to be completed later", "for future use"
  - Each commit should add real value to the project

### R3: STANDARDS AND DOCUMENTATION
- **Follow official rules and documentation**
  - Follow language-specific style guides
  - Use standard patterns when available

### R4: ATOMIC DEVELOPMENT
- **Develop in atomic steps**
  - Small and verifiable changes
  - One change = one specific functionality
  - Facilitate code review and testing

### R5: VERSIONING
- **Document changes by version**
  - Use Git Flow for branch management
  - Keep CHANGELOG.md updated
  - Version following Semantic Versioning (SemVer)

## DOCUMENTATION GUIDELINES

### R6: DOCUMENTATION LOCATION
- **All documentation in /workspace/docs**
  - Technical documentation
  - Development plans
  - Architecture diagrams
  - API specifications
  - User guides
  - Never place documentation files within app directories

### R7: FEATURE PLANNING
- **Document app plans before implementation**
  - Create a plan document for each app/module
  - Include detailed implementation steps
  - Document design decisions and trade-offs
  - Reference relevant patterns and standards

### R8: PENDING FEATURES
- **Register pending features in docs/pending_features.md**
  - Document identified features for future implementation
  - Include brief description and justification
  - Categorize by module/functionality
  - Do not include pending features in code comments

### R9: DOCUMENTATION FORMAT
- **Use Markdown for all documentation**
  - Use headings and sections for organization
  - Include code examples where appropriate
  - Add diagrams when needed for clarity
  - Keep documentation updated with code changes

### R10: MULTILINGUAL APPROACH
- **English as primary language for documentation**
  - Technical documentation in English
  - API documentation in English
  - UI text may be in Spanish with internationalization support
  - Code, variables, and comments in English 
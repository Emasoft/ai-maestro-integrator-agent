# Changelog

All notable changes to this project will be documented in this file.
    ## [1.2.9] - 2026-04-10

### Bug Fixes

- Add AMP communication restriction to all sub-agents    
- Correct governance terminology, version sync, and communication rules    
- Resolve all CPV validation issues    
- Publish.py runs CPV validation remotely + pre-push enforces --strict    
- Ruff F541 — remove extraneous f-prefix in publish.py    
- Remove CPV_PUBLISH_PIPELINE bypass from pre-push hook — CPV --strict always runs    
- Publish.py + pre-push use cpv-remote-validate via uvx    
- Move shutil/subprocess imports to top of file (ruff E402)    
- Use permissive markdownlint config (default: false)    

### Features

- Add compatible-titles and compatible-clients to agent profile    
- Add communication permissions from title-based graph    
- Add smart publish pipeline + pre-push hook enforcement    

### Miscellaneous

- Update uv.lock    

### Ci

- Update validate.yml to use cpv-remote-validate --strict    
- Strict publish.py + pre-push hook + release.yml propagation    



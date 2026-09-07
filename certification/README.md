# Framework certification

This subtree is isolated from normal customer/domain runtime configuration.

Human entrypoint:

```powershell
python certification/bootstrap.py --apply --environment DEV
```

Structure:

```text
bootstrap.py                 one-click preparation entrypoint
framework-executable.json    exact Framework executable identity
config/environments/         non-secret certification environment bindings
fabric/                      certification-only Notebook/Pipeline/Copy/Spark/SQL definitions
project/                     exact certification DatasetConfig/scenarios
extensions/                  bounded Customer certification extension package
support/                     bootstrap implementation helpers
```

A successful bootstrap stops at `READY / NOT_RUN`; it never manufactures certification PASS or release authorization.

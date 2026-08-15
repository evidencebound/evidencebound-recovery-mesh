# Judge video capture run 31875943133

The first one-shot capture failed before any browser request because `/tmp/capture.mjs` could not resolve the repository-local `playwright` package. No judge run was started, no screenshots were uploaded, and the masked judge key was not exposed. The fix is to execute the temporary module from the repository workspace so normal Node package resolution can find `node_modules/playwright`.

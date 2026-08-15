# Video capture security boundary

The protected capture flow is allowed to read the existing judge secret only inside the authenticated GitHub Actions job. The value is masked immediately and is never echoed, committed, uploaded, or rendered in the browser. Screenshots are taken only after the password input has been cleared by the UI. The artifact contains sanitized PNGs and a receipt with provider/run ID only.

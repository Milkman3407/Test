# Network Interface Manager - Incremental Build Plan

This document breaks development into small, reviewable parts so we can move safely from concept to a usable Windows app.

## Part 1: Requirements lock (no code changes)
Collect and confirm these items before implementation changes:

1. **Target users**
   - Help desk only, or end users too?
2. **OS support**
   - Windows 11 only, or Windows 10 as well?
3. **Network scope**
   - IPv4 only (current) or IPv6 also?
4. **Configuration modes**
   - DHCP + Static (current), or also predefined profiles?
5. **DNS behavior**
   - Single DNS, primary/secondary DNS, or DHCP fallback options?
6. **Safety controls**
   - Confirmation prompt before apply?
   - Revert timer if connectivity is lost?
7. **Security expectations**
   - Is UAC prompt acceptable on launch?
   - Do you need code-signing guidance for .exe distribution?
8. **Deployment**
   - Standalone .exe distribution through email, shared drive, or software center?

## Part 2: Input validation hardening
- Add strict IPv4 format validation for static IP fields.
- Add user-friendly field-level error messages.
- Keep current admin-elevation behavior.

## Part 3: UX quality improvements
- Disable static fields when DHCP is selected.
- Add placeholders/examples (e.g., `192.168.1.50`).
- Add a concise, persistent status panel with last operation result.

## Part 4: Operational safety
- Add "Preview command" mode so operators can verify actions before applying.
- Add exportable action log for troubleshooting.

## Part 5: Packaging and rollout
- Build signed `.exe` (if certificate available).
- Add quick-start PDF for non-technical users.
- Provide pilot checklist for first deployment batch.

---

## Suggested immediate next step
Proceed with **Part 2 (input validation hardening)** once Part 1 requirements are confirmed.

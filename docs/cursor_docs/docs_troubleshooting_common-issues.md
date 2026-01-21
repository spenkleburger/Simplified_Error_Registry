# Common Issues | Cursor Docs

Source URL: https://cursor.com/docs/troubleshooting/common-issues

---

Troubleshooting
# Common Issues

Below are common issues and their solutions.

### Networking Issues

First, check your network connectivity. Go to `Cursor Settings` > `Network` and click `Run Diagnostics`. This will test your connection to Cursor's servers and help identify any network-related issues that might be affecting AI features, updates, or other online functionality.

Cursor relies on HTTP/2 for AI features because it handles streamed responses efficiently. If your network doesn't support HTTP/2, you may experience indexing failures and AI feature issues.

This occurs on corporate networks, VPNs, or when using proxies like Zscaler.

To resolve this, enable HTTP/1.1 fallback in app settings (not Cursor settings): press `CMD/CTRL + ,`, search for `HTTP/2`, then enable `Disable HTTP/2`. This forces HTTP/1.1 usage and resolves the issue.

We plan to add automatic detection and fallback.

### Resource Issues (CPU, RAM, etc.)

High CPU or RAM usage can slow your machine or trigger resource warnings.

While large codebases require more resources, high usage typically stems from extensions or settings issues.

If you are seeing a low RAM warning on MacOS, please note that there is a
bug for some users that can show wildly incorrect values. If you are seeing
this, please open the Activity Monitor and look at the "Memory" tab to see the
correct memory usage.

If you're experiencing high CPU or RAM usage, try these steps:

### Check Your Extensions

### Use the Process Explorer

### Monitor System Resources

### Testing a Minimal Installation

## AI Model Issues

If you're experiencing unexpected AI behavior, understanding [how AI models work](/learn/how-ai-models-work) and [their limitations](/learn/hallucination-limitations) can help you work more effectively with Cursor's AI features.

## General FAQs

### I see an update on the changelog but Cursor won't update

### I have issues with my GitHub login in Cursor / How do I log out of GitHub in Cursor?

### I can't use GitHub Codespaces

### I have errors connecting to Remote SSH

### SSH Connection Problems on Windows

### Cursor Tab and Inline Edit do not work behind my corporate proxy

### I just subscribed to Pro but I'm still on the free plan in the app

### When will my usage reset again?

### My Chat/Composer history disappeared after an update

### How do I uninstall Cursor?

### How do I delete my account?

### How do I open Cursor from the command line?

### Unable to Sign In to Cursor

### Suspicious Activity Message
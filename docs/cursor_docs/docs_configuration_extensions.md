# Extensions | Cursor Docs

Source URL: https://cursor.com/docs/configuration/extensions

---

Configuration
# Extensions

Cursor supports VS Code extensions, allowing you to enhance your development environment with additional functionality. Extensions can be installed from the built-in marketplace or directly using extension URLs.

## Extension registry

Cursor uses the Open VSX registry to provide extensions. However, unlike the standard Open VSX implementation, Cursor independently verifies all extensions for security and compatibility.

This verification process ensures:

Extensions are safe to use
They work properly with Cursor's AI features
Performance remains optimal

While Cursor is built on VS Code's foundation, not all VS Code extensions may
be available or work exactly the same way due to Cursor's additional AI
capabilities and verification requirements.

## Installing extensions

### Using the extensions panel

The easiest way to install extensions is through the Extensions panel:

Open the Extensions view (⌘/Ctrl + Shift + X)
Search for the extension you want
Click Install

### Using extension URLs

You can also open extensions directly using a special URL pattern:

```
cursor:extension/publisher.extensionname
```

For example, to open the ChatGPT extension page:

```
cursor:extension/openai.chatgpt
```

This pattern is useful for:

Sharing specific extensions with team members
Creating documentation with direct links to extensions
Automating extension installation in setup scripts

## Managing extensions

### Viewing installed extensions

To see your installed extensions:

Open the Extensions panel (⌘/Ctrl + Shift + X)
Click on the "Installed" filter

### Disabling or uninstalling

Right-click on any installed extension to:

Disable the extension temporarily
Uninstall it completely
Configure extension-specific settings

### Extension settings

Many extensions come with configurable settings. To access them:

Open Settings (⌘/Ctrl + ,)
Search for the extension name
Modify the available settings

## Publisher verification

Extension publishers can request verification to display a verification badge in the marketplace. Verified publishers have undergone additional security review and identity confirmation.

### Requesting verification

To request verification for your extension:

1
### Add marketplace links to your website

On your public website, add a link to the OpenVSX listing for your extension. Place this link prominently (such as in the installation section) alongside links to other marketplaces.
2
### Ensure consistent extension IDs

If your extension is published on multiple marketplaces, use the same
extension ID on OpenVSX as you do elsewhere.
3
### Submit a verification request

Create a [forum post](https://forum.cursor.com/) containing: - Your extension
name - A link to your website where we can verify the OpenVSX registry link
4
### Wait for review

We'll verify the link and add the verification badge to your publisher name once approved.

The verification process helps users identify trusted extensions and ensures a
higher standard of security and authenticity in the marketplace.

## Importing from VS Code

If you're migrating from VS Code, you can import all your extensions automatically. See our [VS Code migration guide](/docs/configuration/migrations/vscode) for detailed instructions.
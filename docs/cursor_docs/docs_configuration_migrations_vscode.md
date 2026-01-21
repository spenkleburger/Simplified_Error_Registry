# VS Code Migration | Cursor Docs

Source URL: https://cursor.com/docs/configuration/migrations/vscode

---

Configuration
# VS Code Migration

Cursor is based upon the VS Code codebase, allowing us to focus on making the best AI-powered coding experience while maintaining a familiar editing environment. This makes it easy to migrate your existing VS Code settings to Cursor.

## Profile Migration

### One-click Import

Here's how to get your entire VS Code setup in one click:

Open the Cursor Settings (⌘/Ctrl + Shift + J)
Navigate to General > Account
Under "VS Code Import", click the Import button

This will transfer your:

Extensions
Themes
Settings
Keybindings

### Manual Profile Migration

If you are moving between machines, or want more control over your settings, you can manually migrate your profile.

#### Exporting a Profile

On your VS Code instance, open the Command Palette (⌘/Ctrl + Shift + P)
Search for "Preferences: Open Profiles (UI)"
Find the profile you want to export on the left sidebar
Click the 3-dot menu and select "Export Profile"
Choose to export it either to your local machine or to a GitHub Gist

#### Importing a Profile

On your Cursor instance, open the Command Palette (⌘/Ctrl + Shift + P)
Search for "Preferences: Open Profiles (UI)"
Click the dropdown menu next to 'New Profile' and click 'Import Profile'
Either paste in the URL of the GitHub Gist or choose 'Select File' to upload a local file
Click 'Import' at the bottom of the dialog to save the profile
Finally, in the sidebar, choose the new profile and click the tick icon to active it

## Settings and Interface

### Settings Menus

Cursor Settings: (⌘/Ctrl + Shift + P), then type "Cursor Settings"
VS Code Settings: (⌘/Ctrl + Shift + P), then type "Preferences: Open Settings (UI)"

### Version Updates

We regularly rebase Cursor onto the latest VS Code version to stay current with features and fixes. To ensure stability, Cursor often uses slightly older VS Code versions.

### Activity Bar Orientation

We made the activity bar horizontal to optimize space for the AI chat interface. If you prefer vertical:

Open the Command Palette (⌘/Ctrl + Shift + P)
Search for "Preferences: Open Settings (UI)"
Search for `workbench.activityBar.orientation`
Set the value to `vertical`
Restart Cursor
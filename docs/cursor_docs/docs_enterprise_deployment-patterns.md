# Deployment Patterns | Cursor Docs

Source URL: https://cursor.com/docs/enterprise/deployment-patterns

---

Account
# Deployment Patterns

This guide covers how to deploy Cursor IDE and CLI tools to developer machines in your organization. Most organizations deploy both the IDE (for daily development work) and the CLI (for automation, CI/CD, and scripting).

For other deployment options like SCM integrations (bugbot, BGA apps) or web-based access, see the relevant integration documentation.

## IDE deployment with MDM

Deploy the Cursor IDE to user workstations and enforce policies through Mobile Device Management (MDM) systems.

### How it works

Your IT team packages Cursor IDE for deployment
Push to user machines via MDM (Jamf, Intune, etc.)
Users receive Cursor on their primary development machines

MDM allows you to enforce policies on the Cursor IDE, such as allowed team IDs and extensions.

You can also enforce settings like workspace trust, and control auto-updates and deployment of new versions.

### MDM Configuration

You can centrally manage specific features of Cursor through device management solutions to ensure it meets the needs of your organization. When you specify a Cursor policy, its value overrides the corresponding Cursor setting on users' devices.

Cursor supports policies on Windows (Group Policy), macOS (configuration profiles), and Linux (JSON policy files, version 2.0+).

Cursor currently provides policies to control the following admin-controlled features:

PolicyDescriptionCursor settingAllowedExtensionsControls which extensions can be installed.`extensions.allowed`AllowedTeamIdControls which team IDs are allowed to log in. Users with unauthorized team IDs are forcefully logged out.`cursorAuth.allowedTeamId`ExtensionGalleryServiceUrlConfigures a custom extension marketplace URL.`extensions.gallery.serviceUrl`NetworkDisableHttp2Disables HTTP/2 for all requests, using HTTP/1.1 instead.`cursor.general.disableHttp2`UpdateModeControls automatic update behavior. Set to 'none' to disable updates.`update.mode`WorkspaceTrustEnabledControls whether Workspace Trust is enabled.`security.workspace.trust.enabled`

#### Windows Group Policy

Cursor has support for Windows Registry-based Group Policy. When policy definitions are installed, admins can use the Local Group Policy Editor to manage the policy values.

To add a policy:

Copy the Policy ADMX and ADML files from `AppData\Local\Programs\cursor\policies`.
Paste the ADMX file into the `C:\Windows\PolicyDefinitions` directory, and the ADML file into the `C:\Windows\PolicyDefinitions\<your-locale>\` directory.
Restart the Local Group Policy Editor.
Set the appropriate policy values (e.g. `{"anysphere": true, "github": true}` for the `AllowedExtensions` policy) in the Local Group Policy Editor.

Policies can be set both at the Computer level and the User level. If both are set, Computer level will take precedence.

Important: When a policy value is set, it overrides the Cursor setting value configured at any level (default, user, workspace, etc.). This is a global override that prevents users from changing these settings.

In Cursor 2.1, we renamed the category name to Cursor in the Group Policy Editor. Old keys still work. We recommend using the current ADMX policy file.

#### Windows Installer

The Windows installer is based on Inno Setup. To install Cursor fully in the background without user interaction, use the following command-line flags:

```
CursorSetup-x64-2.0.exe /SILENT /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CLOSEAPPLICATIONS /LOG=install.log
```

Note: Installers pre-2.0 may incorrectly not respect `/SILENT` flags. Future installers (version 2.0 and later) will ensure that silent installs work correctly.

#### macOS Configuration Profiles

Configuration profiles manage settings on macOS devices. A profile is an XML file with key/value pairs that correspond to available policy. These profiles can be deployed using Mobile Device Management (MDM) solutions like Jamf, Kandji, or Microsoft Intune, or installed manually.

Bundle ID per channel:

The `PayloadType` in your configuration profile must match the Cursor bundle ID for your channel:

ChannelBundle IDProductioncom.todesktop.230313mzl4w4u92Nightlyco.anysphere.cursor.nightly

For most enterprise deployments, use the production bundle ID: `com.todesktop.230313mzl4w4u92`.

### Example .mobileconfig file

##### String policies

The example below demonstrates configuration of the `AllowedExtensions` policy. The policy value starts empty in the sample file (no extensions are allowed).

```
<key>AllowedExtensions</key>
<string></string>
```

Add the appropriate JSON string defining your policy between the `<string>` tags.

```
<key>AllowedExtensions</key>
<string>{"anysphere": true, "github": true}</string>
```

Extension control semantics:

The `AllowedExtensions` policy accepts a JSON object where:

Keys can be publisher names (e.g., `"github"`) or full extension IDs (e.g., `"ms-azuretools.vscode-docker"`)
Values are booleans indicating whether extensions from that publisher or specific extension are allowed
If a publisher is set to `true`, all extensions from that publisher are allowed
Specific extension IDs take precedence over publisher rules

For the `AllowedTeamId` policy, add the comma-separated list of team IDs:

```
<key>AllowedTeamId</key>
<string>1,3,7</string>
```

For the `NetworkDisableHttp2` policy, use a boolean value to disable HTTP/2:

```
<key>NetworkDisableHttp2</key>
<true/>
```

##### Boolean policies

For boolean policies like `WorkspaceTrustEnabled`, use `<true/>` or `<false/>` tags:

```
<key>WorkspaceTrustEnabled</key>
<false/>
```

Or to enable the feature:

```
<key>WorkspaceTrustEnabled</key>
<true/>
```

##### UpdateMode policy

The `UpdateMode` policy controls how Cursor handles automatic updates. This is useful for organizations that want to control when and how updates are deployed.

Available values:

`none` - Disables all automatic updates
`manual` - Users can manually check for updates
`start` - Check for updates when Cursor starts
`default` - Default behavior (same as `start`)
`silentlyApplyOnQuit` - Download updates in the background and apply when Cursor quits

To disable automatic updates:

```
<key>UpdateMode</key>
<string>none</string>
```

##### WorkspaceTrustEnabled policy

The `WorkspaceTrustEnabled` policy controls whether [Workspace Trust](https://code.visualstudio.com/docs/editing/workspaces/workspace-trust) is enabled. When enabled, Cursor prompts users to choose between normal or restricted mode for new workspaces.

Use a boolean value:

```
<key>WorkspaceTrustEnabled</key>
<true/>
```

##### ExtensionGalleryServiceUrl policy

The `ExtensionGalleryServiceUrl` policy configures the extension marketplace URL. This is useful for organizations that want to use a custom extension marketplace or mirror.

Set the URL as a string value:

```
<key>ExtensionGalleryServiceUrl</key>
<string>https://marketplace.example.com</string>
```

##### Deploying with MDM solutions

The `.mobileconfig` file can be uploaded directly to your MDM solution:

Jamf: Upload as a custom configuration profile
Kandji: Add as a custom profile in Library
Microsoft Intune: Deploy as a custom profile with the correct payload domain

Ensure the `PayloadType` matches your Cursor channel's bundle ID.

##### Reference configuration file

A complete example configuration profile is included with Cursor at:

```
# Production channel
/Applications/Cursor.app/Contents/Resources/app/policies/com.todesktop.230313mzl4w4u92.mobileconfig

# Nightly channel
/Applications/Cursor Nightly.app/Contents/Resources/app/policies/co.anysphere.cursor.nightly.mobileconfig
```

The file path varies by channel. Use the appropriate path for your Cursor installation.

Important security considerations:

The provided `.mobileconfig` file initializes all policies available in that version of Cursor
Delete any policies that are not needed to avoid unintentionally restrictive defaults
If you do not edit or remove a policy from the sample, that policy will be enforced with its default value
Policy values override all user and workspace settings globally

Manually install a configuration profile by double-clicking on the `.mobileconfig` profile in Finder and then enabling it in System Preferences under General > Device Management. Removing the profile from System Preferences will remove the policies from Cursor.

For more information on configuration profiles, refer to Apple's documentation.

#### Linux Policy File

Linux distributions don't have a standardized enterprise policy system like Windows Registry or macOS configuration profiles. Cursor reads policies from a JSON file to provide equivalent functionality.

Note: Linux policy file support is available in Cursor version 2.0 and later.

The policy file is located at `~/.cursor/policy.json`.

##### Creating a policy file

Create a JSON file at the location above with policy names as keys and their values. All policies are optional?include only the policies you want to enforce.

### Example policy.json file

##### Policy format

Each policy in the JSON file maps to a policy name:

AllowedExtensions: A JSON string defining allowed extension publishers

```
"AllowedExtensions": "{\"anysphere\": true, \"github\": true}"
```

AllowedTeamId: A comma-separated string of team IDs

```
"AllowedTeamId": "1,3,7"
```

WorkspaceTrustEnabled: A boolean controlling workspace trust

```
"WorkspaceTrustEnabled": true
```

Note: The `AllowedExtensions` value must be a JSON string (escaped quotes), not a JSON object. This matches the format used on Windows and macOS.

##### Deploying policies

Deploy the policy file using your organization's configuration management tools:

Ansible, Puppet, or Chef for automated deployment
NFS or shared network storage for centralized policy files
Package managers with post-install scripts
Container base images for containerized environments

Changes to the policy file take effect when Cursor restarts. The file is monitored for changes, so updates propagate automatically to running instances.

If the policy file doesn't exist, Cursor runs without policy restrictions.

### Automatic updates for non-admin users

Due to Electron framework limitations, Cursor updates require administrator privileges on macOS.

Recommended approaches:

MDM deployment: Use MDM tools (Jamf, Kandji, Intune) to deploy updates centrally with appropriate privileges
Automated deployment tools: Consider tools like [Installomator](https://github.com/Installomator/Installomator) for scripted updates
Disable update prompts: Set the `UpdateMode` policy to `none` to prevent users from seeing failed update notifications

For organizations with non-admin users, the most reliable approach is to manage Cursor updates through your existing software deployment pipeline and disable automatic updates via MDM policy.

## CLI deployment

Run Cursor agents as a headless CLI tool on your infrastructure.

### How it works

Deploy the CLI to your environment (on-prem, corporate cloud, Kubernetes clusters, CI/CD systems)
The CLI is scripted or run in the background or as part of CI
The CLI can access whatever the user can access from their machine (VPN, internal APIs, private package registries, etc.)

### Installation and setup

Install the Cursor CLI:

```
# Install Cursor CLI
curl https://cursor.com/install -fsS | bash

# Set API key for scripts
export CURSOR_API_KEY=your_api_key_here
cursor-agent -p "Analyze this code"
```

See [CLI headless mode documentation](/docs/cli/headless) for full details.

### GitHub Actions integration

Cursor CLI works in GitHub Actions and other CI systems.

See [GitHub Actions integration](/docs/cli/github-actions) for examples.

## Cursor CLI considerations

Whether running in the IDE or as a standalone CLI, Cursor agents have the same security controls:

Same features:

Privacy Mode applies equally
Hooks work for both IDE and CLI
Same model access controls
Same audit logging
Same usage tracking

Same requirements:

Both need network access to Cursor services
Both send code to LLMs (with Privacy Mode protections)
Both require appropriate authentication

The CLI is the same agent with a different interface.

## Network considerations

User machines need access to the following endpoints. Configure firewall and proxy rules accordingly:

`*.cursor.sh` - Backend services and API endpoints
`cursor-cdn.com` - Application downloads and updates
`marketplace.cursorapi.com` - Extension marketplace
Third-party AI provider endpoints (OpenAI, Anthropic, Google, etc.)

When using the `UpdateMode` policy set to `none`, you can restrict access to update endpoints while maintaining access to other services.

The Cursor IDE inherits the machine's network configuration, including VPN access, internal service endpoints, and private package registries.

This means agents running in the IDE can access whatever the user can access from their machine.

See [Network Configuration](/docs/enterprise/network-configuration) for detailed firewall and proxy requirements.

## Minimum Versions

We recommend users stay within one version of our most recent release. Users three or more versions behind our current release will start to see a warning indicating that they need to upgrade. Users four or more versions behind our latest release will see an error forcing them to update. This allows users to experience our latest features, while also staying up to date with our latest performance improvements, stability updates and bug fixes.

For example, if the latest release is 1.7, we recommend all users to be on version 1.6 or 1.7. Users on 1.4 or below will see a warning telling them to update. Users on 1.3 or below will see an error forcing them to update.

When managing Cursor deployments for your organization, we recommend updating your Cursor version regularly.

## Troubleshooting

Proxy configuration problems (see [Network Configuration](/docs/enterprise/network-configuration))
Model access issues (check [Model and Integration Management](/docs/enterprise/model-and-integration-management) or your [team dashboard](/docs/account/teams/dashboard))
Spending limit reached (see [Usage and Spend Controls](/docs/enterprise/usage-and-spend-controls))

## Frequently asked questions

### Does Cursor support policies on Linux?

Yes, starting with version 2.0. Linux uses a file-based policy system at `~/.cursor/policy.json`. See the "Linux Policy File" section above for details on the format and deployment.

### Can I use environment variables in the policy file?

No. The policy file must be a valid JSON file with static values. Use your configuration management tools to generate the file dynamically if needed.

### What happens if the policy file has invalid JSON?

Cursor logs an error and runs without policy restrictions. Check the main process logs for parsing errors.
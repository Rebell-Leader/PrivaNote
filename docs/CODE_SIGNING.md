# Code Signing Setup for GitHub Actions

This document explains how to set up code signing for the PrivaNote application across different platforms.

## Quick Start (No Code Signing)

If you want to build unsigned applications for development/testing, **you don't need to set up any secrets**. The CI will automatically build unsigned binaries that work perfectly for development.

## Required GitHub Secrets (Optional - For Production Releases)

### Windows Code Signing

1. **WINDOWS_CERTIFICATE**: Base64-encoded .p12 certificate file
2. **WINDOWS_CERTIFICATE_PASSWORD**: Password for the certificate

#### How to obtain Windows certificates:
- Purchase a code signing certificate from a trusted CA (DigiCert, Sectigo, etc.)
- Convert to base64:
  - macOS/Linux: `base64 -i certificate.p12 | pbcopy`
  - Windows: `certutil -encode certificate.p12 certificate.txt` then copy the content between the header/footer lines

### macOS Code Signing and Notarization

1. **APPLE_ID**: Your Apple ID email
2. **APPLE_ID_PASS**: App-specific password for your Apple ID
3. **APPLE_TEAM_ID**: Your Apple Developer Team ID (found in Apple Developer portal)
4. **MAC_CERTIFICATE**: Base64-encoded .p12 certificate file
5. **MAC_CERTIFICATE_PASSWORD**: Password for the certificate

#### How to obtain macOS certificates:
- Enroll in Apple Developer Program ($99/year)
- Create "Developer ID Application" certificate in Apple Developer portal
- Download and install in Keychain Access
- Export from Keychain Access as .p12 file (right-click → Export)
- Convert to base64: `base64 -i certificate.p12 | pbcopy`

#### How to create app-specific password:
1. Go to https://appleid.apple.com/
2. Sign in with your Apple ID
3. Go to "App-Specific Passwords"
4. Generate a new password for "GitHub Actions"
5. Copy the generated password (not your regular Apple ID password)

## Setting up GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add each secret with the **exact names** listed above

### Important Notes:
- Secret names are case-sensitive
- Don't include any extra spaces or characters
- For base64 certificates, copy the entire encoded string without line breaks
- Test with one platform first before setting up all certificates

## Current CI Behavior

- **Without secrets**: Builds unsigned applications (works for development)
- **With secrets**: Builds signed applications (required for distribution)
- The CI automatically detects if secrets are present and enables signing accordingly

## Testing Code Signing

### Local Testing (Optional)

You can test code signing locally by setting environment variables:

```bash
# Windows
set CSC_LINK=path/to/certificate.p12
set CSC_KEY_PASSWORD=your_password
npm run dist:win

# macOS
export APPLE_ID=your@email.com
export APPLE_ID_PASS=your_app_specific_password
export APPLE_TEAM_ID=your_team_id
export CSC_LINK=path/to/certificate.p12
export CSC_KEY_PASSWORD=your_password
npm run dist:mac
```

### CI Testing

1. Create a test release to trigger the build workflow
2. Check the Actions tab for build status
3. Verify that signed binaries are produced

## Troubleshooting

### Common Issues

1. **Certificate not found**: Ensure the base64 encoding is correct
2. **Invalid password**: Double-check the certificate password
3. **Apple ID issues**: Ensure 2FA is enabled and app-specific password is used
4. **Team ID not found**: Get your Team ID from Apple Developer portal

### Debugging

Enable debug logging by adding this to your workflow:

```yaml
env:
  DEBUG: electron-builder
```

## Security Notes

- Never commit certificates or passwords to the repository
- Use GitHub's encrypted secrets feature
- Rotate certificates and passwords regularly
- Monitor certificate expiration dates
- Consider using GitHub's OIDC for enhanced security

## Alternative: Skip Code Signing

If you don't need code signing for development builds, you can disable it:

```yaml
env:
  CSC_IDENTITY_AUTO_DISCOVERY: false
```

This will create unsigned binaries that work for testing but may show security warnings to users.

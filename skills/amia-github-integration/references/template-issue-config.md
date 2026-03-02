---
name: template-issue-config
description: "Issue template chooser configuration that disables blank issues and redirects to structured forms."
---

# Issue Template Chooser Configuration

## Table of Contents

- 1. When to Use This Configuration
  - 1.1 What is config.yml and where it goes
  - 1.2 How the issue template chooser works in GitHub
- 2. Disabling Blank Issues
  - 2.1 Why blank issues should be disabled
  - 2.2 The blank_issues_enabled setting
- 3. Contact Links
  - 3.1 Redirecting feature requests to GitHub Discussions
  - 3.2 Redirecting questions to a community forum or chat
  - 3.3 Adding custom external links
- 4. Complete Configuration (Ready to Copy)
- 5. How the Template Chooser Appears to Users
  - 5.1 Visual layout of the chooser page
  - 5.2 Order of templates and links
- 6. Customization Notes
  - 6.1 Adding project-specific contact links
  - 6.2 Combining with issue templates

---

## 1. When to Use This Configuration

### 1.1 What is config.yml and where it goes

The `config.yml` file controls the GitHub Issues template chooser -- the page users see when they click "New Issue" on a repository. It determines whether blank (unstructured) issues are allowed and provides external links for redirecting certain types of requests.

Place the file at `.github/ISSUE_TEMPLATE/config.yml`:

```
your-repo/
  .github/
    ISSUE_TEMPLATE/
      bug_report.yml       <-- bug report form
      docs.yml             <-- documentation issue form
      config.yml           <-- this configuration file
```

### 1.2 How the issue template chooser works in GitHub

When a repository has issue templates, GitHub displays a chooser page instead of opening a blank issue directly. The chooser shows:

1. All YAML issue forms (from `.github/ISSUE_TEMPLATE/*.yml`)
2. All markdown issue templates (from `.github/ISSUE_TEMPLATE/*.md`)
3. Contact links defined in `config.yml`
4. A "Open a blank issue" link (if `blank_issues_enabled` is true)

The `config.yml` file controls items 3 and 4.

---

## 2. Disabling Blank Issues

### 2.1 Why blank issues should be disabled

Blank issues allow users to submit free-form text without any structure. This causes several problems:

- Missing reproduction steps make bugs impossible to investigate
- Missing version information wastes maintainer time asking for basics
- Missing categorization makes triage slower
- Duplicate reports increase because users skip the "search first" checkbox

By disabling blank issues, every report must go through a structured form. This means every bug report has reproduction steps, every documentation issue has a file location, and every reporter has confirmed they searched for duplicates.

### 2.2 The blank_issues_enabled setting

```yaml
blank_issues_enabled: false
```

When set to `false`, the "Open a blank issue" link is removed from the template chooser. Users must select one of the defined templates or follow a contact link.

If set to `true` (the default), users can bypass all templates and submit unstructured issues.

---

## 3. Contact Links

### 3.1 Redirecting feature requests to GitHub Discussions

Feature requests often require discussion and community input before becoming actionable issues. Redirecting them to GitHub Discussions keeps the issue tracker focused on bugs and concrete work items.

```yaml
contact_links:
  - name: "[FEATURE] Feature Request"
    url: https://github.com/YOUR_ORG/YOUR_REPO/discussions/categories/feature-requests
    about: "Suggest a new feature or enhancement. Feature requests are discussed in GitHub Discussions before becoming issues."
```

Replace `YOUR_ORG/YOUR_REPO` with your actual repository path. You must have GitHub Discussions enabled on the repository and create a "Feature Requests" category.

To enable GitHub Discussions:
1. Go to repository Settings
2. Scroll to the Features section
3. Check "Discussions"
4. Create a "Feature Requests" category in the Discussions tab

### 3.2 Redirecting questions to a community forum or chat

Questions about usage, troubleshooting, and general help are better handled in a community space where other users can also benefit from the answers.

```yaml
  - name: "Question / Help"
    url: https://github.com/YOUR_ORG/YOUR_REPO/discussions/categories/q-a
    about: "Ask a question or get help. Use GitHub Discussions Q&A for questions instead of filing an issue."
```

Alternative options for the URL depending on your community setup:

| Community Platform | URL Pattern |
|-------------------|-------------|
| GitHub Discussions | `https://github.com/ORG/REPO/discussions/categories/q-a` |
| Stack Overflow | `https://stackoverflow.com/questions/tagged/your-project` |
| Forum (Discourse) | `https://forum.yourproject.dev` |
| Chat (Matrix) | `https://matrix.to/#/#your-project:matrix.org` |

### 3.3 Adding custom external links

You can add any number of contact links. Each link appears in the template chooser with its name and description.

```yaml
  - name: "Security Vulnerability"
    url: https://github.com/YOUR_ORG/YOUR_REPO/security/advisories/new
    about: "Report a security vulnerability privately. Do NOT file a public issue for security bugs."
```

This is important for security reports, which should never be filed as public issues.

---

## 4. Complete Configuration (Ready to Copy)

Copy the following into `.github/ISSUE_TEMPLATE/config.yml`:

```yaml
blank_issues_enabled: false

contact_links:
  - name: "[FEATURE] Feature Request"
    url: https://github.com/YOUR_ORG/YOUR_REPO/discussions/categories/feature-requests
    about: "Suggest a new feature or enhancement. Feature requests are discussed in GitHub Discussions before becoming issues."

  - name: "Question / Help"
    url: https://github.com/YOUR_ORG/YOUR_REPO/discussions/categories/q-a
    about: "Ask a question or get help. Use GitHub Discussions Q&A instead of filing an issue."

  - name: "Security Vulnerability"
    url: https://github.com/YOUR_ORG/YOUR_REPO/security/advisories/new
    about: "Report a security vulnerability privately. Do NOT file a public issue for security bugs."
```

Replace all instances of `YOUR_ORG/YOUR_REPO` with your actual organization and repository name.

---

## 5. How the Template Chooser Appears to Users

### 5.1 Visual layout of the chooser page

When a user clicks "New Issue", they see a page with this layout:

```
+------------------------------------------------------------------+
|  Choose a template                                                |
+------------------------------------------------------------------+
|                                                                    |
|  [Bug Report]                                          [Get started]|
|  Report a bug or unexpected behavior                               |
|                                                                    |
|  [Documentation Improvement]                           [Get started]|
|  Report missing, incorrect, or improvable documentation            |
|                                                                    |
|  -----------------------------------------------------------      |
|                                                                    |
|  [FEATURE] Feature Request                             [Open]      |
|  Suggest a new feature or enhancement...                           |
|                                                                    |
|  Question / Help                                       [Open]      |
|  Ask a question or get help...                                     |
|                                                                    |
|  Security Vulnerability                                [Open]      |
|  Report a security vulnerability privately...                      |
|                                                                    |
+------------------------------------------------------------------+
```

Issue templates (YAML forms) appear at the top with "Get started" buttons. Contact links appear below a separator with "Open" buttons that navigate to external URLs.

### 5.2 Order of templates and links

Issue templates are displayed in alphabetical order by filename. Contact links are displayed in the order they appear in `config.yml`. To control the order of templates, prefix filenames with numbers:

```
.github/ISSUE_TEMPLATE/
  01-bug_report.yml          <-- appears first
  02-docs.yml                <-- appears second
  config.yml
```

---

## 6. Customization Notes

### 6.1 Adding project-specific contact links

Common additional links for different project types:

For libraries:
```yaml
  - name: "API Question"
    url: https://stackoverflow.com/questions/tagged/your-library
    about: "Ask questions about API usage on Stack Overflow."
```

For applications with paid support:
```yaml
  - name: "Enterprise Support"
    url: https://yourcompany.com/support
    about: "For enterprise customers with support agreements."
```

For projects with a roadmap:
```yaml
  - name: "Roadmap"
    url: https://github.com/orgs/YOUR_ORG/projects/1
    about: "Check the public roadmap to see if your feature is already planned."
```

### 6.2 Combining with issue templates

The `config.yml` works alongside issue templates, not instead of them. A typical complete setup includes:

```
.github/ISSUE_TEMPLATE/
  bug_report.yml       <-- structured bug report form
  docs.yml             <-- documentation improvement form
  config.yml           <-- chooser configuration (this file)
```

The templates define what structured forms are available. The config defines what external links appear and whether blank issues are allowed.

# MailScout - A Python Business Email Finder and Email Validator

MailScout is a Python library designed for finding business email addresses and simple email validation.

It offers a range of tools for email validation, SMTP checks, and generating potential business email addresses based on provided names and common naming conventions.

Important: The library requires your outgoing port 25 to be open to perform SMTP actions. Some cloud services block the port by default (like AWS lambda), and you should configure your cloud network accordingly if Mailscout doesn't work properly. You may try Mailscout on Google Colab without any problem.

## Features

- Generate and find potential business email addresses based on provided names and common patterns.
- Check SMTP deliverability of email addresses.
- Detect catch-all domains.
- Normalize names to create email-friendly formats.
- Bulk email finder for multiple domains.

## Installation

Install MailScout using pip:

```bash
pip install mailscout
```

## Initialization

### Initialize the Scout class

```python
from mailscout import Scout
scout = Scout()
```

The `Scout` class is the core of the MailScout library, providing various functionalities for email finding, processing and validation. When initializing a `Scout` object, you can customize its behavior using several arguments:

### Arguments

- `check_variants (bool)`: If set to `True`, the Scout object will generate and check different variants of email addresses based on provided names. Defaults to `True`.
- `check_prefixes (bool)`: Enables the checking of common email prefixes (like 'info', 'contact', etc.) when generating email addresses. This is useful for finding potential business emails. Defaults to `True`.
- `check_catchall (bool)`: Determines whether the Scout object should check if a domain is a catch-all. A catch-all domain accepts emails sent to any address under that domain. Defaults to `True`.
- `normalize (bool)`: If set to `True`, the Scout object will normalize names to create email-friendly formats. This is particularly useful for names with diacritics or special characters. Defaults to `True`.
- `num_threads (int)`: Specifies the number of threads to use for concurrent email checking. Increasing the number of threads can speed up the process when checking a large number of emails. Defaults to `5`.
- `num_bulk_threads (int)`: Sets the number of threads for bulk email finding tasks. This is separate from `num_threads` to provide flexibility in handling large-scale operations. Defaults to `1`.
- `smtp_timeout (int)`: The timeout in seconds for the SMTP connection. This parameter is crucial to avoid long waits on unresponsive servers. Defaults to `2`.

## Usage

### Find Business Emails with Names

Mailscout generates combinations using the names you provide. These names should ideally belong to the same person, typically a first name and a last name.

To find business emails, we use the `find_valid_emails` method.

Names might be a list of strings.

```python
names = ["Batuhan", "Akyazı"]
# or, names = ["Batuhan Akyazı"]
domain = "example.com"

emails = scout.find_valid_emails(domain, names)

print(emails)
# ['b.akyazi@example.com']
```

You can also provide a list of lists containing strings to check on multiple people.

```python
names = [["Jeff", "Winger"], ["Ben Cheng"], ["Łukas Nowicki"]]
domain = "microsoft.com"

emails = scout.find_valid_emails(domain, names)

print(emails)
# ['jeff@microsoft.com', 'ben.cheng@microsoft.com', 'bencheng@microsoft.com', 'ben@microsoft.com', 'lukas@microsoft.com']
```

Or simply a string.

```python
names = "Jeffrey Tobias Winger"
domain = "microsoft.com"

emails = scout.find_valid_emails(domain, names)

print(emails)
# ['winger.tobias@microsoft.com']
```

### Find Business Emails with Common Prefixes

If you don't provide any names, Mailscout will use brute force on common prefixes to find email addresses.

```python
domain = "microsoft.com"
emails = scout.find_valid_emails(domain)

print(emails)
# ['support@microsoft.com', 'team@microsoft.com', 'marketing@microsoft.com', 'accounts@microsoft.com', 'help@microsoft.com', 'finance@microsoft.com', 'manager@microsoft.com', 'events@microsoft.com', 'community@microsoft.com', 'feedback@microsoft.com', 'dev@microsoft.com', 'developer@microsoft.com', 'status@microsoft.com', 'security@microsoft.com']
```

### Find Business Emails in Bulk

To find valid email addresses in bulk for multiple domains and names, use the `find_valid_emails_bulk` method. This function takes a list of dictionaries, each containing a domain and optional names to check, and returns a list of dictionaries, each containing the domain, names, and a list of valid emails found.

You may think of each list item as a task and provide the data accordingly.

Here is an example of how to use this function:

```python
email_data = [
    {"domain": "example.com", "names": ["John Doe"]},
    {"domain": "example.com", "names": ["Jane Smith"]},
		{"domain": "example.com"}
]

valid_emails = scout.find_valid_emails_bulk(email_data)

print(valid_emails)
# [{'domain': 'example.com', 'names': ['John Doe'], 'valid_emails': ['j.doe@example.com']}, {'domain': 'example2.com', 'names': ['Jane Smith'], 'valid_emails': ['j.smith@example2.com', 'jane.smith@example2.com']}, {'domain': 'example.com', 'valid_emails': ['info@example.com']}]

```

## Utility Methods

Mailscout comes with a variety of utility methods for different tasks.

### Check SMTP Deliverability (Email Validation)

To validate an email with Mailscout, use the `check_smtp` method.

```python
email = "batuhan@microsoft.com"
is_deliverable = scout.check_smtp(email)

print(f"Email {email} is deliverable: {is_deliverable}")
# Email batuhan@microsoft.com is deliverable: False
```

### Checking for Catch-All Domains

The `check_email_catchall` method can be used to determine if a given domain is configured as a catch-all. A catch-all domain is set up to accept emails sent to any address under that domain, even if the specific address does not exist.

```python
domain = "example.com"
is_catchall = scout.check_email_catchall(domain)

print(f"Domain {email} is catch-all: {is_catchall}")
# Email xample.com is catch-all: True
```

### Normalize Names into Email-friendly Format

To normalize a name for an email-friendly format, use the `normalize_name` method. This method converts a non-compliant name into a format that is acceptable for an email address. Here are some examples:

```python
name1 = "Şule"
name2 = "Dzirżyterg"

normalized_name1 = scout.normalize_name(name1)
normalized_name2 = scout.normalize_name(name2)

print(normalized_name1)
# 'sule'
print(normalized_name2)
# 'dzirzyterg'

```

## License
MailScout is released under the MIT License.

## Contact
For questions or feedback, please contact Batuhan Akyazı. (batuhanakydev@gmail.com)

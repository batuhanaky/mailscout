import smtplib
import dns.resolver
import random
from threading import Thread
from queue import Queue
import string
import itertools
from typing import List, Optional, Set, Union, Dict
import unicodedata
from unidecode import unidecode
import re

class Scout:
    def __init__(self, 
            check_variants: bool = True, 
            check_prefixes: bool = True, 
            check_catchall: bool = True,
            normalize: bool = True,
            num_threads: int = 5,
            num_bulk_threads: int = 1,
            smtp_timeout: int = 2) -> None:
        """
        Initialize the Scout object with default settings.

        Args:
            check_variants (bool): Flag to check variants. Defaults to True.
            check_prefixes (bool): Flag to check prefixes. Defaults to True.
            check_catchall (bool): Flag to check catchall. Defaults to True.
            normalize (bool): Flag to normalize data. Defaults to True.
            num_threads (int): Number of email finder threads for concurrency. Defaults to 5.
            num_bulk_threads (int): Number of bulk email finder threads for concurrency. Defaults to 1.
            smtp_timeout (int): Timeout for the SMTP connection. Defaults to 2. (in seconds)
        """
        
        self.check_variants = check_variants
        self.check_prefixes = check_prefixes
        self.check_catchall = check_catchall
        self.normalize = normalize
        self.num_threads = num_threads
        self.num_bulk_threads = num_bulk_threads
        self.smtp_timeout = smtp_timeout


    # SMTP Mail Checker Function
    def check_smtp(self, email: str, port: int = 25) -> bool:
        """
        Check if an email is deliverable using SMTP.

        Args:
        email (str): The email address to check.
        port (int, optional): The port to use for the SMTP connection. Defaults to 25.

        Returns:
        bool: True if the email is deliverable, False otherwise.
        """
        domain = email.split('@')[1]
        try:
            records = dns.resolver.resolve(domain, 'MX')
            mx_record = str(records[0].exchange)
            with smtplib.SMTP(mx_record, port, timeout=self.smtp_timeout) as server:
                server.set_debuglevel(0)
                server.ehlo("example.com")
                server.mail('test@example.com')
                code, message = server.rcpt(email)

            return code == 250
        except Exception as e:
            print(f"Error checking {email}: {e}")
            return False


    # Catch-all checker function, checks whether the domain accepts all addresses
    def check_email_catchall(self, domain: str) -> bool:
        """
        Check if a domain is a catch-all for email addresses.

        A catch-all domain will accept emails sent to any address under that domain,
        even if the specific address does not exist.

        Args:
        domain (str): The domain to check.

        Returns:
        bool: True if the domain is a catch-all, False otherwise.
        """
        random_prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + "falan"
        random_email = f"{random_prefix}@{domain}"
        return self.check_smtp(random_email)

    def normalize_name(self, name: str) -> str:
        """
        Convert a non-email compliant name to a normalized email-friendly format.

        Args:
        name (str): The name to be normalized.

        Returns:
        str: A normalized, email-friendly version of the name.
        """
        # This function is a little bit overkill 
        # I will strip it over time with proper testing
        
        # Basic normalization
        name = name.upper().lower()

        # Normalize using unidecode for proper transliteration
        name = unidecode(name)

        # Normalize to NFKD form which separates characters and their diacritics
        normalized = unicodedata.normalize('NFKD', name)

        # Encode to ASCII bytes, then decode back to string ignoring non-ASCII characters
        ascii_encoded = normalized.encode('ascii', 'ignore').decode('ascii')

        # Replace any remaining non-alphanumeric characters with an empty string
        email_compliant = re.sub(r'[^a-zA-Z0-9]', '', ascii_encoded)

        return email_compliant


    def generate_prefixes(self, domain: str, custom_prefixes: Optional[List[str]] = None) -> List[str]:
        """
        Generate a list of email addresses with common or custom prefixes for a given domain.

        Args:
        domain (str): The domain for which to generate email addresses.
        custom_prefixes (List[str], optional): A list of custom prefixes. If provided, these
                                            prefixes are used instead of the common ones.

        Returns:
        List[str]: A list of email addresses with the specified prefixes.
        """
        common_prefixes = [
            # Business Prefixes
            "info", "contact", "sales", "support", "admin",
            "service", "team", "hello", "marketing", "hr",
            "office", "accounts", "billing", "careers", "jobs",
            "press", "help", "enquiries", "management", "staff",
            "webmaster", "administrator", "customer", "tech",
            "finance", "legal", "compliance", "operations", "it",
            "network", "development", "research", "design", "engineering",
            "production", "purchasing", "logistics", "training",
            "ceo", "director", "manager",
            "executive", "agent", "representative", "partner",
            # Website Management Prefixes
            "blog", "forum", "news", "updates", "events",
            "community", "shop", "store", "feedback",
            "media", "resource", "resources",
            "api", "dev", "developer", "status", "security"
        ]

        prefixes = custom_prefixes if custom_prefixes is not None else common_prefixes
        return [f"{prefix}@{domain}" for prefix in prefixes]

    def generate_email_variants(self, names: List[str], domain: str, normalize: bool = True) -> List[str]:
        """
        Generate a set of email address variants based on a list of names for a given domain.

        This function creates combinations of the provided names, both with and without dots
        between them, and also includes individual names and their first initials.

        Args:
        names (List[str]): A list of names to combine into email address variants.
        domain (str): The domain to be appended to each email variant.
        normalize (bool, optional): If True, normalize the prefixes to email-friendly format.

        Returns:
        List[str]: A list of unique email address variants.
        """
        variants: Set[str] = set()

        assert False not in [isinstance(i, str) for i in names]

        if normalize:
            normalized_names = [self.normalize_name(name) for name in names]
            names = normalized_names

        # Generate combinations of different lengths
        for r in range(1, len(names) + 1):
            for name_combination in itertools.permutations(names, r):
                # Join the names in the combination with and without a dot
                variants.add(''.join(name_combination))
                variants.add('.'.join(name_combination))

        # Add individual names (and their first initials) as variants
        for name in names:
            variants.add(name)
            variants.add(name[0])

        return [f"{variant}@{domain}" for variant in variants]


    def find_valid_emails(self,
                        domain: str, 
                        names: Optional[Union[str, List[str], List[List[str]]]] = None, 
                        )-> List[str]:
        """
        Find valid email addresses for a given domain based on various checks.

        Args:
        domain (str): The domain to check email addresses against.
        names (Union[str, List[str], List[List[str]]], optional): Names to generate email variants. 
            Can be a single string, a list of strings, or a list of lists of strings.

        Returns:
        List[str]: A list of valid email addresses found.
        """
        # Pre-flight checks
        if self.check_catchall:
            if self.check_email_catchall(domain):
                return []

        # Valid e-mail finder function
        def worker():
            while True:
                email = q.get()
                if email is None:  # None is the signal to stop
                    break
                try:
                    if self.check_smtp(email):
                        valid_emails.append(email)
                except Exception as e:
                    print(f"Error processing {domain}: {e}")
                finally:
                    q.task_done()

        valid_emails = []
        email_variants = []
        generated_mails = []

        # Generate email variants based on the type of 'names'
        if self.check_variants and names:
            if isinstance(names, str):
                names = names.split(" ")
            if isinstance(names, list) and names and isinstance(names[0], list):
                for name_list in names:
                    assert isinstance(name_list, list)
                    name_list = self.split_list_data(name_list)
                    email_variants.extend(self.generate_email_variants(name_list, domain, normalize = self.normalize))
            else:
                names = self.split_list_data(names)
                email_variants = self.generate_email_variants(names, domain, normalize = self.normalize)

        if self.check_prefixes and not names:
            generated_mails = self.generate_prefixes(domain)

        all_emails = email_variants + generated_mails

        q = Queue()
        threads = []
        num_worker_threads = self.num_threads  # Number of worker threads, as passed via the argument

        # Start worker threads
        for i in range(num_worker_threads):
            t = Thread(target=worker)
            t.start()
            threads.append(t)

        # Enqueue emails
        for email in all_emails:
            q.put(email)

        # Wait for all tasks to be processed
        q.join()

        # Stop workers
        for i in range(num_worker_threads):
            q.put(None)
        for t in threads:
            t.join()

        return valid_emails



    def find_valid_emails_bulk(self,
        email_data: List[Dict[str, Union[str, List[str]]]], 
        ) -> List[Dict[str, Union[str, List[str], List[Dict[str, str]]]]]:
        """
        Find valid email addresses in bulk for multiple domains and names.

        Args:
        email_data (List[Dict[str, Union[str, List[str]]]]): A list of dictionaries, 
            each containing domain and optional names to check.

        Returns:
        List[Dict[str, Union[str, List[str], List[Dict[str, str]]]]]: A list of dictionaries, 
            each containing the domain, names, and a list of valid emails found.
        """
        # Remove duplicates
        email_data_clean = [i for n, i in enumerate(email_data) if i not in email_data[n + 1:]]

        # Worker function for threading
        def worker():
            while True:
                data = q.get()
                if data is None:  # None is the signal to stop
                    break
                try:
                    domain = data.get("domain")
                    names = data.get("names", [])
                    check_prefixes_value = False if names else self.check_prefixes

                    valid_emails = self.find_valid_emails(
                        domain, names
                    )
                    all_valid_emails.append({"domain": domain, "names": names, "valid_emails": valid_emails})
                except Exception as e:
                    print(f"Error processing {domain}: {e}")
                finally:
                    q.task_done()

        all_valid_emails = []
        q = Queue()
        threads = []
        num_worker_threads = self.num_bulk_threads

        # Start worker threads
        for i in range(num_worker_threads):
            t = Thread(target=worker)
            t.start()
            threads.append(t)

        # Enqueue email data
        for data in email_data_clean:
            q.put(data)

        # Wait for all tasks to be processed
        q.join()

        # Stop workers
        for i in range(num_worker_threads):
            q.put(None)
        for t in threads:
            t.join()

        return all_valid_emails
    
    def split_list_data(self, target):
        new_target = []
        for i in target:
            new_target.extend(i.split(" "))
        return new_target
def is_domain_accepted(domain):
    """Check if a given domain is accepted."""
    from backend.models import EmailDomain
    return EmailDomain.objects.filter(
        domain=domain, status=EmailDomain.STATUS_ACCEPTED).count() > 0


def is_domain_rejected(domain):
    """Check if a domain is rejected."""
    from backend.models import EmailDomain
    return EmailDomain.objects.filter(
        domain=domain, status=EmailDomain.STATUS_REJECTED).count() > 0


def get_domain(email_address):
    """Get the domain from an e-mail address, with leading @."""
    email_address = str(email_address)
    split = email_address.split('@')
    if len(split) != 2:
        return ""
    return '@' + split[1]

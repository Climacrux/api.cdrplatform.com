class CertificateIDConverter:
    regex = "[a-zA-Z]{3}-[a-zA-Z]{3}-[a-zA-Z]{3}"

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)

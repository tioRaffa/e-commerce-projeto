if DEBUG: # type: ignore
    # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
    EMAIL_HOST_USER = '8a2b4840957f6b'
    EMAIL_HOST_PASSWORD = '6d4a5a31342bbf'
    EMAIL_PORT = '2525'
    
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smpt.EmailBackend'
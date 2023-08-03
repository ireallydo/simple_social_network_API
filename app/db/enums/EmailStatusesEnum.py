from enum import Enum


class EmailStatusesEnum(str, Enum):
    """Email verification statuses (verification through hunter io API);
    FAILED is a custom status stating that the response from the server was not received
    due to third party server troubles;
    UNSTATED is a custom status stating that the verification status from the server is unknown
    and update in accordance with changes to hunter io API documentation are needed;
    hunter io API documentation: https://hunter.io/api-documentation/v2#email-verifier"""
    FAILED = 'failed'
    UNSTATED = 'unstated'
    VALID = 'valid'
    INVALID = 'invalid'
    ACCEPT_ALL = 'accept_all'
    WEBMAIL = 'webmail'
    DISPOSABLE = 'disposable'
    UNKNOWN = 'unknown'


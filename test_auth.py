import json
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from jose import jwt, JWSError, JWTError

from auth import check_permissions, get_token_auth_header, AuthError, verify_decode_jwt, requires_auth_permission

JWT_WITH_MANAGER_ROLE_PERMISSIONS = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InBRTzU1ZEV2LUNlb3RUZllnNjlGcyJ9.eyJpc3MiOiJodHRwczovL21haGRpLXRvZG8udXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVmNGUzYmZkMjA3NmE3MDA2NzhmMGMzOCIsImF1ZCI6ImJhY2tlbmQiLCJpYXQiOjE1OTg5NjUyODMsImV4cCI6MTU5ODk3MjQ4MywiYXpwIjoiT3JsUWFHZ0FBcVJWbG1pd01EUWZ4WDRLVEl1dFBOVTAiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbInJlYWQ6YWxsLXVzZXJzIiwicmVhZDpvd24tdG9kb3MiLCJyZWFkOm93bi11c2VyIiwid3JpdGU6YWxsLXVzZXJzIiwid3JpdGU6b3duLXRvZG9zIiwid3JpdGU6b3duLXVzZXIiXX0.LIAGVag-4tgMuF4_vO4SC_6a_ohPcABps8YitfMS9o4cdfySJB9QtggasvJ36ktU76KX0G1XUB196A0BoZuZ78v2JqMqUCNuBJTym0huJI67fxzlci7NIqCI6kaT_jjuzZYDwrh2JlMlxJYtMVI7P-_O-JwwJebFH8CHC-ObQGXiu_UfUJZ85inwnLXVpGQ7QC_2SaJAN1vlmq9XHadD2gso0khNsZ1SxtHD3pUqnr0xWEyJBhuIufpT0CgYfpaoam1lmHoQT1sYpljjLCAe3eO4IxYTS2F7Dkg7LjD94DCrjMdmxZEMs4GLgZwI-rdS8VdfxgA2OVeNhSuoYoFaxw'
JWT_WITH_USER_ROLE_PERMISSIONS = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InBRTzU1ZEV2LUNlb3RUZllnNjlGcyJ9.eyJpc3MiOiJodHRwczovL21haGRpLXRvZG8udXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVmNGUzYzM1MTQ2MTYxMDA2ZDI1N2Q4MSIsImF1ZCI6ImJhY2tlbmQiLCJpYXQiOjE1OTg5NjUzMzgsImV4cCI6MTU5ODk3MjUzOCwiYXpwIjoiT3JsUWFHZ0FBcVJWbG1pd01EUWZ4WDRLVEl1dFBOVTAiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbInJlYWQ6b3duLXRvZG9zIiwicmVhZDpvd24tdXNlciIsIndyaXRlOm93bi10b2RvcyIsIndyaXRlOm93bi11c2VyIl19.ibVribVl2Zpcj2D6OvgY3dshN2zyG-9z8xjELl-CtGyKPa-j7mSPRfhTJhz7ufwDWHLXk7mY2PPnfKvQlDCNEw-q_67RtraXwYG7icGkArKdYW-laCHUR7yWHcPCvlVU9rRBsWvy4Ju7GBIgr-kFrz8PU-CabBLS0FFyexeYjfyQ9ikCwRrlMnJJ-4kiyVeCOoiPH2AGZ6jb6Yv9oYDbKqJWCGpnL8iaPA_ImH7cw2IMZcahiEZyJDZmOW3R7VriN9HsRW2swyfRWxCpgKSxFkJ-SiSwK08CVIu7AZpOEkV9YG2ngAsJO01aIPpXxKz1Cst0TQa_lb_Q7E7oTIfo2g'
AUTH0_KEY_1 = '{"alg": "RS256", "kty": "RSA", "use": "sig", "n": "7kXx5V3FhIp51jM5or7kEWIt9fa3JZkJJaLj6EcdLQ7O0gikYXzJgg3kD9h_Jh8Y0XcK2uowzAViek8Jk2yzZXd8UNWU7LVOVfP63VU3YBu-Z64pZSP1tn-omoJ4LSRXNUP_OUg4XzFon165UkYo71Ail-DXysm6ki0MUmndFYuK4Wxl98zliltyb1lsVXTx7l392U9HVYLvi91W0V1jhcrdlZ2vMplPCwtbQXYxIUwdQSiSfmr930j7UriP7G3Lp7hTNBAX74dwddGmLVaLhSyRupzwJtkClXiu-p5TFgGpBMDEwi9k-pB616-1Shl5UuShyMArJ4loQr3jFGOr8w", "e": "AQAB", "kid": "pQO55dEv-CeotTfYg69Fs", "x5t": "NrOT1auZUbQUJ20Jt4z7Sprz_mk", "x5c": ["MIIDCTCCAfGgAwIBAgIJDIFAP6eVJGOKMA0GCSqGSIb3DQEBCwUAMCIxIDAeBgNVBAMTF21haGRpLXRvZG8udXMuYXV0aDAuY29tMB4XDTIwMDgzMDA3MzQxNloXDTM0MDUwOTA3MzQxNlowIjEgMB4GA1UEAxMXbWFoZGktdG9kby51cy5hdXRoMC5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDuRfHlXcWEinnWMzmivuQRYi319rclmQklouPoRx0tDs7SCKRhfMmCDeQP2H8mHxjRdwra6jDMBWJ6TwmTbLNld3xQ1ZTstU5V8/rdVTdgG75nrillI/W2f6iagngtJFc1Q/85SDhfMWifXrlSRijvUCKX4NfKybqSLQxSad0Vi4rhbGX3zOWKW3JvWWxVdPHuXf3ZT0dVgu+L3VbRXWOFyt2Vna8ymU8LC1tBdjEhTB1BKJJ+av3fSPtSuI/sbcunuFM0EBfvh3B10aYtVouFLJG6nPAm2QKVeK76nlMWAakEwMTCL2T6kHrXr7VKGXlS5KHIwCsniWhCveMUY6vzAgMBAAGjQjBAMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFDBwt5VhsjcO/BNY2dUzig9wOel3MA4GA1UdDwEB/wQEAwIChDANBgkqhkiG9w0BAQsFAAOCAQEAk4b2zTQbWkteYj1A6e4kRlLLzOi0dpiA0H16GfXOkbyPJFgslCUV9osGuXOn6OIFdA1kCQl4OD/gvXAVwzVQ+AioyGRQmp+TKOtofqR7P/tSfUdm0sBHmUNx+unsBU7TleIit8eP839hE1BLK/N44wivfDLPqSNpsV5vG62xQyRsR9q1N93l9vbGVQsncBcYXn1/Dkcg7qLdPIV3JbmHZilCYUiwdkLTH95XSfFUcSXweTPXvpSUrnhTu/g9l1K8kxC38v+c+cTwoSqRBmecG5+DNxZuhApakh1rY2FqCN+vFlIlD3RSA2r6nwh2ZMxw7+5eWFhXF7itn2zyU8fe0A=="]}'
AUTH0_KEY_2 = '{"alg": "RS256", "kty": "RSA", "use": "sig", "n": "0binhf5-QjK4_80g45su4jZyeyY_0eBh-U6jvCq8NHSw36Xrwca0bQd5qmXYeF-AHQ45tskFDnlb5bds97bqoUqeWfqUPOmQyYjHKwooYRna-GOcvFnbOu_KberuXwKpQPO9Pod074kFey0NcxGiGwwpBzgIrfTnNA36VgqLMomKgeuRRdzlehoPi2f1sKFADTBMHucEB4hSj33ZUuvWsxCBmN7_B5MQlR9bH9QorSuyxfarfxeM2pjxjfySMcK5nCiPEi1P56fksbk7Otkzayiq8gA-cLrfUn7XBiGO-976XTHrRPLlhljG3Cjuevh9sIfEINMLkQh5WEaMZ4rpaw", "e": "AQAB", "kid": "8MUQzfGLcMkjqzDpL4nMk", "x5t": "c4BnwKVXKl8hHOVTHdozBgECctI", "x5c": ["MIIDCTCCAfGgAwIBAgIJKwW7j/WwFcGyMA0GCSqGSIb3DQEBCwUAMCIxIDAeBgNVBAMTF21haGRpLXRvZG8udXMuYXV0aDAuY29tMB4XDTIwMDgzMDA3MzQxNloXDTM0MDUwOTA3MzQxNlowIjEgMB4GA1UEAxMXbWFoZGktdG9kby51cy5hdXRoMC5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDRuKeF/n5CMrj/zSDjmy7iNnJ7Jj/R4GH5TqO8Krw0dLDfpevBxrRtB3mqZdh4X4AdDjm2yQUOeVvlt2z3tuqhSp5Z+pQ86ZDJiMcrCihhGdr4Y5y8Wds678pt6u5fAqlA870+h3TviQV7LQ1zEaIbDCkHOAit9Oc0DfpWCosyiYqB65FF3OV6Gg+LZ/WwoUANMEwe5wQHiFKPfdlS69azEIGY3v8HkxCVH1sf1CitK7LF9qt/F4zamPGN/JIxwrmcKI8SLU/np+SxuTs62TNrKKryAD5wut9SftcGIY773vpdMetE8uWGWMbcKO56+H2wh8Qg0wuRCHlYRoxniulrAgMBAAGjQjBAMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFJYHWFWTAPH1s6Jgcq3xddCriS4qMA4GA1UdDwEB/wQEAwIChDANBgkqhkiG9w0BAQsFAAOCAQEAKj0weRnCrQgS1ed7GAEYowHoOKCXBsxDqY06XFQTm3KrElKAf9JnJdCRt/ze60yHo0tnjBux1T1PvPYah7EqojTL44eiQ7tliqTtje1re2Z4FHZiu4TgBRu14d70KW5QaF/Tw8+h2fOtdT4kcV6gYhQGRE7EPhTGRit+XeugZYOtgaTyxIDWXFAX6RRpyrmrWHW/wScCk/H/5HSdiDNKvBZiHZaB5jbPNFN93abjDIE2SAowQ/RzH57tuSRfLPCH91MjDek+WpVmkVl65NfgTFdSks0SVxsQjrGK7S9GjzYOrDCxsn6MDnRgMGZ2kmHwzfkf8wE3LK9aGXHKIpm5ig=="]}'
DECODED_PAYLOAD_OF_MANAGER_TOKEN = '{"iss": "https://mahdi-todo.us.auth0.com/", "sub": "auth0|5f4e3bfd2076a700678f0c38", "aud": "backend", "iat": 1598965283, "exp": 1598972483, "azp": "OrlQaGgAAqRVlmiwMDQfxX4KTIutPNU0", "scope": "", "permissions": ["read:all-users", "read:own-todos", "read:own-user", "write:all-users", "write:own-todos", "write:own-user"]}'
DECODED_PAYLOAD_OF_USER_TOKEN = '{"iss": "https://mahdi-todo.us.auth0.com/", "sub": "auth0|5f4e3c35146161006d257d81", "aud": "backend", "iat": 1598965338, "exp": 1598972538, "azp": "OrlQaGgAAqRVlmiwMDQfxX4KTIutPNU0", "scope": "", "permissions": ["read:own-todos", "read:own-user", "write:own-todos", "write:own-user"]}'

original_jwt_decode = jwt.decode


def jwt_decode_mock(token, algorithms, audience, key):
    if key == json.loads(AUTH0_KEY_1):
        if token == JWT_WITH_MANAGER_ROLE_PERMISSIONS and algorithms == ['RS256'] and audience == 'backend':
            return json.loads(DECODED_PAYLOAD_OF_MANAGER_TOKEN)
        if token == JWT_WITH_USER_ROLE_PERMISSIONS and algorithms == ['RS256'] and audience == 'backend':
            return json.loads(DECODED_PAYLOAD_OF_USER_TOKEN)
    if key == json.loads(AUTH0_KEY_2):
        raise JWTError(JWSError('Signature verification failed.'))
    return original_jwt_decode(token, algorithms=algorithms, audience=audience, key=key)


class AuthTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_check_permissions_fails_when_permission_is_not_included_in_payload(self):
        payload = {
            "permissions": []
        }
        permission = 'read:own-todos'
        with self.assertRaises(AuthError):
            check_permissions(permission, payload)

    def test_check_permissions_succeeds_when_permission_is_included_in_payload(self):
        payload = {
            "permissions": [
                'read:own-todos'
            ]
        }
        permission = 'read:own-todos'
        result = check_permissions(permission, payload)
        self.assertTrue(result)

    def test_get_token_auth_header_returns_the_token(self):
        request_mock = MagicMock()
        request_mock.headers = {'Authorization': f'Bearer {JWT_WITH_MANAGER_ROLE_PERMISSIONS}'}
        with patch('auth.request', request_mock):
            token = get_token_auth_header()
            self.assertEqual(token, JWT_WITH_MANAGER_ROLE_PERMISSIONS)

    def test_get_token_auth_header_fails_when_token_not_present(self):
        request_mock = MagicMock()
        request_mock.headers = {}
        with patch('auth.request', request_mock):
            with self.assertRaises(AuthError):
                get_token_auth_header()

    def test_verify_decode_jwt(self):
        mock = MagicMock(side_effect=jwt_decode_mock)
        with patch('auth.jwt.decode', mock):
            result = verify_decode_jwt(JWT_WITH_MANAGER_ROLE_PERMISSIONS)
            self.assertIn('read:all-users', result['permissions'])

    def test_requires_auth_annotation_passes_when_the_request_has_the_required_permissions(self):
        decode_mock = MagicMock(side_effect=jwt_decode_mock)
        request_mock = MagicMock()
        request_mock.headers = {'Authorization': f'Bearer {JWT_WITH_MANAGER_ROLE_PERMISSIONS}'}

        with patch('auth.jwt.decode', decode_mock):
            with patch('auth.request', request_mock):
                @requires_auth_permission('read:own-todos')
                def test_function(token_payload):
                    if 'read:own-todos' in token_payload['permissions']:
                        return 'passes'
                    else:
                        return 'fails'

                result = test_function()
                self.assertEqual('passes', result)

    def test_requires_auth_annotation_fails_when_the_request_does_not_have_the_required_permissions(self):
        decode_mock = MagicMock(side_effect=jwt_decode_mock)
        request_mock = MagicMock()
        request_mock.headers = {}

        with patch('auth.jwt.decode', decode_mock):
            with patch('auth.request', request_mock):
                @requires_auth_permission('read:own-todos')
                def test_function(token_payload):
                    if 'read:own-todos' in token_payload['permissions']:
                        return 'passes'
                    else:
                        return 'fails'

                with self.assertRaises(AuthError):
                    test_function()
                    self.fail("Shouldn't reach here")

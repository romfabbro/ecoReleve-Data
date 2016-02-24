# from __future__ import absolute_import

# __ver_major__ = 0
# __ver_minor__ = 1
# __ver_patch__ = 2
# __ver_sub__ = ""
# __ver_tuple__ = (__ver_major__, __ver_minor__, __ver_patch__, __ver_sub__)
# __version__ = "%d.%d.%d%s" % __ver_tuple__

# import sys
# import functools

# from datetime import datetime
# from calendar import timegm

# from zope.interface import implementer

# from pyramid.interfaces import IAuthenticationPolicy
# from pyramid.security import Everyone, Authenticated
# from pyramid.authorization import ACLAuthorizationPolicy
# from pyramid.httpexceptions import HTTPUnauthorized
# from pyramid.util import DottedNameResolver

# import jwt

# from .utils import parse_authz_header, normalize_request_object
# from ..pyramid_jwtauth.JWTAuthTktCookieHelper import JWTAuthTktCookieHelper


# def parse_authz_header(request, *default):

#     #return request.cookies.get("ecoReleve-Core")
#     return request.cookies.get("user_id")

# @implementer(IAuthenticationPolicy)
# class JWTAuthenticationPolicy(object):

#     """Pyramid Authentication Policy implementing JWT Access Auth.

#     This class provides an IAuthenticationPolicy implementation based on
#     signed requests, using the JSON Web Token Authentication standard.

#     The plugin can be customized with the following arguments:

#         * find_groups:  a callable taking a userid and a Request object, and
#                         returning a list of the groups that userid is a
#                         member of.

#         * master_secret:  a secret known only by the server, used for signing
#                           JWT auth tokens in the default implementation.

#         * private_key:  An RSA private_key
#         * private_key_file: a file holding an RSA encoded (PEM/DER) key file.

#         * public_key:  An RSA public_key
#         * public_key_file: a file holding an RSA encoded (PEM/DER) key file.

#         * algorithm:  The algorithm used to sign the key (defaults to HS256)

#         * leeway:  The default leeway (as a datetime.timedelta). Defaults to
#                    None

#         * userid_in_claim: The claim that the userid can be found in.  Normally
#                            this is the 'sub' claim of the JWT, but this can
#                            be overridden here.  This is used in
#                            authenticated_userid() and related functions.

#         * scheme: The scheme name used in the ``Authorization`` header. JWT
#           implementations vary in their use of ``JWT`` (our default) or
#           ``Bearer``.

#     The following configuration options are to DISABLE the verification options
#     in the PyJWT decode function.  If the app configures this then it OUGHT to
#     ensure that the claim is verified IN the application.

#         * decode_options (these are passed to the __init__() = undefined OR {}
#           with the following keys (these are the defaults):

#             options = {
#                'verify_signature': True,
#                'verify_exp': True,
#                'verify_nbf': True,
#                'verify_iat': True,
#                'verify_aud': True
#             }

#           i.e to switch off audience checking, pass 'verify_aud': True in
#           decode_options.

#           These are passed as the following as part of the ini options/settings

#           jwtauth.disable_verify_signature = true (default false)
#           jwtauth.disable_verify_exp = true (default false)
#           jwtauth.disable_verify_nbf = true (default false)
#           jwtauth.disable_verify_iat = true (default false)
#           jwtauth.disable_verify_aud = true (default false)

#           NOTE: they are reversed between the settings vs the __init__().

#     The library takes either a master_secret or private_key/public_key pair.
#     In the later case the algorithm must be an RS* version.
#     """

#     # The default value of master_secret is None, which will cause the library
#     # to generate a fresh secret at application startup.
#     master_secret = None

#     def __init__(self,
#                  find_groups=None,
#                  master_secret=None,
#                  private_key=None,
#                  private_key_file=None,
#                  public_key=None,
#                  public_key_file=None,
#                  algorithm='HS256',
#                  leeway=None,
#                  userid_in_claim=None,
#                  scheme='JWT',
#                  decode_options=None):
#         if find_groups is not None:
#             self.find_groups = find_groups
#         if master_secret is not None:
#             self.master_secret = master_secret
#         self.private_key = private_key
#         if private_key_file is not None:
#             with open(private_key_file, 'r') as rsa_priv_file:
#                 self.private_key = rsa_priv_file.read()
#         self.public_key = public_key
#         if public_key_file is not None:
#             with open(public_key_file, 'r') as rsa_pub_file:
#                 self.public_key = rsa_pub_file.read()
#         self.algorithm = algorithm
#         if leeway is not None:
#             self.leeway = leeway
#         else:
#             self.leeway = 0
#         if userid_in_claim is not None:
#             self.userid_in_claim = userid_in_claim
#         else:
#             self.userid_in_claim = 'sub'
#         self.scheme = scheme
#         self.decode_options = decode_options

#         self.cookie = JWTAuthTktCookieHelper(
#             secret = "test"
#         )


#     @classmethod
#     def from_settings(cls, settings={}, prefix="jwtauth.", **extra):
#         """Construct a JWTAuthenticationPolicy from deployment settings.

#         This is a helper function for loading a JWTAuthenticationPolicy from
#         settings provided in the pyramid application registry.  It extracts
#         settings with the given prefix, converts them to the appropriate type
#         and passes them into the constructor.
#         """
#         # Grab out all the settings keys that start with our prefix.
#         jwtauth_settings = {}
#         for name in settings:
#             if not name.startswith(prefix):
#                 continue
#             jwtauth_settings[name[len(prefix):]] = settings[name]
#         # Update with any additional keyword arguments.
#         jwtauth_settings.update(extra)
#         # Pull out the expected keyword arguments.
#         kwds = cls._parse_settings(jwtauth_settings)
#         # Error out if there are unknown settings.
#         for unknown_setting in jwtauth_settings:
#             raise ValueError("unknown jwtauth setting: %s" % unknown_setting)
#         # And finally we can finally create the object.
#         return cls(**kwds)


#     def remember(self, request, principal, **kw):
#         """Get headers to remember to given principal identity.

#         This is a no-op for this plugin; the client is supposed to remember
#         its MAC credentials and use them for all requests.
#         """
#         return self.cookie.remember(request, principal, **kw)

#     def forget(self, request):

#         return self.cookie.forget(request)
#         #return [("WWW-Authenticate", self.scheme)]

#     def challenge(self, request, content="Unauthorized"):
#         print("challenge_______________")
#         """Challenge the user for credentials.

#         This method returns a 401 response using the WWW-Authenticate field
#         as constructed by forget().  You might like to use it as pyramid's
#         "forbidden view" when using this auth policy.
#         """
#         return HTTPUnauthorized(content, headers=self.forget(request))

#     def decode_jwt(self, request, jwtauth_token,
#                    leeway=None, verify=True, options=None):
#         """Decode a JWTAuth token into its claims.

#         This method deocdes the given JWT to provide the claims.  The JWT can
#         fail if the token has expired (with appropriate leeway) or if the
#         token won't validate due to the secret (key) being wrong.

#         If the JWT doesn't verify then a number of Exceptions can be raised:
#             DecodeError() - if the algorithm in the token isn't supported.
#             DecodeError() - if the secret doesn't match (key, etc.)
#             ExpiredSignature() - if the 'exp' claim has expired.

#         If private_key/public key is set then the public_key will be used to
#         decode the key.

#         Note that the 'options' value is normally None, as this function is
#         usually called via the (un)authenticated_userid() which is called by
#         the framework.  Thus the decode 'options' are set as part of
#         configuring the module through Pyramid settings.

#         :param request: the Pyramid Request object
#         :param jwtauth_token: the string (bString - Py3) - of the full token
#                               to decode
#         :param leeway: Integer - the number of seconds of leeway to pass to
#                        jwt.decode()
#         :param verify: Boolean - True to verify - passed to jwt.decode()
#         :param options: set of options for what to verify.
#         """
#         if leeway is None:
#             leeway = self.leeway
#         if self.public_key is not None:
#             key = self.public_key
#         else:
#             key = self.master_secret
#         _options = self.decode_options or {}
#         if options:
#             _options.update(options)
#         if len(_options.keys()) == 0:
#             _options = None
#         claims = jwt.decode(jwtauth_token,
#                             key=key,
#                             leeway=leeway,
#                             verify=verify,
#                             options=_options)
#         return claims

#     def encode_jwt(self, request, claims, key=None, algorithm=None):
#         """Encode a set of claims into a JWT token.

#         This is just a proxy for jwt.encode() but uses the default
#         master_secret that may have been set in configuring the library.

#         If the private_key is set then self.private_key is used for the encode
#         (assuming key = None!)  algorithm also has to be an RS* algorithm and
#         if not set, then self.algorithm is used.
#         """
#         if key is None:
#             if self.private_key is not None:
#                 key = self.private_key
#             else:
#                 key = self.master_secret
#         if algorithm is None:
#             algorithm = self.algorithm
#         # fix for older version of PyJWT which doesn't covert all of the time
#         # claims.  This won't be needed in the future.
#         encode_claims = maybe_encode_time_claims(claims)

#         jwtauth_token = jwt.encode(encode_claims, key=key, algorithm=algorithm)
#         return jwtauth_token

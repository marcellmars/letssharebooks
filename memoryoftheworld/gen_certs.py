import subprocess
import os
import glob
import shutil
import local_env as G

TEMP_OUTPUT = "secrets/templates"
SECRETS = "secrets"

OPENSSL_CA_CNF = '''
HOME            = .
RANDFILE        = $ENV::HOME/.rnd

####################################################################
[ ca ]
default_ca  = CA_default         # The default ca section

[ CA_default ]

default_days      = 1000         # how long to certify for
default_crl_days  = 30           # how long before next CRL
default_md        = sha256       # use public key default MD
preserve          = no           # keep passed DN ordering

x509_extensions = ca_extensions  # The extensions to add to the cert

email_in_dn     = no             # Don't concat the email in the DN
copy_extensions = copy           # Required to copy SANs from CSR to cert

####################################################################
[ req ]
default_bits        = 4096
default_keyfile     = {0}/cakey.pem
distinguished_name  = ca_distinguished_name
x509_extensions     = ca_extensions
string_mask         = utf8only

####################################################################
[ ca_distinguished_name ]
countryName             = Country Name (2 letter code)
stateOrProvinceName     = State or Province Name (full name)
localityName            = Locality Name (eg, city)
organizationName        = Organization Name (eg, company)
organizationalUnitName  = Organizational Unit (eg, division)
commonName              = Common Name (e.g. server FQDN or YOUR name)
emailAddress            = Email Address

####################################################################
[ ca_extensions ]

subjectKeyIdentifier    = hash
authorityKeyIdentifier  = keyid:always, issuer
basicConstraints        = critical, CA:true
keyUsage                = keyCertSign, cRLSign
'''.format(TEMP_OUTPUT)

OPENSSL_CA_EXT_CNF = '''
HOME            = .
RANDFILE        = $ENV::HOME/.rnd

####################################################################
[ ca ]
default_ca  = CA_default         # The default ca section

[ CA_default ]

default_days      = 1000         # how long to certify for
default_crl_days  = 30           # how long before next CRL
default_md        = sha256       # use public key default MD
preserve          = no           # keep passed DN ordering

x509_extensions = ca_extensions  # The extensions to add to the cert

email_in_dn     = no             # Don't concat the email in the DN
copy_extensions = copy           # Required to copy SANs from CSR to cert

certificate     = {0}/cacert.pem # The CA certifcate
private_key     = {0}/cakey.pem  # The CA private key
new_certs_dir   = {0}            # Location for new certs
database        = {0}/index.txt  # Database index file
serial          = {0}/serial.txt # The current serial number

unique_subject  = no             # Set to 'no' to allow creation of
                                 # several certificates with same subject.

####################################################################
[ req ]
default_bits        = 4096
default_keyfile     = {0}/cakey.pem
distinguished_name  = ca_distinguished_name
x509_extensions     = ca_extensions
string_mask         = utf8only

####################################################################
[ ca_distinguished_name ]
countryName             = Country Name (2 letter code)
stateOrProvinceName     = State or Province Name (full name)
localityName            = Locality Name (eg, city)
organizationName        = Organization Name (eg, company)
organizationalUnitName  = Organizational Unit (eg, division)
commonName              = Common Name (e.g. server FQDN or YOUR name)
emailAddress            = Email Address

####################################################################
[ ca_extensions ]

subjectKeyIdentifier    = hash
authorityKeyIdentifier  = keyid:always, issuer
basicConstraints        = critical, CA:true
keyUsage                = keyCertSign, cRLSign

####################################################################
[ signing_policy ]
countryName             = optional
stateOrProvinceName     = optional
localityName            = optional
organizationName        = optional
organizationalUnitName  = optional
commonName              = supplied
emailAddress            = optional

####################################################################
[ signing_req ]
subjectKeyIdentifier    = hash
authorityKeyIdentifier  = keyid,issuer

basicConstraints        = CA:FALSE
keyUsage                = digitalSignature, keyEncipherment
'''.format(TEMP_OUTPUT)

OPENSSL_SERVER_CNF = '''
HOME            = .
RANDFILE        = $ENV::HOME/.rnd

####################################################################
[ req ]
default_bits         = 2048
default_keyfile      = {0}/{1}.key
distinguished_name   = server_distinguished_name
req_extensions       = server_req_extensions
string_mask          = utf8only

####################################################################
[ server_distinguished_name ]
countryName          = Country Name (2 letter code)
stateOrProvinceName  = State or Province Name (full name)
localityName         = Locality Name (eg, city)
organizationName     = Organization Name (eg, company)
commonName           = Common Name (e.g. server FQDN or YOUR name)
emailAddress         = Email Address

####################################################################
[ server_req_extensions ]

subjectKeyIdentifier = hash
basicConstraints     = CA:FALSE
keyUsage             = digitalSignature, keyEncipherment
subjectAltName       = @alternate_names
nsComment            = "OpenSSL Generated Certificate"

####################################################################
[ alternate_names ]

DNS.1       = {1}
DNS.2       = *.{1}
'''.format(SECRETS, G.LSB_DOMAIN)


map(os.remove, glob.glob("{}/*".format(TEMP_OUTPUT)))

with open("{}/index.txt".format(TEMP_OUTPUT), "w") as f:
    f.write("")

with open('{}/serial.txt'.format(TEMP_OUTPUT), 'w') as f:
    f.write('01')


for cnf in ['OPENSSL_CA_CNF', 'OPENSSL_SERVER_CNF', 'OPENSSL_CA_EXT_CNF']:
    with open('{}/{}'.format(TEMP_OUTPUT, cnf), 'w') as f:
        f.write(eval(cnf))

CA = ['openssl', 'req',
      '-x509',
      '-config', '{}/OPENSSL_CA_CNF'.format(TEMP_OUTPUT),
      '-subj', '/C={C}/ST={ST}/L={L}/O={O}/OU={OU}/CN={CN}'
               .format(**G.SELF_SIGN),
      '-newkey', 'rsa:4096', '-sha256',
      '-nodes',
      '-out', '{}/cacert.pem'.format(TEMP_OUTPUT),
      '-outform', 'PEM']

SERVER = ['openssl', 'req',
          '-config', '{}/OPENSSL_SERVER_CNF'.format(TEMP_OUTPUT),
          '-newkey', 'rsa:4096', '-sha256',
          '-nodes',
          '-subj', '/C={C}/ST={ST}/L={L}/O={O}/OU={OU}/CN={CN}'
                   .format(**G.SELF_SIGN),
          '-out', '{}/servercert.csr'.format(TEMP_OUTPUT),
          '-outform', 'PEM']

CA_SIGN = ['openssl', 'ca',
           '-config', '{}/OPENSSL_CA_EXT_CNF'.format(TEMP_OUTPUT),
           '-policy', 'signing_policy',
           '-extensions', 'signing_req',
           '-out', '{}/{}.crt'.format(SECRETS, G.LSB_DOMAIN),
           '-infiles', '{}/servercert.csr'.format(TEMP_OUTPUT)]

subprocess.call(CA)
subprocess.call(SERVER)

yes = subprocess.Popen('yes',
                       stdout=subprocess.PIPE)

ca_sign = subprocess.Popen(CA_SIGN,
                           stdin=yes.stdout,
                           stdout=subprocess.PIPE)

yes.kill()

shutil.copyfile('{}/cacert.pem'.format(TEMP_OUTPUT),
                'nginx/static_web/candy/cacert.pem')

import subprocess
import os
import glob
import shutil
import sys
import optparse
import tempfile

TMP_OUT = tempfile.mkdtemp()
SECRETS = "secrets"

DISTINGUISHED_NAME = {"domain": "example.com",
                      "C": "US",
                      "ST": "Maryland",
                      "L": "Baltimore",
                      "O": "Foobars of the World",
                      "OU": "[let's generate certs]",
                      "CN": "example.com"}


def get_cnfs():
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

    ####################################################################
    [ ca_extensions ]

    subjectKeyIdentifier    = hash
    authorityKeyIdentifier  = keyid:always, issuer
    basicConstraints        = critical, CA:true
    keyUsage                = keyCertSign, cRLSign
    '''.format(TMP_OUT)

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

    ####################################################################
    [ signing_req ]
    subjectKeyIdentifier    = hash
    authorityKeyIdentifier  = keyid,issuer

    basicConstraints        = CA:FALSE
    keyUsage                = digitalSignature, keyEncipherment
    '''.format(TMP_OUT)

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
    '''.format(SECRETS, DISTINGUISHED_NAME['domain'])

    return [['OPENSSL_CA_CNF', OPENSSL_CA_CNF],
            ['OPENSSL_CA_EXT_CNF', OPENSSL_CA_EXT_CNF],
            ['OPENSSL_SERVER_CNF', OPENSSL_SERVER_CNF]]


def prepare_files():
    if not os.path.exists(SECRETS):
        os.makedirs(SECRETS)
    elif not os.path.isdir(SECRETS):
        m = "Check if the paths for the output are \
        colliding with existing files."
        sys.exit(m)

    map(os.remove, glob.glob("{}/*".format(TMP_OUT)))

    with open("{}/index.txt".format(TMP_OUT), "w") as f:
        f.write("")

    with open('{}/serial.txt'.format(TMP_OUT), 'w') as f:
        f.write('01')

    for cnf in get_cnfs():
        with open('{}/{}'.format(TMP_OUT, cnf[0]), 'w') as f:
            f.write(cnf[1])


def generate_certs():
    prepare_files()
    subprocess.call(['openssl', 'req',
                     '-x509',
                     '-config', '{}/OPENSSL_CA_CNF'.format(TMP_OUT),
                     '-subj', '/C={C}/ST={ST}/L={L}/O={O}/OU={OU}/CN={CN}'
                     .format(**DISTINGUISHED_NAME),
                     '-newkey', 'rsa:4096', '-sha256',
                     '-nodes',
                     '-out', '{}/cacert.pem'.format(TMP_OUT),
                     '-outform', 'PEM'])

    subprocess.call(['openssl', 'req',
                     '-config', '{}/OPENSSL_SERVER_CNF'.format(TMP_OUT),
                     '-newkey', 'rsa:4096', '-sha256',
                     '-nodes',
                     '-subj', '/C={C}/ST={ST}/L={L}/O={O}/OU={OU}/CN={CN}'
                     .format(**DISTINGUISHED_NAME),
                     '-out', '{}/servercert.csr'.format(TMP_OUT),
                     '-outform', 'PEM'])

    yes = subprocess.Popen('yes',
                           stdout=subprocess.PIPE)

    c = subprocess.Popen(['openssl', 'ca',
                          '-config', '{}/OPENSSL_CA_EXT_CNF'.format(TMP_OUT),
                          '-policy', 'signing_policy',
                          '-extensions', 'signing_req',
                          '-out', '{}/{}.crt'.format(SECRETS, DISTINGUISHED_NAME['domain']),
                          '-infiles', '{}/servercert.csr'.format(TMP_OUT)],
                         stdin=yes.stdout,
                         stdout=subprocess.PIPE)

    yes.kill()
    c.communicate()
    shutil.copyfile('{}/cacert.pem'.format(TMP_OUT),
                    '{}/{}_cacert.pem'.format(SECRETS, DISTINGUISHED_NAME['domain']))


def remove_files():
    map(os.remove, glob.glob("{}/*".format(TMP_OUT)))
    os.rmdir(TMP_OUT)
    [os.remove(f) for f in glob.glob("{}/*".format(SECRETS))
     if f not in ["{}/{}.key".format(SECRETS, DISTINGUISHED_NAME['domain']),
                  "{}/{}.crt".format(SECRETS, DISTINGUISHED_NAME['domain']),
                  "{}/{}_cacert.pem".format(SECRETS, DISTINGUISHED_NAME['domain'])]]


def print_info():
    print("Domain: {}".format(DISTINGUISHED_NAME['domain']))
    print("Domain info:")
    print("    Common name      : {}".format(DISTINGUISHED_NAME['CN']))
    print("    Organization     : {}".format(DISTINGUISHED_NAME['O']))
    print("    Organization unit: {}".format(DISTINGUISHED_NAME['OU']))
    print("    Country          : {}".format(DISTINGUISHED_NAME['C']))
    print("    State or province: {}".format(DISTINGUISHED_NAME['ST']))
    print("    Location or city : {}".format(DISTINGUISHED_NAME['L']))
    print("\nIf you want to add info via command line args first run it with --help flag.")


def main():
    generate_certs()
    remove_files()


if __name__ == '__main__':
    p = optparse.OptionParser()
    p.add_option('-d', '--domain-name',
                 help="Main domain (e.g. example.com)")
    p.add_option('-c','--country',
                 help="Country Name (2 letter code)")
    p.add_option('-s', '--state',
                 help="State or Province Name (full name)")
    p.add_option('-l', '--location',
                 help="Locality Name (eg, city)")
    p.add_option('-o', '--organization',
                 help="Organization Name (eg, company)")
    p.add_option('-u', '--organization-unit',
                 help="Organizational Unit (eg, division)")
    p.add_option('-n', '--common-name', help="Common Name (e.g. server FQDN or YOUR name)")

    (options, remainder) = p.parse_args()

    if len(sys.argv) > 1:
        if options.domain_name is None:
            print("You should provide at least a main domain name (if using flags).")
            print("If there is no flags, info written in {} is used. Change it if you prefer hardcoding it into file.".format(sys.argv[0]))
            print("Or use flags:\n")
            p.print_help()
            sys.exit(1)

        DISTINGUISHED_NAME['domain'] = options.domain_name
        DISTINGUISHED_NAME['C'] = options.country or ""
        DISTINGUISHED_NAME['ST'] = options.state or ""
        DISTINGUISHED_NAME['L'] = options.location or ""
        DISTINGUISHED_NAME['O'] = options.organization or ""
        DISTINGUISHED_NAME['OU'] = options.organization_unit or ""
        DISTINGUISHED_NAME['CN'] = options.common_name or options.domain_name
        print_info()
    else:
        print("Generating certs by using info written in {}:".format(sys.argv[0]))
        print_info()

    main()

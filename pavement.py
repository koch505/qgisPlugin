from cStringIO import StringIO
import ConfigParser
from datetime import date, datetime
import fnmatch
import os
from paver.easy import *
# this pulls in the sphinx target
from paver.doctools import html
import xmlrpclib
import zipfile

def base_excludes():
    return [
        '.DS_Store',  # on Mac
        '*.pyc',
        'gisdata*'
    ]

def full_excludes():
    excl = base_excludes()
    excl.extend([
        'test',
        'test-output',
        'ext-src',
        'coverage*',
        'nose*',
    ])
    return excl

options(
    plugin = Bunch(
        name = 'opengeo',
        ext_libs = path('src/opengeo/ext-libs'),
        ext_src = path('src/opengeo/ext-src'),
        source_dir = path('src/opengeo'),
        package_dir = path('.'),
        base_excludes = base_excludes(),
        excludes = full_excludes(),
        # skip certain files inadvertently found by exclude pattern globbing
        skip_exclude = ['coverage.xsd']
    ),

    # Default Server Params (can be overridden)
    plugin_server = Bunch(
        server = 'qgis.boundlessgeo.com',
        port = 80,
        protocol = 'http',
        end_point = '/RPC2/'
    ),

    sphinx = Bunch(
        docroot = 'doc',
        sourcedir = 'source',
        builddir = 'build'
    )
)



@task
@cmdopts([
    ('clean', 'c', 'clean out dependencies first'),
    ('develop', 'd', 'do not alter source dependency git checkouts'),
])
def setup(options):
    '''install dependencies'''
    clean = getattr(options, 'clean', False)
    develop = getattr(options, 'develop', False)
    ext_libs = options.plugin.ext_libs
    ext_src = options.plugin.ext_src
    if clean:
        ext_libs.rmtree()
    ext_libs.makedirs()
    runtime, test = read_requirements()
    os.environ['PYTHONPATH']=ext_libs.abspath()
    for req in runtime + test:
        if req.startswith('-e'):
            if not develop:
                # use pip to just process the URL and fetch it in to place
                sh('pip install --no-install --src=%s %s' % (ext_src, req))
            # now change the req to be the location installed to
            # and easy_install will do the rest
            urlspec, req = req.split('#egg=')
            req = ext_src / req
        sh('easy_install -a -d %(ext_libs)s %(dep)s' % {
            'ext_libs' : ext_libs.abspath(),
            'dep' : req
        })


def read_requirements():
    '''return a list of runtime and list of test requirements'''
    lines = open('requirements.txt').readlines()
    lines = [ l for l in [ l.strip() for l in lines] if l ]
    divider = '# test requirements'
    try:
        idx = lines.index(divider)
    except ValueError:
        raise BuildFailure('expected to find "%s" in requirements.txt' % divider)
    not_comments = lambda s,e: [ l for l in lines[s:e] if l[0] != '#']
    return not_comments(0, idx), not_comments(idx+1, None)


@task
def install(options):
    '''install plugin to qgis'''
    plugin_name = options.plugin.name
    src = path(__file__).dirname() / 'src' / plugin_name
    dst = path('~').expanduser() / '.qgis2' / 'python' / 'plugins' / plugin_name
    src = src.abspath()
    dst = dst.abspath()
    if not hasattr(os, 'symlink'):        
        dst.rmtree()
        src.copytree(dst)
    elif not dst.exists():
        src.symlink(dst)


@task
def package(options):
    '''create filtered package for plugin release'''
    package_file = options.plugin.package_dir / ('%s.zip' % options.plugin.name)
    with zipfile.ZipFile(package_file, "w", zipfile.ZIP_DEFLATED) as zip:
        make_zip(zip, options)
    return package_file

@task
def package_with_tests(options):
    '''create filtered package for plugin that includes the test suite'''
    package_file = options.plugin.package_dir / ('%s.zip' % options.plugin.name)
    with zipfile.ZipFile(package_file, "w", zipfile.ZIP_DEFLATED) as zip:
        make_zip(zip, options, basefilters=True)
    return package_file

def make_zip(zip, options, basefilters=False):
    excludes = set(
        options.plugin.base_excludes if basefilters else options.plugin.excludes
    )
    skips = options.plugin.skip_exclude

    src_dir = options.plugin.source_dir
    exclude = lambda p: any([fnmatch.fnmatch(p, e) for e in excludes])

    def filter_excludes(root, items):
        if not items: return []
        # to prevent descending into dirs, modify the list in place
        for item in list(items):  # copy list or iteration values change
            itempath = path(os.path.relpath(root, 'src')) / item
            if exclude(item) and item not in skips:
                debug('excluding %s' % itempath)
                items.remove(item)
        return items

    for root, dirs, files in os.walk(src_dir):
        for f in filter_excludes(root, files):
            relpath = os.path.relpath(root, 'src')
            zip.write(path(root) / f, path(relpath) / f)
        filter_excludes(root, dirs)


@task
@cmdopts([
    ('user=', 'u', 'upload user'),
    ('passwd=', 'p', 'upload password'),
    ('server=', 's', 'alternate server'),
    ('end_point=', 'e', 'alternate endpoint'),
    ('port=', 't', 'alternate port'),
])
def upload(options):
    '''upload the package to the server'''
    package_file = package(options)
    user, passwd = getattr(options, 'user', None), getattr(options, 'passwd', None)
    if not user or not passwd:
        raise BuildFailure('provide user and passwd options to upload task')
    # create URL for XML-RPC calls
    s = options.plugin_server
    server, end_point, port = getattr(options, 'server', None), getattr(options, 'end_point', None), getattr(options, 'port', None)
    if server == None:
        server = s.server
    if end_point == None:
        end_point = s.end_point
    if port == None:
        port = s.port
    uri = "%s://%s:%s@%s:%s%s" % (s.protocol, options['user'], options['passwd'], server, port, end_point)
    info('uploading to %s', uri)
    server = xmlrpclib.ServerProxy(uri, verbose=False)
    try:
        pluginId, versionId = server.plugin.upload(xmlrpclib.Binary(package_file.bytes()))
        info("Plugin ID: %s", pluginId)
        info("Version ID: %s", versionId)
        package_file.unlink()
    except xmlrpclib.Fault, err:
        error("A fault occurred")
        error("Fault code: %d", err.faultCode)
        error("Fault string: %s", err.faultString)
    except xmlrpclib.ProtocolError, err:
        error("Protocol error")
        error("%s : %s", err.errcode, err.errmsg)
        if err.errcode == 403:
            error("Invalid name and password?")

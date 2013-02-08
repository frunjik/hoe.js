from glob import glob

DOIT_CONFIG = {
    'default_tasks': ['check', 'test'],
    'verbosity': 2,
    }


MOCHA_CMD = 'node_modules/mocha/bin/mocha --ui tdd'
HOE_JS = 'src/hoe.js'


def task_check():
    """static checker using jshint"""
    for js_file in (HOE_JS, 'test/test.js'):
        yield {
            'name': js_file,
            'actions': ['jshint --config hint.json ' + js_file],
            'file_dep': ['hint.json', js_file],
            }


def task_test():
    """run unit-tests using mocha"""
    return {
        'actions': [
            MOCHA_CMD + ' --colors --reporter spec'],
        'file_dep': [HOE_JS, 'test/test.js'],
        }

def task_testdoc():
    """run unit-tests using mocha"""
    return {
        'actions': [
            MOCHA_CMD + ' --reporter doc > test/result.html'],
        'file_dep': [HOE_JS, 'test/test.js'],
        }

def task_coverage():
    """annotate for coverage and run tests"""
    yield {
        'name': 'annotate',
        'actions': ['jscoverage --no-highlight src coverage'],
        'file_dep': [HOE_JS],
        'targets': ['coverage/hoe.js'],
        }
    # XXX no reasonable terminal coverage result
    # XXX doesnt report tests failed
    yield {
        'name': 'test',
        'actions': [
            MOCHA_CMD + ' --require setup_cov.js --reporter html-cov > coverage/result.html',
            'echo "check results in coverage/result.html"'
            ],
        'file_dep': ['coverage/hoe.js', 'test/test.js'],
        'targets': ['coverage/result.html'],
        'verbosity': 2,
        }


def task_apidoc():
    """generate API docs using jsdoc"""
    return {
        'actions': ['jsdoc --directory=api src/hoe.js'],
        'file_dep': [HOE_JS],
        }

def task_tutorial():
    """create tutorial from TodoMVC using docco"""
    return {
        'actions': ['docco sample_todomvc/app.js --output tutorial'],
        'file_dep': [HOE_JS, 'sample_todomvc/app.js'],
        'targets': ['tutorial'],
        }

def task_readme():
    """convert README.md into html"""
    return {
        'actions': ['markdown_py README.md > README.html'],
        'file_dep': ['README.md'],
        'targets': ['README.hmtl'],
        }


def task_dist():
    """create distribution files"""
    version = '0.2.0'
    version_comment = "// hoe.js version: %s" % version
    yield {
        'name': 'min',
        'actions': [
            'echo  "' + version_comment + '" > %(targets)s',
            ('uglifyjs2 %(dependencies)s ' +
             '--mangle --compress --comments >> %(targets)s'),
            ],
        'file_dep': [HOE_JS],
        'targets': ['dist/hoe-' + version + '.min.js'],
        'clean': True,
        }

    yield {
        'name': 'dev',
        'actions': [
            'echo  "' + version_comment + '" > %(targets)s',
            'cat %(dependencies)s >> %(targets)s',
            ],
        'file_dep': [HOE_JS],
        'targets': ['dist/hoe-' + version + '.js'],
        'clean': True,
        }


# TODO dev_setup
# sudo apt-get install nodejs
# npm install mocha
# npm install chai
# npm install jquery
# npm install -g jshint
# npm install -g docco
# npm install -g uglify-js2
# sudo apt-get install jscoverage
# sudo apt-get install jsdoc-toolkit


####################### site
def task_site():
    """create full html pages from html fragments from site/doc"""
    head = 'site/template/head.html'
    foot = 'site/template/foot.html'

    for content in glob('site/doc/*.html'):
        name = content.split('/')[-1].rsplit('.', 1)[0]

        # put pages together: head + content + foot
        page = 'site/' + name + '.html'
        yield {
            'basename': 'render',
            'name': name,
            'actions': ['cat %s %s %s > %s' % (head, content, foot, page)],
            'file_dep': [head, foot, content],
            'targets': [page],
            }

    yield {
        'basename': 'site',
        'actions':[],
        'task_dep': ['render'],
        }

def task_deploy():
    """not really deploy, just copy site to folder with git repo for site"""
    actions = []
    for source in ['site/', 'src', 'components', 'test', 'coverage',
                   'api', 'tutorial', 'sample_todomvc', 'dist']:
        actions.append('rsync -avP %s ../hoe-website/' % source)
    return {
        'actions': actions,
        'task_dep': ['site', 'tutorial', 'testdoc', 'coverage', 'apidoc', 'dist'],
        }

# -*- coding: utf-8 -*-

from utilities.myyaml import YAML_EXT
from utilities import template
from utilities import path
from utilities import helpers
from utilities import \
    PROJECT_DIR, BACKEND_DIR, SWAGGER_DIR, ENDPOINTS_CODE_DIR
from utilities.logs import get_logger

log = get_logger(__name__)

TEMPLATE_DIR = 'templates'


class NewEndpointScaffold(object):
    """
    Scaffold necessary directories and file to create
    a new endpoint within the RAPyDo framework
    """

    def __init__(self, project, endpoint_name='foo', service_name=None):
        super(NewEndpointScaffold, self).__init__()

        # custom init
        self.custom_project = project
        self.original_name = endpoint_name
        self.endpoint_name = endpoint_name.lower()
        self.service_name = service_name

        self.backend_dir = path.build([
            PROJECT_DIR,
            self.custom_project,
            BACKEND_DIR,
        ])

        # execute
        self._run()

    def swagger_dir(self):

        self.swagger_path = path.join(
            self.backend_dir, SWAGGER_DIR, self.endpoint_name)

        if self.swagger_path.exists():
            log.warning('Path %s already exists' % self.swagger_path)
            helpers.ask_yes_or_no(
                'Would you like to proceed and overwrite definition?',
                error='Cannot overwrite definition'
            )

        path.create(self.swagger_path, directory=True, force=True)

    @staticmethod
    def save_template(filename, content):
        with open(filename, "w") as fh:
            fh.write(content)

    def render(self, filename, data, outdir='custom', template_filename=None):

        mypath = path.join(outdir, filename)
        if path.file_exists_and_nonzero(mypath):
            # # if you do not want to overwrite
            # log.warning("%s already exists" % filename)
            # return False
            log.info("%s already exists. Overwriting." % filename)

        filepath = str(mypath)

        # FIXME: decide where template dir is
        template_dir = TEMPLATE_DIR
        if template_filename is None:
            template_filename = filename
        templated_content = template.render(
            template_filename, template_dir, **data)

        self.save_template(filepath, templated_content)
        log.debug("rendered %s" % filepath)
        return True

    def swagger_specs(self):
        self.render(
            'specs.%s' % YAML_EXT,
            data={'endpoint_name': self.endpoint_name},
            outdir=self.swagger_path
        )

    def swagger_first_operation(self):
        self.render(
            'get.%s' % YAML_EXT,
            data={'endpoint_name': self.endpoint_name},
            outdir=self.swagger_path
        )

    def swagger(self):
        self.swagger_dir()
        self.swagger_specs()
        self.swagger_first_operation()

    def rest_class(self):

        filename = '%s.py' % self.endpoint_name
        self.class_path = path.join(
            self.backend_dir, ENDPOINTS_CODE_DIR)
        filepath = path.join(self.class_path, filename)

        if self.class_path.exists():
            log.warning('File %s already exists' % filepath)
            helpers.ask_yes_or_no(
                'Would you like to proceed and overwrite that code?',
                error='Cannot overwrite the original file'
            )

        self.render(
            filename,
            template_filename='class.py',
            data={
                'endpoint_name': self.endpoint_name,
                'service_name': self.service_name
            },
            outdir=self.class_path
        )

    def test_class(self):
        pass

    def _run(self):
        self.swagger()

        # # YET TODO
        print("todo")
        self.rest_class()
        self.test_class()
        print("completed")

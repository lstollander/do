# -*- coding: utf-8 -*-

from rapydo.do import project_specs_yaml_path, PROJECT_CONF_FILENAME
from rapydo.utils.myyaml import load_yaml_file
from rapydo.utils.logs import get_logger

log = get_logger(__name__)


def project_configuration(development=False):

    # TODO: generalize this in rapydo.utils?

    ##################
    # Read default configuration
    args = {
        'path': project_specs_yaml_path,
        'skip_error': False,
        'logger': False
    }

    confs = {}
    for f in 'defaults', PROJECT_CONF_FILENAME:
        args['file'] = f
        try:
            confs[f] = load_yaml_file(**args)
            log.debug("(CHECKED) found '%s' rapydo configuration" % f)
        except AttributeError as e:
            log.critical_exit(e)

    specs = confs['defaults']
    custom = confs[PROJECT_CONF_FILENAME]

    # Verify custom project configuration
    prj = custom.get('project')
    if prj is None:
        raise AttributeError("Missing project configuration")
    elif not development:
        check1 = prj.get('title') == 'My project'
        check2 = prj.get('description') == 'Title of my project'
        if check1 or check2:
            filepath = load_yaml_file(return_path=True, **args)
            log.critical_exit(
                "\n\nIt seems like your project is not yet configured...\n" +
                "Please edit file %s" % filepath
            )

    # Mix default and custom configuration
    return mix_dictionary(specs, custom)


def mix_dictionary(base, custom):

    for key, elements in custom.items():

        if key not in base:
            # log.info("Adding %s to configuration" % key)
            base[key] = custom[key]
            continue

        if isinstance(elements, dict):
            mix_dictionary(base[key], custom[key])
        else:
            # log.info("Replacing default %s in configuration" % key)
            base[key] = elements

    return base


def apply_variables(dictionary={}, variables={}):

    new_dict = {}
    for key, value in dictionary.items():
        if isinstance(value, str) and value.startswith('$$'):
            value = variables.get(value.lstrip('$'), None)
        new_dict[key] = value

    return new_dict
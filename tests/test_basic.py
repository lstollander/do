
from git import Repo
from controller.arguments import ArgParser
from controller.app import Application
from utilities.logs import get_logger

log = get_logger(__name__)


def exec_command(capfd, command):
    command = command.split(" ")

    arguments = ArgParser(args=command)

    try:
        Application(arguments)
    # NOTE: docker-compose calls SystemExit at the end of the command...
    except SystemExit:
        log.info('completed')

    out, err = capfd.readouterr()
    out = out.split("\n")
    err = err.split("\n")

    for e in err:
        print(e)

    return out, err


def test_do(capfd):

    # INIT on rapydo-core
    _, err = exec_command(capfd, "rapydo init")
    assert "INFO Created .env file" in err
    assert "INFO Project initialized" in err

    # UPDATE on rapydo-core
    _, err = exec_command(capfd, "rapydo update")
    assert "INFO Created .env file" in err
    assert "INFO All updated" in err

    # _, err = exec_command(capfd, "rapydo build")
    # assert "INFO Image built" in err

    # CHECK on rapydo-core
    _, err = exec_command(capfd, "rapydo check")
    assert "INFO Created .env file" in err
    assert "INFO You are working on rapydo-core, not a fork" in err
    assert "INFO All checked" in err

    # NOW with are on a fork of rapydo-core
    gitobj = Repo(".")
    gitobj.remotes.origin.set_url("just_a_non_url")

    # Missing upstream url
    _, err = exec_command(capfd, "rapydo check")
    assert "EXIT Missing upstream to rapydo/core" in err

    # Create upstream url
    _, err = exec_command(capfd, "rapydo init")
    assert "INFO Created .env file" in err
    assert "INFO Project initialized" in err

    # Check upstream url
    # Also check .env cache
    _, err = exec_command(capfd, "rapydo --cache-env check")
    assert "INFO \u2713 Upstream is set correctly" in err
    assert "DEBUG Using cache for .env" in err
    assert "INFO All checked" in err

    out, err = exec_command(capfd, "rapydo env")
    assert "INFO Created .env file" in err
    assert "project: template" in out

    _, err = exec_command(capfd, "rapydo start")
    assert "INFO Created .env file" in err
    assert "INFO Requesting within compose: 'up'" in err
    assert "INFO Stack started" in err

    _, err = exec_command(capfd, "rapydo status")
    assert "INFO Requesting within compose: 'ps'" in err

    exec_command(capfd, "rapydo log")
    assert "INFO Requesting within compose: 'logs'" in err

    exec_command(capfd, "rapydo bower-install jquery")
    assert "EXIT Missing bower lib, please add the --lib option" in err
    exec_command(capfd, "rapydo bower-install --lib jquery")
    assert "INFO Requesting within compose: 'run'" in err

    exec_command(capfd, "rapydo bower-update jquery")
    assert "EXIT Missing bower lib, please add the --lib option" in err
    exec_command(capfd, "rapydo bower-update --lib jquery")
    assert "INFO Requesting within compose: 'run'" in err

    _, err = exec_command(capfd, "rapydo toggle-freeze")
    assert "INFO Created .env file" in err
    assert "INFO Stack paused" in err

    _, err = exec_command(capfd, "rapydo toggle-freeze")
    assert "INFO Created .env file" in err
    assert "INFO Stack unpaused" in err

    _, err = exec_command(capfd, "rapydo stop")
    assert "INFO Created .env file" in err
    assert "INFO Stack stoped" in err

    _, err = exec_command(capfd, "rapydo restart")
    assert "INFO Created .env file" in err
    assert "INFO Stack restarted" in err

    _, err = exec_command(capfd, "rapydo remove")
    assert "INFO Created .env file" in err
    assert "INFO Requesting within compose: 'stop'" in err
    assert "INFO Stack removed" in err

    _, err = exec_command(capfd, "rapydo clean")
    assert "INFO Created .env file" in err
    assert "INFO Stack cleaned" in err

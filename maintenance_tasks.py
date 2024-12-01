from logging import DEBUG, INFO
from time import sleep
from random import randint

from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_configure

CFG_MAINTENANCE_ENABLE = """
maintenance
  unit System
    quiesce
end
"""
CFG_MAINTENANCE_DISABLE = """
no maintenance
end
"""
CFG_OSPF_DISABLE = """
router ospf 1
  shutdown
end
"""
CFG_OSPF_ENABLE = """
router ospf 1
  no shutdown
end
"""
CFG_ISIS_DISABLE = """
router isis Gandalf
  shutdown
end
"""
CFG_ISIS_ENABLE = """
router isis Gandalf
  no shutdown
end
"""


def relax(task: Task) -> Result:
    seconds = randint(10, 30)
    sleep(seconds)

    # Every now and then, a router does not want to return to work.
    if randint(0, 9) == 9:
        raise Exception(f"{task.host.name} is not in the mood to perform its job.")

    return Result(task.host, result=f"{seconds} seconds of beauty sleep.")


def spa_day(task: Task) -> Result:
    """
    We believe every router deserves some relaxing time.
    """

    # Shutdown ospf or|and isis
    if "ospf" in task.host.groups:
        task.run(
            napalm_configure,
            configuration=CFG_OSPF_DISABLE,
            name="ospf_disalbe",
            severity_level=DEBUG,
        )
    if "isis" in task.host.groups:
        task.run(
            napalm_configure,
            configuration=CFG_ISIS_DISABLE,
            name="isis_disalbe",
            severity_level=DEBUG,
        )

    # Enjoy your spa day
    task.run(relax, severity_level=INFO)

    # Enable ospf or|and isis
    if "ospf" in task.host.groups:
        task.run(
            napalm_configure,
            configuration=CFG_OSPF_ENABLE,
            name="ospf_enable",
            severity_level=DEBUG,
        )
    if "isis" in task.host.groups:
        task.run(
            napalm_configure,
            configuration=CFG_ISIS_ENABLE,
            name="isis_enable",
            severity_level=DEBUG,
        )

    return Result(
        task.host, result=f"{task.host.name} is relaxed and happy to perform its job."
    )


def maintenance(task: Task) -> Result:
    task.run(
        napalm_configure,
        configuration=CFG_MAINTENANCE_ENABLE,
        name="maintenence_enable",
        severity_level=DEBUG,
    )
    sleep(5)

    # Enjoy your spa day
    task.run(spa_day, severity_level=INFO)

    task.run(
        napalm_configure,
        configuration=CFG_MAINTENANCE_DISABLE,
        name="maintenence_disable",
        severity_level=DEBUG,
    )
    sleep(10)

    return Result(task.host, result=f"{task.host.name} is back from the spa day")

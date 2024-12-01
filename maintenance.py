import sys
import typer

from nornir import InitNornir
from nornir.core import Nornir
from nornir.core.filter import F
from nornir_rich.functions import print_inventory, print_result
from nornir_rich.progress_bar import RichProgressBar

from rich.console import Console
from rich.prompt import Confirm


from maintenance_tasks import maintenance

console = Console()
console_error = Console(stderr=True, style="red")


def init_nornir(configuration_file: str = "config.yaml") -> Nornir:
    nr = InitNornir(config_file=configuration_file)

    # We do not want to touche Router from edge1 (R01) or edge2 (R10)
    nr = nr.filter(~F(groups__any=["edge1", "edge2"]))
    return nr


def main(
    configuration_file: typer.FileText = typer.Option(
        "config.yaml",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        metavar="NORNIR_SETTINGS",
        help="Path to the nornir configuration file.",
        envvar="NORNIR_SETTINGS",
    ),
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        count=True,
        help="Multiple verbose levels can be enabled to increase the verbosity of the output when running Nornir by utilizing the corresponding option.",
        show_default=False,
    ),
) -> None:
    nr = init_nornir(str(configuration_file))
    print_inventory(nr.inventory, vars=["conditional_groups"])
    if not Confirm.ask("Do you want to start maintenance?"):
        console_error.print("Maintenance not started")
        raise sys.exit(1)

    nr_with_processors = nr.with_processors([RichProgressBar()])
    result = nr_with_processors.run(task=maintenance)

    if verbose or result.failed:
        level = 10 * (4 - max(0, min(verbose + 1, 4)))
        print_result(result, severity_level=level)


if __name__ == "__main__":
    typer.run(main)

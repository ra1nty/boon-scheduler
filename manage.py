"""Main entry-point for majer_scheduler.

Commands:
    start           Start the scheduler

Usage:
    manage.py start [--mode]
Options:
    --mode          Start the api on specific mode, one of
                    production, development, testing
                    [default : production]
"""
import click
from app.main import run_app

@click.group()
def cli():
    pass

@cli.command()
@click.option('--mode', default='production', help='production/development')
def start(mode):
    run_app(mode)

if __name__ == '__main__':
    cli()  # Execute the function specified by the user.
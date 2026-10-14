"""Compatibility entry point for deployments using the former worker command."""

from .odoo.worker import main


if __name__ == "__main__":
    main()

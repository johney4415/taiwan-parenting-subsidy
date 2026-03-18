from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.core.data_loader import write_json_export


class Command(BaseCommand):
    help = "Export YAML data to JSON for frontend consumption"

    def handle(self, *args: object, **options: object) -> None:
        self.stdout.write("Exporting data to JSON...")
        output_path = write_json_export()
        self.stdout.write(
            self.style.SUCCESS(f"Data exported to {output_path}")
        )

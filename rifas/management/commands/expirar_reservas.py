from django.core.management.base import BaseCommand

from rifas.services import expirar_reservas_vencidas


class Command(BaseCommand):
    help = 'Expira reservas vencidas e libera os numeros associados.'

    def handle(self, *args, **options):
        reservas_expiradas, numeros_liberados = expirar_reservas_vencidas()

        self.stdout.write(
            self.style.SUCCESS(
                f'{reservas_expiradas} reserva(s) expirada(s); {numeros_liberados} numero(s) liberado(s).'
            )
        )

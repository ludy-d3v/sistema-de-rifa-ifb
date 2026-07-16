from django.db import transaction
from django.utils import timezone

from .models import NumeroRifa, Rifa, Transacao


@transaction.atomic
def expirar_reservas_vencidas(rifa=None):
    agora = timezone.now()
    transacoes = Transacao.objects.filter(
        status=Transacao.Status.RESERVADA,
        data_expiracao__lt=agora,
    ).prefetch_related('itens__numero')

    if rifa:
        rifa_id = rifa.pk if isinstance(rifa, Rifa) else rifa
        transacoes = transacoes.filter(rifa_id=rifa_id)

    transacoes = list(transacoes)
    numeros_liberados = 0

    for transacao in transacoes:
        numeros_ids = list(transacao.itens.values_list('numero_id', flat=True))
        numeros_liberados += NumeroRifa.objects.filter(id__in=numeros_ids).update(
            status=NumeroRifa.Status.DISPONIVEL,
            atualizado_em=agora,
        )
        transacao.status = Transacao.Status.EXPIRADA
        transacao.save(update_fields=['status', 'atualizado_em'])

    return len(transacoes), numeros_liberados

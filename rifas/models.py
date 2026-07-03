from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils import timezone


class Rifa(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = 'rascunho', 'Rascunho'
        ATIVA = 'ativa', 'Ativa'
        ENCERRADA = 'encerrada', 'Encerrada'

    titulo = models.CharField('titulo', max_length=150)
    slug = models.SlugField('slug publico', max_length=180, unique=True, blank=True, null=True)
    descricao = models.TextField('descricao', blank=True)
    descricao_html = models.TextField('descricao formatada', blank=True)
    valor_numero = models.DecimalField('valor do numero', max_digits=10, decimal_places=2)
    total_numeros = models.PositiveIntegerField('total de numeros')
    data_sorteio = models.DateTimeField('data do sorteio')
    chave_pix = models.CharField('chave Pix', max_length=150)
    tempo_reserva = models.PositiveIntegerField('tempo de reserva em minutos', default=15)
    status = models.CharField('status da rifa', max_length=20, choices=Status.choices, default=Status.RASCUNHO)
    organizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='organizador',
        on_delete=models.PROTECT,
        related_name='rifas',
    )
    imagem_principal = models.FileField('imagem principal', upload_to='rifas/principais/', blank=True)
    link_transmissao = models.URLField('link da transmissao', blank=True)
    ativo = models.BooleanField('ativo', default=True)
    excluido_em = models.DateTimeField('excluido em', null=True, blank=True)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'rifa'
        verbose_name_plural = 'rifas'

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titulo) or 'rifa'
            slug = base_slug
            contador = 1
            while Rifa.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                contador += 1
                slug = f'{base_slug}-{contador}'
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def possui_vendas(self):
        return self.numeros.filter(status=NumeroRifa.Status.PAGO).exists()

    def soft_delete(self):
        if self.possui_vendas:
            raise ValidationError('Rifas com vendas nao podem ser excluidas.')
        self.ativo = False
        self.excluido_em = timezone.now()
        self.save(update_fields=['ativo', 'excluido_em', 'atualizado_em'])


class NumeroRifa(models.Model):
    class Status(models.TextChoices):
        DISPONIVEL = 'disponivel', 'Disponivel'
        RESERVADO = 'reservado', 'Reservado'
        AGUARDANDO_APROVACAO = 'aguardando_aprovacao', 'Aguardando aprovacao'
        PAGO = 'pago', 'Pago'

    rifa = models.ForeignKey(Rifa, verbose_name='rifa', on_delete=models.CASCADE, related_name='numeros')
    numero = models.PositiveIntegerField('numero')
    status = models.CharField('status do numero', max_length=20, choices=Status.choices, default=Status.DISPONIVEL)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['rifa', 'numero'], name='numero_unico_por_rifa'),
        ]
        ordering = ['numero']
        verbose_name = 'numero da rifa'
        verbose_name_plural = 'numeros da rifa'

    def __str__(self):
        return f'{self.rifa} - {self.numero}'


class Transacao(models.Model):
    class Status(models.TextChoices):
        RESERVADA = 'reservada', 'Reservada'
        AGUARDANDO_APROVACAO = 'aguardando_aprovacao', 'Aguardando aprovacao'
        PAGA = 'paga', 'Paga'
        EXPIRADA = 'expirada', 'Expirada'
        REJEITADA = 'rejeitada', 'Rejeitada'

    comprador_nome = models.CharField('nome do comprador', max_length=150)
    comprador_email = models.EmailField('e-mail do comprador')
    comprador_telefone = models.CharField('telefone do comprador', max_length=20)
    comprador_cpf = models.CharField('CPF do comprador', max_length=14)
    vendedor = models.ForeignKey(
        'vendedores.Vendedor',
        verbose_name='vendedor',
        on_delete=models.PROTECT,
        related_name='transacoes',
        null=True,
        blank=True,
    )
    rifa = models.ForeignKey(Rifa, verbose_name='rifa', on_delete=models.PROTECT, related_name='transacoes')
    data_expiracao = models.DateTimeField('data de expiracao')
    status = models.CharField('status da transacao', max_length=30, choices=Status.choices, default=Status.RESERVADA)
    comprovante = models.FileField('comprovante', upload_to='comprovantes/', blank=True)
    valor_total = models.DecimalField('valor total', max_digits=10, decimal_places=2)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'transacao'
        verbose_name_plural = 'transacoes'

    def __str__(self):
        return f'{self.comprador_nome} - {self.rifa}'


class ItemTransacao(models.Model):
    transacao = models.ForeignKey(Transacao, verbose_name='transacao', on_delete=models.CASCADE, related_name='itens')
    numero = models.ForeignKey(NumeroRifa, verbose_name='numero', on_delete=models.PROTECT, related_name='itens_transacao')
    valor_unitario = models.DecimalField('valor unitario', max_digits=10, decimal_places=2)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['numero__numero']
        verbose_name = 'item da transacao'
        verbose_name_plural = 'itens da transacao'

    def __str__(self):
        return f'{self.transacao} - numero {self.numero.numero}'


class ImagemRifa(models.Model):
    rifa = models.ForeignKey(Rifa, verbose_name='rifa', on_delete=models.CASCADE, related_name='imagens_galeria')
    imagem = models.FileField('imagem', upload_to='rifas/galeria/')
    ordem = models.PositiveSmallIntegerField('ordem', default=1)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['ordem', 'id']
        verbose_name = 'imagem da galeria'
        verbose_name_plural = 'imagens da galeria'

    def __str__(self):
        return f'Imagem {self.ordem} - {self.rifa}'


class Premio(models.Model):
    rifa = models.ForeignKey(Rifa, verbose_name='rifa', on_delete=models.CASCADE, related_name='premios')
    posicao = models.PositiveSmallIntegerField('posicao')
    descricao = models.TextField('descricao')
    imagem = models.FileField('imagem', upload_to='rifas/premios/', blank=True)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['rifa', 'posicao'], name='premio_unico_por_posicao'),
        ]
        ordering = ['posicao']
        verbose_name = 'premio'
        verbose_name_plural = 'premios'

    def __str__(self):
        return f'{self.posicao}o premio - {self.rifa}'

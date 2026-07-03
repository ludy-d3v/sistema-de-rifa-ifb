from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from rifas.models import ItemTransacao, NumeroRifa, Premio, Rifa, Transacao
from vendedores.models import Vendedor, VendedorRifa


class Command(BaseCommand):
    help = 'Limpa dados de teste e cria um cenário de demonstração para o admin.'

    senha_padrao = '12345678'

    @transaction.atomic
    def handle(self, *args, **options):
        self.limpar_dados()
        usuarios = self.criar_usuarios()
        rifas = self.criar_rifas(usuarios)
        vendedores = self.criar_vendedores(usuarios, rifas)
        self.criar_transacoes(rifas, vendedores)

        self.stdout.write(self.style.SUCCESS('Banco de demonstração criado com sucesso.'))
        self.stdout.write(f'Senha padrão dos usuários: {self.senha_padrao}')
        self.stdout.write('Admin: admin@gmail.com')
        self.stdout.write('Organizador: organizador@gmail.com')
        self.stdout.write('Vendedores: maria.vendedora@gmail.com, joao.vendedor@gmail.com')

    def limpar_dados(self):
        User = get_user_model()
        ItemTransacao.objects.all().delete()
        Transacao.objects.all().delete()
        Premio.objects.all().delete()
        NumeroRifa.objects.all().delete()
        VendedorRifa.objects.all().delete()
        Vendedor.objects.all().delete()
        Rifa.objects.all().delete()
        User.objects.exclude(email='admin@gmail.com').delete()

    def criar_usuarios(self):
        User = get_user_model()

        admin, _ = User.objects.update_or_create(
            email='admin@gmail.com',
            defaults={
                'nome': 'Administradora do Sistema',
                'papel': User.Papel.ORGANIZADOR,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            },
        )
        admin.set_password(self.senha_padrao)
        admin.save()

        organizador = User.objects.create_user(
            email='organizador@gmail.com',
            password=self.senha_padrao,
            nome='Ludmilla Oliveira',
            telefone='61999990000',
            cpf='11122233344',
            papel=User.Papel.ORGANIZADOR,
            is_staff=True,
        )

        vendedor_maria = User.objects.create_user(
            email='maria.vendedora@gmail.com',
            password=self.senha_padrao,
            nome='Maria Santos',
            telefone='61988880001',
            cpf='22233344455',
            papel=User.Papel.VENDEDOR,
            is_staff=True,
        )

        vendedor_joao = User.objects.create_user(
            email='joao.vendedor@gmail.com',
            password=self.senha_padrao,
            nome='João Pereira',
            telefone='61988880002',
            cpf='33344455566',
            papel=User.Papel.VENDEDOR,
            is_staff=True,
        )

        return {
            'admin': admin,
            'organizador': organizador,
            'vendedor_maria': vendedor_maria,
            'vendedor_joao': vendedor_joao,
        }

    def criar_rifas(self, usuarios):
        agora = timezone.now()
        organizador = usuarios['organizador']

        notebook = Rifa.objects.create(
            titulo='Rifa Solidária - Notebook',
            descricao='Rifa beneficente para arrecadação de recursos.',
            descricao_html='<p>Rifa beneficente para arrecadação de recursos.</p>',
            valor_numero=Decimal('10.00'),
            total_numeros=100,
            data_sorteio=agora + timezone.timedelta(days=20),
            chave_pix='rifa.notebook@pix.com',
            tempo_reserva=30,
            status=Rifa.Status.ATIVA,
            organizador=organizador,
            link_transmissao='https://youtube.com/@rifafacil',
        )
        smartphone = Rifa.objects.create(
            titulo='Rifa Beneficente - Smartphone',
            descricao='Rifa para campanha comunitária.',
            descricao_html='<p>Rifa para campanha comunitária.</p>',
            valor_numero=Decimal('8.00'),
            total_numeros=80,
            data_sorteio=agora + timezone.timedelta(days=35),
            chave_pix='rifa.smartphone@pix.com',
            tempo_reserva=20,
            status=Rifa.Status.ATIVA,
            organizador=organizador,
        )

        for rifa in [notebook, smartphone]:
            NumeroRifa.objects.bulk_create(
                NumeroRifa(rifa=rifa, numero=numero)
                for numero in range(1, rifa.total_numeros + 1)
            )

        Premio.objects.bulk_create([
            Premio(rifa=notebook, posicao=1, descricao='Notebook Lenovo Ideapad'),
            Premio(rifa=notebook, posicao=2, descricao='Headset gamer'),
            Premio(rifa=smartphone, posicao=1, descricao='Smartphone Samsung Galaxy'),
            Premio(rifa=smartphone, posicao=2, descricao='Caixa de som Bluetooth'),
        ])

        return {'notebook': notebook, 'smartphone': smartphone}

    def criar_vendedores(self, usuarios, rifas):
        organizador = usuarios['organizador']
        maria = Vendedor.objects.create(
            usuario=usuarios['vendedor_maria'],
            organizador=organizador,
            comissao_fixa=Decimal('2.00'),
        )
        joao = Vendedor.objects.create(
            usuario=usuarios['vendedor_joao'],
            organizador=organizador,
            comissao_fixa=Decimal('1.50'),
        )

        VendedorRifa.objects.bulk_create([
            VendedorRifa(vendedor=maria, rifa=rifas['smartphone']),
            VendedorRifa(vendedor=joao, rifa=rifas['notebook']),
        ])

        return {'maria': maria, 'joao': joao}

    def criar_transacoes(self, rifas, vendedores):
        self.criar_transacao(
            rifa=rifas['notebook'],
            vendedor=vendedores['joao'],
            numeros=[1, 2, 3],
            comprador_nome='Ludy Oliveira',
            comprador_email='ludy@email.com',
            comprador_telefone='61982349999',
            comprador_cpf='65465498132',
            status=Transacao.Status.PAGA,
            status_numero=NumeroRifa.Status.PAGO,
        )
        self.criar_transacao(
            rifa=rifas['notebook'],
            vendedor=vendedores['joao'],
            numeros=[4, 5],
            comprador_nome='Ana Souza',
            comprador_email='ana@email.com',
            comprador_telefone='61981234567',
            comprador_cpf='12345678901',
            status=Transacao.Status.AGUARDANDO_APROVACAO,
            status_numero=NumeroRifa.Status.AGUARDANDO_APROVACAO,
        )
        self.criar_transacao(
            rifa=rifas['smartphone'],
            vendedor=vendedores['maria'],
            numeros=[1, 2],
            comprador_nome='Bruno Lima',
            comprador_email='bruno@email.com',
            comprador_telefone='61987654321',
            comprador_cpf='98765432100',
            status=Transacao.Status.RESERVADA,
            status_numero=NumeroRifa.Status.RESERVADO,
        )

    def criar_transacao(self, rifa, vendedor, numeros, status_numero, **dados):
        transacao = Transacao.objects.create(
            rifa=rifa,
            vendedor=vendedor,
            data_expiracao=timezone.now() + timezone.timedelta(minutes=rifa.tempo_reserva),
            valor_total=rifa.valor_numero * len(numeros),
            **dados,
        )
        numeros_obj = list(NumeroRifa.objects.filter(rifa=rifa, numero__in=numeros))
        ItemTransacao.objects.bulk_create(
            ItemTransacao(
                transacao=transacao,
                numero=numero,
                valor_unitario=rifa.valor_numero,
            )
            for numero in numeros_obj
        )
        NumeroRifa.objects.filter(pk__in=[numero.pk for numero in numeros_obj]).update(
            status=status_numero,
            atualizado_em=timezone.now(),
        )

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from vendedores.models import Vendedor, VendedorRifa

from .models import NumeroRifa, Premio, Rifa, Transacao


Usuario = get_user_model()


class RifasAPITestCase(APITestCase):
    def setUp(self):
        self.organizador = Usuario.objects.create_user(
            email='organizador@example.com',
            password='senha-teste-123',
            nome='Organizador',
            papel='organizador',
        )
        self.client.force_authenticate(user=self.organizador)
        self.payload = {
            'titulo': 'Rifa beneficente',
            'descricao': 'Texto simples da rifa',
            'descricao_html': '<p>Texto formatado da rifa</p>',
            'valor_numero': '10.00',
            'total_numeros': 10,
            'data_sorteio': timezone.now().isoformat(),
            'chave_pix': 'pix@example.com',
            'tempo_reserva': 20,
            'status': 'rascunho',
            'link_transmissao': 'https://example.com/live',
        }

    def test_organizador_cria_rifa_e_numeros_sao_gerados(self):
        response = self.client.post(reverse('rifa-list'), self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rifa = Rifa.objects.get()
        self.assertEqual(rifa.numeros.count(), 10)
        self.assertEqual(rifa.numeros.first().status, NumeroRifa.Status.DISPONIVEL)

    def test_lista_apenas_rifas_do_organizador_incluindo_inativas(self):
        rifa = Rifa.objects.create(organizador=self.organizador, **self.payload, ativo=False)

        response = self.client.get(reverse('rifa-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], rifa.id)
        self.assertFalse(response.data[0]['ativo'])

    def test_bloqueia_valor_e_total_apos_primeira_venda(self):
        rifa = Rifa.objects.create(organizador=self.organizador, **self.payload)
        NumeroRifa.objects.create(rifa=rifa, numero=1, status=NumeroRifa.Status.PAGO)

        response = self.client.patch(
            reverse('rifa-detail', args=[rifa.id]),
            {'valor_numero': '20.00', 'total_numeros': 20},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_exclusao_logica_sem_vendas(self):
        response_criacao = self.client.post(reverse('rifa-list'), self.payload, format='json')
        rifa_id = response_criacao.data['id']

        response = self.client.delete(reverse('rifa-detail', args=[rifa_id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Rifa.objects.get(pk=rifa_id).ativo)

    def test_nao_exclui_rifa_com_vendas(self):
        rifa = Rifa.objects.create(organizador=self.organizador, **self.payload)
        NumeroRifa.objects.create(rifa=rifa, numero=1, status=NumeroRifa.Status.PAGO)

        response = self.client.delete(reverse('rifa-detail', args=[rifa.id]))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Rifa.objects.get(pk=rifa.id).ativo)

    def test_crud_de_premio_aninhado_a_rifa(self):
        rifa = Rifa.objects.create(organizador=self.organizador, **self.payload)

        response = self.client.post(
            reverse('premio-list', args=[rifa.id]),
            {'posicao': 1, 'descricao': 'Primeiro premio'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Premio.objects.filter(rifa=rifa, posicao=1).exists())

    def test_endpoint_publico_retorna_rifa_por_slug_com_progresso_e_vendedores(self):
        rifa = Rifa.objects.create(organizador=self.organizador, **{**self.payload, 'status': Rifa.Status.ATIVA})
        Premio.objects.create(rifa=rifa, posicao=1, descricao='Primeiro premio')
        NumeroRifa.objects.create(rifa=rifa, numero=1, status=NumeroRifa.Status.PAGO)
        usuario_vendedor = Usuario.objects.create_user(
            email='vendedor@example.com',
            password='senha-teste-123',
            nome='Vendedor Teste',
            papel='vendedor',
        )
        vendedor = Vendedor.objects.create(
            usuario=usuario_vendedor,
            organizador=self.organizador,
            comissao_fixa='2.50',
        )
        VendedorRifa.objects.create(vendedor=vendedor, rifa=rifa)
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse('rifa-publica', args=[rifa.slug]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['slug'], rifa.slug)
        self.assertEqual(response.data['numeros_pagos'], 1)
        self.assertEqual(len(response.data['vendedores']), 1)
        self.assertEqual(len(response.data['premios']), 1)

    def test_comprador_reserva_numeros_disponiveis(self):
        rifa = Rifa.objects.create(organizador=self.organizador, **{**self.payload, 'status': Rifa.Status.ATIVA})
        numeros = [
            NumeroRifa.objects.create(rifa=rifa, numero=1),
            NumeroRifa.objects.create(rifa=rifa, numero=2),
        ]
        self.client.force_authenticate(user=None)

        response = self.client.post(
            reverse('rifa-reservar', args=[rifa.id]),
            {
                'numeros': [1, 2],
                'comprador_nome': 'Comprador Teste',
                'comprador_email': 'comprador@example.com',
                'comprador_telefone': '61999999999',
                'comprador_cpf': '12345678900',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Transacao.objects.filter(rifa=rifa, itens__numero__in=numeros).exists())
        self.assertEqual(
            NumeroRifa.objects.filter(rifa=rifa, status=NumeroRifa.Status.RESERVADO).count(),
            2,
        )

    def test_nao_reserva_numero_indisponivel(self):
        rifa = Rifa.objects.create(organizador=self.organizador, **{**self.payload, 'status': Rifa.Status.ATIVA})
        NumeroRifa.objects.create(rifa=rifa, numero=1, status=NumeroRifa.Status.RESERVADO)
        self.client.force_authenticate(user=None)

        response = self.client.post(
            reverse('rifa-reservar', args=[rifa.id]),
            {
                'numeros': [1],
                'comprador_nome': 'Comprador Teste',
                'comprador_email': 'comprador@example.com',
                'comprador_telefone': '61999999999',
                'comprador_cpf': '12345678900',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

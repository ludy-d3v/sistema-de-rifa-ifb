from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from rifas.models import Rifa

from .models import Vendedor, VendedorRifa


Usuario = get_user_model()


class VendedoresAPITestCase(APITestCase):
    def setUp(self):
        self.organizador = Usuario.objects.create_user(
            email='organizador@example.com',
            password='senha-teste-123',
            nome='Organizador',
            papel='organizador',
        )
        self.client.force_authenticate(user=self.organizador)
        self.rifa = Rifa.objects.create(
            organizador=self.organizador,
            titulo='Rifa beneficente',
            descricao='Rifa de teste',
            valor_numero='10.00',
            total_numeros=10,
            data_sorteio=timezone.now(),
            chave_pix='pix@example.com',
            tempo_reserva=20,
            status='rascunho',
        )

    def test_organizador_cadastra_vendedor_com_usuario_e_senha_gerados(self):
        response = self.client.post(
            reverse('vendedor-list'),
            {
                'nome': 'Vendedor Teste',
                'email': 'vendedor@example.com',
                'telefone': '61999999999',
                'comissao_fixa': '2.50',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Usuario.objects.filter(email='vendedor@example.com', papel='vendedor').exists())
        self.assertTrue(Vendedor.objects.filter(usuario__email='vendedor@example.com').exists())
        self.assertTrue(response.data['credenciais_enviadas'])
        self.assertIn('senha_temporaria', response.data)

    def test_organizador_lista_apenas_seus_vendedores(self):
        outro_organizador = Usuario.objects.create_user(
            email='outro@example.com',
            password='senha-teste-123',
            nome='Outro Organizador',
            papel='organizador',
        )
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
        outro_usuario_vendedor = Usuario.objects.create_user(
            email='outro.vendedor@example.com',
            password='senha-teste-123',
            nome='Outro Vendedor',
            papel='vendedor',
        )
        Vendedor.objects.create(
            usuario=outro_usuario_vendedor,
            organizador=outro_organizador,
            comissao_fixa='1.50',
        )

        response = self.client.get(reverse('vendedor-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], vendedor.id)

    def test_organizador_associa_e_remove_rifa_do_vendedor(self):
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

        associar_response = self.client.post(
            reverse('vendedor-associar-rifa', args=[vendedor.id]),
            {'rifa_id': self.rifa.id},
            format='json',
        )
        self.assertEqual(associar_response.status_code, status.HTTP_200_OK)
        self.assertTrue(VendedorRifa.objects.get(vendedor=vendedor, rifa=self.rifa).ativo)

        remover_response = self.client.delete(
            reverse('vendedor-remover-rifa', args=[vendedor.id]),
            {'rifa_id': self.rifa.id},
            format='json',
        )

        self.assertEqual(remover_response.status_code, status.HTTP_200_OK)
        self.assertFalse(VendedorRifa.objects.get(vendedor=vendedor, rifa=self.rifa).ativo)

    def test_vendedor_visualiza_apenas_rifas_associadas(self):
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
        VendedorRifa.objects.create(vendedor=vendedor, rifa=self.rifa)
        self.client.force_authenticate(user=usuario_vendedor)

        response = self.client.get(reverse('vendedor-rifas'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['rifa']['id'], self.rifa.id)

    def test_vendedor_acessa_resumo_e_vendas_sem_transacoes(self):
        usuario_vendedor = Usuario.objects.create_user(
            email='vendedor@example.com',
            password='senha-teste-123',
            nome='Vendedor Teste',
            papel='vendedor',
        )
        Vendedor.objects.create(
            usuario=usuario_vendedor,
            organizador=self.organizador,
            comissao_fixa='2.50',
        )
        self.client.force_authenticate(user=usuario_vendedor)

        resumo_response = self.client.get(reverse('vendedor-resumo'))
        vendas_response = self.client.get(reverse('vendedor-vendas'))

        self.assertEqual(resumo_response.status_code, status.HTTP_200_OK)
        self.assertEqual(resumo_response.data['total_numeros_vendidos'], 0)
        self.assertEqual(vendas_response.status_code, status.HTTP_200_OK)
        self.assertEqual(vendas_response.data['resultados'], [])

# Create your tests here.

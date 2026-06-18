from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


Usuario = get_user_model()


class AutenticacaoAPITestCase(APITestCase):
    def setUp(self):
        self.dados_cadastro = {
            'nome': 'Ludmilla Oliveira',
            'email': 'ludy@example.com',
            'telefone': '61999999999',
            'cpf': '',
            'papel': 'organizador',
            'senha': 'senha-forte-123',
        }

    def test_cadastra_organizador(self):
        response = self.client.post(reverse('cadastro'), self.dados_cadastro, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], self.dados_cadastro['email'])
        self.assertEqual(response.data['papel'], 'organizador')
        self.assertTrue(Usuario.objects.filter(email=self.dados_cadastro['email']).exists())

    def test_bloqueia_cadastro_publico_de_vendedor(self):
        payload = {**self.dados_cadastro, 'email': 'vendedor@example.com', 'papel': 'vendedor'}

        response = self.client.post(reverse('cadastro'), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Usuario.objects.filter(email='vendedor@example.com').exists())

    def test_login_retorna_tokens_e_usuario(self):
        Usuario.objects.create_user(
            email='ludy@example.com',
            password='senha-forte-123',
            nome='Ludmilla Oliveira',
            papel='organizador',
        )

        response = self.client.post(
            reverse('login'),
            {'email': 'ludy@example.com', 'password': 'senha-forte-123'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['usuario']['papel'], 'organizador')

    def test_perfil_exige_autenticacao(self):
        response = self.client.get(reverse('perfil'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_usuario_autenticado_visualiza_e_edita_perfil(self):
        usuario = Usuario.objects.create_user(
            email='ludy@example.com',
            password='senha-forte-123',
            nome='Ludmilla Oliveira',
            papel='organizador',
        )
        self.client.force_authenticate(user=usuario)

        response_get = self.client.get(reverse('perfil'))
        response_patch = self.client.patch(
            reverse('perfil'),
            {'telefone': '61988888888'},
            format='json',
        )

        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK)
        usuario.refresh_from_db()
        self.assertEqual(usuario.telefone, '61988888888')

    def test_recuperacao_de_senha_simulada(self):
        Usuario.objects.create_user(
            email='ludy@example.com',
            password='senha-forte-123',
            nome='Ludmilla Oliveira',
        )

        response = self.client.post(
            reverse('recuperar-senha'),
            {'email': 'ludy@example.com'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('link_simulado', response.data)

# Create your tests here.

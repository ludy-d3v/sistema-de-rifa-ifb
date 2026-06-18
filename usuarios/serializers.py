from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


Usuario = get_user_model()


class CadastroSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'telefone', 'cpf', 'papel', 'senha']
        read_only_fields = ['id']

    def validate_papel(self, value):
        if value != Usuario.Papel.ORGANIZADOR:
            raise serializers.ValidationError(
                'Vendedores devem ser cadastrados por um organizador.'
            )
        return value

    def create(self, validated_data):
        senha = validated_data.pop('senha')
        return Usuario.objects.create_user(password=senha, **validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    username_field = Usuario.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['nome'] = user.nome
        token['email'] = user.email
        token['papel'] = user.papel
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        self.user.registrar_acesso()
        data['usuario'] = UsuarioSerializer(self.user).data
        return data


class UsuarioSerializer(serializers.ModelSerializer):
    ativo = serializers.BooleanField(source='is_active', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id',
            'nome',
            'email',
            'telefone',
            'cpf',
            'papel',
            'ativo',
            'ultimo_acesso',
            'criado_em',
        ]
        read_only_fields = ['id', 'email', 'papel', 'ativo', 'ultimo_acesso', 'criado_em']


class RecuperarSenhaSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        self.usuario = Usuario.objects.filter(email__iexact=value, is_active=True).first()
        return value

    def save(self):
        if not self.usuario:
            return {
                'mensagem': 'Se o e-mail existir, as instrucoes de recuperacao serao enviadas.'
            }

        uid = urlsafe_base64_encode(force_bytes(self.usuario.pk))
        token = default_token_generator.make_token(self.usuario)
        return {
            'mensagem': 'Recuperacao de senha simulada com sucesso.',
            'link_simulado': f'/api/redefinir-senha/{uid}/{token}/',
        }


class RedefinirSenhaSerializer(serializers.Serializer):
    nova_senha = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        uid = self.context.get('uid')
        token = self.context.get('token')

        try:
            usuario_id = force_str(urlsafe_base64_decode(uid))
            self.usuario = Usuario.objects.get(pk=usuario_id, is_active=True)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            raise serializers.ValidationError({'token': 'Token invalido.'})

        if not default_token_generator.check_token(self.usuario, token):
            raise serializers.ValidationError({'token': 'Token invalido ou expirado.'})

        return attrs

    def save(self):
        self.usuario.set_password(self.validated_data['nova_senha'])
        self.usuario.save(update_fields=['password'])
        return {'mensagem': 'Senha redefinida com sucesso.'}

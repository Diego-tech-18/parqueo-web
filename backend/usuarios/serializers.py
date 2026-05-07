from rest_framework import serializers
from .models import Usuario


# ── Serializer principal: convierte datos Usuario ↔ JSON ──
class UsuarioSerializer(serializers.ModelSerializer):

    # password solo se escribe, nunca se devuelve al frontend
    password = serializers.CharField(write_only=True, required=False)

    # foto devuelve la URL completa ej: http://localhost:8000/media/usuarios/fotos/foto.jpg
    foto = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model  = Usuario
        fields = [
            'id',
            'email',
            'nombre',
            'apellido',
            'ci',  
            'telefono',        
            'rol',
            'activo',
            'foto',        # imagen de perfil
            'password',    # solo escritura
            'creado_en',
            
        ]
        read_only_fields = ['id', 'creado_en']

    def get_foto(self, obj):
        """Devuelve la URL completa de la foto"""
        request = self.context.get('request')
        if obj.foto and request:
            return request.build_absolute_uri(obj.foto.url)
        return None

    def create(self, validated_data):
        """Al crear usuario encripta la contraseña automáticamente"""
        password = validated_data.pop('password')
        usuario  = Usuario(**validated_data)
        usuario.set_password(password)  # encripta
        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        """Al editar solo cambia contraseña si se envió una nueva"""
        password = validated_data.pop('password', None)

        # Actualiza cada campo que llegó del frontend
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)

        # Solo encripta si se envió una nueva contraseña
        if password:
            instance.set_password(password)

        instance.save()
        return instance


# ── Serializer solo para LOGIN ──
class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)
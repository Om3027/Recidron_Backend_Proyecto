import pytest
from utils.security import get_password_hash, verify_password

class TestSecurityHash:
    """Pruebas unitarias para el algoritmo de hashing seguro (Argon2)."""

    def test_hashing_genera_cadena_valida_y_diferente(self):
        """Verifica que el hash no sea igual a la contraseña en texto plano."""
        password = "MiPasswordSeguro123*"
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 20
        assert hashed != password
        assert "$argon2" in hashed

    def test_verificacion_exitosa_con_password_correcta(self):
        """Verifica que la contraseña correcta valide exitosamente contra el hash."""
        password = "RecidronSecure2026!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_verificacion_falla_con_password_incorrecta(self):
        """Verifica que una contraseña distinta sea rechazada."""
        password = "PasswordCorrecta123"
        hashed = get_password_hash(password)
        
        assert verify_password("PasswordErronea999", hashed) is False
        assert verify_password("", hashed) is False

    def test_salting_genera_hashes_distintos_para_misma_password(self):
        """Verifica que dos llamadas con la misma contraseña generen hashes diferentes debido al salt."""
        password = "MismaPassword123"
        hash_1 = get_password_hash(password)
        hash_2 = get_password_hash(password)
        
        assert hash_1 != hash_2
        assert verify_password(password, hash_1) is True
        assert verify_password(password, hash_2) is True

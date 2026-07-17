import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers import (
    codigo_es_valido, agrupar_por_curso, resumen_curso, generar_token,
    calcular_rangos, calcular_ubicacion, formatear_ubicacion, SIN_CURSO,
)


def test_codigo_valido_exacto():
    assert codigo_es_valido("9999", "9999") is True


def test_codigo_invalido():
    assert codigo_es_valido("1234", "9999") is False


def test_codigo_vacio_o_none():
    assert codigo_es_valido("", "9999") is False
    assert codigo_es_valido(None, "9999") is False


def test_agrupar_por_curso_preserva_orden():
    ests = [
        {"nombre": "A", "curso": "11A"},
        {"nombre": "B", "curso": "11B"},
        {"nombre": "C", "curso": "11A"},
    ]
    grupos = agrupar_por_curso(ests)
    assert list(grupos.keys()) == ["11A", "11B"]
    assert [e["nombre"] for e in grupos["11A"]] == ["A", "C"]


def test_agrupar_curso_nulo_o_vacio_va_a_sin_curso():
    ests = [{"nombre": "X", "curso": None}, {"nombre": "Y", "curso": ""}]
    grupos = agrupar_por_curso(ests)
    assert grupos[SIN_CURSO] == ests


def test_resumen_curso_cuenta_presentes():
    ests = [{"presente": True}, {"presente": False}, {"presente": True}]
    assert resumen_curso(ests) == (2, 3)


def test_resumen_curso_vacio():
    assert resumen_curso([]) == (0, 0)


def test_generar_token_largo_minimo():
    assert len(generar_token()) >= 10


def test_generar_token_solo_caracteres_url_safe():
    import string
    permitidos = set(string.ascii_letters + string.digits + "-_")
    for _ in range(50):
        assert set(generar_token()) <= permitidos


def test_generar_token_no_se_repite():
    tokens = {generar_token() for _ in range(1000)}
    assert len(tokens) == 1000


def test_calcular_rangos_dos_base_mas_extras():
    ests = [
        {"nombre": "A", "cupos_adicionales": 0},   # 2 asientos: 1-2
        {"nombre": "B", "cupos_adicionales": 1},   # 3 asientos: 3-5
        {"nombre": "C", "cupos_adicionales": 3},   # 5 asientos: 6-10
    ]
    rangos = calcular_rangos(ests)
    assert [(r[1], r[2]) for r in rangos] == [(1, 2), (3, 5), (6, 10)]
    assert rangos[0][0] is ests[0]


def test_calcular_rangos_vacio():
    assert calcular_rangos([]) == []


def test_calcular_ubicacion_primera_fila():
    assert calcular_ubicacion(1, 10) == ("Fila A", 1)
    assert calcular_ubicacion(10, 10) == ("Fila A", 10)


def test_calcular_ubicacion_cambio_de_fila():
    assert calcular_ubicacion(11, 10) == ("Fila B", 1)
    assert calcular_ubicacion(3, 2) == ("Fila B", 1)


def test_calcular_ubicacion_mas_alla_de_letras():
    # 15 letras (A-O); la fila 16 se nombra por número
    assert calcular_ubicacion(31, 2) == ("Fila 16", 1)


def test_formatear_ubicacion_misma_fila():
    assert formatear_ubicacion(1, 2, 10) == "Fila A (Sillas 1 a 2)"


def test_formatear_ubicacion_cruza_filas():
    assert formatear_ubicacion(10, 11, 10) == "Fila A Silla 10 hasta Fila B Silla 1"

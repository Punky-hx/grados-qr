import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers import codigo_es_valido, agrupar_por_curso, resumen_curso, SIN_CURSO


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

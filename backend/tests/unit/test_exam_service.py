"""Tests unitarios para exam_service.py."""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4


class TestFisherYatesNoRepeats:
    """T038: El shuffle no repite preguntas en un mismo intento."""

    def test_fisher_yates_no_repeats(self):
        """Dado N preguntas, el shuffle selecciona exactamente N distintas."""
        # Creamos preguntas mock con IDs únicos
        mock_preguntas = [MagicMock(id=i) for i in range(1, 21)]

        from app.services.exam_service import _shuffle_preguntas

        result = _shuffle_preguntas(mock_preguntas, count=10)

        # Verificar que no hay repeticiones
        result_ids = [p.id for p in result]
        assert len(result_ids) == 10
        assert len(set(result_ids)) == 10  # todos únicos

    def test_fisher_yates_count_respected(self):
        """El shuffle retorna exactamente `count` preguntas."""
        mock_preguntas = [MagicMock(id=i) for i in range(1, 11)]

        from app.services.exam_service import _shuffle_preguntas

        for count in [3, 5, 7]:
            result = _shuffle_preguntas(mock_preguntas, count=count)
            assert len(result) == count


class TestScoreCalculation:
    """T039: Cálculo de puntuación y resultado aprobado/reprobado."""

    def test_score_approved(self):
        """75% de respuestas correctas con umbral 70% → aprobado."""
        from app.services.exam_service import _calculate_result

        resultado = _calculate_result(correctas=15, total=20, porcentaje_aprobacion=70.0)
        assert resultado["puntuacion"] == 15
        assert resultado["porcentaje_obtenido"] == 75.0
        assert resultado["resultado"] == "aprobado"

    def test_score_failed(self):
        """60% de respuestas correctas con umbral 70% → reprobado."""
        from app.services.exam_service import _calculate_result

        resultado = _calculate_result(correctas=12, total=20, porcentaje_aprobacion=70.0)
        assert resultado["puntuacion"] == 12
        assert resultado["porcentaje_obtenido"] == 60.0
        assert resultado["resultado"] == "reprobado"

    def test_score_exact_threshold_is_approved(self):
        """Exactamente en el umbral → aprobado (≥, no >)."""
        from app.services.exam_service import _calculate_result

        resultado = _calculate_result(correctas=14, total=20, porcentaje_aprobacion=70.0)
        assert resultado["porcentaje_obtenido"] == 70.0
        assert resultado["resultado"] == "aprobado"

    def test_score_zero_questions(self):
        """0 preguntas respondidas (total=0) no causa ZeroDivisionError."""
        from app.services.exam_service import _calculate_result

        resultado = _calculate_result(correctas=0, total=0, porcentaje_aprobacion=70.0)
        assert resultado["resultado"] == "reprobado"
        assert resultado["porcentaje_obtenido"] == 0.0

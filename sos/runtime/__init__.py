"""Intérprete local de los mismos `WorkflowSpec` que se despliegan en HappyRobot.

Sirve para (1) ejecutar el sistema completo sin Twin (simulador y dashboard en local), y
(2) testear los workflows (variables, SQL, código de los nodos) antes de desplegarlos.
Los agentes (LLM / voz) se sustituyen por *políticas* deterministas en `agents.py`.
"""

from .local import LocalRuntime, RunResult

__all__ = ["LocalRuntime", "RunResult"]

import sys
import io
import contextlib
import traceback
from typing import List, Tuple, Any

class CodeExecutor:
    """Исполнитель кода Python в песочнице.
    
    ВНИМАНИЕ: Использует exec() - небезопасно! В production используйте Docker.
    """
    
    def execute(self, code: str, inputs: List[str]) -> List[dict]:
        """Выполняет код на списке входных данных.
        
        Args:
            code: Python код для выполнения
            inputs: Список входных данных (каждый - строка)
            
        Returns:
            List[dict]: Результаты выполнения для каждого теста
        
        Предполагается, что код читает из stdin и выводит в stdout.
        """
        passed_count = 0
        results = []
        
        for i, inp in enumerate(inputs):
            # Захватываем stdout и stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            success = False
            output = ""
            error = ""
            
            try:
                # Подготавливаем входные данные
                stdin_capture = io.StringIO(inp)
                
                # Выполняем в отдельном контексте для захвата I/O
                with contextlib.redirect_stdout(stdout_capture), \
                     contextlib.redirect_stderr(stderr_capture), \
                     contextlib.redirect_stdin(stdin_capture):
                    
                    # ОПАСНО: exec() небезопасен. В production используйте Docker.
                    # Оборачиваем в try/except блок.
                    exec_globals = {}
                    try:
                        exec(code, exec_globals)
                        success = True
                    except Exception:
                        error = traceback.format_exc()
                        success = False
                
                output = stdout_capture.getvalue().strip()
                if not success:
                    # Ошибка выполнения
                    pass
                
                # Примечание: У нас нет "ожидаемых выходных данных" для скрытых тестов.
                # TaskGenerator генерирует только входные данные.
                # Поэтому мы полагаемся на LLM для проверки корректности выходных данных.
                # Собираем выходные данные и передаём Evaluator LLM для анализа.
                
                results.append({
                    "input": inp,
                    "output": output,
                    "error": error,
                    "success": success
                })
                
            except Exception as e:
                results.append({
                    "input": inp,
                    "output": "",
                    "error": str(e),
                    "success": False
                })
        
        return results

code_executor = CodeExecutor()

# --- THIS IS THE FIX ---
# We now import the specific function and class we need directly.
from google.generativeai.client import configure
from google.generativeai.generative_models import GenerativeModel
from ..config import settings


class GeminiClient:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        # We can now call configure() directly
        configure(api_key=settings.GEMINI_API_KEY)
        # And instantiate GenerativeModel() directly
        self._model = GenerativeModel(model_name)

    def generate_treatment_plan(self, disease_name: str) -> str:
        """Generates a treatment plan for a given onion crop disease."""
        prompt = f"""
        **Rol y Contexto:** Eres un Ingeniero Agrónomo altamente especializado en fitopatología del cultivo de cebolla, con reconocida trayectoria asesorando a agricultores en diversas zonas productoras del Perú. Tu lenguaje debe ser claro, directo y fácil de entender para un agricultor.

        **Diagnóstico Preliminar:** Se ha identificado una posible afectación en una planta de cebolla. El análisis sugiere '{disease_name}'.

        **Tarea:**
        Considerando el diagnóstico '{disease_name}':

        1.  **Si el diagnóstico es 'healthy_leaf' (hoja sana):**
            Tu única respuesta debe ser:
            Planta sana.

        2.  **Si el diagnóstico es una plaga o enfermedad (ej: 'alternaria', 'bul_blight', 'caterpillar', 'fusarium', 'virosis', etc.):**
            Debes proporcionar la siguiente información de manera concisa:

            a.  **Enfermedad/Plaga Identificada:** Describe muy brevemente (1-2 frases) en qué consiste '{disease_name}' y cuál es su principal impacto en la cebolla, considerando las condiciones del Perú.

            b.  **Pasos para el Manejo y Control (enfocado en Perú):** Presenta una lista numerada de acciones prácticas y prioritarias que un agricultor peruano puede implementar. Sé breve en cada paso.
                * **Confirmación Rápida en Campo:** Menciona 1-2 síntomas visuales clave para que el agricultor pueda verificar si se trata de '{disease_name}'.
                * **Primeras Acciones / Manejo Cultural:** Indica 1-2 medidas culturales o de manejo inmediato cruciales y sencillas.
                * **Opciones de Control (si indispensable):** Si es necesario, sugiere de forma general el tipo de producto (biológico o químico) que podría usarse, mencionando algún ejemplo de ingrediente activo común y de bajo riesgo disponible en Perú. Siempre recuerda la importancia de seguir las indicaciones de la etiqueta y, de ser posible, consultar con un técnico agrícola local antes de aplicar.
                * **Prevención Clave:** Un consejo fundamental para prevenir o reducir el problema en futuras siembras de cebolla en su campo.

        **Importante:** La extensión total para el caso de enfermedad/plaga (descripción + pasos) no debe ser muy larga. Prioriza la información más crítica y accionable para el agricultor. Evita detalles excesivamente técnicos a menos que sean indispensables y explícalos de forma sencilla.
        """

        response = self._model.generate_content(prompt)
        return response.text

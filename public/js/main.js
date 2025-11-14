// Definición del nuevo mensaje que vamos a repintar en el párrafo.
const NEW_MESSAGE = "Mensaje desde main.js";

/**
 * Función principal para manipular el DOM una vez que el HTML está cargado.
 * Esta función sigue las mejores prácticas de prevención de errores.
 */
function init() {
    // 1. Obtener la referencia al elemento del párrafo por su ID
    const paragraphElement = document.getElementById("idmsj");

    // 2. Verificar si el elemento existe (práctica de prevención de fallos)
    if (paragraphElement) {
        // --- Lógica de Depuración (Console Log) ---
        const oldMessage = paragraphElement.textContent;
        console.log("--- Verificación de Carga de JavaScript ---");
        console.log("Elemento encontrado con ID 'idmsj'.");
        console.log("Contenido original:", oldMessage);

        // 3. Modificar/Repintar el contenido del párrafo con el nuevo mensaje
        paragraphElement.textContent = NEW_MESSAGE;
        
        console.log("Contenido nuevo repintado:", NEW_MESSAGE);
        console.log("-----------------------------------------");
    } else {
        // Mensaje de error si el elemento no se encuentra
        console.error("ERROR CRÍTICO: No se encontró el elemento con ID 'idmsj'. Verifique el index.html.");
    }
}

// Ejecutar la función inmediatamente. Dado que el <script> está al final del <body>,
// se garantiza que el elemento 'idmsj' ya existe.
init();
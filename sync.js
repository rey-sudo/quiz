const fs = require('fs');
const path = require('path');

// Definir rutas absolutas
const origen = path.join(__dirname, 'mcp', 'output', 'all_questions.json');
const destinoDir = path.join(__dirname, 'public', 'questions');
const destinoFinal = path.join(destinoDir, 'aduanero.json');

console.log('--- [PRE-START] Copiando archivos de datos... ---');

try {
    // Asegurar que la carpeta destino existe
    if (!fs.existsSync(destinoDir)) {
        fs.mkdirSync(destinoDir, { recursive: true });
        console.log('📁 Carpeta creada: public/questions');
    }

    // Copiar el archivo de forma síncrona
    if (fs.existsSync(origen)) {
        fs.copyFileSync(origen, destinoFinal);
        console.log('✅ Archivo all_questions.json copiado correctamente.');
    } else {
        console.error('❌ Error: No se encontró el archivo en mcp/output/all_questions.json');
        // Opcional: process.exit(1) si quieres que el proceso se detenga si no hay datos
    }

    return true
    
} catch (error) {
    console.error('❌ Error crítico en prepare.js:', error);
    process.exit(1); 
}

console.log('--- [PRE-START] Finalizado con éxito ---\n');


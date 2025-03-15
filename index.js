const { generarFacturaJSON } = require("./factura");
const fs = require("fs");
const { create } = require("xmlbuilder2");

// Leer datos de la factura desde el archivo JSON
const datos = JSON.parse(fs.readFileSync("datos.json", "utf-8"));

// Validar datos antes de generar la factura
if (!datos || typeof datos !== 'object' || !datos.numeroFactura || !datos.fecha || !datos.cliente || !datos.productos) {
  console.error("❌ Error: datos.json tiene un formato incorrecto o incompleto.");
  process.exit(1);
}

// Generar la factura en JSON
const facturaJSON = generarFacturaJSON(datos.numeroFactura, datos.fecha, datos.cliente, datos.productos);

// Validar que la factura generada sea válida
if (!facturaJSON || typeof facturaJSON !== 'object' || !facturaJSON.Invoice) {
  console.error("❌ Error: La factura generada no tiene un formato válido.");
  process.exit(1);
}

// Guardar la factura en JSON
fs.writeFileSync("factura.json", JSON.stringify(facturaJSON, null, 2));

// Convertir el JSON a XML de forma segura
const facturaXML = create({ Invoice: facturaJSON.Invoice }).end({ prettyPrint: true });

// Guardar el XML en un archivo
fs.writeFileSync("factura.xml", facturaXML);

console.log("✅ Factura XML generada correctamente en factura.xml");

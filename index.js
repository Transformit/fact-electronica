const { generarFacturaJSON } = require("./factura");
const fs = require("fs");
const { create } = require("xmlbuilder2");

// Leer datos de la factura desde el archivo JSON
const datos = JSON.parse(fs.readFileSync("datos.json", "utf-8"));

// Generar la factura en JSON
const facturaJSON = generarFacturaJSON(datos.numeroFactura, datos.fecha, datos.cliente, datos.productos);

// Guardar la factura en JSON
fs.writeFileSync("factura.json", JSON.stringify(facturaJSON, null, 2));

// Convertir el JSON a XML
const facturaXML = create(facturaJSON).end({ prettyPrint: true });

// Guardar el XML en un archivo
fs.writeFileSync("factura.xml", facturaXML);

console.log("✅ Factura XML generada correctamente en factura.xml");

